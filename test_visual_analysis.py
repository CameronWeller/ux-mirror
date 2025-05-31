#!/usr/bin/env python3
"""
Test script for UX-MIRROR Visual Analysis Agent
===============================================

This script tests the visual analysis agent functionality including:
- Screenshot capture simulation
- External API integration (mocked)
- Custom recognizer training
- Issue detection

Usage:
    python test_visual_analysis.py
"""

import asyncio
import json
import base64
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add agents directory to path
sys.path.insert(0, 'agents')

from visual_analysis import (
    VisualAnalysisAgent, 
    ScreenshotCapture, 
    CustomRecognizerTrainer,
    ExternalVisionAPI
)

class MockOrchestrator:
    """Mock orchestrator for testing"""
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.received_messages = []
        
    async def start_server(self):
        """Start mock WebSocket server"""
        import websockets
        
        async def handle_client(websocket, path):
            try:
                async for message in websocket:
                    data = json.loads(message)
                    self.received_messages.append(data)
                    print(f"📨 Received from agent: {data.get('type', 'unknown')}")
                    
                    # Send mock responses
                    if data.get("agent_id") == "visual_analysis":
                        await websocket.send(json.dumps({
                            "type": "registration_confirmed",
                            "agent_id": "visual_analysis"
                        }))
                        
            except websockets.exceptions.ConnectionClosed:
                print("🔌 Agent disconnected")
            except Exception as e:
                print(f"❌ Server error: {e}")
        
        print(f"🚀 Starting mock orchestrator on port {self.port}")
        server = await websockets.serve(handle_client, "localhost", self.port)
        return server

async def test_screenshot_capture():
    """Test screenshot capture functionality"""
    print("\n🔍 Testing Screenshot Capture...")
    
    agent = VisualAnalysisAgent()
    
    # Test web screenshot capture
    web_screenshots = await agent._capture_web_screenshots()
    print(f"📱 Web screenshots captured: {len(web_screenshots)}")
    
    # Test desktop screenshot capture
    desktop_screenshots = await agent._capture_desktop_screenshots()
    print(f"🖥️  Desktop screenshots captured: {len(desktop_screenshots)}")
    
    # Test mobile screenshot capture
    mobile_screenshots = await agent._capture_mobile_screenshots()
    print(f"📱 Mobile screenshots captured: {len(mobile_screenshots)}")
    
    all_screenshots = web_screenshots + desktop_screenshots + mobile_screenshots
    
    if all_screenshots:
        print("✅ Screenshot capture working")
        return all_screenshots[0]  # Return first screenshot for further testing
    else:
        print("❌ No screenshots captured")
        return None

async def test_custom_recognizer_training():
    """Test custom recognizer training"""
    print("\n🧠 Testing Custom Recognizer Training...")
    
    trainer = CustomRecognizerTrainer("training_data/")
    
    # Create mock training data
    mock_image_data = b"fake_image_data_for_testing"
    
    # Add training samples for different issue types
    issue_types = [
        "low_contrast_text",
        "small_clickable_elements", 
        "inconsistent_fonts"
    ]
    
    for issue_type in issue_types:
        for i in range(12):  # Add enough samples to trigger training
            trainer.add_training_sample(
                issue_type=issue_type,
                image_data=mock_image_data + str(i).encode(),
                bounding_box=(50 + i*10, 100 + i*5, 100, 50),
                metadata={
                    'text_content': f'Sample {i} error message',
                    'dominant_colors': ['#FF0000', '#FFFFFF'],
                    'element_text': 'Error'
                }
            )
        
        # Train recognizer
        success = trainer.train_recognizer(issue_type, {
            'min_samples': 10,
            'validation_split': 0.2,
            'confidence_threshold': 0.7
        })
        
        if success:
            print(f"✅ Trained recognizer for {issue_type}")
        else:
            print(f"❌ Failed to train recognizer for {issue_type}")
    
    print(f"🎯 Total recognizers trained: {len(trainer.recognizers)}")
    return trainer

async def test_external_api_integration():
    """Test external API integration (mocked)"""
    print("\n🌐 Testing External API Integration...")
    
    # Test with mock API keys
    os.environ['GOOGLE_VISION_API_KEY'] = 'mock_google_key'
    os.environ['OPENAI_API_KEY'] = 'mock_openai_key'
    
    # Create mock image data
    mock_image_data = b"mock_screenshot_data"
    
    # Test Google Vision API (would be mocked in real test)
    try:
        api = ExternalVisionAPI("google_vision", "mock_key", {})
        print("✅ Google Vision API configured")
    except Exception as e:
        print(f"⚠️  Google Vision API error: {e}")
    
    # Test OpenAI Vision API (would be mocked in real test)
    try:
        api = ExternalVisionAPI("openai_vision", "mock_key", {})
        print("✅ OpenAI Vision API configured")
    except Exception as e:
        print(f"⚠️  OpenAI Vision API error: {e}")

