#!/usr/bin/env python3
"""
Test Basic Image Loading with OpenCV
Tests for Phase 2, Step 14 of v0.1.0 release
"""

import sys
import os
from pathlib import Path
import tempfile

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestOpenCVImageLoading:
    """Test 14: Test basic image loading with OpenCV"""
    
    def test_import_cv2(self):
        """Prerequisite: Check cv2 is available"""
        try:
            import cv2
            return True, cv2
        except ImportError:
            print("[SKIP] OpenCV not available - install with: pip install opencv-python")
            return False, None
    
    def test_load_image(self):
        """Test 14.1: Load test screenshot with `cv2.imread()`"""
        available, cv2 = self.test_import_cv2()
        if not available:
            return False
        
        try:
            import numpy as np
            
            # Create a test image file
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            test_image[:, :] = [255, 0, 0]  # Blue image
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
                cv2.imwrite(tmp_path, test_image)
            
            try:
                # Load image
                loaded = cv2.imread(tmp_path)
                
                assert loaded is not None, "Image should load successfully"
                assert isinstance(loaded, np.ndarray), "Should return numpy array"
                
                print("[OK] Image loaded successfully with cv2.imread()")
                return True
            finally:
                # Clean up
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        except Exception as e:
            print(f"[ERROR] Failed to load image: {e}")
            return False
    
    def test_image_shape(self):
        """Test 14.2: Verify image shape (height, width, channels)"""
        available, cv2 = self.test_import_cv2()
        if not available:
            return False
        
        try:
            import numpy as np
            
            # Create test image with known dimensions
            height, width, channels = 200, 300, 3
            test_image = np.zeros((height, width, channels), dtype=np.uint8)
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
                cv2.imwrite(tmp_path, test_image)
            
            try:
                loaded = cv2.imread(tmp_path)
                assert loaded is not None, "Image should load"
                
                # Check shape
                loaded_shape = loaded.shape
                assert len(loaded_shape) == 3, "Should have 3 dimensions (height, width, channels)"
                assert loaded_shape[0] == height, f"Height should be {height}"
                assert loaded_shape[1] == width, f"Width should be {width}"
                assert loaded_shape[2] == channels, f"Channels should be {channels}"
                
                print(f"[OK] Image shape verified: {loaded_shape} (height, width, channels)")
                return True
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        except Exception as e:
            print(f"[ERROR] Failed to verify shape: {e}")
            return False
    
    def test_invalid_path(self):
        """Test 14.3: Test with invalid path (should return None)"""
        available, cv2 = self.test_import_cv2()
        if not available:
            return False
        
        try:
            # Try to load non-existent file
            invalid_path = "/nonexistent/path/image.png"
            result = cv2.imread(invalid_path)
            
            assert result is None, "Should return None for invalid path"
            
            print("[OK] Invalid path handled correctly (returns None)")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to test invalid path: {e}")
            return False
    
    def test_different_formats(self):
        """Test 14.4: Test with different formats (PNG, JPG)"""
        available, cv2 = self.test_import_cv2()
        if not available:
            return False
        
        try:
            import numpy as np
            
            test_image = np.zeros((50, 50, 3), dtype=np.uint8)
            test_image[:, :] = [0, 255, 0]  # Green image
            
            formats = [('.png', 'PNG'), ('.jpg', 'JPEG')]
            results = []
            
            for ext, name in formats:
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                    tmp_path = tmp.name
                    cv2.imwrite(tmp_path, test_image)
                
                try:
                    loaded = cv2.imread(tmp_path)
                    assert loaded is not None, f"{name} image should load"
                    results.append(True)
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
            
            if all(results):
                print("[OK] Both PNG and JPG formats work correctly")
                return True
            else:
                print("[WARNING] Some formats failed")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to test formats: {e}")
            return False
    
    def test_image_dtype(self):
        """Test 14.5: Verify image dtype (uint8)"""
        available, cv2 = self.test_import_cv2()
        if not available:
            return False
        
        try:
            import numpy as np
            
            test_image = np.zeros((50, 50, 3), dtype=np.uint8)
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
                cv2.imwrite(tmp_path, test_image)
            
            try:
                loaded = cv2.imread(tmp_path)
                assert loaded is not None, "Image should load"
                
                # Check dtype
                assert loaded.dtype == np.uint8, f"dtype should be uint8, got {loaded.dtype}"
                
                print(f"[OK] Image dtype verified: {loaded.dtype}")
                return True
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        except Exception as e:
            print(f"[ERROR] Failed to verify dtype: {e}")
            return False
    
    def test_grayscale_conversion(self):
        """Test 14.6: Test grayscale conversion: `cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)`"""
        available, cv2 = self.test_import_cv2()
        if not available:
            return False
        
        try:
            import numpy as np
            
            # Create color image
            color_image = np.zeros((100, 100, 3), dtype=np.uint8)
            color_image[:, :] = [128, 64, 192]  # Purple
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
                cv2.imwrite(tmp_path, color_image)
            
            try:
                loaded = cv2.imread(tmp_path)
                assert loaded is not None, "Image should load"
                
                # Convert to grayscale
                gray = cv2.cvtColor(loaded, cv2.COLOR_BGR2GRAY)
                
                # Verify grayscale
                assert len(gray.shape) == 2, "Grayscale should have 2 dimensions"
                assert gray.dtype == np.uint8, "Grayscale dtype should be uint8"
                assert gray.shape[0] == loaded.shape[0], "Height should match"
                assert gray.shape[1] == loaded.shape[1], "Width should match"
                
                print("[OK] Grayscale conversion works correctly")
                print(f"  Original shape: {loaded.shape}, Grayscale shape: {gray.shape}")
                return True
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        except Exception as e:
            print(f"[ERROR] Failed to convert to grayscale: {e}")
            return False


def run_all_tests():
    """Run all image loading tests"""
    print("=" * 60)
    print("OpenCV Image Loading Tests")
    print("=" * 60)
    print()
    print("Phase 2, Step 14: Test basic image loading with OpenCV")
    print()
    
    tests = TestOpenCVImageLoading()
    results = []
    
    print("Test 14.1: Load image with cv2.imread()...")
    results.append(("Load image", tests.test_load_image()))
    print()
    
    print("Test 14.2: Verify image shape...")
    results.append(("Image shape", tests.test_image_shape()))
    print()
    
    print("Test 14.3: Test invalid path...")
    results.append(("Invalid path", tests.test_invalid_path()))
    print()
    
    print("Test 14.4: Test different formats...")
    results.append(("Different formats", tests.test_different_formats()))
    print()
    
    print("Test 14.5: Verify image dtype...")
    results.append(("Image dtype", tests.test_image_dtype()))
    print()
    
    print("Test 14.6: Test grayscale conversion...")
    results.append(("Grayscale conversion", tests.test_grayscale_conversion()))
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
        print("\n[SUCCESS] All image loading tests passed!")
    elif passed >= total - 1:
        print("\n[INFO] Most tests passed (OpenCV may need installation)")
        print("  Install: pip install opencv-python")
    else:
        print("\n[WARNING] Some tests failed")
        print("  Install OpenCV: pip install opencv-python")
    
    print()


if __name__ == '__main__':
    run_all_tests()

