#!/usr/bin/env python3
"""
Simple test to verify GUI components work
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tkinter():
    """Test if tkinter is available"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title("UX-MIRROR Test")
        root.geometry("400x200")
        
        label = tk.Label(root, text="✅ Tkinter is working!\n\nClose this window to continue...", 
                        font=("Arial", 14))
        label.pack(pady=50)
        
        root.mainloop()
        print("✅ Tkinter test passed!")
        return True
    except Exception as e:
        print(f"❌ Tkinter test failed: {e}")
        return False

def test_imports():
    """Test if we can import the main modules"""
    modules_to_test = [
        ("psutil", "System monitoring"),
        ("asyncio", "Async support"),
        ("threading", "Threading support"),
    ]
    
    all_passed = True
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} ({description}) - OK")
        except ImportError as e:
            print(f"❌ {module_name} ({description}) - FAILED: {e}")
            all_passed = False
    
    return all_passed

def test_ux_mirror_modules():
    """Test if UX-MIRROR modules can be imported"""
    print("\nTesting UX-MIRROR modules...")
    
    modules = [
        "ui.dark_theme",
        "core.port_manager",
        "core.adaptive_feedback",
        "core.secure_config"
    ]
    
    all_passed = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
        except ImportError as e:
            print(f"❌ {module} - FAILED: {e}")
            all_passed = False
    
    return all_passed

def main():
    print("🎯 UX-MIRROR GUI Component Test")
    print("=" * 50)
    
    # Test basic imports
    print("\n1. Testing basic dependencies...")
    basic_ok = test_imports()
    
    # Test tkinter
    print("\n2. Testing Tkinter GUI...")
    tkinter_ok = test_tkinter()
    
    # Test UX-MIRROR modules
    print("\n3. Testing UX-MIRROR modules...")
    modules_ok = test_ux_mirror_modules()
    
    # Summary
    print("\n" + "=" * 50)
    if basic_ok and tkinter_ok and modules_ok:
        print("✅ All tests passed! The GUI should work.")
        print("\nTo run the full GUI, use:")
        print("  python ux_mirror_launcher.py")
    else:
        print("❌ Some tests failed. Please install missing dependencies:")
        print("  pip install -r requirements_gui.txt")

if __name__ == "__main__":
    main() 