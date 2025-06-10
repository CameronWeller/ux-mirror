#!/usr/bin/env python3
"""
Main Test Runner for UX-MIRROR Autonomous Testing
Phase 2: Input Automation System

Orchestrates the complete autonomous testing process.
"""

import sys
import time
import logging
import argparse
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import yaml

# Add the autonomous testing modules to path
sys.path.append(str(Path(__file__).parent))

try:
    from ux_mirror_autonomous.core.input_controller import AutonomousInputController
    from ux_mirror_autonomous.core.screen_analyzer import ScreenAnalyzer
    from ux_mirror_autonomous.tests.test_scenarios import GameOfLifeTestScenarios, TestResult
    from ux_mirror_autonomous.utils.vm_manager import VMManager
    from ux_mirror_autonomous.utils.report_generator import ReportGenerator
except ImportError as e:
    print(f"❌ Failed to import autonomous testing modules: {e}")
    print("Please ensure all Phase 2 dependencies are installed:")
    print("pip install pyautogui opencv-python pillow pytesseract psutil pyyaml")
    sys.exit(1)

logger = logging.getLogger(__name__)

class AutonomousTestRunner:
    """Main autonomous test runner orchestrating the complete testing process"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_config()
        self.base_path = Path(__file__).parent
        self.results_dir = self.base_path / "test_results"
        
        # Initialize components
        self.input_controller = None
        self.screen_analyzer = None
        self.test_scenarios = None
        self.vm_manager = None
        self.report_generator = None
        
        # Test execution state
        self.current_session = None
        self.test_results = []
        
        # Setup logging
        self._setup_logging()
        
        logger.info("AutonomousTestRunner initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_path = self.base_path / "config" / "test_config.yaml"
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        # Return default config if file doesn't exist
        return {
            "test_execution": {
                "default_timeout": 300,
                "screenshot_on_action": True,
                "safety_enabled": True
            },
            "performance_thresholds": {
                "min_fps": 30,
                "target_fps": 60,
                "max_ui_response_time": 0.5
            },
            "vm_settings": {
                "vm_memory_limit": 4096,
                "vm_cpu_cores": 2
            }
        }
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        # Create logs directory
        logs_dir = self.results_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        log_level = self.config.get("logging", {}).get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / f"test_runner_{int(time.time())}.log"),
                logging.StreamHandler()
            ]
        )
    
    def initialize_components(self) -> bool:
        """Initialize all testing components"""
        try:
            logger.info("🔧 Initializing autonomous testing components...")
            
            # Initialize input controller
            input_config = self.config.get("input_simulation", {})
            self.input_controller = AutonomousInputController(input_config)
            logger.info("✅ Input controller initialized")
            
            # Initialize screen analyzer
            analyzer_config = self.config.get("ui_detection", {})
            self.screen_analyzer = ScreenAnalyzer(analyzer_config)
            logger.info("✅ Screen analyzer initialized")
            
            # Initialize test scenarios
            self.test_scenarios = GameOfLifeTestScenarios(
                self.input_controller, self.screen_analyzer
            )
            logger.info("✅ Test scenarios loaded")
            
            # Initialize VM manager (if needed)
            vm_config = self.config.get("vm_settings", {})
            self.vm_manager = VMManager(vm_config)
            logger.info("✅ VM manager initialized")
            
            # Initialize report generator
            report_config = self.config.get("reporting", {})
            self.report_generator = ReportGenerator(report_config)
            logger.info("✅ Report generator initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            return False
    
    def pre_test_checks(self) -> bool:
        """Perform pre-test system checks"""
        logger.info("🔍 Performing pre-test checks...")
        
        checks_passed = 0
        total_checks = 4
        
        # Check screen capture capability
        try:
            screenshot = self.screen_analyzer.capture_screen()
            if screenshot.size > 0:
                logger.info("✅ Screen capture working")
                checks_passed += 1
            else:
                logger.error("❌ Screen capture failed")
        except Exception as e:
            logger.error(f"❌ Screen capture error: {e}")
        
        # Check input simulation capability
        try:
            screen_size = self.input_controller.get_screen_size()
            if screen_size[0] > 0 and screen_size[1] > 0:
                logger.info(f"✅ Input simulation ready (screen: {screen_size})")
                checks_passed += 1
            else:
                logger.error("❌ Invalid screen size detected")
        except Exception as e:
            logger.error(f"❌ Input simulation error: {e}")
        
        # Check safety systems
        try:
            safety_ok = self.input_controller.check_safety()
            if safety_ok:
                logger.info("✅ Safety systems operational")
                checks_passed += 1
            else:
                logger.error("❌ Safety check failed")
        except Exception as e:
            logger.error(f"❌ Safety system error: {e}")
        
        # Check test scenarios availability
        try:
            scenario_count = len(self.test_scenarios.scenarios)
            if scenario_count > 0:
                logger.info(f"✅ {scenario_count} test scenarios available")
                checks_passed += 1
            else:
                logger.error("❌ No test scenarios available")
        except Exception as e:
            logger.error(f"❌ Test scenarios error: {e}")
        
        success = checks_passed == total_checks
        logger.info(f"📊 Pre-test checks: {checks_passed}/{total_checks} passed")
        
        return success
    
    def run_test_suite(self, suite_type: str = "basic", 
                      priority_filter: Optional[int] = None,
                      categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run a complete test suite"""
        logger.info(f"🚀 Starting {suite_type} test suite...")
        
        # Create session identifier
        session_id = f"{suite_type}_{int(time.time())}"
        self.current_session = session_id
        
        start_time = time.time()
        
        try:
            # Pre-test checks
            if not self.pre_test_checks():
                logger.error("❌ Pre-test checks failed, aborting test suite")
                return self._create_error_result("Pre-test checks failed")
            
            # Configure test parameters based on suite type
            test_config = self._get_suite_config(suite_type)
            
            if categories:
                test_config["categories"] = categories
            if priority_filter:
                test_config["priority_filter"] = priority_filter
            
            logger.info(f"📋 Test configuration: {test_config}")
            
            # Start the target application if needed
            if test_config.get("auto_start_target", True):
                if not self._start_target_application():
                    logger.warning("⚠️ Failed to start target application, continuing anyway")
            
            # Wait for application to be ready
            ready_timeout = test_config.get("ready_timeout", 10)
            if not self._wait_for_application_ready(ready_timeout):
                logger.warning("⚠️ Application may not be ready")
            
            # Run the actual tests
            results = self.test_scenarios.run_test_suite(
                categories=test_config.get("categories"),
                priority_filter=test_config.get("priority_filter")
            )
            
            # Add session metadata
            results["session_id"] = session_id
            results["suite_type"] = suite_type
            results["config"] = test_config
            results["total_duration"] = time.time() - start_time
            
            # Generate comprehensive report
            report_path = self._generate_final_report(results)
            results["report_path"] = report_path
            
            logger.info(f"✅ Test suite completed successfully!")
            logger.info(f"📊 Results: {results['pass_count']}/{results['total_count']} passed")
            logger.info(f"📁 Report: {report_path}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Test suite execution failed: {e}")
            return self._create_error_result(str(e))
        
        finally:
            # Cleanup
            self._cleanup_test_session()
    
    def _get_suite_config(self, suite_type: str) -> Dict[str, Any]:
        """Get configuration for specific test suite type"""
        configs = {
            "basic": {
                "categories": ["basic"],
                "priority_filter": 1,
                "auto_start_target": True,
                "ready_timeout": 15,
                "description": "Essential functionality tests"
            },
            "full": {
                "categories": None,  # All categories
                "priority_filter": None,  # All priorities
                "auto_start_target": True,
                "ready_timeout": 20,
                "description": "Comprehensive test suite"
            },
            "performance": {
                "categories": ["performance"],
                "priority_filter": 2,
                "auto_start_target": True,
                "ready_timeout": 15,
                "description": "Performance and stability tests"
            },
            "game_logic": {
                "categories": ["game_logic"],
                "priority_filter": 2,
                "auto_start_target": True,
                "ready_timeout": 15,
                "description": "Game-specific logic tests"
            },
            "stress": {
                "categories": ["stress"],
                "priority_filter": 3,
                "auto_start_target": True,
                "ready_timeout": 25,
                "description": "Stress and endurance tests"
            }
        }
        
        return configs.get(suite_type, configs["basic"])
    
    def _start_target_application(self) -> bool:
        """Start the target application (3D Game of Life)"""
        try:
            logger.info("🎮 Starting target application...")
            
            # Look for the game executable
            possible_paths = [
                Path("game-target/build_minimal/x64/Release/minimal_vulkan_app.exe"),
                Path("game-target/build/Release/minimal_vulkan_app.exe"),
                Path("../game-target/build_minimal/x64/Release/minimal_vulkan_app.exe"),
                Path("minimal_vulkan_app.exe")
            ]
            
            game_exe = None
            for path in possible_paths:
                if path.exists():
                    game_exe = path
                    break
            
            if not game_exe:
                logger.warning("⚠️ Game executable not found, autonomous testing will run without target")
                return False
            
            # Start the game process
            import subprocess
            self.game_process = subprocess.Popen([str(game_exe)])
            
            logger.info(f"✅ Target application started: {game_exe}")
            time.sleep(3)  # Allow time for startup
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start target application: {e}")
            return False
    
    def _wait_for_application_ready(self, timeout: float) -> bool:
        """Wait for the target application to be ready for testing"""
        try:
            logger.info(f"⏳ Waiting for application ready (timeout: {timeout}s)...")
            
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Check if we can analyze the game state
                game_state = self.screen_analyzer.analyze_game_state()
                
                if game_state.window_focused:
                    logger.info("✅ Application appears ready for testing")
                    return True
                
                time.sleep(1)
            
            logger.warning("⚠️ Application readiness timeout exceeded")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error waiting for application ready: {e}")
            return False
    
    def _generate_final_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive final report"""
        try:
            logger.info("📄 Generating comprehensive test report...")
            
            if self.report_generator:
                report_path = self.report_generator.generate_full_report(
                    results, self.current_session
                )
                
                if report_path:
                    logger.info(f"✅ Report generated: {report_path}")
                    return report_path
            
            # Fallback: Generate simple JSON report
            timestamp = int(time.time())
            report_path = self.results_dir / f"test_report_{timestamp}.json"
            
            with open(report_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"✅ Basic report saved: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate report: {e}")
            return ""
    
    def _cleanup_test_session(self):
        """Cleanup after test session"""
        try:
            logger.info("🧹 Cleaning up test session...")
            
            # Stop target application if we started it
            if hasattr(self, 'game_process') and self.game_process:
                try:
                    self.game_process.terminate()
                    logger.info("✅ Target application stopped")
                except:
                    pass
            
            # Reset input controller
            if self.input_controller:
                self.input_controller.end_session("cleanup")
            
            # Save session data
            if self.current_session:
                session_data = {
                    "session_id": self.current_session,
                    "timestamp": time.time(),
                    "completed": True
                }
                
                session_file = self.results_dir / f"session_{self.current_session}.json"
                with open(session_file, 'w') as f:
                    json.dump(session_data, f, indent=2)
            
            logger.info("✅ Cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result structure"""
        return {
            "success": False,
            "error": error_message,
            "total_count": 0,
            "pass_count": 0,
            "fail_count": 0,
            "error_count": 1,
            "pass_rate": 0.0,
            "total_duration": 0.0,
            "test_results": []
        }
    
    def get_available_suites(self) -> List[Dict[str, Any]]:
        """Get list of available test suites"""
        return [
            {
                "name": "basic",
                "display_name": "Basic Test Suite",
                "description": "Essential functionality tests (~5 minutes)",
                "estimated_duration": 300
            },
            {
                "name": "full", 
                "display_name": "Full Test Suite",
                "description": "Comprehensive testing (~30 minutes)",
                "estimated_duration": 1800
            },
            {
                "name": "performance",
                "display_name": "Performance Tests",
                "description": "FPS, memory, response time analysis (~10 minutes)",
                "estimated_duration": 600
            },
            {
                "name": "game_logic",
                "display_name": "Game Logic Tests", 
                "description": "3D Game of Life specific testing (~15 minutes)",
                "estimated_duration": 900
            },
            {
                "name": "stress",
                "display_name": "Stress Tests",
                "description": "Extended stability testing (~45 minutes)",
                "estimated_duration": 2700
            }
        ]

