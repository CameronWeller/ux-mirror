"""
UX-MIRROR Testing Framework
==========================

A modern, modular UX testing framework with AI-powered content validation.

Main Components:
- core: Core UXTester class and main functionality
- vision: AI vision analysis for content validation  
- metrics: Performance and timing metrics
- utils: Helper functions and utilities
"""

try:
    from .core import UXTester
    from .metrics import PerformanceMetrics
    from .utils import load_config, validate_config
    __all__ = ["UXTester", "PerformanceMetrics", "load_config", "validate_config"]
except ImportError:
    # Allow individual module imports even if some dependencies are missing
    __all__ = []

__version__ = "0.2.0" 