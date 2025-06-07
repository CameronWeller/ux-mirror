#!/usr/bin/env python3
"""
VM Manager for UX-MIRROR Autonomous Testing
Phase 1: Infrastructure Setup

Handles VM creation, configuration, and lifecycle management.
"""

import os
import sys
import subprocess
import yaml
import time
import logging
import requests
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class VMManager:
    """Manages VM lifecycle for autonomous testing"""
    
    def __init__(self, config_path: str = None):
        self.base_path = Path(__file__).parent.parent
        self.config_path = config_path or self.base_path / "config" / "vm_config.yaml"
        self.config = self.load_config()
        self.vm_name = self.config['vm_settings']['name']
        
    def load_config(self) -> Dict[str, Any]:
        """Load VM configuration from YAML"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load VM config: {e}")
            raise
    
    def check_virtualization_support(self) -> bool:
        """Check if virtualization is supported on the host"""
        try:
            # Check for hardware virtualization support
            result = subprocess.run(['lscpu'], capture_output=True, text=True)
            if 'Virtualization:' in result.stdout:
                logger.info("✅ Hardware virtualization supported")
                return True
            else:
                logger.warning("⚠️ Hardware virtualization may not be supported")
                return False
        except Exception as e:
            logger.error(f"Failed to check virtualization support: {e}")
            return False
    
    def check_gnome_boxes(self) -> bool:
        """Check if GNOME Boxes is installed"""
        try:
            result = subprocess.run(['which', 'gnome-boxes'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ GNOME Boxes found")
                return True
            else:
                logger.info("⚠️ GNOME Boxes not found")
                return False
        except Exception as e:
            logger.error(f"Failed to check GNOME Boxes: {e}")
            return False
    
    def install_gnome_boxes(self) -> bool:
        """Install GNOME Boxes if not present"""
        try:
            logger.info("📦 Installing GNOME Boxes...")
            result = subprocess.run([
                'sudo', 'apt', 'update', '&&', 
                'sudo', 'apt', 'install', '-y', 'gnome-boxes'
            ], shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ GNOME Boxes installed successfully")
                return True
            else:
                logger.error(f"❌ Failed to install GNOME Boxes: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to install GNOME Boxes: {e}")
            return False
    
    def download_pop_os_iso(self) -> str:
        """Download Pop!_OS ISO if not present"""
        iso_url = self.config['iso_download']['url']
        iso_filename = os.path.basename(iso_url)
        iso_path = self.base_path / "downloads" / iso_filename
        
        # Create downloads directory
        iso_path.parent.mkdir(exist_ok=True)
        
        if iso_path.exists():
            logger.info(f"✅ Pop!_OS ISO already exists: {iso_path}")
            return str(iso_path)
        
        try:
            logger.info(f"📥 Downloading Pop!_OS ISO from {iso_url}")
            logger.info("⏳ This may take several minutes...")
            
            response = requests.get(iso_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(iso_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress indicator
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r📥 Downloaded: {percent:.1f}%", end='', flush=True)
            
            print()  # New line after progress
            logger.info(f"✅ Pop!_OS ISO downloaded: {iso_path}")
            return str(iso_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to download Pop!_OS ISO: {e}")
            raise
    
    def create_vm(self, memory_gb: int = None) -> bool:
        """Create a new VM with specified configuration"""
        try:
            # Use provided memory or default from config
            memory = memory_gb or self.config['vm_settings']['memory_gb']
            
            # Download ISO first
            iso_path = self.download_pop_os_iso()
            
            logger.info(f"🔧 Creating VM: {self.vm_name}")
            logger.info(f"   Memory: {memory}GB")
            logger.info(f"   CPU Cores: {self.config['vm_settings']['cpu_cores']}")
            logger.info(f"   Storage: {self.config['vm_settings']['storage_gb']}GB")
            
            # Create VM using GNOME Boxes command line
            cmd = [
                'gnome-boxes',
                '--create',
                f'--name={self.vm_name}',
                f'--memory={memory * 1024}',  # Convert to MB
                f'--disk-size={self.config["vm_settings"]["storage_gb"]}',
                f'--cpu-cores={self.config["vm_settings"]["cpu_cores"]}',
                iso_path
            ]
            
            logger.info(f"🚀 Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ VM created successfully")
                return True
            else:
                logger.error(f"❌ Failed to create VM: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create VM: {e}")
            return False
    
    def start_vm(self) -> bool:
        """Start the VM"""
        try:
            logger.info(f"▶️ Starting VM: {self.vm_name}")
            
            result = subprocess.run([
                'gnome-boxes', '--start', self.vm_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ VM started successfully")
                return True
            else:
                logger.error(f"❌ Failed to start VM: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start VM: {e}")
            return False
    
    def stop_vm(self) -> bool:
        """Stop the VM"""
        try:
            logger.info(f"⏹️ Stopping VM: {self.vm_name}")
            
            result = subprocess.run([
                'gnome-boxes', '--stop', self.vm_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ VM stopped successfully")
                return True
            else:
                logger.error(f"❌ Failed to stop VM: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to stop VM: {e}")
            return False
    
    def delete_vm(self) -> bool:
        """Delete the VM"""
        try:
            logger.info(f"🗑️ Deleting VM: {self.vm_name}")
            
            result = subprocess.run([
                'gnome-boxes', '--delete', self.vm_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ VM deleted successfully")
                return True
            else:
                logger.error(f"❌ Failed to delete VM: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete VM: {e}")
            return False
    
    def get_vm_status(self) -> str:
        """Get current VM status"""
        try:
            result = subprocess.run([
                'gnome-boxes', '--list'
            ], capture_output=True, text=True)
            
            if self.vm_name in result.stdout:
                if "running" in result.stdout.lower():
                    return "running"
                elif "stopped" in result.stdout.lower():
                    return "stopped"
                else:
                    return "unknown"
            else:
                return "not_found"
                
        except Exception as e:
            logger.error(f"Failed to get VM status: {e}")
            return "error"
    
    def setup_vm_environment(self) -> bool:
        """Setup the VM environment after initial creation"""
        try:
            logger.info("🔧 Setting up VM environment...")
            
            # Wait for VM to be ready
            logger.info("⏳ Waiting for VM to be ready...")
            time.sleep(30)
            
            # Here we would normally run setup commands via SSH or guest additions
            # For now, we'll create a setup script that can be run manually
            setup_script = self.create_setup_script()
            logger.info(f"📝 Setup script created: {setup_script}")
            logger.info("🔧 Run this script inside the VM to complete setup")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup VM environment: {e}")
            return False
    
    def create_setup_script(self) -> str:
        """Create a setup script for the VM"""
        script_content = """#!/bin/bash
