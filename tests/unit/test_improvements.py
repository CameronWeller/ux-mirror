#!/usr/bin/env python3
"""
Test script for UX-MIRROR workflow improvements

Tests the new features:
1. Port management system
2. Adaptive feedback engine  
3. Application detection
4. Standalone launcher functionality
"""

import sys
import traceback
from pathlib import Path

def test_port_manager():
    """Test the port management system"""
    print("🔌 Testing Port Manager...")
    try:
        from core.port_manager import get_port_manager, allocate_service_port
        
        # Test port allocation
        port_manager = get_port_manager()
        port1 = allocate_service_port("test_service_1", 8765)
        port2 = allocate_service_port("test_service_2")
        
        print(f"   ✅ Allocated ports: {port1}, {port2}")
        
        # Test status
        status = port_manager.get_status()
        print(f"   📊 Port manager status: {status['active_allocations']} active allocations")
        
        return True
    except Exception as e:
        print(f"   ❌ Port manager test failed: {e}")
        return False

def test_adaptive_feedback():
    """Test the adaptive feedback engine"""
    print("🧠 Testing Adaptive Feedback Engine...")
    try:
        from core.adaptive_feedback import AdaptiveFeedbackEngine, UserEngagementAction
        
        # Create engine
        engine = AdaptiveFeedbackEngine()
        
        # Start session
        session = engine.start_session("test_session", {"app": "test_app"})
        print(f"   ✅ Started session: {session.session_id}")
        
        # Test action determination
        action, context = engine.determine_action("test_session")
        print(f"   🎯 Initial action: {action.value}")
        print(f"   📊 Context: confidence={context.get('confidence', 0):.3f}")
        
        return True
    except Exception as e:
        print(f"   ❌ Adaptive feedback test failed: {e}")
        return False

def test_application_detector():
    """Test the application detection system"""
    print("📱 Testing Application Detector...")
    try:
        # Import from launcher
        sys.path.append('.')
        from ux_mirror_launcher import ApplicationDetector
        
        detector = ApplicationDetector()
        apps = detector.detect_applications()
        
        print(f"   ✅ Detected {len(apps)} applications")
        
        # Show some examples
        for i, app in enumerate(apps[:3]):  # Show first 3
            print(f"   📱 {app['display_name']} ({app['category']})")
        
        return True
    except Exception as e:
        print(f"   ❌ Application detector test failed: {e}")
        traceback.print_exc()
        return False

def test_orchestrator_improvements():
    """Test the unified system improvements"""
    print("🎯 Testing Unified System Improvements...")
    try:
        # Agent system removed - using unified architecture
        from core.screenshot_analyzer import ScreenshotAnalyzer
        
        # Test creation
        analyzer = ScreenshotAnalyzer()
        print(f"   ✅ ScreenshotAnalyzer created successfully")
        
        # Test that it has required methods
        assert hasattr(analyzer, 'capture_screenshot')
        assert hasattr(analyzer, 'analyze_image')
        print(f"   ⚙️ Required methods available")
        
        return True
    except Exception as e:
        print(f"   ❌ Unified system test failed: {e}")
        return False

def test_file_structure():
    """Test that all new files are in place"""
    print("📁 Testing File Structure...")
    
    required_files = [
        "core/port_manager.py",
        "core/adaptive_feedback.py", 
        "ux_mirror_launcher.py",
        "UX_MIRROR_WORKFLOW_IMPROVEMENTS.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🎯 UX-MIRROR Workflow Improvements Test Suite")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Port Manager", test_port_manager),
        ("Adaptive Feedback", test_adaptive_feedback),
        ("Application Detector", test_application_detector),
        ("Orchestrator Improvements", test_orchestrator_improvements)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'=' * 50}")
    print("📊 Test Results Summary:")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All workflow improvements are working correctly!")
        print("\n📋 Ready for next steps:")
        print("   1. Test the standalone launcher: python ux_mirror_launcher.py")
        print("   2. Run analysis on pygame game")
        print("   3. Test adaptive feedback with real application")
    else:
        print("⚠️  Some improvements need attention before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 