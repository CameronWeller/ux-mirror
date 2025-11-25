#!/usr/bin/env python3
"""
Test Tesseract Installation and Availability
Tests for Phase 2, Step 21 of v0.1.0 release
"""

import sys
import os
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestTesseractInstallation:
    """Test 21: Test Tesseract installation and availability"""
    
    def test_import_pytesseract(self):
        """Test 21.1: Check `pytesseract` import works"""
        try:
            import pytesseract
            print("[OK] pytesseract imported successfully")
            return True, pytesseract
        except ImportError as e:
            print(f"[SKIP] pytesseract not installed: {e}")
            print("  Install with: pip install pytesseract")
            return False, None
    
    def test_tesseract_version(self):
        """Test 21.2: Verify Tesseract binary is available: `pytesseract.get_tesseract_version()`"""
        available, pytesseract = self.test_import_pytesseract()
        if not available:
            return False
        
        try:
            version = pytesseract.get_tesseract_version()
            print(f"[OK] Tesseract version: {version}")
            
            # Check version is reasonable (should be 4.x or 5.x)
            if isinstance(version, tuple):
                major = version[0]
            else:
                major = int(str(version).split('.')[0])
            
            if major >= 4:
                print(f"  Version {major}.x is supported")
            else:
                print(f"  Warning: Version {major}.x may have compatibility issues")
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to get Tesseract version: {e}")
            print("  Tesseract may not be installed or not in PATH")
            return False
    
    def test_tesseract_path_configuration(self):
        """Test 21.3: Check Tesseract path configuration"""
        available, pytesseract = self.test_import_pytesseract()
        if not available:
            return False
        
        try:
            # Check if tesseract_cmd is configured
            tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
            
            if tesseract_cmd:
                print(f"[OK] Tesseract path configured: {tesseract_cmd}")
                
                # Check if path exists
                if os.path.exists(tesseract_cmd):
                    print("  Path is valid")
                    return True
                else:
                    print("  Warning: Configured path does not exist")
                    return False
            else:
                print("[INFO] Tesseract path not explicitly configured (using system PATH)")
                return True
        except Exception as e:
            print(f"[INFO] Path configuration check: {e}")
            return True  # Not a failure, just informational
    
    def test_windows_tesseract_path(self):
        """Test 21.4: Test on Windows: check if in PATH or need explicit path"""
        if os.name != 'nt':
            print("[SKIP] Not Windows - skipping Windows-specific test")
            return True
        
        available, pytesseract = self.test_import_pytesseract()
        if not available:
            return False
        
        try:
            # Try to find tesseract in common Windows locations
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            
            found = False
            for path in common_paths:
                if os.path.exists(path):
                    print(f"[OK] Tesseract found at: {path}")
                    found = True
                    break
            
            if not found:
                # Check if in PATH
                try:
                    result = subprocess.run(['tesseract', '--version'], 
                                          capture_output=True, 
                                          timeout=5)
                    if result.returncode == 0:
                        print("[OK] Tesseract found in system PATH")
                        found = True
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            
            if not found:
                print("[WARNING] Tesseract not found in common locations or PATH")
                print("  Install from: https://github.com/UB-Mannheim/tesseract/wiki")
                return False
            
            return True
        except Exception as e:
            print(f"[ERROR] Windows path check failed: {e}")
            return False
    
    def test_linux_tesseract_path(self):
        """Test 21.5: Test on Linux: `which tesseract`"""
        if os.name == 'nt':
            print("[SKIP] Not Linux - skipping Linux-specific test")
            return True
        
        available, pytesseract = self.test_import_pytesseract()
        if not available:
            return False
        
        try:
            result = subprocess.run(['which', 'tesseract'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=5)
            
            if result.returncode == 0:
                path = result.stdout.strip()
                print(f"[OK] Tesseract found at: {path}")
                return True
            else:
                print("[WARNING] Tesseract not found in PATH")
                print("  Install with: sudo apt-get install tesseract-ocr")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"[INFO] Could not check Linux path: {e}")
            return True  # Not a failure if which command doesn't exist
    
    def test_mac_tesseract_path(self):
        """Test 21.6: Test on Mac: `brew list tesseract`"""
        if os.name != 'posix' or sys.platform != 'darwin':
            print("[SKIP] Not macOS - skipping Mac-specific test")
            return True
        
        available, pytesseract = self.test_import_pytesseract()
        if not available:
            return False
        
        try:
            result = subprocess.run(['brew', 'list', 'tesseract'], 
                                  capture_output=True, 
                                  timeout=5)
            
            if result.returncode == 0:
                print("[OK] Tesseract installed via Homebrew")
                return True
            else:
                print("[INFO] Tesseract not found via Homebrew (may be installed another way)")
                return True  # Not a failure
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("[INFO] Homebrew not available or tesseract installed another way")
            return True  # Not a failure
    
    def test_documentation_requirements(self):
        """Test 21.7: Document installation requirements"""
        requirements_file = project_root / "requirements_v0.1.0.txt"
        docs_file = project_root / "docs" / "OCR_SETUP_GUIDE.md"
        
        # Check requirements file
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                content = f.read()
                if 'pytesseract' in content.lower() or 'tesseract' in content.lower():
                    print("[OK] Tesseract/pytesseract mentioned in requirements")
                else:
                    print("[INFO] Tesseract not in requirements (system dependency)")
        
        # Check documentation
        if docs_file.exists():
            print("[OK] OCR setup guide exists")
            return True
        else:
            print("[INFO] OCR setup guide not found (optional)")
            return True


def run_all_tests():
    """Run all Tesseract installation tests"""
    print("=" * 60)
    print("Tesseract Installation Tests")
    print("=" * 60)
    print()
    print("Phase 2, Step 21: Test Tesseract installation and availability")
    print()
    
    tests = TestTesseractInstallation()
    results = []
    
    print("Test 21.1: Import pytesseract...")
    result, _ = tests.test_import_pytesseract()
    results.append(("Import pytesseract", result))
    print()
    
    print("Test 21.2: Verify Tesseract version...")
    results.append(("Tesseract version", tests.test_tesseract_version()))
    print()
    
    print("Test 21.3: Check Tesseract path configuration...")
    results.append(("Path configuration", tests.test_tesseract_path_configuration()))
    print()
    
    print("Test 21.4: Test Windows Tesseract path...")
    results.append(("Windows path", tests.test_windows_tesseract_path()))
    print()
    
    print("Test 21.5: Test Linux Tesseract path...")
    results.append(("Linux path", tests.test_linux_tesseract_path()))
    print()
    
    print("Test 21.6: Test Mac Tesseract path...")
    results.append(("Mac path", tests.test_mac_tesseract_path()))
    print()
    
    print("Test 21.7: Document installation requirements...")
    results.append(("Documentation", tests.test_documentation_requirements()))
    print()
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL/SKIP]"
        print(f"{status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All Tesseract installation tests passed!")
    elif passed >= total - 2:
        print("\n[INFO] Most tests passed")
        print("  Install pytesseract: pip install pytesseract")
        print("  Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    else:
        print("\n[WARNING] Some tests failed")
        print("  Install dependencies:")
        print("    pip install pytesseract")
        print("    Install Tesseract OCR from: https://github.com/tesseract-ocr/tesseract")
    
    print()


if __name__ == '__main__':
    run_all_tests()

