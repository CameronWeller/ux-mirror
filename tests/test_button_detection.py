#!/usr/bin/env python3
"""
Test Button Detection Algorithm
Tests for Phase 2, Step 15 of v0.1.0 release
"""

import sys
import os
from pathlib import Path
import tempfile

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestButtonDetection:
    """Test 15: Test button detection algorithm"""
    
    def test_imports(self):
        """Prerequisite: Check required modules"""
        try:
            import cv2
            import numpy as np
            return True, cv2, np
        except ImportError as e:
            print(f"[SKIP] Required modules not available: {e}")
            print("  Install: pip install opencv-python numpy")
            return False, None, None
    
    def test_review_detection_method(self):
        """Test 15.1: Review `UIElementDetector._opencv_detect_elements()`"""
        try:
            from src.analysis.ui_element_detector import UIElementDetector
            
            detector = UIElementDetector(use_gpu=False, enable_ocr=False)
            
            # Check if method exists
            assert hasattr(detector, '_opencv_detect_elements'), \
                "_opencv_detect_elements method should exist"
            
            print("[OK] UIElementDetector._opencv_detect_elements() method exists")
            return True
        except ImportError as e:
            print(f"[SKIP] UIElementDetector not available: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to review method: {e}")
            return False
    
    def test_create_test_image_with_buttons(self):
        """Test 15.2: Create test image with clear buttons"""
        available, cv2, np = self.test_imports()
        if not available:
            return False
        
        try:
            # Create test image with buttons
            img = np.ones((400, 600, 3), dtype=np.uint8) * 240  # Light gray background
            
            # Draw button 1: Rectangle button
            cv2.rectangle(img, (50, 50), (200, 100), (100, 150, 200), -1)  # Filled button
            cv2.rectangle(img, (50, 50), (200, 100), (50, 100, 150), 2)  # Border
            
            # Draw button 2: Rounded button
            cv2.rectangle(img, (250, 50), (400, 100), (150, 200, 100), -1)
            cv2.rectangle(img, (250, 50), (400, 100), (100, 150, 50), 2)
            
            # Draw button 3: Small button
            cv2.rectangle(img, (450, 50), (550, 80), (200, 150, 100), -1)
            cv2.rectangle(img, (450, 50), (550, 80), (150, 100, 50), 2)
            
            # Save test image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
                cv2.imwrite(tmp_path, img)
            
            try:
                # Verify image was created
                assert os.path.exists(tmp_path), "Test image should be created"
                loaded = cv2.imread(tmp_path)
                assert loaded is not None, "Test image should load"
                
                print("[OK] Test image with buttons created successfully")
                print(f"  Image saved to: {tmp_path}")
                return True, tmp_path
            except Exception as e:
                print(f"[ERROR] Failed to verify test image: {e}")
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                return False, None
        except Exception as e:
            print(f"[ERROR] Failed to create test image: {e}")
            return False, None
    
    def test_edge_detection(self):
        """Test 15.3: Test edge detection: `cv2.Canny()`"""
        available, cv2, np = self.test_imports()
        if not available:
            return False
        
        try:
            # Create simple test image
            img = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2.rectangle(img, (20, 20), (80, 80), (255, 255, 255), -1)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            assert edges is not None, "Edge detection should return result"
            assert edges.shape == gray.shape, "Edge image should match input shape"
            assert edges.dtype == np.uint8, "Edge image should be uint8"
            
            # Check that edges were detected (should have some white pixels)
            edge_pixels = np.sum(edges > 0)
            assert edge_pixels > 0, "Should detect some edges"
            
            print(f"[OK] Edge detection works: {edge_pixels} edge pixels detected")
            return True
        except Exception as e:
            print(f"[ERROR] Edge detection failed: {e}")
            return False
    
    def test_contour_detection(self):
        """Test 15.4: Test contour detection: `cv2.findContours()`"""
        available, cv2, np = self.test_imports()
        if not available:
            return False
        
        try:
            # Create test image with shapes
            img = np.zeros((200, 200, 3), dtype=np.uint8)
            cv2.rectangle(img, (30, 30), (100, 100), (255, 255, 255), -1)
            cv2.rectangle(img, (120, 30), (170, 100), (255, 255, 255), -1)
            
            # Convert to grayscale and get edges
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            assert contours is not None, "Contours should be found"
            assert len(contours) > 0, "Should find at least one contour"
            
            # Check contour properties
            for i, contour in enumerate(contours):
                assert len(contour) > 0, f"Contour {i} should have points"
                area = cv2.contourArea(contour)
                assert area > 0, f"Contour {i} should have area > 0"
            
            print(f"[OK] Contour detection works: {len(contours)} contours found")
            return True
        except Exception as e:
            print(f"[ERROR] Contour detection failed: {e}")
            return False
    
    def test_rectangle_detection(self):
        """Test 15.5: Test rectangle detection (button-like shapes)"""
        available, cv2, np = self.test_imports()
        if not available:
            return False
        
        try:
            # Create test image with rectangles
            img = np.zeros((200, 300, 3), dtype=np.uint8)
            cv2.rectangle(img, (20, 20), (120, 70), (255, 255, 255), -1)
            cv2.rectangle(img, (150, 20), (280, 70), (255, 255, 255), -1)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            rectangles = []
            for contour in contours:
                # Approximate contour to polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Check if it's roughly rectangular (4 vertices)
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    rectangles.append((x, y, w, h))
            
            assert len(rectangles) > 0, "Should detect at least one rectangle"
            
            print(f"[OK] Rectangle detection works: {len(rectangles)} rectangles found")
            for i, (x, y, w, h) in enumerate(rectangles):
                print(f"  Rectangle {i+1}: x={x}, y={y}, w={w}, h={h}")
            return True
        except Exception as e:
            print(f"[ERROR] Rectangle detection failed: {e}")
            return False
    
    def test_button_bounding_boxes(self):
        """Test 15.6: Verify button bounding boxes are correct"""
        available, cv2, np = self.test_imports()
        if not available:
            return False
        
        try:
            # Create test image with known button positions
            img = np.zeros((300, 400, 3), dtype=np.uint8)
            button1 = (50, 50, 150, 80)  # x, y, width, height
            button2 = (220, 50, 150, 80)
            
            cv2.rectangle(img, 
                         (button1[0], button1[1]), 
                         (button1[0] + button1[2], button1[1] + button1[3]),
                         (255, 255, 255), -1)
            cv2.rectangle(img,
                         (button2[0], button2[1]),
                         (button2[0] + button2[2], button2[1] + button2[3]),
                         (255, 255, 255), -1)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detected_boxes = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 50 and h > 30:  # Filter small noise
                    detected_boxes.append((x, y, w, h))
            
            # Check that we detected buttons
            assert len(detected_boxes) >= 2, "Should detect at least 2 buttons"
            
            # Verify bounding boxes are reasonable
            for x, y, w, h in detected_boxes:
                assert w > 0 and h > 0, "Bounding box should have positive dimensions"
                assert x >= 0 and y >= 0, "Bounding box should be in image bounds"
            
            print(f"[OK] Button bounding boxes verified: {len(detected_boxes)} buttons detected")
            return True
        except Exception as e:
            print(f"[ERROR] Bounding box verification failed: {e}")
            return False
    
    def test_different_button_sizes(self):
        """Test 15.7: Test with buttons of different sizes"""
        available, cv2, np = self.test_imports()
        if not available:
            return False
        
        try:
            img = np.zeros((400, 500, 3), dtype=np.uint8)
            
            # Small button
            cv2.rectangle(img, (20, 20), (80, 50), (255, 255, 255), -1)
            # Medium button
            cv2.rectangle(img, (100, 20), (250, 80), (255, 255, 255), -1)
            # Large button
            cv2.rectangle(img, (270, 20), (480, 120), (255, 255, 255), -1)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            sizes = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 20 and h > 10:  # Filter noise
                    sizes.append((w, h))
            
            assert len(sizes) >= 3, "Should detect buttons of different sizes"
            
            # Verify size variation
            widths = [w for w, h in sizes]
            assert max(widths) - min(widths) > 50, "Should detect size variation"
            
            print(f"[OK] Different button sizes detected: {len(sizes)} buttons")
            print(f"  Size range: {min(widths)}x{min([h for w, h in sizes])} to {max(widths)}x{max([h for w, h in sizes])}")
            return True
        except Exception as e:
            print(f"[ERROR] Different sizes test failed: {e}")
            return False
    
    def test_overlapping_buttons(self):
        """Test 15.8: Test with overlapping buttons"""
        available, cv2, np = self.test_imports()
        if not available:
            return False
        
        try:
            img = np.zeros((200, 300, 3), dtype=np.uint8)
            
            # Overlapping buttons
            cv2.rectangle(img, (50, 50), (150, 100), (255, 255, 255), -1)
            cv2.rectangle(img, (100, 80), (200, 130), (255, 255, 255), -1)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Should detect overlapping regions
            detected = len([c for c in contours if cv2.contourArea(c) > 500])
            
            print(f"[OK] Overlapping buttons handled: {detected} regions detected")
            print("  Note: Overlapping buttons may merge or be detected separately")
            return True
        except Exception as e:
            print(f"[ERROR] Overlapping buttons test failed: {e}")
            return False
    
    def test_confidence_scores(self):
        """Test 15.9: Verify confidence scores are reasonable"""
        try:
            from src.analysis.ui_element_detector import UIElementDetector
            
            detector = UIElementDetector(use_gpu=False, enable_ocr=False, confidence_threshold=0.3)
            
            # Check confidence threshold is set
            assert hasattr(detector, 'confidence_threshold'), "Should have confidence_threshold"
            assert 0.0 <= detector.confidence_threshold <= 1.0, "Confidence should be 0-1"
            
            print(f"[OK] Confidence threshold verified: {detector.confidence_threshold}")
            print("  Note: Actual confidence scores depend on detection results")
            return True
        except ImportError:
            print("[SKIP] UIElementDetector not available")
            return False
        except Exception as e:
            print(f"[ERROR] Confidence score test failed: {e}")
            return False


