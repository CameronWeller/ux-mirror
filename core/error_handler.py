#!/usr/bin/env python3
"""
UX-MIRROR Error Handler
======================

Provides context-aware error handling with automatic retry mechanisms,
exponential backoff, and error reporting.

Author: UX-MIRROR System
Version: 1.0.0
"""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Type, Union, TypeVar
from datetime import datetime, timedelta
import random
import json
from collections import defaultdict
from dataclasses import dataclass

from .exceptions import (
    UXMirrorException, ErrorSeverity, ErrorCategory,
    NetworkError, ResourceError, GPUError, APIError
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True  # Add random jitter to prevent thundering herd
    retryable_exceptions: List[Type[Exception]] = None
    on_retry: Optional[Callable[[Exception, int], None]] = None
    
    def __post_init__(self):
        if self.retryable_exceptions is None:
            # Default retryable exceptions
            self.retryable_exceptions = [
                NetworkError,
                ResourceError,
                APIError,
                ConnectionError,
                TimeoutError,
            ]


class ErrorHandler:
    """
    Centralized error handling with retry logic and reporting.
    
    Features:
    - Automatic retry with exponential backoff
    - Context-aware error handling
    - Error aggregation and reporting
    - Circuit breaker pattern
    """
    
    def __init__(self):
        self.error_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'last_error': None,
            'first_seen': None,
            'last_seen': None,
            'recovery_attempts': 0,
            'successful_recoveries': 0
        })
        
        # Circuit breaker state
        self.circuit_breakers: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'state': 'closed',  # closed, open, half-open
            'failure_count': 0,
            'last_failure': None,
            'last_success': None,
            'failure_threshold': 5,
            'success_threshold': 2,
            'timeout': timedelta(minutes=5)
        })
        
        # Global error handlers
        self.error_handlers: Dict[Type[Exception], List[Callable]] = defaultdict(list)
        
        # Error reporting callbacks
        self.error_reporters: List[Callable] = []
        
        logger.info("Error Handler initialized")
    
    def register_error_handler(self, exception_type: Type[Exception], handler: Callable):
        """Register a custom error handler for specific exception types"""
        self.error_handlers[exception_type].append(handler)
    
    def register_error_reporter(self, reporter: Callable):
        """Register an error reporting callback"""
        self.error_reporters.append(reporter)
    
    def retry(self, config: Optional[RetryConfig] = None):
        """
        Decorator for adding retry logic to functions.
        
        Usage:
            @error_handler.retry(RetryConfig(max_attempts=5))
            async def flaky_operation():
                # code that might fail
        """
        if config is None:
            config = RetryConfig()
        
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                return await self._retry_async(func, config, *args, **kwargs)
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                return self._retry_sync(func, config, *args, **kwargs)
            
            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    async def _retry_async(self, func: Callable, config: RetryConfig, *args, **kwargs) -> Any:
        """Async retry implementation"""
        last_exception = None
        attempt = 0
        
        func_name = f"{func.__module__}.{func.__name__}"
        
        while attempt < config.max_attempts:
            try:
                # Check circuit breaker
                if not self._check_circuit_breaker(func_name):
                    raise ResourceError(
                        f"Circuit breaker open for {func_name}",
                        resource_type='function',
                        context={'circuit_breaker_state': self.circuit_breakers[func_name]}
                    )
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Success - update circuit breaker
                self._on_success(func_name)
                
                return result
                
            except Exception as e:
                last_exception = e
                attempt += 1
                
                # Check if exception is retryable
                if not self._is_retryable(e, config.retryable_exceptions):
                    self._on_error(func_name, e)
                    raise
                
                # Calculate delay
                delay = self._calculate_delay(attempt, config)
                
                # Log retry attempt
                logger.warning(
                    f"Retry attempt {attempt}/{config.max_attempts} for {func_name} "
                    f"after {type(e).__name__}: {str(e)}. Waiting {delay:.1f}s"
                )
                
                # Call retry callback if provided
                if config.on_retry:
                    try:
                        config.on_retry(e, attempt)
                    except Exception as callback_error:
                        logger.error(f"Error in retry callback: {callback_error}")
                
                # Wait before retry
                if attempt < config.max_attempts:
                    await asyncio.sleep(delay)
                    
                self._on_error(func_name, e)
        
        # All retries exhausted
        if isinstance(last_exception, UXMirrorException):
            last_exception.add_context('retry_attempts', attempt)
            last_exception.add_recovery_suggestion(
                f"Operation failed after {attempt} attempts. Consider increasing retry limit or timeout."
            )
        
        raise last_exception
    
    def _retry_sync(self, func: Callable, config: RetryConfig, *args, **kwargs) -> Any:
        """Sync retry implementation"""
        last_exception = None
        attempt = 0
        
        func_name = f"{func.__module__}.{func.__name__}"
        
        while attempt < config.max_attempts:
            try:
                # Check circuit breaker
                if not self._check_circuit_breaker(func_name):
                    raise ResourceError(
                        f"Circuit breaker open for {func_name}",
                        resource_type='function',
                        context={'circuit_breaker_state': self.circuit_breakers[func_name]}
                    )
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Success - update circuit breaker
                self._on_success(func_name)
                
                return result
                
            except Exception as e:
                last_exception = e
                attempt += 1
                
                # Check if exception is retryable
                if not self._is_retryable(e, config.retryable_exceptions):
                    self._on_error(func_name, e)
                    raise
                
                # Calculate delay
                delay = self._calculate_delay(attempt, config)
                
                # Log retry attempt
                logger.warning(
                    f"Retry attempt {attempt}/{config.max_attempts} for {func_name} "
                    f"after {type(e).__name__}: {str(e)}. Waiting {delay:.1f}s"
                )
                
                # Call retry callback if provided
                if config.on_retry:
                    try:
                        config.on_retry(e, attempt)
                    except Exception as callback_error:
                        logger.error(f"Error in retry callback: {callback_error}")
                
                # Wait before retry
                if attempt < config.max_attempts:
                    time.sleep(delay)
                    
                self._on_error(func_name, e)
        
        # All retries exhausted
        if isinstance(last_exception, UXMirrorException):
            last_exception.add_context('retry_attempts', attempt)
            last_exception.add_recovery_suggestion(
                f"Operation failed after {attempt} attempts. Consider increasing retry limit or timeout."
            )
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay with exponential backoff and optional jitter"""
        # Exponential backoff
        delay = min(
            config.initial_delay * (config.exponential_base ** (attempt - 1)),
            config.max_delay
        )
        
        # Add jitter if enabled
        if config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def _is_retryable(self, exception: Exception, retryable_types: List[Type[Exception]]) -> bool:
        """Check if exception is retryable"""
        # Check direct type match
        for exc_type in retryable_types:
            if isinstance(exception, exc_type):
                return True
        
        # Check if it's a UXMirrorException with retryable severity
        if isinstance(exception, UXMirrorException):
            # Don't retry critical or security errors
            if exception.severity in [ErrorSeverity.CRITICAL]:
                return False
            if exception.category == ErrorCategory.SECURITY:
                return False
                
        return False
    
    def _check_circuit_breaker(self, identifier: str) -> bool:
        """Check if circuit breaker allows operation"""
        breaker = self.circuit_breakers[identifier]
        
        if breaker['state'] == 'closed':
            return True
        
        if breaker['state'] == 'open':
            # Check if timeout has passed
            if breaker['last_failure']:
                time_since_failure = datetime.now() - breaker['last_failure']
                if time_since_failure > breaker['timeout']:
                    # Move to half-open state
                    breaker['state'] = 'half-open'
                    breaker['failure_count'] = 0
                    logger.info(f"Circuit breaker for {identifier} moved to half-open state")
                    return True
            return False
        
        # Half-open state - allow limited traffic
        return True
    
    def _on_success(self, identifier: str):
        """Handle successful operation"""
        breaker = self.circuit_breakers[identifier]
        breaker['last_success'] = datetime.now()
        
        if breaker['state'] == 'half-open':
            breaker['failure_count'] = 0
            if breaker.get('success_count', 0) >= breaker['success_threshold']:
                breaker['state'] = 'closed'
                breaker['success_count'] = 0
                logger.info(f"Circuit breaker for {identifier} closed after successful recovery")
            else:
                breaker['success_count'] = breaker.get('success_count', 0) + 1
    
    def _on_error(self, identifier: str, exception: Exception):
        """Handle operation error"""
        # Update error stats
        stats = self.error_stats[identifier]
        stats['count'] += 1
        stats['last_error'] = {
            'type': type(exception).__name__,
            'message': str(exception),
            'timestamp': datetime.now().isoformat()
        }
        if stats['first_seen'] is None:
            stats['first_seen'] = datetime.now().isoformat()
        stats['last_seen'] = datetime.now().isoformat()
        
        # Update circuit breaker
        breaker = self.circuit_breakers[identifier]
        breaker['failure_count'] += 1
        breaker['last_failure'] = datetime.now()
        
        if breaker['failure_count'] >= breaker['failure_threshold']:
            if breaker['state'] != 'open':
                breaker['state'] = 'open'
                logger.error(f"Circuit breaker for {identifier} opened after {breaker['failure_count']} failures")
        
        # Call error handlers
        self._call_error_handlers(exception)
        
        # Report error
        self._report_error(identifier, exception)
    
    def _call_error_handlers(self, exception: Exception):
        """Call registered error handlers"""
        # Find matching handlers
        for exc_type, handlers in self.error_handlers.items():
            if isinstance(exception, exc_type):
                for handler in handlers:
                    try:
                        handler(exception)
                    except Exception as e:
                        logger.error(f"Error in error handler: {e}")
    
    def _report_error(self, identifier: str, exception: Exception):
        """Report error to registered reporters"""
        error_report = {
            'identifier': identifier,
            'timestamp': datetime.now().isoformat(),
            'exception': {
                'type': type(exception).__name__,
                'message': str(exception),
                'is_ux_mirror_exception': isinstance(exception, UXMirrorException)
            },
            'stats': dict(self.error_stats[identifier]),
            'circuit_breaker': dict(self.circuit_breakers[identifier])
        }
        
        if isinstance(exception, UXMirrorException):
            error_report['exception'].update(exception.to_dict()['error'])
        
        for reporter in self.error_reporters:
            try:
                reporter(error_report)
            except Exception as e:
                logger.error(f"Error in error reporter: {e}")
    
    def handle_error(self, exception: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle an error with context and return structured error response.
        
        Args:
            exception: The exception to handle
            context: Additional context information
            
        Returns:
            Structured error response
        """
        # Add context if it's a UXMirrorException
        if isinstance(exception, UXMirrorException) and context:
            for key, value in context.items():
                exception.add_context(key, value)
        
        # Create structured response
        if isinstance(exception, UXMirrorException):
            error_response = exception.to_dict()
        else:
            # Convert regular exception to structured format
            error_response = {
                'error': {
                    'message': str(exception),
                    'type': type(exception).__name__,
                    'severity': ErrorSeverity.MEDIUM.value,
                    'category': ErrorCategory.UNKNOWN.value,
                    'timestamp': datetime.now().isoformat(),
                    'context': context or {},
                    'recovery_suggestions': [
                        "Check error logs for more details",
                        "Retry the operation"
                    ]
                }
            }
        
        # Call handlers and reporters
        self._call_error_handlers(exception)
        identifier = context.get('operation', 'unknown') if context else 'unknown'
        self._report_error(identifier, exception)
        
        return error_response
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get current error statistics"""
        return {
            'error_stats': dict(self.error_stats),
            'circuit_breakers': dict(self.circuit_breakers),
            'summary': {
                'total_errors': sum(stats['count'] for stats in self.error_stats.values()),
                'open_circuit_breakers': sum(
                    1 for breaker in self.circuit_breakers.values() 
                    if breaker['state'] == 'open'
                ),
                'operations_with_errors': len(self.error_stats)
            }
        }
    
    def reset_circuit_breaker(self, identifier: str):
        """Manually reset a circuit breaker"""
        if identifier in self.circuit_breakers:
            breaker = self.circuit_breakers[identifier]
            breaker['state'] = 'closed'
            breaker['failure_count'] = 0
            breaker['success_count'] = 0
            logger.info(f"Circuit breaker for {identifier} manually reset")


# Global error handler instance
_error_handler = None

def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


# Convenience decorators
def retry(config: Optional[RetryConfig] = None):
    """Convenience decorator for retry logic"""
    return get_error_handler().retry(config)


def with_error_handling(operation_name: str):
    """
    Decorator that adds error handling to a function.
    
    Usage:
        @with_error_handling("process_screenshot")
        async def process_screenshot(image):
            # code that might fail
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = {
                    'operation': operation_name,
                    'function': f"{func.__module__}.{func.__name__}",
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
                error_response = get_error_handler().handle_error(e, context)
                
                # Re-raise the exception with added context
                if isinstance(e, UXMirrorException):
                    raise
                else:
                    raise UXMirrorException(
                        str(e),
                        cause=e,
                        context=context
                    )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    'operation': operation_name,
                    'function': f"{func.__module__}.{func.__name__}",
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
                error_response = get_error_handler().handle_error(e, context)
                
                # Re-raise the exception with added context
                if isinstance(e, UXMirrorException):
                    raise
                else:
                    raise UXMirrorException(
                        str(e),
                        cause=e,
                        context=context
                    )
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator