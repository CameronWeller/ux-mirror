"""
Centralized Configuration Manager for the entire codebase.
Consolidates all configuration loading logic into one place.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging
from dataclasses import dataclass, field
from functools import lru_cache

logger = logging.getLogger(__name__)

@dataclass
class ConfigSchema:
    """Define expected configuration structure"""
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_vision_api_key: str = ""
    
    # Performance Settings
    response_time_threshold: int = 500
    ui_change_threshold: float = 0.05
    screenshot_quality: int = 85
    
    # Feature Flags
    content_validation_enabled: bool = True
    auto_generate_insights: bool = True
    real_time_monitoring: bool = False
    
    # System Settings
    port_range_start: int = 8765
    port_range_end: int = 8864
    heartbeat_timeout: int = 60
    analysis_interval: int = 10
    
    # Agent-specific configs
    agent_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

class ConfigManager:
    """
    Singleton configuration manager that handles all config operations.
    Supports multiple config sources: env files, JSON, YAML, environment variables.
    """
    
    _instance = None
    _config: ConfigSchema = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = ConfigSchema()
            self._load_all_configs()
    
    def _load_all_configs(self):
        """Load configuration from all available sources"""
        # 1. Load from default locations
        self._load_env_file("config.env")
        self._load_json_file("config.json")
        self._load_yaml_file("config.yaml")
        
        # 2. Load from environment variables
        self._load_from_environment()
        
        # 3. Load agent-specific configs
        self._load_agent_configs()
        
        logger.info("Configuration loaded successfully")
    
    def _load_env_file(self, filepath: str):
        """Load configuration from .env file"""
        try:
            if Path(filepath).exists():
                with open(filepath, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            self._set_config_value(key.strip(), value.strip())
        except Exception as e:
            logger.debug(f"Could not load env file {filepath}: {e}")
    
    def _load_json_file(self, filepath: str):
        """Load configuration from JSON file"""
        try:
            if Path(filepath).exists():
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    self._merge_config(data)
        except Exception as e:
            logger.debug(f"Could not load JSON file {filepath}: {e}")
    
    def _load_yaml_file(self, filepath: str):
        """Load configuration from YAML file"""
        try:
            if Path(filepath).exists():
                with open(filepath, 'r') as f:
                    data = yaml.safe_load(f)
                    self._merge_config(data)
        except Exception as e:
            logger.debug(f"Could not load YAML file {filepath}: {e}")
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_mapping = {
            'OPENAI_API_KEY': 'openai_api_key',
            'ANTHROPIC_API_KEY': 'anthropic_api_key',
            'GOOGLE_VISION_API_KEY': 'google_vision_api_key',
            'UX_RESPONSE_THRESHOLD': 'response_time_threshold',
            'UX_UI_CHANGE_THRESHOLD': 'ui_change_threshold',
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.environ.get(env_var)
            if value:
                self._set_config_value(config_key, value)
    
    def _load_agent_configs(self):
        """Load agent-specific configurations"""
        agent_config_dir = Path("config/agents")
        if agent_config_dir.exists():
            for config_file in agent_config_dir.glob("*.json"):
                agent_name = config_file.stem
                try:
                    with open(config_file, 'r') as f:
                        self._config.agent_configs[agent_name] = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load agent config {config_file}: {e}")
    
    def _set_config_value(self, key: str, value: str):
        """Set a configuration value with type conversion"""
        key_lower = key.lower()
        
        # Map environment variable names to config attributes
        if key == 'RESPONSE_TIME_THRESHOLD':
            self._config.response_time_threshold = int(value) if value else 500
        elif key == 'UI_CHANGE_THRESHOLD':
            self._config.ui_change_threshold = float(value) if value else 0.05
        elif key == 'SCREENSHOT_QUALITY':
            self._config.screenshot_quality = int(value) if value else 85
        elif key == 'CONTENT_VALIDATION_ENABLED':
            self._config.content_validation_enabled = value.lower() in ('true', '1', 'yes')
        elif key.endswith('_API_KEY'):
            setattr(self._config, key_lower, value)
    
    def _merge_config(self, data: Dict[str, Any]):
        """Merge dictionary data into configuration"""
        for key, value in data.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
            elif key == 'agent_configs':
                self._config.agent_configs.update(value)
    
    @lru_cache(maxsize=128)
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        # Support nested keys with dot notation
        if '.' in key:
            parts = key.split('.')
            value = self._config
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part, default)
                else:
                    value = getattr(value, part, default)
            return value
        
        return getattr(self._config, key, default)
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent"""
        return self._config.agent_configs.get(agent_name, {})
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        if hasattr(self._config, key):
            setattr(self._config, key, value)
            # Clear cache when config changes
            self.get.cache_clear()
    
    def reload(self):
        """Reload all configurations"""
        self._config = ConfigSchema()
        self._load_all_configs()
        self.get.cache_clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            k: v for k, v in self._config.__dict__.items()
            if not k.startswith('_')
        }

# Global singleton instance
config_manager = ConfigManager()

# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value"""
    return config_manager.get(key, default)

def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """Get configuration for a specific agent"""
    return config_manager.get_agent_config(agent_name)

def reload_config():
    """Reload all configurations"""
    config_manager.reload()