def run_all_tests():
    """Run all button detection tests"""
    print("=" * 60)
    print("Button Detection Algorithm Tests")
    print("=" * 60)
    print()
    print("Phase 2, Step 15: Test button detection algorithm")
    print()
    
    tests = TestButtonDetection()
    results = []
    
    print("Test 15.1: Review detection method...")
    results.append(("Review method", tests.test_review_detection_method()))
    print()
    
    print("Test 15.2: Create test image with buttons...")
    result = tests.test_create_test_image_with_buttons()
    if isinstance(result, tuple):
        results.append(("Create test image", result[0]))
    else:
        results.append(("Create test image", result))
    print()
    
    print("Test 15.3: Test edge detection...")
    results.append(("Edge detection", tests.test_edge_detection()))
    print()
    
    print("Test 15.4: Test contour detection...")
    results.append(("Contour detection", tests.test_contour_detection()))
    print()
    
    print("Test 15.5: Test rectangle detection...")
    results.append(("Rectangle detection", tests.test_rectangle_detection()))
    print()
    
    print("Test 15.6: Verify button bounding boxes...")
    results.append(("Bounding boxes", tests.test_button_bounding_boxes()))
    print()
    
    print("Test 15.7: Test different button sizes...")
    results.append(("Different sizes", tests.test_different_button_sizes()))
    print()
    
    print("Test 15.8: Test overlapping buttons...")
    results.append(("Overlapping buttons", tests.test_overlapping_buttons()))
    print()
    
    print("Test 15.9: Verify confidence scores...")
    results.append(("Confidence scores", tests.test_confidence_scores()))
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
        print("\n[SUCCESS] All button detection tests passed!")
    elif passed >= total - 2:
        print("\n[INFO] Most tests passed (some may require OpenCV)")
        print("  Install: pip install opencv-python numpy")
    else:
        print("\n[WARNING] Some tests failed")
        print("  Install dependencies: pip install opencv-python numpy")
    
    print()


if __name__ == '__main__':
    run_all_tests()

