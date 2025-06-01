#!/usr/bin/env python3
"""
UX-MIRROR VM Environment Setup
=============================

Setup script for configuring the VM orchestrator environment.
Checks dependencies, initializes directories, and validates configuration.

Author: UX-MIRROR System
Version: 1.0.0
"""

import os
import sys
import json
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🚀 UX-MIRROR VM Environment Setup")
    print("=" * 60)
    print()

def print_step(step: str, description: str):
    """Print setup step"""
    print(f"📋 Step: {step}")
    print(f"   {description}")
    print()

def check_python_version() -> bool:
    """Check if Python version is compatible"""
    print_step("Python Version Check", "Verifying Python 3.11+ is installed")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Requires 3.11+")
        print("   Please upgrade Python to 3.11 or higher")
        return False

def check_virtualbox() -> bool:
    """Check if VirtualBox is installed"""
    print_step("VirtualBox Check", "Verifying VirtualBox installation")
    
    try:
        # Check VBoxManage command
        result = subprocess.run(
            ["VBoxManage", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ VirtualBox {version} - Installed")
            return True
        else:
            print("   ❌ VirtualBox not found")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ VirtualBox not found or not in PATH")
        print("   Please install VirtualBox 7.0+ from https://www.virtualbox.org/")
        return False

def check_virtualization_support() -> bool:
    """Check if hardware virtualization is enabled"""
    print_step("Virtualization Support", "Checking hardware virtualization")
    
    system = platform.system()
    
    if system == "Windows":
        try:
            # Check for Hyper-V and VT-x
            result = subprocess.run(
                ["systeminfo"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout.lower()
            
            if "hyper-v requirements" in output:
                if "virtualization enabled in firmware: yes" in output:
                    print("   ✅ Hardware virtualization enabled")
                    return True
                else:
                    print("   ⚠️  Hardware virtualization may not be enabled")
                    print("   Please enable VT-x/AMD-V in BIOS/UEFI settings")
                    return False
            else:
                print("   ⚠️  Unable to detect virtualization status")
                print("   Please ensure VT-x/AMD-V is enabled in BIOS")
                return True  # Assume it's okay
                
        except subprocess.TimeoutExpired:
            print("   ⚠️  Timeout checking virtualization support")
            return True
            
    elif system == "Linux":
        try:
            # Check /proc/cpuinfo for virtualization flags
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()
                
            if "vmx" in cpuinfo or "svm" in cpuinfo:
                print("   ✅ Hardware virtualization supported")
                return True
            else:
                print("   ❌ Hardware virtualization not detected")
                return False
                
        except FileNotFoundError:
            print("   ⚠️  Unable to check virtualization support")
            return True
    else:
        print("   ⚠️  Virtualization check not supported on this platform")
        return True

def check_memory_requirements() -> bool:
    """Check if system has sufficient memory"""
    print_step("Memory Check", "Verifying system memory requirements")
    
    try:
        import psutil
        
        total_memory = psutil.virtual_memory().total / (1024**3)  # GB
        available_memory = psutil.virtual_memory().available / (1024**3)  # GB
        
        print(f"   Total Memory: {total_memory:.1f} GB")
        print(f"   Available Memory: {available_memory:.1f} GB")
        
        if total_memory >= 16:
            print("   ✅ Sufficient memory for VM operations")
            return True
        elif total_memory >= 8:
            print("   ⚠️  Limited memory - recommend 16GB+ for multiple VMs")
            return True
        else:
            print("   ❌ Insufficient memory - minimum 8GB required")
            return False
            
    except ImportError:
        print("   ⚠️  Unable to check memory (psutil not available)")
        return True

def check_disk_space() -> bool:
    """Check available disk space"""
    print_step("Disk Space Check", "Verifying available disk space")
    
    try:
        import psutil
        
        disk_usage = psutil.disk_usage('.')
        free_space = disk_usage.free / (1024**3)  # GB
        total_space = disk_usage.total / (1024**3)  # GB
        
        print(f"   Total Disk Space: {total_space:.1f} GB")
        print(f"   Free Disk Space: {free_space:.1f} GB")
        
        if free_space >= 100:
            print("   ✅ Sufficient disk space")
            return True
        elif free_space >= 50:
            print("   ⚠️  Limited disk space - recommend 100GB+ free")
            return True
        else:
            print("   ❌ Insufficient disk space - minimum 50GB free required")
            return False
            
    except ImportError:
        print("   ⚠️  Unable to check disk space (psutil not available)")
        return True

def install_dependencies() -> bool:
    """Install required Python packages"""
    print_step("Dependencies Installation", "Installing required Python packages")
    
    requirements_files = [
        "requirements-vm-core.txt",
        "requirements-vm.txt"
    ]
    
    # Use core requirements if full requirements fail
    for req_file in requirements_files:
        if os.path.exists(req_file):
            try:
                print(f"   Installing packages from {req_file}...")
                
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", req_file],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    print(f"   ✅ Dependencies installed from {req_file}")
                    return True
                else:
                    print(f"   ⚠️  Some packages from {req_file} failed to install:")
                    print(f"   {result.stderr}")
                    
                    if req_file == "requirements-vm-core.txt":
                        print("   ❌ Core dependencies failed - setup cannot continue")
                        return False
                    else:
                        print("   Falling back to core requirements...")
                        continue
                        
            except subprocess.TimeoutExpired:
                print(f"   ❌ Timeout installing from {req_file}")
                if req_file == "requirements-vm-core.txt":
                    return False
                else:
                    continue
    
    print("   ❌ No requirements files found")
    return False

def create_directories() -> bool:
    """Create necessary directories"""
    print_step("Directory Setup", "Creating required directories")
    
    directories = [
        "config",
        "logs",
        "vms",
        "snapshots",
        "iso",
        "temp"
    ]
    
    try:
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            print(f"   📁 Created: {directory}/")
        
        print("   ✅ All directories created")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to create directories: {e}")
        return False

def validate_configuration() -> bool:
    """Validate configuration files"""
    print_step("Configuration Validation", "Checking configuration files")
    
    config_file = "config/vm_orchestrator.json"
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Basic validation
            required_sections = [
                "vm_defaults",
                "resource_limits", 
                "automation",
                "networking"
            ]
            
            for section in required_sections:
                if section not in config:
                    print(f"   ❌ Missing configuration section: {section}")
                    return False
            
            print("   ✅ Configuration file is valid")
            return True
            
        except json.JSONDecodeError as e:
            print(f"   ❌ Invalid JSON in configuration file: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Error reading configuration: {e}")
            return False
    else:
        print("   ⚠️  Configuration file not found - will be created with defaults")
        return True

def test_vm_operations() -> bool:
    """Test basic VM operations"""
    print_step("VM Operations Test", "Testing basic VirtualBox operations")
    
    try:
        # Try to list VMs
        result = subprocess.run(
            ["VBoxManage", "list", "vms"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            vm_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            print(f"   ✅ VirtualBox operations working ({vm_count} existing VMs)")
            return True
        else:
            print(f"   ❌ VirtualBox operations failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ Timeout testing VirtualBox operations")
        return False
    except Exception as e:
        print(f"   ❌ Error testing VirtualBox operations: {e}")
        return False

def create_sample_scripts() -> bool:
    """Create sample usage scripts"""
    print_step("Sample Scripts", "Creating sample usage scripts")
    
    try:
        # Create quick start script
        quick_start = """#!/usr/bin/env python3
# Quick start script for UX-MIRROR VM Orchestrator

import asyncio
from vm_orchestrator import VMOrchestrator, VMConfiguration

async def main():
    orchestrator = VMOrchestrator()
    await orchestrator.initialize()
    
    print("VM Orchestrator started successfully!")
    print("System status:", orchestrator.get_system_status())

if __name__ == "__main__":
    asyncio.run(main())
"""
        
        with open("quick_start_example.py", "w") as f:
            f.write(quick_start)
        
        # Create CLI examples
        cli_examples = """# UX-MIRROR VM CLI Examples

# Create a new VM
python vm_cli.py create --name test-vm --memory 4096 --disk 50

# Start the VM
python vm_cli.py start --name test-vm

# Check VM status
python vm_cli.py status --name test-vm

# List all VMs
python vm_cli.py list

# Take a screenshot and analyze UI
python vm_cli.py screenshot --name test-vm --analyze

# Execute a command (requires SSH setup in VM)
python vm_cli.py exec --name test-vm --command "dir" --username admin --password yourpass

# Create a snapshot
python vm_cli.py snapshot --name test-vm --snapshot-name "clean-state"

# Stop the VM
python vm_cli.py stop --name test-vm

# System status
python vm_cli.py system-status
"""
        
        with open("CLI_EXAMPLES.md", "w") as f:
            f.write(cli_examples)
        
        print("   📄 Created: quick_start_example.py")
        print("   📄 Created: CLI_EXAMPLES.md")
        print("   ✅ Sample scripts created")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to create sample scripts: {e}")
        return False

def print_final_instructions():
    """Print final setup instructions"""
    print()
    print("=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Start the VM orchestrator:")
    print("   python vm_orchestrator.py")
    print()
    print("2. Or use the CLI to create your first VM:")
    print("   python vm_cli.py create --name my-first-vm")
    print("   python vm_cli.py start --name my-first-vm")
    print()
    print("3. Check out the examples:")
    print("   python quick_start_example.py")
    print("   cat CLI_EXAMPLES.md")
    print()
    print("4. View system status:")
    print("   python vm_cli.py system-status")
    print()
    print("For more help, see README.md or run:")
    print("   python vm_cli.py --help")
    print()

def main():
    """Main setup function"""
    print_header()
    
    checks = [
        ("Python Version", check_python_version),
        ("VirtualBox", check_virtualbox),
        ("Virtualization Support", check_virtualization_support),
        ("Memory Requirements", check_memory_requirements),
        ("Disk Space", check_disk_space),
        ("Dependencies", install_dependencies),
        ("Directory Structure", create_directories),
        ("Configuration", validate_configuration),
        ("VM Operations", test_vm_operations),
        ("Sample Scripts", create_sample_scripts)
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            print(f"   ❌ Error in {check_name}: {e}")
            failed_checks.append(check_name)
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 Setup Summary")
    print("=" * 60)
    
    if not failed_checks:
        print("✅ All checks passed! UX-MIRROR VM environment is ready.")
        print_final_instructions()
        return 0
    else:
        print(f"❌ {len(failed_checks)} check(s) failed:")
        for check in failed_checks:
            print(f"   - {check}")
        print()
        print("Please resolve the failed checks and run setup again.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 