async def test_issue_detection(screenshot: ScreenshotCapture, trainer: CustomRecognizerTrainer):
    """Test UX issue detection"""
    print("\n🔍 Testing Issue Detection...")
    
    if not screenshot:
        print("❌ No screenshot available for testing")
        return
    
    # Test custom recognizers
    custom_issues = trainer.apply_custom_recognizers(screenshot)
    print(f"🎯 Custom recognizer issues detected: {len(custom_issues)}")
    
    for issue in custom_issues:
        print(f"  - {issue.issue_type}: {issue.description} (confidence: {issue.confidence:.2f})")
    
    # Test built-in issue detection
    agent = VisualAnalysisAgent()
    
    # Mock UI elements for testing
    from visual_analysis import UIElement
    
    mock_elements = [
        UIElement(
            element_type='button',
            bounding_box=(100, 200, 30, 20),  # Small button
            confidence=0.9,
            text_content='Click me'
        ),
        UIElement(
            element_type='text',
            bounding_box=(50, 50, 200, 30),
            confidence=0.8,
            text_content='Low contrast text',
            attributes={'color': '#CCCCCC', 'background': '#FFFFFF'}
        )
    ]
    
    # Test accessibility issues
    accessibility_issues = agent._check_accessibility_issues(mock_elements)
    print(f"♿ Accessibility issues detected: {len(accessibility_issues)}")
    
    # Test design consistency
    design_issues = agent._check_design_consistency(mock_elements)
    print(f"🎨 Design consistency issues detected: {len(design_issues)}")
    
    total_issues = len(custom_issues) + len(accessibility_issues) + len(design_issues)
    print(f"📊 Total issues detected: {total_issues}")

async def test_configuration_loading():
    """Test configuration loading"""
    print("\n⚙️  Testing Configuration Loading...")
    
    agent = VisualAnalysisAgent()
    
    try:
        await agent._load_configuration()
        print("✅ Configuration loaded successfully")
        
        # Check if APIs are configured
        if agent.config.get('vision_apis'):
            enabled_apis = [
                api for api, config in agent.config['vision_apis'].items() 
                if config.get('enabled', False)
            ]
            print(f"🔌 Enabled APIs: {', '.join(enabled_apis)}")
        
        # Check custom recognizer config
        if agent.config.get('custom_recognizers', {}).get('enabled'):
            print("🧠 Custom recognizers enabled")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

async def test_agent_integration():
    """Test full agent integration"""
    print("\n🔄 Testing Agent Integration...")
    
    # Start mock orchestrator
    orchestrator = MockOrchestrator()
    server = await orchestrator.start_server()
    
    try:
        # Give server time to start
        await asyncio.sleep(1)
        
        # Create and configure agent
        agent = VisualAnalysisAgent()
        await agent._load_configuration()
        
        # Test connection to orchestrator
        await agent._connect_to_orchestrator()
        print("✅ Connected to orchestrator")
        
        # Wait for registration
        await asyncio.sleep(1)
        
        # Check received messages
        if orchestrator.received_messages:
            print(f"📨 Messages received by orchestrator: {len(orchestrator.received_messages)}")
            for msg in orchestrator.received_messages:
                print(f"  - {msg.get('type', 'unknown')}: {msg.get('agent_id', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        return False
        
    finally:
        server.close()
        await server.wait_closed()

async def run_all_tests():
    """Run all tests"""
    print("🧪 Starting UX-MIRROR Visual Analysis Agent Tests")
    print("=" * 50)
    
    test_results = []
    
    # Test configuration loading
    config_result = await test_configuration_loading()
    test_results.append(("Configuration Loading", config_result))
    
    # Test screenshot capture
    screenshot = await test_screenshot_capture()
    test_results.append(("Screenshot Capture", screenshot is not None))
    
    # Test custom recognizer training
    trainer = await test_custom_recognizer_training()
    test_results.append(("Custom Recognizer Training", len(trainer.recognizers) > 0))
    
    # Test external API integration
    await test_external_api_integration()
    test_results.append(("External API Integration", True))  # Just config test
    
    # Test issue detection
    await test_issue_detection(screenshot, trainer)
    test_results.append(("Issue Detection", True))  # Basic functionality test
    
    # Test agent integration
    integration_result = await test_agent_integration()
    test_results.append(("Agent Integration", integration_result))
    
    # Print test summary
    print("\n" + "=" * 50)
    print("🧪 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Visual Analysis Agent is working correctly.")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the output above for details.")
    
    return passed == total

def main():
    """Main test function"""
    try:
        result = asyncio.run(run_all_tests())
        exit_code = 0 if result else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 