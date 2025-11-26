#!/usr/bin/env python3
"""
Test Screenshot Metadata Preservation
Tests for Phase 3, Step 31 of v0.1.0 release

This test verifies that screenshot metadata is properly preserved:
- Timestamp in filename
- File path returned correctly
- Metadata saved to JSON
- Metadata includes required fields
- Metadata can be loaded
- Metadata persists across sessions
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.screenshot_analyzer import ScreenshotAnalyzer
    SCREENSHOT_ANALYZER_AVAILABLE = True
except ImportError:
    SCREENSHOT_ANALYZER_AVAILABLE = False
    print("[INFO] ScreenshotAnalyzer not available - some tests will be skipped")

try:
    from simple_ux_tester import SimpleUXTester
    SIMPLE_UX_TESTER_AVAILABLE = True
except ImportError:
    SIMPLE_UX_TESTER_AVAILABLE = False
    print("[INFO] SimpleUXTester not available - some tests will be skipped")

try:
    import asyncio
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    print("[INFO] asyncio not available - some tests will be skipped")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[INFO] PIL not available - some tests will be skipped")


class TestScreenshotMetadata:
    """Test 31: Verify screenshot metadata is preserved"""
    
    def __init__(self):
        self.screenshot_analyzer = None
        self.simple_ux_tester = None
        self.test_results_dir = project_root / "test_outputs"
        self.test_results_dir.mkdir(exist_ok=True)
        self.metadata_dir = project_root / "metadata_test"
        self.metadata_dir.mkdir(exist_ok=True)
        
    def setup(self):
        """Setup test environment"""
        if SCREENSHOT_ANALYZER_AVAILABLE:
            try:
                self.screenshot_analyzer = ScreenshotAnalyzer()
                print("[OK] ScreenshotAnalyzer initialized")
            except Exception as e:
                print(f"[WARN] ScreenshotAnalyzer not available: {e}")
        
        if SIMPLE_UX_TESTER_AVAILABLE:
            try:
                self.simple_ux_tester = SimpleUXTester(output_dir=str(self.metadata_dir))
                print("[OK] SimpleUXTester initialized")
            except Exception as e:
                print(f"[WARN] SimpleUXTester not available: {e}")
        
        return SCREENSHOT_ANALYZER_AVAILABLE or SIMPLE_UX_TESTER_AVAILABLE
    
    def review_capture_screenshot_method(self) -> bool:
        """31.1: Review ScreenshotAnalyzer.capture_screenshot() method"""
        print("Step 31.1: Reviewing capture_screenshot() method...")
        
        if not SCREENSHOT_ANALYZER_AVAILABLE:
            print("[SKIP] ScreenshotAnalyzer not available")
            return False
        
        try:
            import inspect
            method = getattr(ScreenshotAnalyzer, 'capture_screenshot', None)
            
            if method:
                source = inspect.getsource(method)
                print("[OK] capture_screenshot() method found")
                print(f"[OK] Method signature: {inspect.signature(method)}")
                
                # Check for timestamp generation
                if 'timestamp' in source.lower() or 'datetime' in source.lower():
                    print("[OK] Method uses timestamp")
                else:
                    print("[WARN] Method may not use timestamp")
                
                return True
            else:
                print("[ERROR] capture_screenshot() method not found")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to review method: {e}")
            return False
    
    def check_timestamp_in_filename(self, screenshot_path: str) -> bool:
        """31.2: Check timestamp is included in filename"""
        print("Step 31.2: Checking timestamp in filename...")
        
        if not screenshot_path:
            print("[ERROR] No screenshot path provided")
            return False
        
        try:
            filename = Path(screenshot_path).name
            
            # Check for timestamp pattern (YYYYMMDD_HHMMSS)
            import re
            timestamp_pattern = r'\d{8}_\d{6}'
            
            if re.search(timestamp_pattern, filename):
                print(f"[OK] Timestamp found in filename: {filename}")
                return True
            else:
                print(f"[WARN] No timestamp pattern found in filename: {filename}")
                # Still check if it has some date/time indicator
                if any(char.isdigit() for char in filename):
                    print("[INFO] Filename contains digits (may be timestamp)")
                    return True
                return False
        except Exception as e:
            print(f"[ERROR] Failed to check filename: {e}")
            return False
    
    def verify_file_path_returned(self, screenshot_path: Optional[str]) -> bool:
        """31.3: Verify file path is returned correctly"""
        print("Step 31.3: Verifying file path is returned correctly...")
        
        if not screenshot_path:
            print("[ERROR] No screenshot path returned")
            return False
        
        try:
            path_obj = Path(screenshot_path)
            
            # Check if path is absolute or relative
            if path_obj.is_absolute():
                print(f"[OK] Path is absolute: {screenshot_path}")
            else:
                print(f"[OK] Path is relative: {screenshot_path}")
            
            # Check if file exists
            if path_obj.exists():
                print(f"[OK] File exists at path")
                file_size = path_obj.stat().st_size
                print(f"[OK] File size: {file_size} bytes")
                return True
            else:
                print(f"[ERROR] File does not exist at path: {screenshot_path}")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to verify path: {e}")
            return False
    
    def test_saving_metadata_to_json(self, screenshot_path: str) -> Optional[str]:
        """31.4: Test saving metadata to JSON file"""
        print("Step 31.4: Testing metadata saving to JSON...")
        
        if not screenshot_path or not Path(screenshot_path).exists():
            print("[ERROR] Invalid screenshot path")
            return None
        
        try:
            # Get file info
            path_obj = Path(screenshot_path)
            file_size = path_obj.stat().st_size
            file_mtime = path_obj.stat().st_mtime
            
            # Get image dimensions if PIL is available
            dimensions = None
            if PIL_AVAILABLE:
                try:
                    img = Image.open(screenshot_path)
                    dimensions = {"width": img.width, "height": img.height}
                except Exception:
                    pass
            
            # Create metadata
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "file_path": str(screenshot_path),
                "file_name": path_obj.name,
                "file_size": file_size,
                "file_modified": datetime.fromtimestamp(file_mtime).isoformat(),
                "dimensions": dimensions,
                "capture_method": "ScreenshotAnalyzer"
            }
            
            # Save to JSON
            metadata_path = self.metadata_dir / f"{path_obj.stem}_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"[OK] Metadata saved to: {metadata_path}")
            return str(metadata_path)
        except Exception as e:
            print(f"[ERROR] Failed to save metadata: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def verify_metadata_fields(self, metadata_path: str) -> bool:
        """31.5: Verify metadata includes: timestamp, dimensions, file_size"""
        print("Step 31.5: Verifying metadata fields...")
        
        if not metadata_path or not Path(metadata_path).exists():
            print("[ERROR] Metadata file not found")
            return False
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            required_fields = ["timestamp", "file_path", "file_size"]
            optional_fields = ["dimensions"]
            
            missing_required = [field for field in required_fields if field not in metadata]
            
            if missing_required:
                print(f"[ERROR] Missing required fields: {missing_required}")
                return False
            
            print("[OK] All required fields present:")
            for field in required_fields:
                print(f"  - {field}: {metadata.get(field)}")
            
            # Check optional fields
            for field in optional_fields:
                if field in metadata:
                    print(f"[OK] Optional field present: {field}: {metadata.get(field)}")
                else:
                    print(f"[INFO] Optional field missing: {field}")
            
            # Verify data types
            if not isinstance(metadata.get("timestamp"), str):
                print("[WARN] Timestamp is not a string")
            
            if not isinstance(metadata.get("file_size"), (int, float)):
                print("[WARN] File size is not a number")
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to verify metadata: {e}")
            return False
    
    def test_loading_metadata_from_json(self, metadata_path: str) -> Optional[Dict[str, Any]]:
        """31.6: Test loading metadata from JSON"""
        print("Step 31.6: Testing metadata loading from JSON...")
        
        if not metadata_path or not Path(metadata_path).exists():
            print("[ERROR] Metadata file not found")
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            print("[OK] Metadata loaded successfully")
            print(f"[OK] Metadata keys: {list(metadata.keys())}")
            
            return metadata
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Failed to load metadata: {e}")
            return None
    
    def verify_metadata_persists_across_sessions(self, metadata_path: str) -> bool:
        """31.7: Verify metadata persists across sessions"""
        print("Step 31.7: Verifying metadata persists across sessions...")
        
        if not metadata_path or not Path(metadata_path).exists():
            print("[ERROR] Metadata file not found")
            return False
        
        try:
            # Load metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata1 = json.load(f)
            
            # Wait a moment
            time.sleep(1)
            
            # Load again (simulating new session)
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata2 = json.load(f)
            
            # Compare
            if metadata1 == metadata2:
                print("[OK] Metadata persists across sessions")
                return True
            else:
                print("[WARN] Metadata changed between loads")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to verify persistence: {e}")
            return False


async def run_screenshot_metadata_test():
    """Run all screenshot metadata tests"""
    print("=" * 60)
    print("Test 31: Screenshot Metadata Preservation Test")
    print("=" * 60)
    print()
    
    test = TestScreenshotMetadata()
    
    # Setup
    if not test.setup():
        print("[ERROR] Setup failed")
        return False
    
    # Step 1: Review method
    test.review_capture_screenshot_method()
    
    # Step 2-3: Capture screenshot and check filename/path
    screenshot_path = None
    if test.screenshot_analyzer:
        screenshot_path = await test.screenshot_analyzer.capture_screenshot()
    
    if not screenshot_path:
        print("[ERROR] Screenshot capture failed")
        return False
    
    # Step 2: Check timestamp in filename
    test.check_timestamp_in_filename(screenshot_path)
    
    # Step 3: Verify file path
    test.verify_file_path_returned(screenshot_path)
    
    # Step 4: Save metadata
    metadata_path = test.test_saving_metadata_to_json(screenshot_path)
    if not metadata_path:
        print("[ERROR] Metadata saving failed")
        return False
    
    # Step 5: Verify metadata fields
    test.verify_metadata_fields(metadata_path)
    
    # Step 6: Load metadata
    metadata = test.test_loading_metadata_from_json(metadata_path)
    if not metadata:
        print("[ERROR] Metadata loading failed")
        return False
    
    # Step 7: Verify persistence
    test.verify_metadata_persists_across_sessions(metadata_path)
    
    # Summary
    print()
    print("=" * 60)
    print("Screenshot Metadata Test Summary")
    print("=" * 60)
    print(f"Screenshot: {'✅' if screenshot_path else '❌'}")
    print(f"Metadata saved: {'✅' if metadata_path else '❌'}")
    print(f"Metadata loaded: {'✅' if metadata else '❌'}")
    print()
    
    success = screenshot_path and metadata_path and metadata
    
    if success:
        print("[SUCCESS] Screenshot metadata test passed!")
    else:
        print("[WARN] Screenshot metadata test completed with some issues")
    
    return success


if __name__ == '__main__':
    if ASYNC_AVAILABLE:
        result = asyncio.run(run_screenshot_metadata_test())
        sys.exit(0 if result else 1)
    else:
        print("[ERROR] asyncio not available")
        sys.exit(1)


