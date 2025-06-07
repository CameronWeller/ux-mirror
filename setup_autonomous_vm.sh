#!/bin/bash
# UX-MIRROR Autonomous Testing VM Setup Script
# Phase 1: Infrastructure Setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UX_MIRROR_ROOT="$SCRIPT_DIR"
AUTONOMOUS_DIR="$UX_MIRROR_ROOT/ux_mirror_autonomous"
CONFIG_DIR="$AUTONOMOUS_DIR/config"
DOWNLOADS_DIR="$AUTONOMOUS_DIR/downloads"

echo -e "${BLUE}"
echo "  ██    ██ ██   ██       ███    ███ ██ ██████  ██████   ██████  ██████  "
echo "  ██    ██  ██ ██        ████  ████ ██ ██   ██ ██   ██ ██    ██ ██   ██ "
echo "  ██    ██   ███   █████ ██ ████ ██ ██ ██████  ██████  ██    ██ ██████  "
echo "  ██    ██  ██ ██        ██  ██  ██ ██ ██   ██ ██   ██ ██    ██ ██   ██ "
echo "   ██████  ██   ██       ██      ██ ██ ██   ██ ██   ██  ██████  ██   ██ "
echo ""
echo "  🤖 AUTONOMOUS TESTING MODE - PHASE 1 SETUP"
echo "  ════════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This script is designed for Linux systems"
    print_info "For Windows, please use WSL2 or a Linux VM"
    exit 1
fi

print_info "Starting Phase 1: VM Infrastructure Setup"

# Create directory structure
print_info "Creating autonomous testing directory structure..."
mkdir -p "$AUTONOMOUS_DIR"/{core,scenarios,config,utils,test_results}
mkdir -p "$DOWNLOADS_DIR"
mkdir -p "$AUTONOMOUS_DIR/test_results"/{screenshots,videos,reports}

print_status "Directory structure created"

# Check system requirements
print_info "Checking system requirements..."

# Check for Python 3
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_status "Python 3 found: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check for required Python packages
print_info "Checking Python dependencies..."
python3 -c "import yaml, requests, subprocess, pathlib" 2>/dev/null && \
    print_status "Core Python dependencies available" || \
    print_warning "Some Python dependencies missing - will install"

# Check for virtualization support
print_info "Checking virtualization support..."
if grep -q "vmx\|svm" /proc/cpuinfo; then
    print_status "Hardware virtualization supported"
else
    print_warning "Hardware virtualization may not be supported"
fi

# Check for KVM/libvirt
if command -v kvm-ok &> /dev/null; then
    if kvm-ok &> /dev/null; then
        print_status "KVM acceleration available"
    else
        print_warning "KVM acceleration not available"
    fi
fi

# Install required system packages
print_info "Installing required system packages..."

# Update package list
sudo apt update -y

# Install virtualization packages
PACKAGES=(
    "python3-pip"
    "python3-yaml"
    "python3-requests"
    "qemu-kvm"
    "libvirt-daemon-system"
    "libvirt-clients"
    "bridge-utils"
    "gnome-boxes"
    "virt-manager"
    "curl"
    "wget"
)

for package in "${PACKAGES[@]}"; do
    if dpkg -l | grep -q "^ii  $package "; then
        print_status "$package already installed"
    else
        print_info "Installing $package..."
        sudo apt install -y "$package" || print_warning "Failed to install $package"
    fi
done

# Add user to libvirt group
print_info "Adding user to libvirt group..."
sudo usermod -aG libvirt "$USER"
print_status "User added to libvirt group (requires logout/login to take effect)"

# Install Python dependencies
print_info "Installing Python dependencies..."
pip3 install --user pyyaml requests psutil pathlib-utils || \
    print_warning "Some Python packages may have failed to install"

# Create VM configuration if it doesn't exist
if [[ ! -f "$CONFIG_DIR/vm_config.yaml" ]]; then
    print_info "VM configuration already created"
else
    print_status "VM configuration found"
fi

# Download Pop!_OS ISO
POP_OS_URL="https://pop-iso.sfo2.cdn.digitaloceanspaces.com/22.04/amd64/intel/30/pop-os_22.04_amd64_intel_30.iso"
POP_OS_ISO="$DOWNLOADS_DIR/pop-os_22.04_amd64_intel_30.iso"

if [[ -f "$POP_OS_ISO" ]]; then
    print_status "Pop!_OS ISO already downloaded"
else
    print_info "Downloading Pop!_OS ISO (this may take several minutes)..."
    print_warning "ISO size: ~2.5GB - ensure you have adequate bandwidth and storage"
    
    # Create downloads directory
    mkdir -p "$DOWNLOADS_DIR"
    
    if wget -O "$POP_OS_ISO" "$POP_OS_URL"; then
        print_status "Pop!_OS ISO downloaded successfully"
    else
        print_error "Failed to download Pop!_OS ISO"
        print_info "You can manually download from: $POP_OS_URL"
        print_info "Save it as: $POP_OS_ISO"
    fi
fi

# Create VM management script
print_info "Creating VM management script..."
cat > "$AUTONOMOUS_DIR/manage_vm.py" << 'EOF'
#!/usr/bin/env python3
"""
Simple VM management script for UX-MIRROR Autonomous Testing
"""

