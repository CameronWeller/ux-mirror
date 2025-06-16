#!/usr/bin/env python3
"""
Run the UX-MIRROR GUI Application
"""

import sys
import subprocess
import importlib.util
from pathlib import Path

def check_dependency(module_name):
    """Check if a module is installed"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def install_missing_dependencies():
    """Install missing critical dependencies"""
    critical_deps = [
        'tkinter',
        'psutil',
        'asyncio',
        'pydantic',
        'aiohttp',
        'websockets'
    ]
    
    missing = []
    
    # Check tkinter separately as it's part of Python standard library
    try:
        import tkinter
    except ImportError:
        print("ERROR: tkinter is not available. Please install python3-tk:")
        print("  Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  Windows: tkinter should be included with Python")
        print("  macOS: tkinter should be included with Python")
        return False
    
    # Check other dependencies
    for dep in critical_deps[1:]:  # Skip tkinter as we already checked it
        if not check_dependency(dep):
            missing.append(dep)
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Installing missing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("Failed to install dependencies. Please install manually:")
            print(f"  pip install {' '.join(missing)}")
            return False
    
    return True

def main():
    """Main entry point"""
    print("🎯 Starting UX-MIRROR GUI...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check and install dependencies
    if not install_missing_dependencies():
        sys.exit(1)
    
    # Try to import and run the launcher
    try:
        from ux_mirror_launcher import main as launcher_main
        
        print("✅ All dependencies loaded successfully")
        print("🚀 Launching UX-MIRROR GUI...")
        
        # Run the launcher
        launcher_main()
        
    except ImportError as e:
        print(f"ERROR: Failed to import launcher: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to start GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 