"""
Unit tests for core UX testing functionality.
"""
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.ux_tester.core import UXTester


class TestUXTester:
    """Test cases for UXTester class."""
    
    @patch('src.ux_tester.core.load_config')
    @patch('src.ux_tester.core.validate_config')
    @patch('src.ux_tester.core.setup_logging')
    @patch('src.ux_tester.core.ensure_directory')
    @patch('src.ux_tester.core.ScreenshotCapture')
    @patch('src.ux_tester.core.VisualAnalyzer')
    @patch('src.ux_tester.core.ContentValidator')
    def test_init_with_default_config(self, mock_content_validator, mock_visual_analyzer, 
                                     mock_screenshot_capture, mock_ensure_directory,
                                     mock_setup_logging, mock_validate_config, mock_load_config):
        """Test UXTester initialization with default config."""
        # Mock config
        mock_config = {
            'screenshot_quality': 85,
            'ui_change_threshold': 0.05,
            'content_validation_enabled': True,
            'openai_api_key': 'test_key',
            'anthropic_api_key': 'test_key'
        }
        mock_load_config.return_value = mock_config
        mock_validate_config.return_value = mock_config
        mock_ensure_directory.return_value = Path("/test")
        
        tester = UXTester()
        
        # Verify initialization calls
        mock_load_config.assert_called_once()
        mock_validate_config.assert_called_once_with(mock_config)
        mock_setup_logging.assert_called_once()
        mock_ensure_directory.assert_called_once_with("ux_captures")
        mock_screenshot_capture.assert_called_once()
        mock_visual_analyzer.assert_called_once()
        mock_content_validator.assert_called_once()
        
        assert tester.config == mock_config
    
    @patch('src.ux_tester.core.validate_config')
    @patch('src.ux_tester.core.setup_logging')
    @patch('src.ux_tester.core.ensure_directory')
    @patch('src.ux_tester.core.ScreenshotCapture')
    @patch('src.ux_tester.core.VisualAnalyzer')
    def test_init_with_custom_config(self, mock_visual_analyzer, mock_screenshot_capture,
                                    mock_ensure_directory, mock_setup_logging, mock_validate_config):
        """Test UXTester initialization with custom config."""
        custom_config = {
            'screenshot_quality': 90,
            'ui_change_threshold': 0.1,
            'content_validation_enabled': False
        }
        mock_validate_config.return_value = custom_config
        mock_ensure_directory.return_value = Path("/test")
        
        tester = UXTester(config=custom_config, output_dir="custom_dir")
        
        mock_validate_config.assert_called_once_with(custom_config)
        mock_ensure_directory.assert_called_once_with("custom_dir")
        assert tester.content_validator is None  # Should be None when disabled
    
    def test_capture_screenshot(self):
        """Test screenshot capture delegation."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.screenshot_capture = Mock()
            
            expected_result = (Path("test.png"), {"test": "metadata"})
            tester.screenshot_capture.capture_screenshot.return_value = expected_result
            
            result = tester.capture_screenshot("test_label")
            
            tester.screenshot_capture.capture_screenshot.assert_called_once_with("test_label")
            assert result == expected_result
    
    def test_capture_before(self):
        """Test before screenshot capture delegation."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.screenshot_capture = Mock()
            
            expected_result = (Path("before.png"), {"test": "metadata"})
            tester.screenshot_capture.capture_before.return_value = expected_result
            
            result = tester.capture_before("expected content")
            
            tester.screenshot_capture.capture_before.assert_called_once_with("expected content")
            assert result == expected_result
    
    def test_capture_after(self):
        """Test after screenshot capture delegation."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.screenshot_capture = Mock()
            
            expected_result = (Path("after.png"), {"test": "metadata"})
            tester.screenshot_capture.capture_after.return_value = expected_result
            
            result = tester.capture_after("expected content")
            
            tester.screenshot_capture.capture_after.assert_called_once_with("expected content")
            assert result == expected_result
    
    def test_analyze_screenshots_no_files_found(self):
        """Test screenshot analysis when no files are found."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.screenshot_capture = Mock()
            tester.screenshot_capture.find_latest_pair.return_value = (None, None)
            
            result = tester.analyze_screenshots()
            
            assert 'error' in result
            assert 'instructions' in result
    
    @patch('src.ux_tester.core.logger')
    def test_analyze_screenshots_success_without_content_validation(self, mock_logger):
        """Test successful screenshot analysis without content validation."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.screenshot_capture = Mock()
            tester.visual_analyzer = Mock()
            tester.content_validator = None
            tester.output_dir = Path("/test")
            
            # Mock file paths
            before_path = Mock()
            before_path.name = "before.png"
            after_path = Mock()
            after_path.name = "after.png"
            
            tester.screenshot_capture.find_latest_pair.return_value = (before_path, after_path)
            
            # Mock analysis result
            analysis_result = {
                'before_file': 'before.png',
                'after_file': 'after.png',
                'results': {'test': 'data'}
            }
            tester.visual_analyzer.analyze_screenshots.return_value = analysis_result
            
            # Mock private methods
            tester._save_analysis_results = Mock()
            tester._print_analysis_summary = Mock()
            
            result = tester.analyze_screenshots()
            
            tester.visual_analyzer.analyze_screenshots.assert_called_once_with(before_path, after_path)
            tester._save_analysis_results.assert_called_once()
            tester._print_analysis_summary.assert_called_once()
            assert result == analysis_result
    
    @patch('src.ux_tester.core.logger')
    def test_analyze_screenshots_with_content_validation(self, mock_logger):
        """Test screenshot analysis with content validation."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.screenshot_capture = Mock()
            tester.visual_analyzer = Mock()
            tester.content_validator = Mock()
            tester.output_dir = Path("/test")
            
            # Mock file paths
            before_path = Mock()
            before_path.name = "before.png"
            after_path = Mock()
            after_path.name = "after.png"
            
            tester.screenshot_capture.find_latest_pair.return_value = (before_path, after_path)
            
            # Mock metadata with expected content
            tester.screenshot_capture.load_metadata.side_effect = [
                {},  # before metadata
                {'expected_content': 'test content'}  # after metadata
            ]
            
            # Mock analysis result
            analysis_result = {
                'before_file': 'before.png',
                'after_file': 'after.png',
                'results': {'test': 'data'}
            }
            tester.visual_analyzer.analyze_screenshots.return_value = analysis_result
            
            # Mock content validation
            content_validation_result = {'validation': 'result'}
            tester.content_validator.validate_content.return_value = content_validation_result
            
            # Mock private methods
            tester._save_analysis_results = Mock()
            tester._print_analysis_summary = Mock()
            
            result = tester.analyze_screenshots()
            
            tester.content_validator.validate_content.assert_called_once_with(after_path, 'test content')
            assert result['results']['content_validation'] == content_validation_result
    
    def test_validate_content_expectations_no_validator(self):
        """Test content validation when validator is not enabled."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.content_validator = None
            
            result = tester.validate_content_expectations()
            
            assert 'error' in result
            assert 'Content validation not enabled' in result['error']
    
    def test_validate_content_expectations_no_files(self):
        """Test content validation when no files are found."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.content_validator = Mock()
            tester.screenshot_capture = Mock()
            tester.screenshot_capture.find_latest_pair.return_value = (None, None)
            
            result = tester.validate_content_expectations()
            
            assert 'error' in result
    
    def test_validate_content_expectations_no_expected_content(self):
        """Test content validation when no expected content is found."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.content_validator = Mock()
            tester.screenshot_capture = Mock()
            
            before_path = Mock()
            after_path = Mock()
            tester.screenshot_capture.find_latest_pair.return_value = (before_path, after_path)
            tester.screenshot_capture.load_metadata.return_value = {}
            
            result = tester.validate_content_expectations()
            
            assert 'error' in result
            assert 'No expected content specified' in result['error']
    
    def test_validate_content_expectations_success(self):
        """Test successful content validation."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.content_validator = Mock()
            tester.screenshot_capture = Mock()
            
            before_path = Mock()
            after_path = Mock()
            tester.screenshot_capture.find_latest_pair.return_value = (before_path, after_path)
            tester.screenshot_capture.load_metadata.side_effect = [
                {},  # before metadata
                {'expected_content': 'test content'}  # after metadata
            ]
            
            validation_result = {'validation': 'result'}
            tester.content_validator.validate_content.return_value = validation_result
            
            result = tester.validate_content_expectations()
            
            assert result['expected_content'] == 'test content'
            assert result['before_validation'] == validation_result
            assert result['after_validation'] == validation_result
    
    def test_list_captures(self):
        """Test list captures delegation."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.screenshot_capture = Mock()
            
            expected_result = {'captures': 'data'}
            tester.screenshot_capture.list_captures.return_value = expected_result
            
            result = tester.list_captures()
            
            tester.screenshot_capture.list_captures.assert_called_once()
            assert result == expected_result
    
    def test_clean_old_captures(self):
        """Test clean old captures delegation."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.screenshot_capture = Mock()
            
            tester.screenshot_capture.clean_old_captures.return_value = 5
            
            result = tester.clean_old_captures(keep_count=10)
            
            tester.screenshot_capture.clean_old_captures.assert_called_once_with(10)
            assert result == 5
    
    @patch('builtins.open')
    @patch('src.ux_tester.core.json.dump')
    @patch('src.ux_tester.core.datetime')
    @patch('src.ux_tester.core.logger')
    def test_save_analysis_results_success(self, mock_logger, mock_datetime, mock_json_dump, mock_open):
        """Test successful analysis results saving."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.output_dir = Path("/test")
            
            mock_datetime.now.return_value.strftime.return_value = "20240101_120000_123"
            
            analysis = {'test': 'data'}
            tester._save_analysis_results(analysis)
            
            mock_open.assert_called_once()
            mock_json_dump.assert_called_once()
    
    @patch('src.ux_tester.core.logger')
    def test_save_analysis_results_error(self, mock_logger):
        """Test analysis results saving error handling."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            tester.output_dir = None  # This will cause an error
            
            analysis = {'test': 'data'}
            tester._save_analysis_results(analysis)
            
            # Should log warning on error
            mock_logger.warning.assert_called()
    
    @patch('builtins.print')
    def test_print_analysis_summary_basic(self, mock_print):
        """Test basic analysis summary printing."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            
            analysis = {
                'before_file': 'before.png',
                'after_file': 'after.png',
                'timestamp': '2024-01-01T12:00:00',
                'results': {
                    'response_time_ms': 200,
                    'ui_changed': True,
                    'ui_change_score': 0.1
                }
            }
            
            tester._print_analysis_summary(analysis)
            
            # Should call print multiple times
            assert mock_print.call_count > 5
    
    @patch('builtins.print')
    def test_print_analysis_summary_with_ux_assessment(self, mock_print):
        """Test analysis summary printing with UX assessment."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            
            analysis = {
                'before_file': 'before.png',
                'after_file': 'after.png',
                'timestamp': '2024-01-01T12:00:00',
                'results': {
                    'response_time_ms': 50,
                    'ui_changed': True,
                    'ui_change_score': 0.1,
                    'ux_assessment': {
                        'overall_score': 0.9,
                        'issues': ['Test issue'],
                        'recommendations': ['Test recommendation']
                    }
                }
            }
            
            tester._print_analysis_summary(analysis)
            
            # Should call print multiple times including issues and recommendations
            assert mock_print.call_count > 10
    
    @patch('builtins.print')
    def test_print_analysis_summary_with_content_validation(self, mock_print):
        """Test analysis summary printing with content validation."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            
            analysis = {
                'before_file': 'before.png',
                'after_file': 'after.png',
                'timestamp': '2024-01-01T12:00:00',
                'results': {
                    'content_validation': {
                        'expected_content': 'test content',
                        'consensus': {
                            'content_matches': True,
                            'confidence': 0.9,
                            'description': 'Test description'
                        }
                    }
                }
            }
            
            tester._print_analysis_summary(analysis)
            
            # Should call print multiple times including content validation
            assert mock_print.call_count > 8
    
    @patch('builtins.print')
    def test_print_analysis_summary_with_error(self, mock_print):
        """Test analysis summary printing with error."""
        with patch.object(UXTester, '__init__', lambda x: None):
            tester = UXTester()
            
            analysis = {
                'results': {
                    'error': 'Test error',
                    'instructions': ['Step 1', 'Step 2']
                }
            }
            
            tester._print_analysis_summary(analysis)
            
            # Should print error and instructions
            assert mock_print.call_count > 5 