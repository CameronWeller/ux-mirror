#!/usr/bin/env python3
"""
UX-MIRROR Custom Exception Hierarchy
===================================

Provides context-aware exceptions with automatic error tracking,
recovery suggestions, and structured error reporting.

Author: UX-MIRROR System
Version: 1.0.0
"""

import logging
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "critical"  # System cannot continue
    HIGH = "high"         # Major functionality impaired
    MEDIUM = "medium"     # Some features affected
    LOW = "low"          # Minor issues
    INFO = "info"        # Informational only


class ErrorCategory(Enum):
    """Error categories for classification"""
    CONFIGURATION = "configuration"
    NETWORK = "network"
    GPU = "gpu"
    ANALYSIS = "analysis"
    AGENT = "agent"
    SECURITY = "security"
    VALIDATION = "validation"
    RESOURCE = "resource"
    INTEGRATION = "integration"
    UNKNOWN = "unknown"


class UXMirrorException(Exception):
    """
    Base exception class for all UX-MIRROR exceptions.
    
    Provides:
    - Context tracking
    - Error categorization
    - Recovery suggestions
    - Structured error data
    """
    
    def __init__(self, 
                 message: str,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 context: Optional[Dict[str, Any]] = None,
                 recovery_suggestions: Optional[List[str]] = None,
                 cause: Optional[Exception] = None):
        """
        Initialize UX-MIRROR exception.
        
        Args:
            message: Human-readable error message
            severity: Error severity level
            category: Error category for classification
            context: Additional context data
            recovery_suggestions: List of recovery suggestions
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.category = category
        self.context = context or {}
        self.recovery_suggestions = recovery_suggestions or []
        self.cause = cause
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()
        
        # Add system context
        self.context.update({
            'timestamp': self.timestamp.isoformat(),
            'severity': severity.value,
            'category': category.value,
            'exception_type': self.__class__.__name__
        })
        
        # Log the error
        self._log_error()
    
    def _log_error(self):
        """Log the error with appropriate level"""
        log_message = f"[{self.category.value}] {self.message}"
        
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, extra=self.context)
        elif self.severity == ErrorSeverity.HIGH:
            logger.error(log_message, extra=self.context)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, extra=self.context)
        else:
            logger.info(log_message, extra=self.context)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization"""
        return {
            'error': {
                'message': self.message,
                'type': self.__class__.__name__,
                'severity': self.severity.value,
                'category': self.category.value,
                'timestamp': self.timestamp.isoformat(),
                'context': self.context,
                'recovery_suggestions': self.recovery_suggestions,
                'traceback': self.traceback if self.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH] else None
            }
        }
    
    def add_context(self, key: str, value: Any):
        """Add additional context after exception creation"""
        self.context[key] = value
    
    def add_recovery_suggestion(self, suggestion: str):
        """Add a recovery suggestion"""
        self.recovery_suggestions.append(suggestion)


# Configuration Exceptions
class ConfigurationError(UXMirrorException):
    """Configuration-related errors"""
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION,
            **kwargs
        )
        if config_key:
            self.add_context('config_key', config_key)
        
        # Add common recovery suggestions
        self.recovery_suggestions.extend([
            "Check configuration file syntax",
            "Verify all required configuration keys are present",
            "Ensure configuration values are within valid ranges",
            "Run configuration validation: python -m ux_mirror.validate_config"
        ])


class ConfigurationValidationError(ConfigurationError):
    """Configuration validation failed"""
    def __init__(self, message: str, validation_errors: List[str], **kwargs):
        super().__init__(message, **kwargs)
        self.add_context('validation_errors', validation_errors)
        self.add_recovery_suggestion("Fix validation errors listed in context")


# GPU/Resource Exceptions
class GPUError(UXMirrorException):
    """GPU-related errors"""
    def __init__(self, message: str, device_id: Optional[int] = None, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.GPU,
            **kwargs
        )
        if device_id is not None:
            self.add_context('device_id', device_id)
        
        self.recovery_suggestions.extend([
            "Check GPU drivers are properly installed",
            "Verify CUDA/ROCm installation",
            "Try running with CPU fallback: export UX_MIRROR_FORCE_CPU=1",
            "Check GPU memory availability"
        ])


