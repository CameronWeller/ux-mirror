"""
Common Module - Shared components for code reuse across the project.
Import all frequently used utilities for convenient access.
"""

# Configuration Management
from .config_manager import (
    ConfigManager,
    config_manager,
    get_config,
    get_agent_config,
    reload_config
)

# Base Classes
from .base_agent import BaseAgent, AgentMetrics

# Utilities
from .utils import (
    # File Operations
    ensure_directory,
    safe_json_load,
    safe_json_save,
    get_file_hash,
    
    # Time Utilities
    timestamp_now,
    parse_timestamp,
    time_since,
    format_duration,
    
    # Async Utilities
    async_retry,
    run_with_timeout,
    
    # Data Processing
    chunk_list,
    flatten_dict,
    merge_dicts,
    
    # Validation
    validate_port,
    validate_url,
    sanitize_filename,
    
    # Performance
    Timer,
    measure_performance,
    
    # Logging
    setup_logger,
    
    # System
    get_system_info,
    is_port_available,
    
    # Error Handling
    SafeExecutor
)

# Version
__version__ = "1.0.0"

# Convenience imports - commonly used together
__all__ = [
    # Config
    'get_config',
    'get_agent_config',
    'ConfigManager',
    
    # Base Classes
    'BaseAgent',
    'AgentMetrics',
    
    # Essential Utils
    'ensure_directory',
    'safe_json_load',
    'safe_json_save',
    'Timer',
    'async_retry',
    'setup_logger',
    'timestamp_now',
    
    # All utils accessible via utils submodule
    'utils'
]