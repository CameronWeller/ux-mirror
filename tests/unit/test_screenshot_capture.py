"""
Unit tests for screenshot capture functionality.
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
import pytest
import unittest
from datetime import datetime

from src.capture.screenshot import ScreenshotCapture


class TestScreenshotCapture(unittest.TestCase):
    """Test cases for ScreenshotCapture class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.capture = ScreenshotCapture(output_dir=self.temp_dir, quality=85)
    
    def test_init_creates_output_directory(self):
        """Test that initialization creates output directory."""
        with patch.object(Path, 'mkdir') as mock_mkdir:
            capture = ScreenshotCapture()
            mock_mkdir.assert_called_once_with(exist_ok=True)
            assert capture.quality == 85
    
    @patch('src.capture.screenshot.ImageGrab.grab')
    @patch('src.capture.screenshot.datetime')
    def test_capture_screenshot_success(self, mock_datetime, mock_grab):
        """Test successful screenshot capture."""
        # Mock datetime - the actual implementation uses [:-3] to truncate microseconds
        mock_now = Mock()
        mock_now.strftime.return_value = "20240101_120000_123456"  # Full microseconds
        mock_now.isoformat.return_value = "2024-01-01T12:00:00"
        mock_datetime.now.return_value = mock_now
        
        # Mock screenshot
        mock_screenshot = Mock()
        mock_screenshot.size = (1920, 1080)
        mock_grab.return_value = mock_screenshot
        
        # Mock file operations
        with patch('builtins.open', mock_open()) as mock_file:
            filepath, metadata = self.capture.capture_screenshot("test")
        
        # Verify results - timestamp should be truncated to milliseconds
        expected_timestamp = "20240101_120000_123"  # [:-3] truncation
        assert filepath.name == f"{expected_timestamp}_test.png"
        assert metadata['timestamp'] == expected_timestamp
        assert metadata['label'] == "test"
        assert metadata['size'] == (1920, 1080)
        assert metadata['capture_time'] == "2024-01-01T12:00:00"
        
        # Verify screenshot was saved
        mock_screenshot.save.assert_called_once()
        
        # Verify metadata was saved
        mock_file.assert_called()
    
    @patch('src.capture.screenshot.ImageGrab.grab')
    def test_capture_screenshot_failure(self, mock_grab):
        """Test screenshot capture failure."""
        mock_grab.side_effect = Exception("Screenshot failed")
        
        with pytest.raises(Exception, match="Screenshot failed"):
            self.capture.capture_screenshot("test")
    
    @patch('src.capture.screenshot.ImageGrab.grab')
    @patch('src.capture.screenshot.datetime')
    def test_capture_before_without_content(self, mock_datetime, mock_grab):
        """Test capture_before without content."""
        mock_now = Mock()
        mock_now.strftime.return_value = "20240101_120000_123456"
        mock_now.isoformat.return_value = "2024-01-01T12:00:00"
        mock_datetime.now.return_value = mock_now
        
        mock_screenshot = Mock()
        mock_screenshot.size = (1920, 1080)
        mock_grab.return_value = mock_screenshot

        with patch('builtins.open', mock_open()):
            filepath, metadata = self.capture.capture_before()

        assert "_before.png" in filepath.name
    
    @patch('src.capture.screenshot.ImageGrab.grab')
    @patch('src.capture.screenshot.datetime')
    def test_capture_before_with_content(self, mock_datetime, mock_grab):
        """Test capture_before with content."""
        mock_now = Mock()
        mock_now.strftime.return_value = "20240101_120000_123456"
        mock_now.isoformat.return_value = "2024-01-01T12:00:00"
        mock_datetime.now.return_value = mock_now
        
        mock_screenshot = Mock()
        mock_screenshot.size = (1920, 1080)
        mock_grab.return_value = mock_screenshot

        with patch('builtins.open', mock_open()):
            filepath, metadata = self.capture.capture_before("test content")

        assert "_before.png" in filepath.name
        assert metadata['expected_content'] == "test content"
    
    @patch('src.capture.screenshot.ImageGrab.grab')
    @patch('src.capture.screenshot.datetime')
    def test_capture_after_with_content(self, mock_datetime, mock_grab):
        """Test capture_after with content."""
        mock_now = Mock()
        mock_now.strftime.return_value = "20240101_120000_123456"
        mock_now.isoformat.return_value = "2024-01-01T12:00:00"
        mock_datetime.now.return_value = mock_now
        
        mock_screenshot = Mock()
        mock_screenshot.size = (1920, 1080)
        mock_grab.return_value = mock_screenshot

        with patch('builtins.open', mock_open()):
            filepath, metadata = self.capture.capture_after("test content")

        assert "_after.png" in filepath.name
        assert metadata['expected_content'] == "test content"
    
    @patch.object(Path, 'glob')
    def test_find_latest_pair_no_files(self, mock_glob):
        """Test find_latest_pair with no files."""
        mock_glob.return_value = []
        
        before_file, after_file = self.capture.find_latest_pair()
        
        assert before_file is None
        assert after_file is None
    
    @patch.object(Path, 'glob')
    def test_find_latest_pair_with_files(self, mock_glob):
        """Test find_latest_pair with files."""
        # Mock files
        before_file = Mock()
        before_file.name = "20240101_120000_123_before.png"
        before_file.stem = "20240101_120000_123_before"
        after_file = Mock()
        after_file.name = "20240101_120000_123_after.png"
        after_file.stem = "20240101_120000_123_after"
        
        mock_glob.side_effect = [[before_file], [after_file]]
        
        result_before, result_after = self.capture.find_latest_pair()
        
        assert result_before == before_file
        assert result_after == after_file
    
    @patch.object(Path, 'glob')
    def test_list_captures_empty(self, mock_glob):
        """Test list_captures with no files."""
        mock_glob.return_value = []
        
        captures = self.capture.list_captures()
        
        assert captures['total_screenshots'] == 0
        assert captures['files'] == []
    
    @patch.object(Path, 'glob')
    def test_list_captures_with_files(self, mock_glob):
        """Test list_captures with files."""
        # Mock file with proper stat method
        mock_file = Mock()
        mock_file.name = "20240101_120000_123_before.png"
        mock_file.with_suffix.return_value.exists.return_value = False
        
        # Mock the stat method to return a proper stat result
        mock_stat_result = Mock()
        mock_stat_result.st_size = 1024 * 1024  # 1MB
        mock_file.stat.return_value = mock_stat_result

        mock_glob.return_value = [mock_file]

        captures = self.capture.list_captures()

        assert captures['total_screenshots'] == 1
        assert captures['before_screenshots'] == 1
        assert captures['latest_capture'] == "20240101_120000_123_before.png"
        assert len(captures['files']) == 1
        assert captures['files'][0]['filename'] == "20240101_120000_123_before.png"
        assert captures['files'][0]['size_mb'] == 1.0
    
    @patch.object(Path, 'glob')
    def test_clean_old_captures(self, mock_glob):
        """Test cleaning old captures."""
        # Create 10 mock files (5 PNG + 5 JSON) with different modification times
        all_files = []
        
        # Create PNG files
        for i in range(5):
            mock_file = Mock()
            mock_file.name = f"file_{i}.png"
            mock_stat_result = Mock()
            mock_stat_result.st_mtime = i  # Different timestamps
            mock_file.stat.return_value = mock_stat_result
            mock_file.unlink = Mock()
            all_files.append(mock_file)
        
        # Create JSON files
        for i in range(5):
            mock_file = Mock()
            mock_file.name = f"file_{i}.json"
            mock_stat_result = Mock()
            mock_stat_result.st_mtime = i + 5  # Different timestamps
            mock_file.stat.return_value = mock_stat_result
            mock_file.unlink = Mock()
            all_files.append(mock_file)

        # Mock glob to return PNG files first, then JSON files
        mock_glob.side_effect = [all_files[:5], all_files[5:]]

        deleted_count = self.capture.clean_old_captures(keep_count=2)

        # With 10 files total, keep_count=2 means keep 4 files (2*2)
        # So should delete 6 files
        assert deleted_count == 6
        
        # The implementation sorts all files by mtime and keeps the newest 4
        # Files with mtime 9,8,7,6 should be kept (newest 4)
        # Files with mtime 5,4,3,2,1,0 should be deleted (oldest 6)
        
        # Count how many unlink calls were made
        total_unlink_calls = sum(1 for f in all_files if f.unlink.called)
        assert total_unlink_calls == 6
    
    def test_load_metadata_file_not_exists(self):
        """Test load_metadata when file doesn't exist."""
        with patch.object(Path, 'exists', return_value=False):
            metadata = self.capture.load_metadata(Path("nonexistent.json"))
            assert metadata == {}
    
    def test_load_metadata_success(self):
        """Test successful metadata loading."""
        test_metadata = {"test": "data"}
        
        with patch.object(Path, 'exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(test_metadata))):
                metadata = self.capture.load_metadata(Path("test.json"))
                assert metadata == test_metadata
    
    def test_load_metadata_json_error(self):
        """Test metadata loading with JSON error."""
        with patch.object(Path, 'exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="invalid json")):
                metadata = self.capture.load_metadata(Path("test.json"))
                assert metadata == {}


if __name__ == '__main__':
    unittest.main() 