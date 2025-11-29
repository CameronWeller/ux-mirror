"""
Common Utilities Module - Shared functions for the entire codebase.
Consolidates frequently used utilities to reduce duplication.
"""

import os
import json
import logging
import hashlib
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Callable
from functools import wraps, lru_cache
import time

logger = logging.getLogger(__name__)

# ============= File Operations =============

def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    Used across multiple modules for directory creation.
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def safe_json_load(filepath: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Safely load JSON file with error handling.
    Returns None if file doesn't exist or is invalid.
    """
    try:
        path = Path(filepath)
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
    return None

def safe_json_save(data: Dict[str, Any], filepath: Union[str, Path], 
                   indent: int = 2) -> bool:
    """
    Safely save data to JSON file with error handling.
    Returns True if successful, False otherwise.
    """
    try:
        path = Path(filepath)
        ensure_directory(path.parent)
        with open(path, 'w') as f:
            json.dump(data, f, indent=indent, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
        return False

@lru_cache(maxsize=128)
def get_file_hash(filepath: Union[str, Path]) -> Optional[str]:
    """
    Calculate MD5 hash of a file (cached for performance).
    Used for detecting file changes.
    """
    try:
        path = Path(filepath)
        if path.exists():
            with open(path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {filepath}: {e}")
    return None

# ============= Time and Date Utilities =============

def timestamp_now() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def parse_timestamp(timestamp: str) -> Optional[datetime]:
    """Parse ISO format timestamp"""
    try:
        return datetime.fromisoformat(timestamp)
    except Exception:
        return None

def time_since(start_time: datetime) -> float:
    """Calculate seconds elapsed since start_time"""
    return (datetime.now() - start_time).total_seconds()

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

# ============= Async Utilities =============

def async_retry(max_attempts: int = 3, delay: float = 1.0, 
                backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Decorator for retrying async functions with exponential backoff.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(f"{func.__name__} attempt {attempt} failed: {e}. Retrying in {current_delay}s...")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1
            
        return wrapper
    return decorator

async def run_with_timeout(coro, timeout: float, default=None):
    """
    Run a coroutine with a timeout.
    Returns default value if timeout occurs.
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"Coroutine timed out after {timeout}s")
        return default

# ============= Data Processing Utilities =============

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.
    Example: {'a': {'b': 1}} -> {'a.b': 1}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    dict2 values override dict1 values for matching keys.
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

# ============= Validation Utilities =============

def validate_port(port: int) -> bool:
    """Validate if port number is in valid range"""
    return 1 <= port <= 65535

def validate_url(url: str) -> bool:
    """Basic URL validation"""
    return url.startswith(('http://', 'https://', 'ws://', 'wss://'))

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    Useful for saving files with user-provided names.
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

# ============= Performance Monitoring =============

class Timer:
    """Context manager for timing code execution"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start_time
        logger.debug(f"{self.name} took {self.elapsed:.3f}s")

def measure_performance(func: Callable):
    """Decorator to measure function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.debug(f"{func.__name__} executed in {elapsed:.3f}s")
        return result
    return wrapper

# ============= Logging Utilities =============

def setup_logger(name: str, level: str = "INFO", 
                 log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    Used by all modules for consistent logging.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        ensure_directory(Path(log_file).parent)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)
    
    return logger

# ============= System Utilities =============

@lru_cache(maxsize=1)
def get_system_info() -> Dict[str, Any]:
    """Get basic system information (cached)"""
    import platform
    import psutil
    
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'memory_available': psutil.virtual_memory().available
    }

def is_port_available(port: int, host: str = 'localhost') -> bool:
    """Check if a port is available for binding"""
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False

# ============= Error Handling Utilities =============

class SafeExecutor:
    """
    Context manager for safe execution with error logging.
    Prevents exceptions from propagating while logging them.
    """
    
    def __init__(self, operation_name: str, default_return=None):
        self.operation_name = operation_name
        self.default_return = default_return
        self.error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            logger.error(f"Error in {self.operation_name}: {exc_val}")
            return True  # Suppress exception
    
    def execute(self, func: Callable, *args, **kwargs):
        """Execute a function within the safe context"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.error = e
            logger.error(f"Error executing {func.__name__} in {self.operation_name}: {e}")
            return self.default_return