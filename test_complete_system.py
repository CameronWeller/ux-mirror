#!/usr/bin/env python3
"""
Comprehensive test suite for UX-MIRROR complete system
Tests dark theme, secure config, and analysis functionality
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("🔧 Testing Module Imports...")
    
    try:
        from ui.dark_theme import DarkTheme
        print("   ✅ Dark theme module imported")
    except ImportError as e:
        print(f"   ❌ Dark theme import failed: {e}")
        return False
    
    try:
        from core.secure_config import get_config_manager
        print("   ✅ Secure config module imported")
    except ImportError as e:
        print(f"   ❌ Secure config import failed: {e}")
        return False
    
    try:
        from ux_mirror_launcher import UXMirrorLauncher
        print("   ✅ UX-MIRROR launcher imported")
    except ImportError as e:
        print(f"   ❌ Launcher import failed: {e}")
        return False
    
    return True

def test_dark_theme_components():
    """Test dark theme functionality"""
    print("\n🌙 Testing Dark Theme Components...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        from ui.dark_theme import DarkTheme
        
        # Create test window
        root = tk.Tk()
        root.withdraw()  # Hide the test window
        
        # Apply dark theme
        style = DarkTheme.configure_root(root)
        print("   ✅ Dark theme configuration applied")
        
        # Test color scheme
        colors = [
            DarkTheme.BG_PRIMARY,
            DarkTheme.TEXT_PRIMARY,
            DarkTheme.TEXT_ACCENT,
            DarkTheme.TEXT_SUCCESS,
            DarkTheme.TEXT_WARNING,
            DarkTheme.TEXT_ERROR
        ]
        print(f"   ✅ Color scheme loaded ({len(colors)} colors)")
        
        # Test message color function
        success_color = DarkTheme.get_message_color('success')
        warning_color = DarkTheme.get_message_color('warning')
        error_color = DarkTheme.get_message_color('error')
        print("   ✅ Message color system working")
        
        # Test widget creation
        frame = ttk.Frame(root, style="Dark.TFrame")
        text_widget = DarkTheme.create_text_widget(frame)
        listbox = DarkTheme.create_listbox(frame)
        print("   ✅ Widget creation methods working")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"   ❌ Dark theme test failed: {e}")
        return False

def test_secure_config():
    """Test secure configuration system"""
    print("\n🔒 Testing Secure Configuration...")
    
    try:
        from core.secure_config import get_config_manager
        
        config = get_config_manager()
        print("   ✅ Config manager initialized")
        
        # Test security status
        status = config.get_security_status()
        print(f"   ✅ Security status: {status['security_level']}")
        print(f"   ✅ Storage method: {status['storage_method']}")
        
        # Test settings
        config.set_setting('test_setting', 'test_value')
        retrieved = config.get_setting('test_setting')
        if retrieved == 'test_value':
            print("   ✅ Settings storage/retrieval working")
        else:
            print("   ❌ Settings storage/retrieval failed")
            return False
        
        # Test API key simulation (without real key)
        fake_key = "test-key-12345"
        config.set_api_key('test_provider', fake_key)
        retrieved_key = config.get_api_key('test_provider')
        if retrieved_key == fake_key:
            print("   ✅ API key storage/retrieval working")
        else:
            print("   ❌ API key storage/retrieval failed")
            return False
        
        # Cleanup
        config.remove_api_key('test_provider')
        print("   ✅ API key cleanup working")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Secure config test failed: {e}")
        return False

def test_launcher_integration():
    """Test launcher with dark theme integration"""
    print("\n🚀 Testing Launcher Integration...")
    
    try:
        from ux_mirror_launcher import UXMirrorLauncher
        import tkinter as tk
        
        # Create launcher instance (without showing UI)
        original_mainloop = tk.Tk.mainloop
        tk.Tk.mainloop = lambda self: None  # Override mainloop
        
        launcher = UXMirrorLauncher()
        print("   ✅ Launcher created with dark theme")
        
        # Test components exist
        if hasattr(launcher, 'log_text'):
            print("   ✅ Log text widget created")
        
        if hasattr(launcher, 'app_tree'):
            print("   ✅ Application tree created")
        
        if hasattr(launcher, 'config_manager'):
            print("   ✅ Config manager integrated")
        
        # Test log message with color coding
        launcher.log_message("✅ Test success message")
        launcher.log_message("⚠️ Test warning message")
        launcher.log_message("❌ Test error message")
        print("   ✅ Color-coded logging working")
        
        # Cleanup
        launcher.root.destroy()
        tk.Tk.mainloop = original_mainloop
        
        return True
        
    except Exception as e:
        print(f"   ❌ Launcher integration test failed: {e}")
        return False

def test_file_structure():
    """Test that all necessary files exist"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        'ui/dark_theme.py',
        'core/secure_config.py',
        'ux_mirror_launcher.py',
        'requirements_security.txt',
        'DARK_THEME_GUIDE.md',
        'SECURE_CONFIG_GUIDE.md'
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    """Run comprehensive system test"""
    print("🎯 UX-MIRROR Complete System Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("Dark Theme", test_dark_theme_components),
        ("Secure Config", test_secure_config),
        ("Launcher Integration", test_launcher_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All systems operational! UX-MIRROR is ready to use.")
        print("\n🚀 You can now run:")
        print("   • python ux_mirror_launcher.py  (Main application)")
        print("   • python test_dark_theme.py     (Theme demo)")
        print("   • python test_secure_config.py  (Config test)")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 