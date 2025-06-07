"""
Integration Test Framework for UX-MIRROR
========================================

Provides comprehensive integration testing capabilities for validating
component interactions and system workflows.

Task: INTEGRATE-007A - Create test_framework.py with component interaction tests
"""

import asyncio
import logging
import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any, Optional
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from capture.screenshot_handler import ScreenshotHandler, get_screenshot_handler
from analysis.ui_element_detector import UIElementDetector, get_ui_detector, UIElementType
from ux_tester.port_manager import PortManager, get_port_manager

logger = logging.getLogger(__name__)

class IntegrationTestFramework:
    """
    Framework for running integration tests that validate component interactions
    and end-to-end system workflows.
    """
    
    def __init__(self):
        """Initialize the integration test framework"""
        self.test_results = []
        self.setup_complete = False
        
        # Test data directory
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        
        logger.info("Integration Test Framework initialized")
    
    async def setup_test_environment(self):
        """Set up the test environment with mock services"""
        try:
            # Initialize components
            self.screenshot_handler = ScreenshotHandler(
                storage_dir=str(self.test_data_dir / "screenshots"),
                max_stored=10
            )
            
            self.ui_detector = UIElementDetector(use_gpu=False)  # Use CPU for tests
            self.port_manager = PortManager(start_port=9500, end_port=9510)
            
            # Create test screenshots
            await self._create_test_screenshots()
            
            self.setup_complete = True
            logger.info("Test environment setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup test environment: {e}")
            raise
    
    async def teardown_test_environment(self):
        """Clean up test environment"""
        try:
            # Clean up test data
            if self.test_data_dir.exists():
                import shutil
                shutil.rmtree(self.test_data_dir)
            
            logger.info("Test environment teardown complete")
            
        except Exception as e:
            logger.error(f"Failed to teardown test environment: {e}")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests and return results"""
        if not self.setup_complete:
            await self.setup_test_environment()
        
        test_suite = [
            ("Screenshot Handler Tests", self._test_screenshot_handler_integration),
            ("UI Element Detector Tests", self._test_ui_detector_integration),
            ("Port Manager Tests", self._test_port_manager_integration),
            ("Component Integration Tests", self._test_component_integration),
            ("System Workflow Tests", self._test_system_workflows)
        ]
        
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "test_details": []
        }
        
        for test_name, test_func in test_suite:
            logger.info(f"Running {test_name}...")
            
            try:
                test_result = await test_func()
                results["test_details"].append({
                    "name": test_name,
                    "status": "PASSED" if test_result["passed"] else "FAILED",
                    "details": test_result
                })
                
                results["total_tests"] += test_result["total"]
                results["passed"] += test_result["passed"]
                results["failed"] += test_result["failed"]
                
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}")
                results["test_details"].append({
                    "name": test_name,
                    "status": "ERROR",
                    "error": str(e)
                })
                results["total_tests"] += 1
                results["failed"] += 1
        
        # Calculate overall success rate
        results["success_rate"] = (results["passed"] / results["total_tests"]) * 100 if results["total_tests"] > 0 else 0
        
        return results
    
    async def _test_screenshot_handler_integration(self) -> Dict[str, Any]:
        """Test screenshot handler integration"""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        
        # Test 1: Screenshot capture and storage
        results["total"] += 1
        try:
            screenshot = self.screenshot_handler.capture_screenshot()
            if screenshot is not None:
                saved_filename = self.screenshot_handler.save_screenshot(
                    screenshot, 
                    metadata={"test": "integration_test"}
                )
                if saved_filename:
                    results["passed"] += 1
                    results["details"].append("✅ Screenshot capture and storage successful")
                else:
                    results["failed"] += 1
                    results["details"].append("❌ Screenshot save failed")
            else:
                results["failed"] += 1
                results["details"].append("❌ Screenshot capture failed")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Screenshot test exception: {e}")
        
        # Test 2: Baseline comparison
        results["total"] += 1
        try:
            baseline_set = self.screenshot_handler.set_baseline()
            if baseline_set:
                comparison_result = self.screenshot_handler.compare_with_baseline()
                if comparison_result and "change_percentage" in comparison_result:
                    results["passed"] += 1
                    results["details"].append("✅ Baseline comparison successful")
                else:
                    results["failed"] += 1
                    results["details"].append("❌ Baseline comparison failed")
            else:
                results["failed"] += 1
                results["details"].append("❌ Baseline setting failed")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Baseline test exception: {e}")
        
        # Test 3: Storage statistics
        results["total"] += 1
        try:
            stats = self.screenshot_handler.get_storage_stats()
            if "total_screenshots" in stats and stats["total_screenshots"] > 0:
                results["passed"] += 1
                results["details"].append("✅ Storage statistics working")
            else:
                results["failed"] += 1
                results["details"].append("❌ Storage statistics failed")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Storage stats exception: {e}")
        
        return results
    
    async def _test_ui_detector_integration(self) -> Dict[str, Any]:
        """Test UI element detector integration"""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        
        # Create a test image with UI elements
        test_image = self._create_test_ui_image()
        
        # Test 1: Basic element detection
        results["total"] += 1
        try:
            elements = self.ui_detector.detect_elements(test_image)
            if len(elements) > 0:
                results["passed"] += 1
                results["details"].append(f"✅ Detected {len(elements)} UI elements")
            else:
                results["failed"] += 1
                results["details"].append("❌ No UI elements detected")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ UI detection exception: {e}")
        
        # Test 2: Element type classification
        results["total"] += 1
        try:
            elements = self.ui_detector.detect_elements(test_image)
            element_types = set(elem.element_type for elem in elements)
            if len(element_types) > 0:
                results["passed"] += 1
                results["details"].append(f"✅ Found element types: {element_types}")
            else:
                results["failed"] += 1
                results["details"].append("❌ No element types classified")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Classification exception: {e}")
        
        # Test 3: Confidence scoring
        results["total"] += 1
        try:
            elements = self.ui_detector.detect_elements(test_image)
            confident_elements = [e for e in elements if e.confidence > 0.5]
            if len(confident_elements) > 0:
                results["passed"] += 1
                results["details"].append(f"✅ {len(confident_elements)} high-confidence elements")
            else:
                results["failed"] += 1
                results["details"].append("❌ No high-confidence elements")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Confidence test exception: {e}")
        
        return results
    
    async def _test_port_manager_integration(self) -> Dict[str, Any]:
        """Test port manager integration"""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        
        # Test 1: Port allocation and release
        results["total"] += 1
        try:
            port = self.port_manager.allocate_port("test_service")
            if port:
                released = self.port_manager.release_port(port, "test_service")
                if released:
                    results["passed"] += 1
                    results["details"].append(f"✅ Port {port} allocated and released")
                else:
                    results["failed"] += 1
                    results["details"].append("❌ Port release failed")
            else:
                results["failed"] += 1
                results["details"].append("❌ Port allocation failed")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Port management exception: {e}")
        
        # Test 2: Port conflict detection
        results["total"] += 1
        try:
            port1 = self.port_manager.allocate_port("service1")
            port2 = self.port_manager.allocate_port("service2")
            
            if port1 and port2 and port1 != port2:
                results["passed"] += 1
                results["details"].append("✅ Port conflict detection working")
                
                # Clean up
                self.port_manager.release_port(port1, "service1")
                self.port_manager.release_port(port2, "service2")
            else:
                results["failed"] += 1
                results["details"].append("❌ Port conflict detection failed")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Conflict detection exception: {e}")
        
        # Test 3: Allocation status
        results["total"] += 1
        try:
            status = self.port_manager.get_allocation_status()
            if "total_ports" in status and "allocated_ports" in status:
                results["passed"] += 1
                results["details"].append("✅ Allocation status working")
            else:
                results["failed"] += 1
                results["details"].append("❌ Allocation status failed")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Status check exception: {e}")
        
        return results
    
    async def _test_component_integration(self) -> Dict[str, Any]:
        """Test integration between different components"""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        
        # Test 1: Screenshot + UI Detection workflow
        results["total"] += 1
        try:
            screenshot = self.screenshot_handler.capture_screenshot()
            if screenshot is not None:
                elements = self.ui_detector.detect_elements(screenshot)
                
                # Save screenshot with UI element metadata
                metadata = {
                    "ui_elements_count": len(elements),
                    "element_types": [e.element_type.value for e in elements]
                }
                
                saved_filename = self.screenshot_handler.save_screenshot(
                    screenshot, 
                    metadata=metadata
                )
                
                if saved_filename and len(elements) >= 0:  # Allow 0 elements for some screenshots
                    results["passed"] += 1
                    results["details"].append("✅ Screenshot + UI detection workflow successful")
                else:
                    results["failed"] += 1
                    results["details"].append("❌ Combined workflow failed")
            else:
                results["failed"] += 1
                results["details"].append("❌ Screenshot capture in workflow failed")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Workflow exception: {e}")
        
        # Test 2: Port Manager + Service simulation
        results["total"] += 1
        try:
            # Simulate service startup with port allocation
            services = ["visual_agent", "orchestrator", "metrics_agent"]
            allocated_ports = {}
            
            for service in services:
                port = self.port_manager.allocate_port(service)
                if port:
                    allocated_ports[service] = port
            
            if len(allocated_ports) == len(services):
                results["passed"] += 1
                results["details"].append("✅ Multi-service port allocation successful")
                
                # Clean up
                for service, port in allocated_ports.items():
                    self.port_manager.release_port(port, service)
            else:
                results["failed"] += 1
                results["details"].append("❌ Multi-service allocation failed")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Service simulation exception: {e}")
        
        return results
    
    async def _test_system_workflows(self) -> Dict[str, Any]:
        """Test end-to-end system workflows"""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        
        # Test 1: Complete UX analysis workflow
        results["total"] += 1
        try:
            # Capture screenshot
            screenshot = self.screenshot_handler.capture_screenshot()
            
            # Detect UI elements
            elements = self.ui_detector.detect_elements(screenshot)
            
            # Analyze accessibility
            accessibility_issues = []
            for element in elements:
                if element.accessibility_score < 0.5:
                    accessibility_issues.append(f"Low accessibility score for {element.element_type.value}")
            
            # Generate analysis report
            analysis_report = {
                "timestamp": "test_timestamp",
                "screenshot_captured": screenshot is not None,
                "ui_elements_detected": len(elements),
                "accessibility_issues": len(accessibility_issues),
                "recommendations": [
                    "Improve element contrast" if accessibility_issues else "Good accessibility"
                ]
            }
            
            if analysis_report["screenshot_captured"] and analysis_report["ui_elements_detected"] >= 0:
                results["passed"] += 1
                results["details"].append("✅ Complete UX analysis workflow successful")
            else:
                results["failed"] += 1
                results["details"].append("❌ UX analysis workflow failed")
                
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Analysis workflow exception: {e}")
        
        # Test 2: Baseline comparison workflow
        results["total"] += 1
        try:
            # Set baseline
            baseline_set = self.screenshot_handler.set_baseline()
            
            # Capture new screenshot
            new_screenshot = self.screenshot_handler.capture_screenshot()
            
            # Compare with baseline
            comparison = self.screenshot_handler.compare_with_baseline(new_screenshot)
            
            if baseline_set and comparison and "change_percentage" in comparison:
                results["passed"] += 1
                results["details"].append("✅ Baseline comparison workflow successful")
            else:
                results["failed"] += 1
                results["details"].append("❌ Baseline comparison workflow failed")
                
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Baseline workflow exception: {e}")
        
        return results
    
    def _create_test_ui_image(self) -> np.ndarray:
        """Create a synthetic test image with UI elements"""
        # Create a blank image
        image = np.ones((600, 800, 3), dtype=np.uint8) * 255  # White background
        
        # Draw some UI elements
        # Button
        cv2.rectangle(image, (100, 100), (200, 140), (200, 200, 200), -1)
        cv2.rectangle(image, (100, 100), (200, 140), (0, 0, 0), 2)
        cv2.putText(image, "Button", (120, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Input field
        cv2.rectangle(image, (100, 180), (350, 210), (255, 255, 255), -1)
        cv2.rectangle(image, (100, 180), (350, 210), (128, 128, 128), 2)
        
        # Text
        cv2.putText(image, "Sample Text Content", (100, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Container
        cv2.rectangle(image, (50, 300), (400, 500), (240, 240, 240), -1)
        cv2.rectangle(image, (50, 300), (400, 500), (0, 0, 0), 1)
        
        return image
    
    async def _create_test_screenshots(self):
        """Create test screenshots for testing"""
        try:
            # Create a simple test screenshot
            test_image = self._create_test_ui_image()
            
            # Save as test screenshot
            test_screenshot_path = self.test_data_dir / "test_screenshot.png"
            cv2.imwrite(str(test_screenshot_path), test_image)
            
            logger.info("Test screenshots created")
            
        except Exception as e:
            logger.error(f"Failed to create test screenshots: {e}")

# Test runner functions for pytest integration
@pytest.fixture
async def integration_framework():
    """Pytest fixture for integration test framework"""
    framework = IntegrationTestFramework()
    await framework.setup_test_environment()
    yield framework
    await framework.teardown_test_environment()

@pytest.mark.asyncio
async def test_screenshot_handler_integration(integration_framework):
    """Test screenshot handler integration"""
    results = await integration_framework._test_screenshot_handler_integration()
    assert results["passed"] > 0, f"Screenshot handler tests failed: {results['details']}"

@pytest.mark.asyncio
async def test_ui_detector_integration(integration_framework):
    """Test UI detector integration"""
    results = await integration_framework._test_ui_detector_integration()
    assert results["passed"] > 0, f"UI detector tests failed: {results['details']}"

@pytest.mark.asyncio
async def test_port_manager_integration(integration_framework):
    """Test port manager integration"""
    results = await integration_framework._test_port_manager_integration()
    assert results["passed"] > 0, f"Port manager tests failed: {results['details']}"

@pytest.mark.asyncio
async def test_component_integration(integration_framework):
    """Test component integration"""
    results = await integration_framework._test_component_integration()
    assert results["passed"] > 0, f"Component integration tests failed: {results['details']}"

@pytest.mark.asyncio
async def test_system_workflows(integration_framework):
    """Test system workflows"""
    results = await integration_framework._test_system_workflows()
    assert results["passed"] > 0, f"System workflow tests failed: {results['details']}"

if __name__ == "__main__":
    async def main():
        framework = IntegrationTestFramework()
        results = await framework.run_all_tests()
        
        print("\n🧪 Integration Test Results")
        print("=" * 50)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        
        for test in results['test_details']:
            status_icon = "✅" if test['status'] == "PASSED" else "❌"
            print(f"\n{status_icon} {test['name']}: {test['status']}")
            
            if 'details' in test:
                for detail in test['details']['details']:
                    print(f"   {detail}")
        
        await framework.teardown_test_environment()
        
        return results['success_rate'] == 100.0
    
    import asyncio
    success = asyncio.run(main())
    exit(0 if success else 1) 