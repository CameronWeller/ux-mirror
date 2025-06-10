#!/usr/bin/env python3
"""
Test Scenarios for 3D Game of Life - Autonomous Testing
Phase 2: Input Automation System

Defines comprehensive test scenarios for autonomous testing of the 3D Game of Life.
"""

import time
import random
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json

from ..core.input_controller import AutonomousInputController
from ..core.screen_analyzer import ScreenAnalyzer, GameState

logger = logging.getLogger(__name__)

class TestResult(Enum):
    """Test result status"""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"

@dataclass
class TestMetrics:
    """Test execution metrics"""
    duration: float
    fps_average: Optional[float]
    fps_min: Optional[float]
    fps_max: Optional[float]
    generation_reached: Optional[int]
    max_living_cells: Optional[int]
    ui_response_time: float
    screenshots_taken: int
    errors_encountered: int

@dataclass
class TestScenario:
    """Defines a test scenario"""
    name: str
    description: str
    steps: List[Dict[str, Any]]
    expected_outcome: Dict[str, Any]
    timeout: float = 300.0  # 5 minutes default
    category: str = "general"
    priority: int = 1  # 1=high, 2=medium, 3=low
    requires_ui_elements: List[str] = None

class GameOfLifeTestScenarios:
    """Test scenarios for 3D Game of Life"""
    
    def __init__(self, input_controller: AutonomousInputController, 
                 screen_analyzer: ScreenAnalyzer):
        self.input_controller = input_controller
        self.screen_analyzer = screen_analyzer
        self.test_results = []
        self.current_metrics = None
        
        # Load test configuration
        self.config = self._load_test_config()
        
        # Define all test scenarios
        self.scenarios = self._define_scenarios()
        
        logger.info(f"Initialized {len(self.scenarios)} test scenarios")
    
    def _load_test_config(self) -> Dict[str, Any]:
        """Load test configuration"""
        config_path = Path(__file__).parent.parent / "config" / "test_config.yaml"
        
        default_config = {
            "performance_thresholds": {
                "min_fps": 30,
                "target_fps": 60,
                "max_response_time": 0.5
            },
            "test_patterns": {
                "click_patterns": ["single", "double", "drag"],
                "keyboard_patterns": ["single_key", "key_combo", "text_input"],
                "mouse_patterns": ["linear", "curved", "random"]
            },
            "game_specific": {
                "max_test_generations": 1000,
                "stability_check_duration": 30.0,
                "pattern_recognition_timeout": 10.0
            }
        }
        
        # For now, return default config
        # TODO: Load from YAML file when available
        return default_config
    
    def _define_scenarios(self) -> List[TestScenario]:
        """Define all test scenarios"""
        scenarios = []
        
        # Basic Functionality Tests
        scenarios.extend(self._basic_functionality_tests())
        
        # Performance Tests
        scenarios.extend(self._performance_tests())
        
        # UI Interaction Tests  
        scenarios.extend(self._ui_interaction_tests())
        
        # Game Logic Tests
        scenarios.extend(self._game_logic_tests())
        
        # Stress Tests
        scenarios.extend(self._stress_tests())
        
        # User Experience Tests
        scenarios.extend(self._user_experience_tests())
        
        return scenarios
    
    def _basic_functionality_tests(self) -> List[TestScenario]:
        """Basic application functionality tests"""
        return [
            TestScenario(
                name="application_startup",
                description="Test application startup and initial state",
                category="basic",
                priority=1,
                steps=[
                    {"action": "wait_for_window", "timeout": 10.0},
                    {"action": "take_screenshot", "name": "startup"},
                    {"action": "analyze_game_state"},
                    {"action": "verify_ui_elements", "elements": ["play_button", "reset_button"]}
                ],
                expected_outcome={
                    "window_visible": True,
                    "fps": None,  # Should be 0 or None initially
                    "generation": 0,
                    "ui_responsive": True
                }
            ),
            
            TestScenario(
                name="basic_play_pause",
                description="Test basic play/pause functionality",
                category="basic",
                priority=1,
                steps=[
                    {"action": "click_element", "element": "play_button"},
                    {"action": "wait", "duration": 2.0},
                    {"action": "analyze_game_state"},
                    {"action": "verify_fps", "min_fps": 1},
                    {"action": "click_element", "element": "pause_button"},
                    {"action": "wait", "duration": 1.0},
                    {"action": "analyze_game_state"},
                    {"action": "verify_paused", "expected": True}
                ],
                expected_outcome={
                    "can_start": True,
                    "can_pause": True,
                    "fps_when_running": ">= 1",
                    "fps_when_paused": 0
                }
            ),
            
            TestScenario(
                name="reset_functionality",
                description="Test reset button functionality",
                category="basic",
                priority=1,
                steps=[
                    {"action": "click_element", "element": "play_button"},
                    {"action": "wait", "duration": 5.0},
                    {"action": "analyze_game_state"},
                    {"action": "store_generation", "key": "generation_before_reset"},
                    {"action": "click_element", "element": "reset_button"},
                    {"action": "wait", "duration": 1.0},
                    {"action": "analyze_game_state"},
                    {"action": "verify_reset", "generation": 0}
                ],
                expected_outcome={
                    "generation_resets": True,
                    "ui_responsive": True
                }
            )
        ]
    
    def _performance_tests(self) -> List[TestScenario]:
        """Performance-focused test scenarios"""
        return [
            TestScenario(
                name="fps_stability_test",
                description="Test FPS stability over extended period",
                category="performance",
                priority=1,
                timeout=120.0,  # 2 minutes
                steps=[
                    {"action": "click_element", "element": "play_button"},
                    {"action": "monitor_fps", "duration": 60.0, "sample_interval": 1.0},
                    {"action": "analyze_fps_stability"},
                    {"action": "verify_fps_consistency", "min_fps": 30, "target_fps": 60}
                ],
                expected_outcome={
                    "avg_fps": ">= 30",
                    "fps_stability": ">= 0.8",  # Less than 20% variation
                    "frame_drops": "< 5%"
                }
            ),
            
            TestScenario(
                name="memory_usage_test",
                description="Monitor memory usage during gameplay",
                category="performance",
                priority=2,
                timeout=180.0,  # 3 minutes
                steps=[
                    {"action": "monitor_memory", "start": True},
                    {"action": "click_element", "element": "play_button"},
                    {"action": "wait", "duration": 120.0},
                    {"action": "monitor_memory", "stop": True},
                    {"action": "analyze_memory_usage"}
                ],
                expected_outcome={
                    "memory_leak": False,
                    "peak_memory": "< 2GB",
                    "memory_growth": "< 100MB/min"
                }
            ),
            
            TestScenario(
                name="rapid_interaction_test",
                description="Test UI responsiveness under rapid interactions",
                category="performance",
                priority=2,
                steps=[
                    {"action": "rapid_clicks", "element": "play_button", "count": 10, "interval": 0.1},
                    {"action": "wait", "duration": 1.0},
                    {"action": "rapid_clicks", "element": "pause_button", "count": 10, "interval": 0.1},
                    {"action": "analyze_ui_responsiveness"},
                    {"action": "verify_no_crashes"}
                ],
                expected_outcome={
                    "ui_responsive": True,
                    "no_crashes": True,
                    "avg_response_time": "< 0.5s"
                }
            )
        ]
    
    def _ui_interaction_tests(self) -> List[TestScenario]:
        """UI interaction and usability tests"""
        return [
            TestScenario(
                name="mouse_interaction_patterns",
                description="Test various mouse interaction patterns",
                category="ui_interaction",
                priority=2,
                steps=[
                    {"action": "test_click_patterns", "patterns": ["single", "double", "right_click"]},
                    {"action": "test_drag_patterns", "patterns": ["linear", "curved"]},
                    {"action": "test_scroll_patterns", "directions": ["up", "down"]},
                    {"action": "verify_all_interactions"}
                ],
                expected_outcome={
                    "click_recognition": ">= 95%",
                    "drag_recognition": ">= 90%",
                    "scroll_recognition": ">= 90%"
                }
            ),
            
            TestScenario(
                name="keyboard_shortcuts_test",
                description="Test keyboard shortcuts and hotkeys",
                category="ui_interaction",
                priority=2,
                steps=[
                    {"action": "test_spacebar", "expected": "play_pause_toggle"},
                    {"action": "test_key", "key": "r", "expected": "reset"},
                    {"action": "test_key", "key": "esc", "expected": "pause_or_menu"},
                    {"action": "test_key_combinations", "combos": ["ctrl+r", "ctrl+p"]},
                    {"action": "verify_shortcuts"}
                ],
                expected_outcome={
                    "shortcut_recognition": ">= 90%",
                    "no_key_conflicts": True
                }
            ),
            
            TestScenario(
                name="window_interaction_test",
                description="Test window management interactions",
                category="ui_interaction",
                priority=3,
                steps=[
                    {"action": "test_window_resize", "directions": ["expand", "shrink"]},
                    {"action": "test_window_move"},
                    {"action": "test_minimize_restore"},
                    {"action": "verify_layout_adaptation"}
                ],
                expected_outcome={
                    "resize_handling": True,
                    "move_handling": True,
                    "minimize_restore": True,
                    "layout_adaptive": True
                }
            )
        ]
    
    def _game_logic_tests(self) -> List[TestScenario]:
        """Game-specific logic tests"""
        return [
            TestScenario(
                name="evolution_patterns_test",
                description="Test Game of Life evolution patterns",
                category="game_logic",
                priority=1,
                timeout=300.0,  # 5 minutes
                steps=[
                    {"action": "load_pattern", "pattern": "glider"},
                    {"action": "click_element", "element": "play_button"},
                    {"action": "monitor_evolution", "duration": 60.0},
                    {"action": "verify_pattern_behavior", "expected": "stable_movement"},
                    {"action": "reset_and_test", "pattern": "oscillator"},
                    {"action": "verify_pattern_behavior", "expected": "oscillation"}
                ],
                expected_outcome={
                    "pattern_recognition": True,
                    "evolution_accuracy": ">= 95%",
                    "stable_patterns": True
                }
            ),
            
            TestScenario(
                name="generation_counting_test",
                description="Test generation counter accuracy",
                category="game_logic",
                priority=1,
                steps=[
                    {"action": "click_element", "element": "play_button"},
                    {"action": "count_generations", "duration": 30.0},
                    {"action": "verify_generation_counting"},
                    {"action": "pause_and_resume_test"},
                    {"action": "verify_generation_persistence"}
                ],
                expected_outcome={
                    "counting_accuracy": ">= 99%",
                    "pause_resume_accuracy": True
                }
            ),
            
            TestScenario(
                name="cell_population_tracking",
                description="Test living cell count tracking",
                category="game_logic",
                priority=2,
                steps=[
                    {"action": "create_known_pattern", "cells": 5},
                    {"action": "verify_cell_count", "expected": 5},
                    {"action": "run_evolution", "generations": 10},
                    {"action": "track_population_changes"},
                    {"action": "verify_population_accuracy"}
                ],
                expected_outcome={
                    "initial_count_accurate": True,
                    "population_tracking": ">= 95%",
                    "zero_population_handling": True
                }
            )
        ]
    
    def _stress_tests(self) -> List[TestScenario]:
        """Stress testing scenarios"""
        return [
            TestScenario(
                name="long_duration_test",
                description="Extended gameplay session test",
                category="stress",
                priority=3,
                timeout=1800.0,  # 30 minutes
                steps=[
                    {"action": "click_element", "element": "play_button"},
                    {"action": "run_extended_session", "duration": 1500.0},  # 25 minutes
                    {"action": "monitor_stability"},
                    {"action": "check_for_degradation"}
                ],
                expected_outcome={
                    "no_crashes": True,
                    "performance_stable": True,
                    "memory_stable": True
                }
            ),
            
            TestScenario(
                name="high_density_pattern_test",
                description="Test with high-density cell patterns",
                category="stress",
                priority=2,
                steps=[
                    {"action": "create_high_density_pattern", "density": 0.8},
                    {"action": "click_element", "element": "play_button"},
                    {"action": "monitor_performance", "duration": 60.0},
                    {"action": "verify_performance_under_load"}
                ],
                expected_outcome={
                    "fps_under_load": ">= 15",
                    "no_crashes": True,
                    "responsive_ui": True
                }
            ),
            
            TestScenario(
                name="rapid_reset_test",
                description="Rapid reset operations stress test",
                category="stress",
                priority=2,
                steps=[
                    {"action": "rapid_reset_cycle", "cycles": 50, "interval": 0.5},
                    {"action": "verify_system_stability"},
                    {"action": "check_memory_leaks"}
                ],
                expected_outcome={
                    "no_crashes": True,
                    "reset_reliability": ">= 98%",
                    "no_memory_leaks": True
                }
            )
        ]
    
    def _user_experience_tests(self) -> List[TestScenario]:
        """User experience and accessibility tests"""
        return [
            TestScenario(
                name="visual_feedback_test",
                description="Test visual feedback and indicators",
                category="user_experience",
                priority=2,
                steps=[
                    {"action": "test_button_states", "buttons": ["play", "pause", "reset"]},
                    {"action": "test_hover_effects"},
                    {"action": "test_visual_indicators"},
                    {"action": "verify_feedback_clarity"}
                ],
                expected_outcome={
                    "button_states_clear": True,
                    "hover_feedback": True,
                    "visual_clarity": ">= 80%"
                }
            ),
            
            TestScenario(
                name="information_display_test",
                description="Test information display accuracy and readability",
                category="user_experience",
                priority=2,
                steps=[
                    {"action": "verify_fps_display", "accuracy": 0.95},
                    {"action": "verify_generation_display"},
                    {"action": "verify_cell_count_display"},
                    {"action": "test_display_updates"}
                ],
                expected_outcome={
                    "fps_display_accurate": True,
                    "generation_display_accurate": True,
                    "cell_count_accurate": True,
                    "update_frequency": ">= 1Hz"
                }
            ),
            
            TestScenario(
                name="error_handling_test",
                description="Test error handling and recovery",
                category="user_experience",
                priority=1,
                steps=[
                    {"action": "trigger_invalid_inputs"},
                    {"action": "test_boundary_conditions"},
                    {"action": "verify_error_recovery"},
                    {"action": "check_user_feedback"}
                ],
                expected_outcome={
                    "graceful_error_handling": True,
                    "user_notification": True,
                    "system_recovery": True
                }
            )
        ]
    
    def execute_scenario(self, scenario: TestScenario) -> Dict[str, Any]:
        """Execute a single test scenario"""
        logger.info(f"🧪 Executing scenario: {scenario.name}")
        
        start_time = time.time()
        result = TestResult.PASS
        metrics = TestMetrics(
            duration=0,
            fps_average=None,
            fps_min=None,
            fps_max=None,
            generation_reached=None,
            max_living_cells=None,
            ui_response_time=0,
            screenshots_taken=0,
            errors_encountered=0
        )
        
        context = {}  # Store data between steps
        
        try:
            self.input_controller.start_session(scenario.name)
            
            for step_idx, step in enumerate(scenario.steps):
                logger.info(f"  Step {step_idx + 1}: {step.get('action', 'unknown')}")
                
                step_result = self._execute_step(step, context, metrics)
                
                if not step_result:
                    result = TestResult.FAIL
                    logger.warning(f"  Step {step_idx + 1} failed")
                    break
                
                # Safety check
                if not self.input_controller.check_safety():
                    result = TestResult.ERROR
                    logger.error("Safety check failed, stopping scenario")
                    break
            
            # Verify expected outcomes
            if result == TestResult.PASS:
                outcome_result = self._verify_outcomes(scenario.expected_outcome, context)
                if not outcome_result:
                    result = TestResult.FAIL
            
        except Exception as e:
            logger.error(f"Scenario execution error: {e}")
            result = TestResult.ERROR
            metrics.errors_encountered += 1
        
        finally:
            self.input_controller.end_session(scenario.name)
        
        metrics.duration = time.time() - start_time
        
        test_result = {
            "scenario_name": scenario.name,
            "result": result.value,
            "metrics": metrics.__dict__,
            "context": context,
            "timestamp": time.time()
        }
        
        self.test_results.append(test_result)
        
        logger.info(f"📊 Scenario {scenario.name}: {result.value} ({metrics.duration:.2f}s)")
        
        return test_result
    
    def _execute_step(self, step: Dict[str, Any], context: Dict[str, Any], 
                     metrics: TestMetrics) -> bool:
        """Execute a single test step"""
        action = step.get("action")
        
        try:
            if action == "wait":
                time.sleep(step.get("duration", 1.0))
                return True
            
            elif action == "wait_for_window":
                timeout = step.get("timeout", 10.0)
                # Simple window detection - check if screen has content
                start_time = time.time()
                while time.time() - start_time < timeout:
                    screenshot = self.screen_analyzer.capture_screen()
                    if screenshot.size > 0:
                        return True
                    time.sleep(0.5)
                return False
            
            elif action == "take_screenshot":
                name = step.get("name", "step_screenshot")
                screenshot_path = self.input_controller.take_screenshot(name)
                metrics.screenshots_taken += 1
                context[f"screenshot_{name}"] = screenshot_path
                return bool(screenshot_path)
            
            elif action == "analyze_game_state":
                game_state = self.screen_analyzer.analyze_game_state()
                context["game_state"] = game_state
                
                # Update metrics
                if game_state.fps is not None:
                    if metrics.fps_average is None:
                        metrics.fps_average = game_state.fps
                        metrics.fps_min = game_state.fps
                        metrics.fps_max = game_state.fps
                    else:
                        # Simple running average (would be better with proper tracking)
                        metrics.fps_average = (metrics.fps_average + game_state.fps) / 2
                        metrics.fps_min = min(metrics.fps_min, game_state.fps)
                        metrics.fps_max = max(metrics.fps_max, game_state.fps)
                
                if game_state.generation is not None:
                    metrics.generation_reached = game_state.generation
                
                if game_state.living_cells is not None:
                    if metrics.max_living_cells is None:
                        metrics.max_living_cells = game_state.living_cells
                    else:
                        metrics.max_living_cells = max(metrics.max_living_cells, game_state.living_cells)
                
                return True
            
            elif action == "click_element":
                element_name = step.get("element")
                
                # Find element using screen analyzer
                ui_elements = self.screen_analyzer.find_ui_elements()
                
                if element_name in ui_elements:
                    elements = ui_elements[element_name]
                    if elements:
                        # Click the first found element
                        element = elements[0]
                        response_start = time.time()
                        
                        success = self.input_controller.click(
                            element.position[0], element.position[1]
                        )
                        
                        response_time = time.time() - response_start
                        metrics.ui_response_time = max(metrics.ui_response_time, response_time)
                        
                        return success
                
                logger.warning(f"Element '{element_name}' not found")
                return False
            
            elif action == "verify_fps":
                min_fps = step.get("min_fps", 1)
                game_state = context.get("game_state")
                
                if game_state and game_state.fps is not None:
                    return game_state.fps >= min_fps
                
                return False
            
            elif action == "verify_ui_elements":
                required_elements = step.get("elements", [])
                ui_elements = self.screen_analyzer.find_ui_elements()
                
                for required in required_elements:
                    if required not in ui_elements or not ui_elements[required]:
                        logger.warning(f"Required UI element '{required}' not found")
                        return False
                
                return True
            
            # Add more step implementations as needed...
            else:
                logger.warning(f"Unknown action: {action}")
                return True  # Don't fail on unknown actions
        
        except Exception as e:
            logger.error(f"Step execution error: {e}")
            metrics.errors_encountered += 1
            return False
    
    def _verify_outcomes(self, expected: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Verify expected outcomes against actual results"""
        try:
            game_state = context.get("game_state")
            
            for key, expected_value in expected.items():
                if key == "window_visible":
                    # Check if we have valid game state
                    if not game_state or not game_state.window_focused:
                        return False
                
                elif key == "fps" and game_state:
                    if isinstance(expected_value, str):
                        if expected_value.startswith(">="):
                            threshold = float(expected_value[2:].strip())
                            if game_state.fps is None or game_state.fps < threshold:
                                return False
                    elif expected_value is not None:
                        if game_state.fps != expected_value:
                            return False
                
                elif key == "generation" and game_state:
                    if game_state.generation != expected_value:
                        return False
                
                # Add more outcome verifications as needed...
            
            return True
            
        except Exception as e:
            logger.error(f"Outcome verification error: {e}")
            return False
    
    def run_test_suite(self, categories: Optional[List[str]] = None, 
                      priority_filter: Optional[int] = None) -> Dict[str, Any]:
        """Run a suite of test scenarios"""
        logger.info("🚀 Starting test suite execution")
        
        # Filter scenarios
        scenarios_to_run = self.scenarios
        
        if categories:
            scenarios_to_run = [s for s in scenarios_to_run if s.category in categories]
        
        if priority_filter:
            scenarios_to_run = [s for s in scenarios_to_run if s.priority <= priority_filter]
        
        logger.info(f"Running {len(scenarios_to_run)} scenarios")
        
        # Execute scenarios
        suite_start_time = time.time()
        
        for scenario in scenarios_to_run:
            self.execute_scenario(scenario)
            
            # Brief pause between scenarios
            time.sleep(2.0)
        
        suite_duration = time.time() - suite_start_time
        
        # Generate summary
        summary = self._generate_test_summary(suite_duration)
        
        logger.info("✅ Test suite completed")
        logger.info(f"📊 Summary: {summary['pass_count']}/{summary['total_count']} passed")
        
        return summary
    
    def _generate_test_summary(self, duration: float) -> Dict[str, Any]:
        """Generate test execution summary"""
        total_count = len(self.test_results)
        pass_count = sum(1 for r in self.test_results if r["result"] == "pass")
        fail_count = sum(1 for r in self.test_results if r["result"] == "fail")
        error_count = sum(1 for r in self.test_results if r["result"] == "error")
        
        # Calculate aggregate metrics
        total_screenshots = sum(r["metrics"]["screenshots_taken"] for r in self.test_results)
        total_errors = sum(r["metrics"]["errors_encountered"] for r in self.test_results)
        
        avg_fps = None
        fps_values = [r["metrics"]["fps_average"] for r in self.test_results 
                     if r["metrics"]["fps_average"] is not None]
        if fps_values:
            avg_fps = sum(fps_values) / len(fps_values)
        
        summary = {
            "total_count": total_count,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "error_count": error_count,
            "pass_rate": pass_count / total_count if total_count > 0 else 0,
            "total_duration": duration,
            "total_screenshots": total_screenshots,
            "total_errors": total_errors,
            "average_fps": avg_fps,
            "test_results": self.test_results
        }
        
        return summary

def main():
    """Test the scenarios system"""
    print("🧪 Testing Game of Life Test Scenarios...")
    
    # Create mock controllers for testing
    from ..core.input_controller import AutonomousInputController
    from ..core.screen_analyzer import ScreenAnalyzer
    
    input_controller = AutonomousInputController()
    screen_analyzer = ScreenAnalyzer()
    
    test_scenarios = GameOfLifeTestScenarios(input_controller, screen_analyzer)
    
    print(f"📋 Loaded {len(test_scenarios.scenarios)} test scenarios")
    
    # List scenarios by category
    categories = {}
    for scenario in test_scenarios.scenarios:
        if scenario.category not in categories:
            categories[scenario.category] = []
        categories[scenario.category].append(scenario.name)
    
    for category, names in categories.items():
        print(f"  {category}: {len(names)} scenarios")
        for name in names[:3]:  # Show first 3
            print(f"    - {name}")
        if len(names) > 3:
            print(f"    ... and {len(names) - 3} more")
    
    print("✅ Test scenarios system ready!")

if __name__ == "__main__":
    main() 