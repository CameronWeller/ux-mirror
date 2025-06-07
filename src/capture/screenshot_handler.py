"""
Screenshot Handler Module for UX-MIRROR
======================================

Handles screenshot capture, storage, and management.
Extracted from visual analysis agent for better modularity.

Task: EXTRACT-005A - Create screenshot_handler.py with capture and storage functionality
"""

import os
import cv2
import numpy as np
import logging
from PIL import Image, ImageGrab
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path
import hashlib
import json

logger = logging.getLogger(__name__)

class ScreenshotHandler:
    """
    Handles screenshot capture, storage, and management operations.
    Provides a clean interface for screenshot-related functionality.
    """
    
    def __init__(self, storage_dir: str = "screenshots", max_stored: int = 100):
        """
        Initialize the ScreenshotHandler
        
        Args:
            storage_dir: Directory to store screenshots
            max_stored: Maximum number of screenshots to keep in storage
        """
        self.storage_dir = Path(storage_dir)
        self.max_stored = max_stored
        self.current_screenshot: Optional[np.ndarray] = None
        self.previous_screenshot: Optional[np.ndarray] = None
        self.baseline_screenshot: Optional[np.ndarray] = None
        
        # Create storage directory if it doesn't exist
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Load metadata if exists
        self.metadata_file = self.storage_dir / "metadata.json"
        self.screenshots_metadata = self._load_metadata()
        
        logger.info(f"ScreenshotHandler initialized with storage at {self.storage_dir}")
    
    def capture_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """
        Capture a screenshot of the screen or specified region
        
        Args:
            region: Optional region tuple (x, y, width, height) to capture
            
        Returns:
            Screenshot as numpy array in BGR format, or None if capture fails
        """
        try:
            if region:
                # Capture specific region
                x, y, width, height = region
                screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            else:
                # Capture full screen
                screenshot = ImageGrab.grab()
            
            if screenshot is None:
                logger.error("Failed to capture screenshot")
                return None
            
            # Convert to numpy array and BGR format for OpenCV compatibility
            screenshot_array = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2BGR)
            
            # Update current and previous
            self.previous_screenshot = self.current_screenshot
            self.current_screenshot = screenshot_bgr
            
            logger.debug(f"Screenshot captured: {screenshot_bgr.shape}")
            return screenshot_bgr
            
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None
    
    def save_screenshot(self, screenshot: np.ndarray, filename: Optional[str] = None, 
                       metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Save screenshot to storage with metadata
        
        Args:
            screenshot: Screenshot array to save
            filename: Optional custom filename (will generate if not provided)
            metadata: Optional metadata to associate with screenshot
            
        Returns:
            Saved filename or None if save fails
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"screenshot_{timestamp}.png"
            
            filepath = self.storage_dir / filename
            
            # Convert BGR to RGB for saving
            screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(screenshot_rgb)
            image.save(filepath)
            
            # Calculate hash for deduplication
            screenshot_hash = self._calculate_hash(screenshot)
            
            # Store metadata
            screenshot_metadata = {
                "filename": filename,
                "timestamp": datetime.now().isoformat(),
                "size": screenshot.shape,
                "hash": screenshot_hash,
                "metadata": metadata or {}
            }
            
            self.screenshots_metadata[filename] = screenshot_metadata
            self._save_metadata()
            
            # Cleanup old screenshots if needed
            self._cleanup_old_screenshots()
            
            logger.info(f"Screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving screenshot: {e}")
            return None
    
    def load_screenshot(self, filename: str) -> Optional[np.ndarray]:
        """
        Load a screenshot from storage
        
        Args:
            filename: Name of the screenshot file to load
            
        Returns:
            Screenshot as numpy array in BGR format, or None if load fails
        """
        try:
            filepath = self.storage_dir / filename
            
            if not filepath.exists():
                logger.error(f"Screenshot file not found: {filename}")
                return None
            
            # Load and convert to BGR
            image = Image.open(filepath)
            screenshot_array = np.array(image)
            
            if len(screenshot_array.shape) == 3:
                screenshot_bgr = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2BGR)
            else:
                screenshot_bgr = screenshot_array
            
            logger.debug(f"Screenshot loaded: {filename}")
            return screenshot_bgr
            
        except Exception as e:
            logger.error(f"Error loading screenshot {filename}: {e}")
            return None
    
    def set_baseline(self, screenshot: Optional[np.ndarray] = None) -> bool:
        """
        Set a baseline screenshot for comparisons
        
        Args:
            screenshot: Screenshot to use as baseline (captures new if None)
            
        Returns:
            True if baseline was set successfully
        """
        try:
            if screenshot is None:
                screenshot = self.capture_screenshot()
                if screenshot is None:
                    return False
            
            self.baseline_screenshot = screenshot.copy()
            
            # Save baseline to storage
            baseline_filename = self.save_screenshot(
                screenshot, 
                "baseline.png",
                {"type": "baseline", "set_at": datetime.now().isoformat()}
            )
            
            if baseline_filename:
                logger.info("Baseline screenshot set and saved")
                return True
            else:
                logger.error("Failed to save baseline screenshot")
                return False
                
        except Exception as e:
            logger.error(f"Error setting baseline: {e}")
            return False
    
    def get_baseline(self) -> Optional[np.ndarray]:
        """
        Get the current baseline screenshot
        
        Returns:
            Baseline screenshot or None if not set
        """
        return self.baseline_screenshot
    
    def compare_with_baseline(self, screenshot: Optional[np.ndarray] = None) -> Optional[Dict[str, Any]]:
        """
        Compare a screenshot with the baseline
        
        Args:
            screenshot: Screenshot to compare (captures new if None)
            
        Returns:
            Comparison results dictionary or None if comparison fails
        """
        try:
            if self.baseline_screenshot is None:
                logger.warning("No baseline screenshot set for comparison")
                return None
            
            if screenshot is None:
                screenshot = self.capture_screenshot()
                if screenshot is None:
                    return None
            
            # Ensure same dimensions
            if screenshot.shape != self.baseline_screenshot.shape:
                logger.warning("Screenshot dimensions don't match baseline")
                # Resize to match baseline
                h, w = self.baseline_screenshot.shape[:2]
                screenshot = cv2.resize(screenshot, (w, h))
            
            # Calculate difference
            diff = cv2.absdiff(self.baseline_screenshot, screenshot)
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            
            # Calculate change metrics
            total_pixels = diff_gray.size
            changed_pixels = np.count_nonzero(diff_gray > 10)  # Threshold for meaningful change
            change_percentage = (changed_pixels / total_pixels) * 100
            
            # Calculate mean squared error
            mse = np.mean((self.baseline_screenshot.astype("float") - screenshot.astype("float")) ** 2)
            
            comparison_result = {
                "timestamp": datetime.now().isoformat(),
                "change_percentage": change_percentage,
                "changed_pixels": changed_pixels,
                "total_pixels": total_pixels,
                "mse": mse,
                "has_significant_change": change_percentage > 5.0  # 5% threshold
            }
            
            logger.debug(f"Baseline comparison: {change_percentage:.2f}% change")
            return comparison_result
            
        except Exception as e:
            logger.error(f"Error comparing with baseline: {e}")
            return None
    
    def find_duplicates(self) -> List[List[str]]:
        """
        Find duplicate screenshots based on hash comparison
        
        Returns:
            List of lists, each containing filenames of duplicate screenshots
        """
        try:
            hash_groups = {}
            
            for filename, metadata in self.screenshots_metadata.items():
                file_hash = metadata.get("hash")
                if file_hash:
                    if file_hash not in hash_groups:
                        hash_groups[file_hash] = []
                    hash_groups[file_hash].append(filename)
            
            # Return groups with more than one file
            duplicates = [group for group in hash_groups.values() if len(group) > 1]
            
            if duplicates:
                logger.info(f"Found {len(duplicates)} groups of duplicate screenshots")
            
            return duplicates
            
        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            return []
    
    def cleanup_duplicates(self) -> int:
        """
        Remove duplicate screenshots, keeping the newest one
        
        Returns:
            Number of files removed
        """
        try:
            duplicates = self.find_duplicates()
            removed_count = 0
            
            for duplicate_group in duplicates:
                # Sort by timestamp, keep the newest
                sorted_group = sorted(
                    duplicate_group,
                    key=lambda f: self.screenshots_metadata[f]["timestamp"],
                    reverse=True
                )
                
                # Remove all but the first (newest)
                for filename in sorted_group[1:]:
                    filepath = self.storage_dir / filename
                    if filepath.exists():
                        filepath.unlink()
                        removed_count += 1
                    
                    # Remove from metadata
                    if filename in self.screenshots_metadata:
                        del self.screenshots_metadata[filename]
            
            if removed_count > 0:
                self._save_metadata()
                logger.info(f"Removed {removed_count} duplicate screenshots")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up duplicates: {e}")
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get statistics about screenshot storage
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            total_files = len(self.screenshots_metadata)
            total_size = 0
            
            for filename in self.screenshots_metadata:
                filepath = self.storage_dir / filename
                if filepath.exists():
                    total_size += filepath.stat().st_size
            
            duplicates = len(self.find_duplicates())
            
            return {
                "total_screenshots": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "storage_directory": str(self.storage_dir),
                "duplicate_groups": duplicates,
                "has_baseline": self.baseline_screenshot is not None
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}
    
    def _calculate_hash(self, screenshot: np.ndarray) -> str:
        """Calculate hash of screenshot for deduplication"""
        return hashlib.md5(screenshot.tobytes()).hexdigest()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load screenshots metadata from file"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {}
    
    def _save_metadata(self):
        """Save screenshots metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.screenshots_metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def _cleanup_old_screenshots(self):
        """Remove old screenshots if storage limit exceeded"""
        try:
            if len(self.screenshots_metadata) <= self.max_stored:
                return
            
            # Sort by timestamp, oldest first
            sorted_files = sorted(
                self.screenshots_metadata.items(),
                key=lambda x: x[1]["timestamp"]
            )
            
            # Remove oldest files
            files_to_remove = len(sorted_files) - self.max_stored
            for i in range(files_to_remove):
                filename = sorted_files[i][0]
                filepath = self.storage_dir / filename
                
                if filepath.exists():
                    filepath.unlink()
                
                del self.screenshots_metadata[filename]
            
            if files_to_remove > 0:
                self._save_metadata()
                logger.info(f"Cleaned up {files_to_remove} old screenshots")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Global instance for easy access
_screenshot_handler_instance: Optional[ScreenshotHandler] = None

def get_screenshot_handler() -> ScreenshotHandler:
    """
    Get the global ScreenshotHandler instance
    
    Returns:
        Global ScreenshotHandler instance
    """
    global _screenshot_handler_instance
    if _screenshot_handler_instance is None:
        _screenshot_handler_instance = ScreenshotHandler()
    return _screenshot_handler_instance 