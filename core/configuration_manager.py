#!/usr/bin/env python3
"""
UX-MIRROR Unified Configuration Manager
======================================

Centralized configuration management with:
- JSON schema validation
- Environment-specific overrides
- Hot-reloading capabilities
- Secure storage for sensitive data
- Configuration merging and inheritance

Author: UX-MIRROR System
Version: 1.0.0
"""

import json
import logging
import os
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import yaml
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import JSON schema validation
try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    jsonschema = None
    JSONSCHEMA_AVAILABLE = False
    logging.warning("jsonschema not available - configuration validation disabled")

# Import secure storage
from .secure_config import get_config_manager

logger = logging.getLogger(__name__)


class ConfigurationChangeHandler(FileSystemEventHandler):
    """Handles configuration file changes for hot-reloading"""
    
    def __init__(self, callback: Callable):
        self.callback = callback
        self.last_modified = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Debounce rapid changes
        file_path = event.src_path
        current_time = datetime.now().timestamp()
        
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < 1.0:  # 1 second debounce
                return
                
        self.last_modified[file_path] = current_time
        self.callback(file_path)


class ConfigurationManager:
    """
    Unified configuration management system for UX-MIRROR.
    
    Features:
    - Hierarchical configuration loading (defaults -> user -> environment)
    - JSON schema validation
    - Hot-reloading of configuration files
    - Secure storage for sensitive data
    - Environment variable substitution
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        
        # Configuration paths
        self.base_dir = Path(__file__).parent.parent
        self.config_dir = self.base_dir / "config"
        self.schemas_dir = self.config_dir / "schemas"
        
        # Create directories if needed
        self.config_dir.mkdir(exist_ok=True)
        self.schemas_dir.mkdir(exist_ok=True)
        
        # Configuration storage
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.config_files: Dict[str, Path] = {}
        
        # Secure config manager for sensitive data
        self.secure_config = get_config_manager()
        
        # Change callbacks
        self.change_callbacks: List[Callable] = []
        
        # File watcher for hot-reloading
        self.observer = None
        self.enable_hot_reload = True
        
        # Load initial configurations
        self._load_all_configurations()
        
        # Start file watcher
        if self.enable_hot_reload:
            self._start_file_watcher()
        
        logger.info("Configuration Manager initialized")
    
    def _load_all_configurations(self):
        """Load all configuration files and schemas"""
        # Load schemas first
        self._load_schemas()
        
        # Load configuration files
        config_files = [
            "orchestrator_config.json",
            "vision_config.json",
            "api_config.json",
            "monitoring_config.json",
            "agent_config.json"
        ]
        
        for config_file in config_files:
            config_path = self.config_dir / config_file
            if config_path.exists():
                config_name = config_file.replace('_config.json', '')
                self._load_config_file(config_name, config_path)
        
        # Load environment-specific overrides
        self._load_environment_overrides()
    
    def _load_schemas(self):
        """Load all JSON schemas for validation"""
        schema_files = self.schemas_dir.glob("*.json")
        
        for schema_file in schema_files:
            try:
                with open(schema_file, 'r') as f:
                    schema_name = schema_file.stem.replace('_schema', '')
                    self.schemas[schema_name] = json.load(f)
                    logger.debug(f"Loaded schema: {schema_name}")
            except Exception as e:
                logger.error(f"Failed to load schema {schema_file}: {e}")
    
    def _load_config_file(self, config_name: str, file_path: Path) -> bool:
        """Load a single configuration file"""
        try:
            # Support both JSON and YAML
            with open(file_path, 'r') as f:
                if file_path.suffix == '.yaml' or file_path.suffix == '.yml':
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # Process environment variables
            config_data = self._substitute_env_vars(config_data)
            
            # Validate against schema if available
            if config_name in self.schemas and JSONSCHEMA_AVAILABLE:
                try:
                    jsonschema.validate(config_data, self.schemas[config_name])
                except jsonschema.ValidationError as e:
                    logger.error(f"Configuration validation failed for {config_name}: {e}")
                    return False
            
            # Store configuration
            self.configs[config_name] = config_data
            self.config_files[config_name] = file_path
            
            logger.info(f"Loaded configuration: {config_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load configuration {file_path}: {e}")
            return False
    
    def _substitute_env_vars(self, config: Any) -> Any:
        """Recursively substitute environment variables in configuration"""
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Check for ${VAR_NAME} pattern
            if config.startswith('${') and config.endswith('}'):
                var_name = config[2:-1]
                default = None
                
                # Check for default value ${VAR_NAME:default}
                if ':' in var_name:
                    var_name, default = var_name.split(':', 1)
                
                return os.getenv(var_name, default if default else config)
        
        return config
    
    def _load_environment_overrides(self):
        """Load environment-specific configuration overrides"""
        env = os.getenv('UX_MIRROR_ENV', 'development')
        
        # Look for environment-specific config files
        env_files = [
            self.config_dir / f"config.{env}.json",
            self.config_dir / f"config.{env}.yaml",
            Path.home() / f".ux_mirror/config.{env}.json",
            Path.home() / f".ux_mirror/config.{env}.yaml"
        ]
        
        for env_file in env_files:
            if env_file.exists():
                logger.info(f"Loading environment overrides from {env_file}")
                try:
                    with open(env_file, 'r') as f:
                        if env_file.suffix in ['.yaml', '.yml']:
                            overrides = yaml.safe_load(f)
                        else:
                            overrides = json.load(f)
                    
                    # Merge overrides into existing configs
                    for config_name, config_overrides in overrides.items():
                        if config_name in self.configs:
                            self.configs[config_name] = self._deep_merge(
                                self.configs[config_name], 
                                config_overrides
                            )
                        else:
                            self.configs[config_name] = config_overrides
                            
                except Exception as e:
                    logger.error(f"Failed to load environment overrides from {env_file}: {e}")
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _start_file_watcher(self):
        """Start watching configuration files for changes"""
        try:
            self.observer = Observer()
            handler = ConfigurationChangeHandler(self._on_config_changed)
            
            # Watch config directory
            self.observer.schedule(handler, str(self.config_dir), recursive=False)
            
            # Watch user config directory
            user_config_dir = Path.home() / ".ux_mirror"
            if user_config_dir.exists():
                self.observer.schedule(handler, str(user_config_dir), recursive=False)
            
            self.observer.start()
            logger.info("Configuration hot-reload watcher started")
            
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
            self.enable_hot_reload = False
    
    def _on_config_changed(self, file_path: str):
        """Handle configuration file changes"""
        file_path = Path(file_path)
        
        # Find which config this file belongs to
        for config_name, config_file in self.config_files.items():
            if config_file == file_path:
                logger.info(f"Reloading configuration: {config_name}")
                if self._load_config_file(config_name, file_path):
                    self._notify_change_callbacks(config_name)
                break
    
    def _notify_change_callbacks(self, config_name: str):
        """Notify registered callbacks of configuration changes"""
        for callback in self.change_callbacks:
            try:
                callback(config_name, self.configs.get(config_name, {}))
            except Exception as e:
                logger.error(f"Error in configuration change callback: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Examples:
            get('orchestrator.task_processing.max_concurrent_tasks')
            get('api.endpoints.status_endpoint')
        """
        keys = key.split('.')
        
        if len(keys) == 0:
            return default
        
        # First key is the config name
        config_name = keys[0]
        if config_name not in self.configs:
            return default
        
        # Navigate through nested keys
        value = self.configs[config_name]
        for k in keys[1:]:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, persist: bool = False) -> bool:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Dot-notated key (e.g., 'orchestrator.monitoring.interval')
            value: Value to set
            persist: Whether to save to file
        """
        keys = key.split('.')
        
        if len(keys) == 0:
            return False
        
        config_name = keys[0]
        
        # Ensure config exists
        if config_name not in self.configs:
            self.configs[config_name] = {}
        
        # Navigate to parent
        current = self.configs[config_name]
        for k in keys[1:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set value
        if len(keys) > 1:
            current[keys[-1]] = value
        else:
            self.configs[config_name] = value
        
        # Persist if requested
        if persist and config_name in self.config_files:
            self._save_config(config_name)
        
        # Notify callbacks
        self._notify_change_callbacks(config_name)
        
        return True
    
    def _save_config(self, config_name: str) -> bool:
        """Save configuration to file"""
        if config_name not in self.config_files:
            return False
        
        try:
            file_path = self.config_files[config_name]
            
            with open(file_path, 'w') as f:
                if file_path.suffix in ['.yaml', '.yml']:
                    yaml.dump(self.configs[config_name], f, default_flow_style=False)
                else:
                    json.dump(self.configs[config_name], f, indent=2)
            
            logger.info(f"Saved configuration: {config_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration {config_name}: {e}")
            return False
    
    def get_config(self, config_name: str) -> Dict[str, Any]:
        """Get entire configuration by name"""
        return self.configs.get(config_name, {}).copy()
    
    def register_change_callback(self, callback: Callable):
        """Register a callback for configuration changes"""
        if callback not in self.change_callbacks:
            self.change_callbacks.append(callback)
    
    def unregister_change_callback(self, callback: Callable):
        """Unregister a configuration change callback"""
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
    
    def reload_all(self):
        """Reload all configurations"""
        logger.info("Reloading all configurations...")
        self._load_all_configurations()
        
        # Notify all callbacks
        for config_name in self.configs:
            self._notify_change_callbacks(config_name)
    
    def get_secure_value(self, key: str, provider: str = None) -> Optional[str]:
        """Get secure value (e.g., API key) from secure storage"""
        if provider:
            return self.secure_config.get_api_key(provider)
        return self.secure_config.get_setting(key)
    
    def set_secure_value(self, key: str, value: str, provider: str = None) -> bool:
        """Set secure value in secure storage"""
        if provider:
            return self.secure_config.set_api_key(provider, value)
        return self.secure_config.set_setting(key, value)
    
    def validate_config(self, config_name: str, config_data: Dict[str, Any] = None) -> tuple[bool, List[str]]:
        """
        Validate configuration against schema.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if not JSONSCHEMA_AVAILABLE:
            return True, ["Schema validation not available"]
        
        if config_name not in self.schemas:
            return True, ["No schema defined for this configuration"]
        
        if config_data is None:
            config_data = self.configs.get(config_name, {})
        
        try:
            jsonschema.validate(config_data, self.schemas[config_name])
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e)]
    
    def export_config(self, config_name: str, file_path: Path, include_secure: bool = False):
        """Export configuration to file"""
        if config_name not in self.configs:
            raise ValueError(f"Configuration '{config_name}' not found")
        
        config_data = self.configs[config_name].copy()
        
        # Optionally include secure values
        if include_secure:
            # Add secure values as placeholders
            config_data['_secure_values'] = {
                'note': 'Replace these placeholders with actual values',
                'api_keys': {}
            }
            
            for provider in ['anthropic', 'openai', 'google']:
                key = self.secure_config.get_api_key(provider)
                if key:
                    config_data['_secure_values']['api_keys'][provider] = 'REPLACE_WITH_ACTUAL_KEY'
        
        # Save to file
        with open(file_path, 'w') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                yaml.dump(config_data, f, default_flow_style=False)
            else:
                json.dump(config_data, f, indent=2)
    
    def get_checksum(self, config_name: str) -> str:
        """Get configuration checksum for change detection"""
        if config_name not in self.configs:
            return ""
        
        config_str = json.dumps(self.configs[config_name], sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def shutdown(self):
        """Cleanup resources"""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        
        logger.info("Configuration Manager shutdown complete")


# Singleton instance getter
def get_configuration_manager() -> ConfigurationManager:
    """Get the singleton Configuration Manager instance"""
    return ConfigurationManager()