class GPUMemoryError(GPUError):
    """GPU memory allocation failed"""
    def __init__(self, message: str, required_memory_mb: float, available_memory_mb: float, **kwargs):
        super().__init__(message, **kwargs)
        self.add_context('required_memory_mb', required_memory_mb)
        self.add_context('available_memory_mb', available_memory_mb)
        self.add_recovery_suggestion(f"Free up at least {required_memory_mb - available_memory_mb:.1f}MB of GPU memory")
        self.add_recovery_suggestion("Reduce batch size or model complexity")


# Network/Communication Exceptions
class NetworkError(UXMirrorException):
    """Network-related errors"""
    def __init__(self, message: str, endpoint: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.NETWORK,
            **kwargs
        )
        if endpoint:
            self.add_context('endpoint', endpoint)
        
        self.recovery_suggestions.extend([
            "Check network connectivity",
            "Verify firewall settings",
            "Ensure the target service is running",
            "Check proxy configuration if applicable"
        ])


class AgentCommunicationError(NetworkError):
    """Agent communication failed"""
    def __init__(self, message: str, agent_id: str, **kwargs):
        super().__init__(message, **kwargs)
        self.add_context('agent_id', agent_id)
        self.add_recovery_suggestion(f"Restart agent: {agent_id}")
        self.add_recovery_suggestion("Check agent logs for errors")


# Analysis Exceptions
class AnalysisError(UXMirrorException):
    """Analysis-related errors"""
    def __init__(self, message: str, analysis_type: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.ANALYSIS,
            **kwargs
        )
        if analysis_type:
            self.add_context('analysis_type', analysis_type)


class ScreenshotCaptureError(AnalysisError):
    """Screenshot capture failed"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, analysis_type='screenshot_capture', **kwargs)
        self.recovery_suggestions.extend([
            "Ensure the target application is running",
            "Check display permissions",
            "Verify graphics drivers are up to date",
            "Try alternative capture method"
        ])


class AIAnalysisError(AnalysisError):
    """AI analysis failed"""
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(message, analysis_type='ai_analysis', **kwargs)
        if provider:
            self.add_context('provider', provider)
        self.recovery_suggestions.extend([
            "Check API key configuration",
            "Verify API rate limits",
            "Ensure network connectivity to AI service",
            "Try alternative AI provider"
        ])


# Security Exceptions
class SecurityError(UXMirrorException):
    """Security-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SECURITY,
            **kwargs
        )


class AuthenticationError(SecurityError):
    """Authentication failed"""
    def __init__(self, message: str, auth_method: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        if auth_method:
            self.add_context('auth_method', auth_method)
        self.recovery_suggestions.extend([
            "Verify credentials are correct",
            "Check authentication token expiration",
            "Ensure proper permissions are granted"
        ])


# Resource Exceptions
class ResourceError(UXMirrorException):
    """Resource-related errors"""
    def __init__(self, message: str, resource_type: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.RESOURCE,
            **kwargs
        )
        if resource_type:
            self.add_context('resource_type', resource_type)


class ResourceExhaustedError(ResourceError):
    """Resource exhausted"""
    def __init__(self, message: str, resource_type: str, current_usage: Any, limit: Any, **kwargs):
        super().__init__(message, resource_type=resource_type, **kwargs)
        self.add_context('current_usage', current_usage)
        self.add_context('limit', limit)
        self.recovery_suggestions.extend([
            f"Reduce {resource_type} usage",
            f"Increase {resource_type} limits",
            "Restart to free up resources"
        ])


# Validation Exceptions
class ValidationError(UXMirrorException):
    """Validation-related errors"""
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            **kwargs
        )
        if field:
            self.add_context('field', field)
        if value is not None:
            self.add_context('invalid_value', str(value))


