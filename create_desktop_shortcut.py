#!/usr/bin/env python3
"""
Desktop Shortcut Creator for UX-MIRROR + 3D Game of Life
Creates a clickable desktop shortcut for easy access
"""

import os
import sys
from pathlib import Path
import winshell
from win32com.client import Dispatch

def create_desktop_shortcut():
    """Create a desktop shortcut for the UX-MIRROR launcher"""
    
    # Get paths
    base_path = Path.cwd()
    launcher_script = base_path / "launch_ux_mirror.py"
    launcher_bat = base_path / "launch_ux_mirror.bat"
    
    # Desktop path
    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, "UX-MIRROR + 3D Game of Life.lnk")
    
    # Determine which launcher to use
    if launcher_bat.exists():
        target = str(launcher_bat)
        icon_path = None
    elif launcher_script.exists():
        target = f'"{sys.executable}" "{launcher_script}"'
        icon_path = None
    else:
        print("❌ Error: No launcher found!")
        return False
    
    try:
        # Create shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = str(base_path)
        shortcut.Description = "UX-MIRROR + 3D Game of Life - Intelligent UX Analysis"
        
        if icon_path:
            shortcut.IconLocation = icon_path
        
        shortcut.save()
        
        print(f"✅ Desktop shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating shortcut: {e}")
        return False

def create_start_menu_shortcut():
    """Create a start menu shortcut"""
    
    try:
        # Get paths
        base_path = Path.cwd()
        launcher_bat = base_path / "launch_ux_mirror.bat"
        
        # Start menu path
        start_menu = winshell.start_menu()
        programs_path = os.path.join(start_menu, "Programs")
        shortcut_path = os.path.join(programs_path, "UX-MIRROR + 3D Game of Life.lnk")
        
        # Create shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = str(launcher_bat)
        shortcut.WorkingDirectory = str(base_path)
        shortcut.Description = "UX-MIRROR + 3D Game of Life - Intelligent UX Analysis"
        shortcut.save()
        
        print(f"✅ Start menu shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating start menu shortcut: {e}")
        return False

def main():
    """Main entry point"""
    print("🎯 UX-MIRROR Shortcut Creator")
    print("=" * 40)
    
    # Check if running on Windows
    if sys.platform != "win32":
        print("❌ This script is designed for Windows only")
        return
    
    # Try to import required modules
    try:
        import winshell
        from win32com.client import Dispatch
    except ImportError:
        print("❌ Required modules not found. Installing...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "pywin32", "winshell"])
        try:
            import winshell
            from win32com.client import Dispatch
        except ImportError:
            print("❌ Failed to install required modules")
            return
    
    # Create shortcuts
    desktop_success = create_desktop_shortcut()
    start_menu_success = create_start_menu_shortcut()
    
    if desktop_success or start_menu_success:
        print("\n🎉 Shortcuts created successfully!")
        print("You can now launch UX-MIRROR + 3D Game of Life from:")
        if desktop_success:
            print("  📍 Desktop shortcut")
        if start_menu_success:
            print("  📍 Start Menu -> Programs")
    else:
        print("\n❌ Failed to create shortcuts")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 