"""
Unit tests for screenshot capture functionality.
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pytest

from src.capture.screenshot import ScreenshotCapture


class TestScreenshotCapture:
    """Test cases for ScreenshotCapture class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.capture = ScreenshotCapture(output_dir=self.temp_dir, quality=85)
    
    def test_init_creates_output_directory(self):
        """Test that initialization creates output directory."""
        assert self.capture.output_dir.exists()
        assert self.capture.quality == 85
    
    @patch('src.capture.screenshot.ImageGrab.grab')
    @patch('src.capture.screenshot.datetime')
    def test_capture_screenshot_success(self, mock_datetime, mock_grab):
        """Test successful screenshot capture."""
        # Mock datetime
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000_123"
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
        
        # Mock screenshot
        mock_screenshot = Mock()
        mock_screenshot.size = (1920, 1080)
        mock_grab.return_value = mock_screenshot
        
        # Mock file operations
        with patch('builtins.open', mock_open()) as mock_file:
            filepath, metadata = self.capture.capture_screenshot("test")
        
        # Verify results
        assert filepath.name == "20240101_120000_123_test.png"
        assert metadata['label'] == "test"
        assert metadata['size'] == (1920, 1080)
        
        # Verify screenshot was saved
        mock_screenshot.save.assert_called_once()
        
        # Verify metadata was saved
        mock_file.assert_called()
    
    @patch('src.capture.screenshot.ImageGrab.grab')
    def test_capture_screenshot_failure(self, mock_grab):
        """Test screenshot capture failure handling."""
        mock_grab.side_effect = Exception("Screenshot failed")
        
        with pytest.raises(Exception, match="Screenshot failed"):
            self.capture.capture_screenshot("test")
    
    @patch.object(ScreenshotCapture, 'capture_screenshot')
    def test_capture_before_without_content(self, mock_capture):
        """Test capture_before without expected content."""
        mock_path = Path("test.png")
        mock_metadata = {'filename': 'test.png'}
        mock_capture.return_value = (mock_path, mock_metadata)
        
        filepath, metadata = self.capture.capture_before()
        
        mock_capture.assert_called_once_with("before")
        assert filepath == mock_path
        assert metadata == mock_metadata
    
    @patch.object(ScreenshotCapture, 'capture_screenshot')
    def test_capture_before_with_content(self, mock_capture):
        """Test capture_before with expected content."""
        mock_path = Path("test.png")
        mock_metadata = {'filename': 'test.png'}
        mock_capture.return_value = (mock_path, mock_metadata)
        
        with patch('builtins.open', mock_open()) as mock_file:
            filepath, metadata = self.capture.capture_before("Expected content")
        
        mock_capture.assert_called_once_with("before")
        assert 'expected_content' in metadata
        mock_file.assert_called()
    
    @patch.object(ScreenshotCapture, 'capture_screenshot')
    def test_capture_after_with_content(self, mock_capture):
        """Test capture_after with expected content."""
        mock_path = Path("test.png")
        mock_metadata = {'filename': 'test.png'}
        mock_capture.return_value = (mock_path, mock_metadata)
        
        with patch('builtins.open', mock_open()) as mock_file:
            filepath, metadata = self.capture.capture_after("Expected content")
        
        mock_capture.assert_called_once_with("after")
        assert 'expected_content' in metadata
        mock_file.assert_called()
    
    def test_find_latest_pair_no_files(self):
        """Test find_latest_pair when no files exist."""
        before_path, after_path = self.capture.find_latest_pair()
        assert before_path is None
        assert after_path is None
    
    @patch.object(Path, 'glob')
    def test_find_latest_pair_with_files(self, mock_glob):
        """Test find_latest_pair with matching files."""
        # Mock file paths
        before_file = Mock()
        before_file.stem = "20240101_120000_123_before"
        after_file = Mock()
        after_file.stem = "20240101_120001_456_after"
        
        def glob_side_effect(pattern):
            if "_before.png" in pattern:
                return [before_file]
            elif "_after.png" in pattern:
                return [after_file]
            return []
        
        mock_glob.side_effect = glob_side_effect
        
        before_path, after_path = self.capture.find_latest_pair()
        
        assert before_path == before_file
        assert after_path == after_file
    
    @patch.object(Path, 'glob')
    def test_list_captures_empty(self, mock_glob):
        """Test list_captures with no files."""
        mock_glob.return_value = []
        
        captures = self.capture.list_captures()
        
        assert captures['total_screenshots'] == 0
        assert captures['latest_capture'] is None
        assert captures['files'] == []
    
    @patch.object(Path, 'glob')
    @patch.object(Path, 'stat')
    def test_list_captures_with_files(self, mock_stat, mock_glob):
        """Test list_captures with files."""
        # Mock file
        mock_file = Mock()
        mock_file.name = "20240101_120000_123_before.png"
        mock_file.with_suffix.return_value.exists.return_value = False
        
        # Mock file stats
        mock_stat_result = Mock()
        mock_stat_result.st_size = 1024 * 1024  # 1MB
        mock_stat.return_value = mock_stat_result
        
        mock_glob.return_value = [mock_file]
        
        captures = self.capture.list_captures()
        
        assert captures['total_screenshots'] == 1
        assert captures['before_screenshots'] == 1
        assert captures['latest_capture'] == mock_file.name
        assert len(captures['files']) == 1
    
    @patch.object(Path, 'glob')
    @patch.object(Path, 'unlink')
    @patch.object(Path, 'stat')
    def test_clean_old_captures(self, mock_stat, mock_unlink, mock_glob):
        """Test cleaning old captures."""
        # Mock files
        files = []
        for i in range(5):
            mock_file = Mock()
            mock_file.stat.return_value.st_mtime = i
            files.append(mock_file)
        
        mock_glob.return_value = files
        
        deleted_count = self.capture.clean_old_captures(keep_count=2)
        
        assert deleted_count == 1  # Should delete 1 file (5 files - 2*2 keep)
    
    def test_load_metadata_file_not_exists(self):
        """Test load_metadata when file doesn't exist."""
        mock_path = Mock()
        mock_path.with_suffix.return_value.exists.return_value = False
        
        metadata = self.capture.load_metadata(mock_path)
        
        assert metadata == {}
    
    def test_load_metadata_success(self):
        """Test successful metadata loading."""
        mock_path = Mock()
        mock_path.with_suffix.return_value.exists.return_value = True
        
        test_metadata = {'test': 'data'}
        
        with patch('builtins.open', mock_open(read_data=json.dumps(test_metadata))):
            metadata = self.capture.load_metadata(mock_path)
        
        assert metadata == test_metadata
    
    def test_load_metadata_json_error(self):
        """Test metadata loading with JSON error."""
        mock_path = Mock()
        mock_path.with_suffix.return_value.exists.return_value = True
        mock_path.name = "test.png"
        
        with patch('builtins.open', mock_open(read_data="invalid json")):
            metadata = self.capture.load_metadata(mock_path)
        
        assert metadata == {} 