def main(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Main entry point for autonomous testing"""
    
    # Parse command line arguments if running directly
    if config is None and __name__ == "__main__":
        parser = argparse.ArgumentParser(description="UX-MIRROR Autonomous Testing")
        parser.add_argument("--suite", default="basic", 
                          choices=["basic", "full", "performance", "game_logic", "stress"],
                          help="Test suite to run")
        parser.add_argument("--categories", nargs="*",
                          help="Specific test categories to run")
        parser.add_argument("--priority", type=int, choices=[1, 2, 3],
                          help="Maximum priority level to run")
        parser.add_argument("--config", type=str,
                          help="Path to custom config file")
        
        args = parser.parse_args()
        
        # Load custom config if specified
        if args.config:
            config_path = Path(args.config)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
        
        # Create config from args
        if config is None:
            config = {
                "test_suite": args.suite,
                "categories": args.categories,
                "priority_filter": args.priority
            }
    
    # Default config for launcher integration
    if config is None:
        config = {"test_suite": "basic"}
    
    print("🤖 UX-MIRROR Autonomous Testing System")
    print("Phase 2: Input Automation System")
    print("=" * 50)
    
    # Initialize test runner
    runner = AutonomousTestRunner(config)
    
    if not runner.initialize_components():
        print("❌ Failed to initialize testing components")
        return runner._create_error_result("Component initialization failed")
    
    # Extract test parameters
    suite_type = config.get("test_suite", "basic")
    categories = config.get("categories")
    priority_filter = config.get("priority_filter")
    
    print(f"🚀 Running {suite_type} test suite...")
    if categories:
        print(f"📋 Categories: {', '.join(categories)}")
    if priority_filter:
        print(f"⭐ Priority filter: {priority_filter}")
    print()
    
    # Run the test suite
    results = runner.run_test_suite(
        suite_type=suite_type,
        categories=categories,
        priority_filter=priority_filter
    )
    
    # Print summary
    if results.get("success", True):  # Default to True for backward compatibility
        print("✅ Test suite completed successfully!")
        print(f"📊 Results: {results['pass_count']}/{results['total_count']} tests passed")
        print(f"⏱️ Duration: {results['total_duration']:.1f} seconds")
        
        if results.get("report_path"):
            print(f"📁 Full report: {results['report_path']}")
    else:
        print("❌ Test suite failed!")
        print(f"Error: {results.get('error', 'Unknown error')}")
    
    return results

if __name__ == "__main__":
    try:
        result = main()
        exit_code = 0 if result.get("success", True) else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 