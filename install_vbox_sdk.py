#!/usr/bin/env python3
"""
VirtualBox SDK Installer
=======================

Downloads and installs the VirtualBox SDK for Python integration.
"""

import os
import sys
import shutil
import zipfile
import urllib.request
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VirtualBoxSDKInstaller:
    def __init__(self):
        self.vbox_path = r"C:\Program Files\Oracle\VirtualBox"
        self.sdk_url = "https://download.virtualbox.org/virtualbox/7.0.18/VirtualBoxSDK-7.0.18-162988.zip"
        self.temp_dir = Path("temp_sdk")
        self.sdk_dir = Path("sdk")  # Local SDK directory
        self.python_site_packages = self._get_site_packages_path()
        
    def _get_site_packages_path(self):
        """Get the site-packages directory for the current Python environment"""
        import site
        return site.getsitepackages()[0]
        
    def download_sdk(self):
        """Download the VirtualBox SDK"""
        logger.info("Downloading VirtualBox SDK...")
        
        try:
            # Create temp directory
            self.temp_dir.mkdir(exist_ok=True)
            
            # Download SDK
            zip_path = self.temp_dir / "sdk.zip"
            urllib.request.urlretrieve(self.sdk_url, zip_path)
            
            logger.info("SDK downloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download SDK: {e}")
            return False
    
    def extract_sdk(self):
        """Extract the SDK files"""
        logger.info("Extracting SDK files...")
        
        try:
            zip_path = self.temp_dir / "sdk.zip"
            
            # Create SDK directory if it doesn't exist
            self.sdk_dir.mkdir(exist_ok=True)
            
            # Extract files
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # Copy SDK files to local directory
            sdk_source = self.temp_dir / "sdk"
            if sdk_source.exists():
                for item in sdk_source.iterdir():
                    if item.is_file():
                        shutil.copy2(item, self.sdk_dir / item.name)
                    else:
                        shutil.copytree(item, self.sdk_dir / item.name, dirs_exist_ok=True)
            
            # Copy Python bindings to site-packages
            bindings_dir = self.sdk_dir / "bindings" / "python"
            if bindings_dir.exists():
                for file in bindings_dir.glob("*.py"):
                    shutil.copy2(file, self.python_site_packages / file.name)
            
            logger.info("SDK files extracted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to extract SDK: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def run(self):
        """Run the complete installation process"""
        logger.info("Starting VirtualBox SDK installation...")
        
        if not self.download_sdk():
            return False
            
        if not self.extract_sdk():
            return False
            
        self.cleanup()
        
        logger.info("VirtualBox SDK installation completed successfully!")
        return True

if __name__ == "__main__":
    installer = VirtualBoxSDKInstaller()
    if installer.run():
        print("\nSDK installation completed successfully!")
        print("\nNext steps:")
        print("1. Run setup_vm_environment.py to complete the setup")
    else:
        print("\nSDK installation failed. Please check the logs above for details.") 