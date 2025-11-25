#!/usr/bin/env python3
"""
Quick MVP Test Script
=====================

Simple test script to verify UX-MIRROR v0.1.0 is working.
"""

import os
import sys
import asyncio
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    required = {
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'numpy': 'numpy',
        'anthropic': 'anthropic',
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [MISSING] {package}")
            missing.append(package)
    
    if missing:
        print(f"\n[MISSING] Dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("[OK] All dependencies installed\n")
    return True

def check_api_key():
    """Check if API key is set"""
    print("Checking API keys...")
    
    api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY')
    
    if api_key:
        print(f"  [OK] API key found ({'Anthropic' if os.getenv('ANTHROPIC_API_KEY') else 'OpenAI'})")
        print()
        return True
    else:
        print("  [MISSING] No API key found")
        print("\nSet your API key:")
        print("  Windows: $env:ANTHROPIC_API_KEY = 'your_key'")
        print("  Linux/Mac: export ANTHROPIC_API_KEY='your_key'")
        print()
        return False

async def test_screenshot_capture():
    """Test screenshot capture"""
    print("Testing screenshot capture...")
    
    try:
        from core.screenshot_analyzer import ScreenshotAnalyzer
        
        analyzer = ScreenshotAnalyzer()
        screenshot_path = await analyzer.capture_screenshot()
        
        if screenshot_path and Path(screenshot_path).exists():
            print(f"  [OK] Screenshot captured: {screenshot_path}")
            print()
            return True
        else:
            print("  [FAIL] Screenshot capture failed")
            print()
            return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        print()
        return False

async def test_basic_analysis():
    """Test basic image analysis"""
    print("Testing basic analysis...")
    
    try:
        from core.screenshot_analyzer import ScreenshotAnalyzer
        
        analyzer = ScreenshotAnalyzer()
        screenshot_path = await analyzer.capture_screenshot()
        
        if not screenshot_path:
            print("  [FAIL] No screenshot to analyze")
            return False
        
        result = await analyzer.analyze_image(screenshot_path)
        
        if result and 'quality_score' in result:
            print(f"  [OK] Analysis complete")
            print(f"    Quality Score: {result['quality_score']:.2f}")
            print(f"    UI Elements: {len(result.get('ui_elements', []))}")
            print()
            return True
        else:
            print("  [FAIL] Analysis failed")
            print()
            return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

def test_cli():
    """Test CLI availability"""
    print("Testing CLI...")
    
    try:
        from cli.main import create_parser
        
        parser = create_parser()
        print("  [OK] CLI parser created")
        print()
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        print()
        return False

def test_gui_imports():
    """Test GUI launcher imports"""
    print("Testing GUI launcher...")
    
    try:
        # Just check if we can import, don't actually start GUI
        import tkinter
        print("  [OK] tkinter available")
        
        # Check if launcher file exists
        launcher_path = Path("ux_mirror_launcher.py")
        if launcher_path.exists():
            print("  [OK] Launcher file found")
            print()
            return True
        else:
            print("  [FAIL] Launcher file not found")
            print()
            return False
    except ImportError:
        print("  [FAIL] tkinter not available (GUI won't work)")
        print()
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("UX-MIRROR v0.1.0 MVP Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Check dependencies
    results.append(("Dependencies", check_dependencies()))
    
    # Check API key
    results.append(("API Key", check_api_key()))
    
    # Test screenshot capture
    results.append(("Screenshot Capture", await test_screenshot_capture()))
    
    # Test basic analysis
    results.append(("Basic Analysis", await test_basic_analysis()))
    
    # Test CLI
    results.append(("CLI", test_cli()))
    
    # Test GUI
    results.append(("GUI Launcher", test_gui_imports()))
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! MVP is ready to use.")
        print("\nNext steps:")
        print("  1. Set your API key: $env:ANTHROPIC_API_KEY = 'your_key'")
        print("  2. Run GUI: python ux_mirror_launcher.py")
        print("  3. Or use CLI: ux-tester test --before")
    else:
        print("\n[WARNING] Some tests failed. Check the errors above.")
        print("Most issues can be fixed by:")
        print("  1. Installing dependencies: pip install -r requirements_v0.1.0.txt")
        print("  2. Setting API key: $env:ANTHROPIC_API_KEY = 'your_key'")
    
    print()

if __name__ == "__main__":
    asyncio.run(main())
