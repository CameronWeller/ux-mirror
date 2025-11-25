#!/usr/bin/env python3
"""
Create Desktop Shortcut for UX-MIRROR v0.1.0
Creates a Windows desktop shortcut to launch the GUI launcher
"""

import os
import sys
from pathlib import Path

def create_windows_shortcut():
    """Create Windows desktop shortcut"""
    try:
        import win32com.client
    except ImportError:
        print("[INFO] pywin32 not available. Creating batch file instead.")
        return create_batch_file()
    
    # Get paths
    project_root = Path(__file__).parent.absolute()
    launcher_path = project_root / "ux_mirror_launcher.py"
    python_exe = sys.executable
    desktop = Path.home() / "Desktop"
    
    # Ensure Desktop exists
    desktop.mkdir(parents=True, exist_ok=True)
    
    # Create shortcut
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut_path = desktop / "UX-MIRROR v0.1.0.lnk"
        shortcut = shell.CreateShortCut(str(shortcut_path))
        
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{launcher_path}"'
        shortcut.WorkingDirectory = str(project_root)
        shortcut.IconLocation = python_exe
        shortcut.Description = "UX-MIRROR v0.1.0 - AI-Powered UX Analysis Tool"
        
        shortcut.save()
        
        print(f"[SUCCESS] Desktop shortcut created: {shortcut_path}")
        return True
    except Exception as e:
        print(f"[INFO] Could not create .lnk shortcut: {e}")
        print("  Creating batch file instead...")
        return create_batch_file()

def create_batch_file():
    """Create batch file as fallback"""
    project_root = Path(__file__).parent.absolute()
    launcher_path = project_root / "ux_mirror_launcher.py"
    python_exe = sys.executable
    desktop = Path.home() / "Desktop"
    
    # Ensure Desktop directory exists
    desktop.mkdir(parents=True, exist_ok=True)
    
    batch_content = f"""@echo off
cd /d "{project_root}"
"{python_exe}" "{launcher_path}"
pause
"""
    
    batch_path = desktop / "UX-MIRROR v0.1.0.bat"
    with open(batch_path, 'w') as f:
        f.write(batch_content)
    
    print(f"[SUCCESS] Batch file created: {batch_path}")
    print("  Note: You can create a shortcut from this batch file manually")
    return True

def create_powershell_script():
    """Create PowerShell script as alternative"""
    project_root = Path(__file__).parent.absolute()
    launcher_path = project_root / "ux_mirror_launcher.py"
    python_exe = sys.executable
    desktop = Path.home() / "Desktop"
    
    ps_content = f"""# UX-MIRROR v0.1.0 Launcher
Set-Location "{project_root}"
& "{python_exe}" "{launcher_path}"
"""
    
    ps_path = desktop / "UX-MIRROR v0.1.0.ps1"
    with open(ps_path, 'w', encoding='utf-8') as f:
        f.write(ps_content)
    
    print(f"[SUCCESS] PowerShell script created: {ps_path}")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("UX-MIRROR v0.1.0 - Desktop Shortcut Creator")
    print("=" * 60)
    print()
    
    if os.name == 'nt':  # Windows
        print("Creating Windows desktop shortcut...")
        if create_windows_shortcut():
            print()
            print("[SUCCESS] Shortcut created successfully!")
            print("  You can now launch UX-MIRROR from your desktop")
        else:
            print()
            print("Creating alternative launcher files...")
            create_batch_file()
            create_powershell_script()
    else:
        print("Creating launcher script for non-Windows system...")
        create_powershell_script()
    
    print()
    print("=" * 60)
    print("Done!")
    print("=" * 60)

