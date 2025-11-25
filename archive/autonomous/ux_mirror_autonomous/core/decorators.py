#!/usr/bin/env python3
"""
Decorators for UX-MIRROR Testing Framework
Provides reusable decorators for cross-cutting concerns
"""

import functools
import time
import logging
from typing import Callable, Any, Optional, Dict
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class PerformanceMetrics:
    """Tracks performance metrics for decorated methods"""
    
    def __init__(self):
        self.metrics = {}
        self.call_counts = {}
        self.total_times = {}
        
    def record(self, method_name: str, execution_time: float):
        """Record execution metrics"""
        if method_name not in self.metrics:
            self.metrics[method_name] = []
            self.call_counts[method_name] = 0
            self.total_times[method_name] = 0
            
        self.metrics[method_name].append(execution_time)
        self.call_counts[method_name] += 1
        self.total_times[method_name] += execution_time
        
    def get_stats(self, method_name: str) -> Dict[str, float]:
        """Get statistics for a method"""
        if method_name not in self.metrics:
            return {}
            
        times = self.metrics[method_name]
        return {
            'count': self.call_counts[method_name],
            'total_time': self.total_times[method_name],
            'avg_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times)
        }

# Global metrics instance
performance_metrics = PerformanceMetrics()

def safety_check(*, 
                 log_calls: bool = True,
                 track_performance: bool = True,
                 pre_conditions: Optional[Callable] = None,
                 post_conditions: Optional[Callable] = None):
    """
    Decorator for safety checking in autonomous operations
    
    Args:
        log_calls: Whether to log method calls
        track_performance: Whether to track performance metrics
        pre_conditions: Optional callable for additional pre-condition checks
        post_conditions: Optional callable for post-condition validation
    
    Usage:
        @safety_check()
        def move_mouse(self, x: int, y: int) -> bool:
            # implementation
            
        @safety_check(pre_conditions=lambda self: self.is_initialized)
        def critical_operation(self) -> bool:
            # implementation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            method_name = f"{self.__class__.__name__}.{func.__name__}"
            
            # Log method call
            if log_calls:
                logger.info(f"Calling {method_name} with args={args}, kwargs={kwargs}")
            
            # Check safety conditions
            if hasattr(self, 'check_safety') and not self.check_safety():
                logger.warning(f"Safety check failed for {method_name}")
                # Return appropriate default based on return type hint
                return_type = func.__annotations__.get('return', None)
                if return_type == bool:
                    return False
                elif return_type in (int, float):
                    return 0
                else:
                    return None
            
            # Check custom pre-conditions
            if pre_conditions and not pre_conditions(self):
                logger.warning(f"Pre-condition failed for {method_name}")
                return False
            
            # Track performance
            start_time = time.time() if track_performance else None
            
            try:
                # Execute the actual method
                result = func(self, *args, **kwargs)
                
                # Check post-conditions
                if post_conditions and not post_conditions(self, result):
                    logger.warning(f"Post-condition failed for {method_name}")
                    return False
                
                return result
                
            except Exception as e:
                logger.error(f"Error in {method_name}: {e}")
                raise
                
            finally:
                # Record performance metrics
                if track_performance and start_time:
                    execution_time = time.time() - start_time
                    performance_metrics.record(method_name, execution_time)
                    
                    if execution_time > 1.0:  # Log slow operations
                        logger.warning(f"{method_name} took {execution_time:.2f}s")
        
        return wrapper
    return decorator

def retry(max_attempts: int = 3, 
          delay: float = 1.0,
          backoff_factor: float = 2.0,
          exceptions: tuple = (Exception,)):
    """
    Decorator for retrying operations with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(f"All attempts failed for {func.__name__}")
            
            # Re-raise the last exception if all attempts failed
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator

def screenshot_on_error(screenshot_dir: Optional[Path] = None):
    """
    Decorator to take a screenshot when an error occurs
    
    Args:
        screenshot_dir: Directory to save screenshots (defaults to ./error_screenshots)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                # Take screenshot if the object has the capability
                if hasattr(self, 'take_screenshot'):
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    error_name = f"error_{func.__name__}_{timestamp}"
                    
                    try:
                        screenshot_path = self.take_screenshot(error_name)
                        logger.error(f"Error screenshot saved: {screenshot_path}")
                    except:
                        logger.error("Failed to take error screenshot")
                
                # Re-raise the original exception
                raise
                
        return wrapper
    return decorator

def validate_bounds(x_param: str = 'x', y_param: str = 'y'):
    """
    Decorator to validate screen coordinate bounds
    
    Args:
        x_param: Name of the x coordinate parameter
        y_param: Name of the y coordinate parameter
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            # Get screen size if available
            if hasattr(self, 'get_screen_size'):
                width, height = self.get_screen_size()
                
                # Extract coordinates from args or kwargs
                import inspect
                sig = inspect.signature(func)
                bound_args = sig.bind(self, *args, **kwargs)
                bound_args.apply_defaults()
                
                x = bound_args.arguments.get(x_param)
                y = bound_args.arguments.get(y_param)
                
                # Validate bounds
                if x is not None and (x < 0 or x >= width):
                    logger.warning(f"X coordinate {x} out of bounds [0, {width})")
                    bound_args.arguments[x_param] = max(0, min(x, width - 1))
                    
                if y is not None and (y < 0 or y >= height):
                    logger.warning(f"Y coordinate {y} out of bounds [0, {height})")
                    bound_args.arguments[y_param] = max(0, min(y, height - 1))
                
                # Call with potentially modified arguments
                return func(*bound_args.args, **bound_args.kwargs)
            else:
                # No validation possible, call normally
                return func(self, *args, **kwargs)
                
        return wrapper
    return decorator

def thread_safe(lock_attr: str = '_lock'):
    """
    Decorator to make methods thread-safe using a lock
    
    Args:
        lock_attr: Name of the lock attribute on the instance
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            # Get or create lock
            if not hasattr(self, lock_attr):
                import threading
                setattr(self, lock_attr, threading.RLock())
            
            lock = getattr(self, lock_attr)
            
            with lock:
                return func(self, *args, **kwargs)
                
        return wrapper
    return decorator