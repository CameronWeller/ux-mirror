"""
UX-MIRROR Autonomous Testing Framework
Phase 2: Input Automation System

Autonomous testing framework for UX analysis with intelligent input simulation.
"""

__version__ = "2.0.0"
__author__ = "UX-MIRROR Team"
__description__ = "Autonomous Testing Framework for UX Analysis"

# Package imports for easy access
try:
    from .core.input_controller import AutonomousInputController
    from .core.screen_analyzer import ScreenAnalyzer
    from .tests.test_scenarios import GameOfLifeTestScenarios
    from .utils.vm_manager import VMManager
    from .utils.report_generator import ReportGenerator
    
    __all__ = [
        'AutonomousInputController',
        'ScreenAnalyzer', 
        'GameOfLifeTestScenarios',
        'VMManager',
        'ReportGenerator'
    ]
    
except ImportError:
    # Graceful degradation if dependencies aren't installed
    __all__ = []

def get_version():
    """Get the current version of the autonomous testing framework"""
    return __version__

def get_info():
    """Get framework information"""
    return {
        "name": "UX-MIRROR Autonomous Testing",
        "version": __version__,
        "phase": "Phase 2: Input Automation System", 
        "description": __description__,
        "author": __author__
    } 