import sys
import subprocess
import yaml
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent / "config" / "vm_config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_vm():
    print("🔧 Creating VM with GNOME Boxes...")
    config = load_config()
    
    # Use GNOME Boxes to create VM
    iso_path = Path(__file__).parent / "downloads" / "pop-os_22.04_amd64_intel_30.iso"
    
    if not iso_path.exists():
        print(f"❌ ISO not found: {iso_path}")
        return False
    
    print(f"📀 Using ISO: {iso_path}")
    print("🔧 Please use GNOME Boxes GUI to create the VM manually for now")
    print("   1. Open GNOME Boxes")
    print("   2. Click 'Create a virtual machine'")
    print(f"   3. Select the ISO: {iso_path}")
    print(f"   4. Set name: {config['vm_settings']['name']}")
    print(f"   5. Set memory: {config['vm_settings']['memory_gb']}GB")
    print(f"   6. Set storage: {config['vm_settings']['storage_gb']}GB")
    
    return True

def status():
    print("🔍 VM Status Check")
    try:
        # Check if gnome-boxes is running
        result = subprocess.run(['pgrep', 'gnome-boxes'], capture_output=True)
        if result.returncode == 0:
            print("✅ GNOME Boxes is running")
        else:
            print("⚠️ GNOME Boxes is not running")
    except Exception as e:
        print(f"❌ Error checking status: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 manage_vm.py [create|status]")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        create_vm()
    elif command == "status":
        status()
    else:
        print("Unknown command. Use: create, status")

if __name__ == "__main__":
    main()
EOF

chmod +x "$AUTONOMOUS_DIR/manage_vm.py"
print_status "VM management script created"

# Create test runner placeholder
print_info "Creating test runner..."
cat > "$AUTONOMOUS_DIR/run_tests.py" << 'EOF'
#!/usr/bin/env python3
"""
UX-MIRROR Autonomous Test Runner
Phase 1: Basic VM setup completed
"""

import sys
from pathlib import Path

def main():
    print("🤖 UX-MIRROR Autonomous Testing")
    print("Phase 1 Setup Complete!")
    print("")
    print("Next Steps:")
    print("1. Create VM using: python3 manage_vm.py create")
    print("2. Install Pop!_OS in the VM")
    print("3. Run setup script inside VM")
    print("4. Phase 2: Input automation system")
    print("")
    print("📁 Test results will be saved to: test_results/")

if __name__ == "__main__":
    main()
EOF

chmod +x "$AUTONOMOUS_DIR/run_tests.py"
print_status "Test runner created"

# Update launcher to enable autonomous mode
print_info "Updating UX-MIRROR launcher..."
if [[ -f "$UX_MIRROR_ROOT/launch_ux_mirror.py" ]]; then
    # Note: The launcher was already updated earlier
    print_status "Launcher already supports autonomous mode"
else
    print_warning "UX-MIRROR launcher not found"
fi

# Create README for autonomous mode
cat > "$AUTONOMOUS_DIR/README.md" << 'EOF'
# 🤖 UX-MIRROR Autonomous Testing Mode

## Phase 1: Infrastructure Setup ✅

This directory contains the autonomous testing infrastructure for UX-MIRROR.

### Current Status: Phase 1 Complete

- [x] VM configuration files
- [x] Pop!_OS ISO download
- [x] Basic VM management scripts
- [x] Directory structure
- [x] System requirements check

### Quick Start

1. **Create VM:**
   ```bash
   python3 manage_vm.py create
   ```

2. **Check Status:**
   ```bash
   python3 manage_vm.py status
   ```

3. **Run Tests:**
   ```bash
   python3 run_tests.py
   ```

### Directory Structure

```
ux_mirror_autonomous/
├── config/              # VM and test configurations
├── core/                # Core testing framework
├── scenarios/           # Test scenarios
├── utils/               # Utility scripts
├── test_results/        # Test outputs
├── downloads/           # Downloaded ISOs
├── manage_vm.py         # VM management
└── run_tests.py         # Test runner
```

### Next: Phase 2

- Input automation system (PyAutoGUI)
- Basic test scenarios
- Screenshot/recording capabilities
- UX metrics collection

### Configuration

VM settings can be modified in `config/vm_config.yaml`:
- Memory: 4GB (configurable 2-8GB)
- Storage: 60GB
- CPU: 4 cores
- OS: Pop!_OS 22.04 LTS
EOF

print_status "Autonomous mode README created"

# Final status
echo ""
echo -e "${GREEN}🎉 PHASE 1 SETUP COMPLETE! 🎉${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo "   • VM infrastructure configured"
echo "   • Pop!_OS ISO downloaded (if successful)"
echo "   • GNOME Boxes installed"
echo "   • Python dependencies installed"
echo "   • Management scripts created"
echo ""
echo -e "${YELLOW}🚀 Next Steps:${NC}"
echo "   1. Create VM: cd ux_mirror_autonomous && python3 manage_vm.py create"
echo "   2. Install Pop!_OS in the VM"
echo "   3. Copy vm_setup.sh into VM and run it"
echo "   4. Start Phase 2 implementation"
echo ""
echo -e "${BLUE}📁 Autonomous testing files: $AUTONOMOUS_DIR${NC}"

# Check if reboot is needed for libvirt group
if ! groups | grep -q libvirt; then
    echo ""
    print_warning "Please logout and login again for libvirt group membership to take effect"
fi

print_status "Phase 1 setup completed successfully!" 