class SchemaValidationError(ValidationError):
    """Schema validation failed"""
    def __init__(self, message: str, schema_errors: List[Dict[str, Any]], **kwargs):
        super().__init__(message, **kwargs)
        self.add_context('schema_errors', schema_errors)
        for error in schema_errors:
            self.add_recovery_suggestion(f"Fix: {error.get('message', 'Unknown error')}")


# Integration Exceptions
class IntegrationError(UXMirrorException):
    """External integration errors"""
    def __init__(self, message: str, service: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.INTEGRATION,
            **kwargs
        )
        if service:
            self.add_context('service', service)


class APIError(IntegrationError):
    """External API error"""
    def __init__(self, message: str, service: str, status_code: Optional[int] = None, 
                 response_body: Optional[str] = None, **kwargs):
        super().__init__(message, service=service, **kwargs)
        if status_code:
            self.add_context('status_code', status_code)
        if response_body:
            self.add_context('response_body', response_body[:500])  # Limit response size
        
        # Add status code specific suggestions
        if status_code == 401:
            self.add_recovery_suggestion("Check API authentication credentials")
        elif status_code == 429:
            self.add_recovery_suggestion("Rate limit exceeded - wait before retrying")
        elif status_code == 500:
            self.add_recovery_suggestion("External service error - try again later")


# Agent Exceptions
class AgentError(UXMirrorException):
    """Agent-related errors"""
    def __init__(self, message: str, agent_id: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AGENT,
            **kwargs
        )
        if agent_id:
            self.add_context('agent_id', agent_id)


class AgentInitializationError(AgentError):
    """Agent initialization failed"""
    def __init__(self, message: str, agent_id: str, **kwargs):
        super().__init__(message, agent_id=agent_id, **kwargs)
        self.recovery_suggestions.extend([
            f"Check agent configuration for {agent_id}",
            "Verify agent dependencies are installed",
            "Check system resources availability"
        ])


class AgentTimeoutError(AgentError):
    """Agent operation timed out"""
    def __init__(self, message: str, agent_id: str, operation: str, timeout_seconds: float, **kwargs):
        super().__init__(message, agent_id=agent_id, **kwargs)
        self.add_context('operation', operation)
        self.add_context('timeout_seconds', timeout_seconds)
        self.recovery_suggestions.extend([
            f"Increase timeout for {operation}",
            f"Check if agent {agent_id} is overloaded",
            "Consider scaling agent resources"
        ])


# Factory function for creating exceptions from error data
def from_error_data(error_data: Dict[str, Any]) -> UXMirrorException:
    """
    Create an exception instance from error data dictionary.
    
    Useful for deserializing errors from API responses or logs.
    """
    error_info = error_data.get('error', error_data)
    
    # Map exception types to classes
    exception_map = {
        'ConfigurationError': ConfigurationError,
        'ConfigurationValidationError': ConfigurationValidationError,
        'GPUError': GPUError,
        'GPUMemoryError': GPUMemoryError,
        'NetworkError': NetworkError,
        'AgentCommunicationError': AgentCommunicationError,
        'AnalysisError': AnalysisError,
        'ScreenshotCaptureError': ScreenshotCaptureError,
        'AIAnalysisError': AIAnalysisError,
        'SecurityError': SecurityError,
        'AuthenticationError': AuthenticationError,
        'ResourceError': ResourceError,
        'ResourceExhaustedError': ResourceExhaustedError,
        'ValidationError': ValidationError,
        'SchemaValidationError': SchemaValidationError,
        'IntegrationError': IntegrationError,
        'APIError': APIError,
        'AgentError': AgentError,
        'AgentInitializationError': AgentInitializationError,
        'AgentTimeoutError': AgentTimeoutError
    }
    
    exception_type = error_info.get('type', 'UXMirrorException')
    exception_class = exception_map.get(exception_type, UXMirrorException)
    
    # Create exception instance
    exc = exception_class(
        message=error_info.get('message', 'Unknown error'),
        context=error_info.get('context', {}),
        recovery_suggestions=error_info.get('recovery_suggestions', [])
    )
    
    return exc