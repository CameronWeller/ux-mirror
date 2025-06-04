"""
Unit tests for utility functions.
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from src.ux_tester.utils import load_config, validate_config, setup_logging, ensure_directory


class TestLoadConfig:
    """Test configuration loading functionality."""
    
    def test_load_config_defaults(self):
        """Test loading default configuration when no file exists."""
        with patch('pathlib.Path.exists', return_value=False):
            config = load_config("nonexistent.env")
            
        expected_keys = [
            'response_time_threshold', 'ui_change_threshold', 'screenshot_quality',
            'openai_api_key', 'anthropic_api_key', 'google_vision_api_key',
            'content_validation_enabled'
        ]
        
        for key in expected_keys:
            assert key in config
            
        assert config['response_time_threshold'] == 500
        assert config['ui_change_threshold'] == 0.05
        assert config['screenshot_quality'] == 85
        assert config['content_validation_enabled'] is True
    
    def test_load_config_from_file(self):
        """Test loading configuration from a valid file."""
        config_content = """
# Test configuration
RESPONSE_TIME_THRESHOLD=1000
UI_CHANGE_THRESHOLD=0.1
SCREENSHOT_QUALITY=90
CONTENT_VALIDATION_ENABLED=false
OPENAI_API_KEY=test_openai_key
ANTHROPIC_API_KEY=test_anthropic_key
"""
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=config_content)):
                config = load_config("test.env")
        
        assert config['response_time_threshold'] == 1000
        assert config['ui_change_threshold'] == 0.1
        assert config['screenshot_quality'] == 90
        assert config['content_validation_enabled'] is False
        assert config['openai_api_key'] == 'test_openai_key'
        assert config['anthropic_api_key'] == 'test_anthropic_key'
    
    def test_load_config_with_empty_values(self):
        """Test loading configuration with empty values falls back to defaults."""
        config_content = """
RESPONSE_TIME_THRESHOLD=
UI_CHANGE_THRESHOLD=
SCREENSHOT_QUALITY=
"""
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=config_content)):
                config = load_config("test.env")
        
        assert config['response_time_threshold'] == 500
        assert config['ui_change_threshold'] == 0.05
        assert config['screenshot_quality'] == 85
    
    def test_load_config_ignores_comments_and_invalid_lines(self):
        """Test that comments and invalid lines are ignored."""
        config_content = """
# This is a comment
RESPONSE_TIME_THRESHOLD=750
invalid_line_without_equals
# Another comment
UI_CHANGE_THRESHOLD=0.08
"""
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=config_content)):
                config = load_config("test.env")
        
        assert config['response_time_threshold'] == 750
        assert config['ui_change_threshold'] == 0.08


class TestValidateConfig:
    """Test configuration validation functionality."""
    
    def test_validate_config_valid_values(self):
        """Test validation with valid configuration values."""
        config = {
            'response_time_threshold': 1000,
            'ui_change_threshold': 0.1,
            'screenshot_quality': 85
        }
        
        validated = validate_config(config)
        
        assert validated == config
    
    def test_validate_config_invalid_ui_change_threshold(self):
        """Test validation corrects invalid UI change threshold."""
        config = {
            'response_time_threshold': 500,
            'ui_change_threshold': 1.5,  # Invalid: > 1.0
            'screenshot_quality': 85
        }
        
        with patch('src.ux_tester.utils.logger.warning') as mock_warning:
            validated = validate_config(config)
            
        assert validated['ui_change_threshold'] == 0.05
        mock_warning.assert_called_with("Invalid UI change threshold, using default")
    
    def test_validate_config_invalid_response_time(self):
        """Test validation corrects invalid response time threshold."""
        config = {
            'response_time_threshold': 50,  # Invalid: < 100
            'ui_change_threshold': 0.05,
            'screenshot_quality': 85
        }
        
        with patch('src.ux_tester.utils.logger.warning') as mock_warning:
            validated = validate_config(config)
            
        assert validated['response_time_threshold'] == 500
        mock_warning.assert_called_with("Invalid response time threshold, using default")
    
    def test_validate_config_invalid_screenshot_quality(self):
        """Test validation corrects invalid screenshot quality."""
        config = {
            'response_time_threshold': 500,
            'ui_change_threshold': 0.05,
            'screenshot_quality': 150  # Invalid: > 100
        }
        
        with patch('src.ux_tester.utils.logger.warning') as mock_warning:
            validated = validate_config(config)
            
        assert validated['screenshot_quality'] == 85
        mock_warning.assert_called_with("Invalid screenshot quality, using default")


class TestEnsureDirectory:
    """Test directory creation functionality."""
    
    def test_ensure_directory_creates_new_directory(self):
        """Test that ensure_directory creates a new directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = os.path.join(temp_dir, "test_subdir")
            
            result = ensure_directory(test_path)
            
            assert result.exists()
            assert result.is_dir()
            assert str(result) == test_path
    
    def test_ensure_directory_with_existing_directory(self):
        """Test that ensure_directory works with existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = ensure_directory(temp_dir)
            
            assert result.exists()
            assert result.is_dir()
    
    def test_ensure_directory_creates_nested_directories(self):
        """Test that ensure_directory creates nested directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = os.path.join(temp_dir, "level1", "level2", "level3")
            
            result = ensure_directory(nested_path)
            
            assert result.exists()
            assert result.is_dir()
            assert str(result) == nested_path


class TestSetupLogging:
    """Test logging setup functionality."""
    
    def test_setup_logging_with_different_levels(self):
        """Test that setup_logging works with different log levels."""
        import logging
        
        # Test with different levels
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            with patch('logging.basicConfig') as mock_config:
                setup_logging(level)
                
                mock_config.assert_called_once_with(
                    level=getattr(logging, level),
                    format='%(levelname)s: %(message)s'
                )
    
    def test_setup_logging_default_level(self):
        """Test that setup_logging uses WARNING as default level."""
        import logging
        
        with patch('logging.basicConfig') as mock_config:
            setup_logging()
            
            mock_config.assert_called_once_with(
                level=logging.WARNING,
                format='%(levelname)s: %(message)s'
            ) 