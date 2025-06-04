"""
Utility functions for the UX testing framework.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from environment file.
    
    Args:
        config_path: Path to config file, defaults to 'config.env'
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = "config.env"
    
    config = {
        'response_time_threshold': 500,
        'ui_change_threshold': 0.05,
        'screenshot_quality': 85,
        'openai_api_key': '',
        'anthropic_api_key': '',
        'google_vision_api_key': '',
        'content_validation_enabled': True
    }
    
    try:
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Type conversion based on key
                        if key == 'RESPONSE_TIME_THRESHOLD':
                            config['response_time_threshold'] = int(value) if value else 500
                        elif key == 'UI_CHANGE_THRESHOLD':
                            config['ui_change_threshold'] = float(value) if value else 0.05
                        elif key == 'SCREENSHOT_QUALITY':
                            config['screenshot_quality'] = int(value) if value else 85
                        elif key == 'CONTENT_VALIDATION_ENABLED':
                            config['content_validation_enabled'] = value.lower() in ('true', '1', 'yes')
                        elif key.endswith('_API_KEY'):
                            config[key.lower()] = value
        else:
            logger.warning(f"Config file {config_path} not found, using defaults")
            
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        
    return config


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize configuration values.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Validated configuration dictionary
    """
    validated = config.copy()
    
    # Validate thresholds
    if not 0 < validated['ui_change_threshold'] <= 1.0:
        logger.warning("Invalid UI change threshold, using default")
        validated['ui_change_threshold'] = 0.05
        
    if not 100 <= validated['response_time_threshold'] <= 10000:
        logger.warning("Invalid response time threshold, using default")
        validated['response_time_threshold'] = 500
        
    if not 1 <= validated['screenshot_quality'] <= 100:
        logger.warning("Invalid screenshot quality, using default")
        validated['screenshot_quality'] = 85
    
    return validated


def setup_logging(log_level: str = "WARNING") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(levelname)s: %(message)s'
    )


def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path 