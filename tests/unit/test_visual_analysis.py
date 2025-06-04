"""
Unit tests for visual analysis functionality.
"""
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from src.analysis.visual_analysis import VisualAnalyzer


class TestVisualAnalyzer:
    """Test cases for VisualAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = VisualAnalyzer(ui_change_threshold=0.05)
    
    def test_init(self):
        """Test analyzer initialization."""
        assert self.analyzer.ui_change_threshold == 0.05
    
    @patch('src.analysis.visual_analysis.cv2')
    @patch('src.analysis.visual_analysis.np')
    def test_detect_ui_changes_success(self, mock_np, mock_cv2):
        """Test successful UI change detection."""
        # Mock images
        before_img = np.zeros((100, 100, 3), dtype=np.uint8)
        after_img = np.ones((100, 100, 3), dtype=np.uint8)
        
        # Mock cv2 functions
        mock_cv2.cvtColor.side_effect = [
            np.zeros((100, 100), dtype=np.uint8),  # before_gray
            np.ones((100, 100), dtype=np.uint8)    # after_gray
        ]
        mock_cv2.absdiff.return_value = np.ones((100, 100), dtype=np.uint8)
        mock_np.count_nonzero.return_value = 5000
        
        change_score = self.analyzer.detect_ui_changes(before_img, after_img)
        
        assert change_score == 0.5  # 5000 / 10000
    
    @patch('src.analysis.visual_analysis.cv2')
    def test_detect_ui_changes_different_sizes(self, mock_cv2):
        """Test UI change detection with different image sizes."""
        before_img = np.zeros((100, 100, 3), dtype=np.uint8)
        after_img = np.zeros((200, 200, 3), dtype=np.uint8)
        
        # Mock cv2.resize to return same size images
        mock_cv2.resize.side_effect = [before_img, after_img]
        mock_cv2.cvtColor.side_effect = [
            np.zeros((100, 100), dtype=np.uint8),
            np.zeros((100, 100), dtype=np.uint8)
        ]
        mock_cv2.absdiff.return_value = np.zeros((100, 100), dtype=np.uint8)
        
        change_score = self.analyzer.detect_ui_changes(before_img, after_img)
        
        # Should call resize for both images
        assert mock_cv2.resize.call_count == 2
        assert change_score == 0.0
    
    def test_detect_ui_changes_error_handling(self):
        """Test error handling in UI change detection."""
        # Pass invalid inputs to trigger exception
        change_score = self.analyzer.detect_ui_changes(None, None)
        assert change_score == 0.0
    
    @patch('src.analysis.visual_analysis.datetime')
    def test_calculate_response_time_success(self, mock_datetime):
        """Test successful response time calculation."""
        # Mock file paths
        before_path = Mock()
        before_path.stem = "20240101_120000_123_before"
        after_path = Mock()
        after_path.stem = "20240101_120001_456_after"
        
        # Mock datetime parsing
        from datetime import datetime
        mock_datetime.strptime.side_effect = [
            datetime(2024, 1, 1, 12, 0, 0, 123000),
            datetime(2024, 1, 1, 12, 0, 1, 456000)
        ]
        
        response_time = self.analyzer.calculate_response_time(before_path, after_path)
        
        assert response_time == 1333.0  # 1.333 seconds in milliseconds
    
    def test_calculate_response_time_error(self):
        """Test response time calculation error handling."""
        before_path = Mock()
        before_path.stem = "invalid_timestamp"
        after_path = Mock()
        after_path.stem = "invalid_timestamp"
        
        response_time = self.analyzer.calculate_response_time(before_path, after_path)
        assert response_time == 0.0
    
    @patch('src.analysis.visual_analysis.cv2')
    @patch('src.analysis.visual_analysis.np')
    def test_check_visual_quality_success(self, mock_np, mock_cv2):
        """Test successful visual quality check."""
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Mock cv2 functions
        gray_img = np.zeros((100, 100), dtype=np.uint8)
        mock_cv2.cvtColor.return_value = gray_img
        
        # Mock Laplacian
        laplacian_result = Mock()
        laplacian_result.var.return_value = 150.0
        mock_cv2.Laplacian.return_value = laplacian_result
        
        # Mock numpy functions
        mock_np.mean.return_value = 128.0
        gray_img.std = Mock(return_value=50.0)
        
        # Mock histogram
        hist = np.ones((8, 8, 8))
        mock_cv2.calcHist.return_value = hist
        mock_np.count_nonzero.return_value = 256
        
        quality = self.analyzer.check_visual_quality(img)
        
        assert quality['blur_score'] == 150.0
        assert quality['is_blurry'] is False
        assert quality['brightness'] == 128.0
        assert quality['contrast'] == 50.0
    
    def test_check_visual_quality_error_handling(self):
        """Test visual quality check error handling."""
        quality = self.analyzer.check_visual_quality(None)
        
        # Should return default values on error
        assert quality['blur_score'] == 0.0
        assert quality['brightness'] == 0.0
    
    def test_assess_ux_quality_excellent(self):
        """Test UX quality assessment with excellent metrics."""
        analysis_results = {
            'response_time_ms': 50,
            'ui_change_score': 0.1,
            'visual_quality': {
                'is_blurry': False,
                'is_too_dark': False,
                'is_too_bright': False,
                'contrast': 50
            }
        }
        
        assessment = self.analyzer.assess_ux_quality(analysis_results)
        
        assert assessment['responsiveness'] == 'excellent'
        assert assessment['visual_feedback'] == 'clear'
        assert assessment['overall_score'] > 0.8
        assert len(assessment['issues']) == 0
    
    def test_assess_ux_quality_poor(self):
        """Test UX quality assessment with poor metrics."""
        analysis_results = {
            'response_time_ms': 2000,
            'ui_change_score': 0.01,
            'visual_quality': {
                'is_blurry': True,
                'is_too_dark': True,
                'is_too_bright': False,
                'contrast': 10
            }
        }
        
        assessment = self.analyzer.assess_ux_quality(analysis_results)
        
        assert assessment['responsiveness'] == 'very_slow'
        assert assessment['visual_feedback'] == 'minimal'
        assert assessment['overall_score'] < 0.6
        assert len(assessment['issues']) > 0
        assert len(assessment['recommendations']) > 0
    
    def test_assess_ux_quality_error_handling(self):
        """Test UX quality assessment error handling."""
        assessment = self.analyzer.assess_ux_quality(None)
        
        # Should return default assessment on error
        assert assessment['overall_score'] == 0.0
        assert assessment['responsiveness'] == 'unknown'
    
    @patch('src.analysis.visual_analysis.cv2')
    def test_analyze_screenshots_success(self, mock_cv2):
        """Test successful screenshot analysis."""
        before_path = Mock()
        before_path.name = "before.png"
        after_path = Mock()
        after_path.name = "after.png"
        
        # Mock cv2.imread
        mock_img = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_cv2.imread.return_value = mock_img
        
        # Mock other methods
        with patch.object(self.analyzer, 'detect_ui_changes', return_value=0.1):
            with patch.object(self.analyzer, 'calculate_response_time', return_value=200.0):
                with patch.object(self.analyzer, 'check_visual_quality', return_value={}):
                    with patch.object(self.analyzer, 'assess_ux_quality', return_value={}):
                        analysis = self.analyzer.analyze_screenshots(before_path, after_path)
        
        assert analysis['before_file'] == "before.png"
        assert analysis['after_file'] == "after.png"
        assert 'results' in analysis
    
    @patch('src.analysis.visual_analysis.cv2')
    def test_analyze_screenshots_load_error(self, mock_cv2):
        """Test screenshot analysis with image loading error."""
        before_path = Mock()
        after_path = Mock()
        
        # Mock cv2.imread to return None (load failure)
        mock_cv2.imread.return_value = None
        
        analysis = self.analyzer.analyze_screenshots(before_path, after_path)
        
        assert 'error' in analysis['results']
    
    @patch('src.analysis.visual_analysis.cv2')
    @patch('src.analysis.visual_analysis.datetime')
    def test_create_diff_image_success(self, mock_datetime, mock_cv2):
        """Test successful difference image creation."""
        before_path = Mock()
        after_path = Mock()
        
        # Mock images
        mock_img = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_cv2.imread.return_value = mock_img
        mock_cv2.absdiff.return_value = mock_img
        mock_cv2.convertScaleAbs.return_value = mock_img
        
        # Mock datetime
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        
        # Mock parent directory
        before_path.parent = Path("/test")
        
        output_path = self.analyzer.create_diff_image(before_path, after_path)
        
        assert output_path is not None
        mock_cv2.imwrite.assert_called_once()
    
    @patch('src.analysis.visual_analysis.cv2')
    def test_create_diff_image_load_error(self, mock_cv2):
        """Test difference image creation with load error."""
        before_path = Mock()
        after_path = Mock()
        
        # Mock cv2.imread to return None
        mock_cv2.imread.return_value = None
        
        output_path = self.analyzer.create_diff_image(before_path, after_path)
        
        assert output_path is None
    
    @patch('src.analysis.visual_analysis.cv2')
    def test_create_diff_image_different_sizes(self, mock_cv2):
        """Test difference image creation with different sized images."""
        before_path = Mock()
        after_path = Mock()
        
        # Mock images with different sizes
        before_img = np.zeros((100, 100, 3), dtype=np.uint8)
        after_img = np.zeros((200, 200, 3), dtype=np.uint8)
        
        mock_cv2.imread.side_effect = [before_img, after_img]
        mock_cv2.resize.return_value = before_img
        mock_cv2.absdiff.return_value = before_img
        mock_cv2.convertScaleAbs.return_value = before_img
        
        # Mock parent directory
        before_path.parent = Path("/test")
        
        output_path = self.analyzer.create_diff_image(before_path, after_path)
        
        # Should call resize
        mock_cv2.resize.assert_called()
        assert output_path is not None 