"""
Screenshot capture functionality for UX testing.

This module handles all screenshot capture operations with metadata tracking.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

from PIL import Image, ImageGrab
import logging

logger = logging.getLogger(__name__)


class ScreenshotCapture:
    """Handles screenshot capture with metadata tracking."""
    
    def __init__(self, output_dir: str = "ux_captures", quality: int = 85):
        """
        Initialize screenshot capture.
        
        Args:
            output_dir: Directory to save screenshots
            quality: JPEG quality (1-100)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.quality = quality
        
    def capture_screenshot(self, label: str = "screenshot") -> Tuple[Path, Dict[str, Any]]:
        """
        Capture a screenshot with timestamp and metadata.
        
        Args:
            label: Label for the screenshot
            
        Returns:
            Tuple of (filepath, metadata)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{timestamp}_{label}.png"
        filepath = self.output_dir / filename
        
        logger.info(f"Capturing screenshot: {filename}")
        
        try:
            # Capture screenshot
            screenshot = ImageGrab.grab()
            screenshot.save(filepath, quality=self.quality)
            
            # Create metadata
            metadata = {
                'filename': filename,
                'timestamp': timestamp,
                'label': label,
                'size': screenshot.size,
                'capture_time': datetime.now().isoformat(),
                'quality': self.quality
            }
            
            # Save metadata
            metadata_file = filepath.with_suffix('.json')
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Screenshot saved: {filepath}")
            return filepath, metadata
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            raise
    
    def capture_before(self, expected_content: Optional[str] = None) -> Tuple[Path, Dict[str, Any]]:
        """
        Capture 'before' screenshot with optional content expectation.
        
        Args:
            expected_content: Description of expected content
            
        Returns:
            Tuple of (filepath, metadata)
        """
        filepath, metadata = self.capture_screenshot("before")
        
        if expected_content:
            metadata['expected_content'] = expected_content
            metadata_file = filepath.with_suffix('.json')
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        return filepath, metadata
    
    def capture_after(self, expected_content: Optional[str] = None) -> Tuple[Path, Dict[str, Any]]:
        """
        Capture 'after' screenshot with optional content expectation.
        
        Args:
            expected_content: Description of expected content
            
        Returns:
            Tuple of (filepath, metadata)
        """
        filepath, metadata = self.capture_screenshot("after")
        
        if expected_content:
            metadata['expected_content'] = expected_content
            metadata_file = filepath.with_suffix('.json')
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        return filepath, metadata
    
    def find_latest_pair(self) -> Tuple[Optional[Path], Optional[Path]]:
        """
        Find the most recent Before/after screenshot pair.
        
        Returns:
            Tuple of (before_path, after_path) or (None, None) if not found
        """
        before_files = list(self.output_dir.glob("*_before.png"))
        after_files = list(self.output_dir.glob("*_after.png"))
        
        if not before_files or not after_files:
            return None, None
            
        # Sort by timestamp (filename starts with timestamp)
        before_files.sort(reverse=True)
        after_files.sort(reverse=True)
        
        # Find matching pair (same timestamp prefix)
        for before_file in before_files:
            before_timestamp = before_file.stem.split('_')[0]
            
            for after_file in after_files:
                after_timestamp = after_file.stem.split('_')[0]
                
                # Look for after screenshot within reasonable time window
                if abs(int(after_timestamp) - int(before_timestamp)) < 100000:  # 10 seconds
                    return before_file, after_file
        
        # If no perfect match, use most recent of each
        return before_files[0], after_files[0]
    
    def list_captures(self) -> Dict[str, Any]:
        """
        List all captured screenshots with metadata.
        
        Returns:
            Dictionary with capture information
        """
        captures = {
            'total_screenshots': 0,
            'before_screenshots': 0,
            'after_screenshots': 0,
            'other_screenshots': 0,
            'latest_capture': None,
            'files': []
        }
        
        # Find all screenshot files
        screenshot_files = list(self.output_dir.glob("*.png"))
        captures['total_screenshots'] = len(screenshot_files)
        
        if not screenshot_files:
            return captures
        
        # Sort by timestamp
        screenshot_files.sort(reverse=True)
        captures['latest_capture'] = screenshot_files[0].name
        
        # Categorize and collect metadata
        for filepath in screenshot_files:
            if '_before.png' in filepath.name:
                captures['before_screenshots'] += 1
            elif '_after.png' in filepath.name:
                captures['after_screenshots'] += 1
            else:
                captures['other_screenshots'] += 1
            
            # Load metadata if available
            metadata_file = filepath.with_suffix('.json')
            metadata = {}
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                except Exception as e:
                    logger.warning(f"Could not load metadata for {filepath.name}: {e}")
            
            captures['files'].append({
                'filename': filepath.name,
                'size_mb': round(filepath.stat().st_size / (1024 * 1024), 2),
                'metadata': metadata
            })
        
        return captures
    
    def clean_old_captures(self, keep_count: int = 20) -> int:
        """
        Clean old screenshot captures, keeping the most recent ones.
        
        Args:
            keep_count: Number of recent captures to keep
            
        Returns:
            Number of files deleted
        """
        screenshot_files = list(self.output_dir.glob("*.png"))
        metadata_files = list(self.output_dir.glob("*.json"))
        
        all_files = screenshot_files + metadata_files
        
        if len(all_files) <= keep_count * 2:  # Keep pairs (screenshot + metadata)
            return 0
        
        # Sort by modification time
        all_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # Keep the most recent files
        files_to_keep = all_files[:keep_count * 2]
        files_to_delete = all_files[keep_count * 2:]
        
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                deleted_count += 1
                logger.info(f"Deleted old capture: {file_path.name}")
            except Exception as e:
                logger.warning(f"Could not delete {file_path.name}: {e}")
        
        return deleted_count
    
    def load_metadata(self, image_path: Path) -> Dict[str, Any]:
        """
        Load metadata for an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Metadata dictionary
        """
        metadata_file = image_path.with_suffix('.json')
        
        if not metadata_file.exists():
            return {}
        
        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load metadata for {image_path.name}: {e}")
            return {} 