# UX-MIRROR Autonomous Testing VM Setup Script
# Run this inside the Pop!_OS VM

set -e

echo "🚀 Setting up UX-MIRROR Autonomous Testing Environment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system packages
echo "📦 Installing system packages..."
sudo apt install -y \\
    python3 python3-pip python3-tk \\
    git curl wget build-essential \\
    cmake ninja-build \\
    vulkan-tools vulkan-validationlayers-dev spirv-tools \\
    xdotool scrot imagemagick \\
    vnc4server x11vnc

# Install Python packages
echo "🐍 Installing Python packages..."
pip3 install --user \\
    pyautogui opencv-python pillow \\
    psutil selenium playwright \\
    pytest requests pyyaml \\
    numpy matplotlib

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python3 -m playwright install

# Create test directories
echo "📁 Creating test directories..."
mkdir -p ~/test_results/screenshots
mkdir -p ~/test_results/videos
mkdir -p ~/test_results/reports

# Setup PyAutoGUI failsafe
echo "🛡️ Setting up PyAutoGUI safety..."
python3 -c "
import pyautogui
pyautogui.FAILSAFE = True
print('PyAutoGUI failsafe enabled')
"

# Create desktop shortcut for UX-MIRROR
echo "🖥️ Creating desktop shortcut..."
cat > ~/Desktop/ux-mirror-autonomous.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=UX-MIRROR Autonomous
Comment=UX-MIRROR Autonomous Testing
Exec=python3 ~/ux-mirror/ux_mirror_autonomous/run_tests.py
Icon=utilities-terminal
Terminal=true
Categories=Development;
EOF

chmod +x ~/Desktop/ux-mirror-autonomous.desktop

echo "✅ VM setup completed!"
echo "🎯 You can now run autonomous tests from the desktop shortcut"
"""
        
        script_path = self.base_path / "vm_setup.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        return str(script_path)

def main():
    """Main function for testing VM manager"""
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        vm_manager = VMManager()
        
        print("🔍 Checking system requirements...")
        
        # Check virtualization support
        if not vm_manager.check_virtualization_support():
            print("⚠️ Warning: Virtualization support may be limited")
        
        # Check GNOME Boxes
        if not vm_manager.check_gnome_boxes():
            print("📦 Installing GNOME Boxes...")
            if not vm_manager.install_gnome_boxes():
                print("❌ Failed to install GNOME Boxes")
                return False
        
        print("✅ System requirements check completed")
        
        # Check if VM already exists
        status = vm_manager.get_vm_status()
        print(f"🔍 VM Status: {status}")
        
        if status == "not_found":
            print("🔧 Creating new VM...")
            if vm_manager.create_vm():
                print("✅ VM created successfully")
                if vm_manager.setup_vm_environment():
                    print("✅ VM environment setup completed")
            else:
                print("❌ Failed to create VM")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"VM Manager failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 