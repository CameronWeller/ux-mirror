#!/usr/bin/env python3
"""
UX-MIRROR VM Environment Setup
=============================

This script sets up the VM environment for UX-MIRROR, including:
1. VirtualBox SDK installation
2. Python dependencies
3. Environment configuration
4. Test VM creation
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VMEnvironmentSetup:
    def __init__(self):
        self.vbox_path = r"C:\Program Files\Oracle\VirtualBox"
        # Check both system and local SDK paths
        self.sdk_paths = [
            os.path.join(self.vbox_path, "sdk", "bindings", "python"),
            os.path.join(os.getcwd(), "sdk", "bindings", "python")
        ]
        self.python_site_packages = self._get_site_packages_path()
        
    def _get_site_packages_path(self):
        """Get the site-packages directory for the current Python environment"""
        import site
        return site.getsitepackages()[0]
    
    def check_virtualbox_installation(self):
        """Check if VirtualBox is installed and accessible"""
        try:
            result = subprocess.run(
                ["VBoxManage", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info(f"VirtualBox found: {result.stdout.strip()}")
                return True
            return False
        except FileNotFoundError:
            logger.error("VirtualBox not found. Please install VirtualBox first.")
            return False
    
    def install_sdk_bindings(self):
        """Install VirtualBox SDK Python bindings"""
        sdk_path = None
        for path in self.sdk_paths:
            if os.path.exists(path):
                sdk_path = path
                break
        if not sdk_path:
            logger.error(f"VirtualBox SDK not found in any known location: {self.sdk_paths}")
            return False
        # Copy SDK files to site-packages
        try:
            for file in os.listdir(sdk_path):
                if file.endswith('.py'):
                    src = os.path.join(sdk_path, file)
                    dst = os.path.join(self.python_site_packages, file)
                    shutil.copy2(src, dst)
            logger.info(f"SDK bindings installed successfully from {sdk_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to install SDK bindings: {e}")
            return False
    
    def setup_environment(self):
        """Set up the VM environment"""
        # Add VirtualBox to PATH
        os.environ["PATH"] = f"{self.vbox_path};{os.environ['PATH']}"
        
        # Add SDK to Python path
        if self.sdk_paths[0] not in sys.path:
            sys.path.append(self.sdk_paths[0])
        
        # Create necessary directories
        Path("config").mkdir(exist_ok=True)
        Path("vm_templates").mkdir(exist_ok=True)
        Path("vm_snapshots").mkdir(exist_ok=True)
        
        logger.info("Environment setup completed")
        return True
    
    def verify_setup(self):
        """Verify the setup by testing VirtualBox API access"""
        try:
            import vboxapi
            vbox = vboxapi.VirtualBoxManager(None, None)
            logger.info(f"VirtualBox API test successful. Version: {vbox.vbox.version}")
            return True
        except Exception as e:
            logger.error(f"VirtualBox API test failed: {e}")
            return False
    
    def run(self):
        """Run the complete setup process"""
        logger.info("Starting VM environment setup...")
        
        if not self.check_virtualbox_installation():
            return False
            
        if not self.install_sdk_bindings():
            return False
            
        if not self.setup_environment():
            return False
            
        if not self.verify_setup():
            return False
            
        logger.info("VM environment setup completed successfully!")
        return True

if __name__ == "__main__":
    setup = VMEnvironmentSetup()
    if setup.run():
        print("\nSetup completed successfully!")
        print("\nNext steps:")
        print("1. Create a test VM: python vm_cli.py create --name test-vm")
        print("2. Start the VM: python vm_cli.py start --name test-vm")
        print("3. Check status: python vm_cli.py status --name test-vm")
    else:
        print("\nSetup failed. Please check the logs above for details.") 