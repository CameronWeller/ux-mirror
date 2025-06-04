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

from .core import UXTester
from .metrics import PerformanceMetrics
from .utils import load_config, validate_config

__version__ = "0.2.0"
__all__ = ["UXTester", "PerformanceMetrics", "load_config", "validate_config"] 