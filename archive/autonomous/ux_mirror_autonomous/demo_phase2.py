#!/usr/bin/env python3
"""
Phase 2 Demonstration Script
UX-MIRROR Autonomous Testing System

Demonstrates the capabilities of the Phase 2 input automation system.
"""

import time
import sys
from pathlib import Path

# Add autonomous framework to path
sys.path.append(str(Path(__file__).parent))

from ux_mirror_autonomous.core.input_controller import AutonomousInputController
from ux_mirror_autonomous.core.screen_analyzer import ScreenAnalyzer
from ux_mirror_autonomous.tests.test_scenarios import GameOfLifeTestScenarios

def demonstrate_input_controller():
    """Demonstrate the autonomous input controller capabilities"""
    print("\n🖱️ AUTONOMOUS INPUT CONTROLLER DEMO")
    print("=" * 50)
    
    try:
        controller = AutonomousInputController()
        
        # Get screen info
        screen_size = controller.get_screen_size()
        print(f"📺 Screen Size: {screen_size[0]} x {screen_size[1]}")
        
        # Take a screenshot
        print("📸 Taking screenshot...")
        screenshot_path = controller.take_screenshot("demo_screenshot")
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        # Test safety systems
        safety_ok = controller.check_safety()
        print(f"🛡️ Safety Systems: {'✅ Operational' if safety_ok else '❌ Warning'}")
        
        # Demonstrate configuration
        config = controller.config
        print(f"⚙️ Mouse Speed: {config.get('mouse_speed', 'default')}")
        print(f"⚙️ Click Timing: {config.get('click_timing', 'default')}")
        print(f"⚙️ Error Simulation: {config.get('error_simulation', 0) * 100}%")
        
        print("✅ Input controller demonstration completed!")
        
    except Exception as e:
        print(f"❌ Input controller demo failed: {e}")

def demonstrate_screen_analyzer():
    """Demonstrate the screen analyzer capabilities"""
    print("\n👁️ SCREEN ANALYZER DEMO")
    print("=" * 50)
    
    try:
        analyzer = ScreenAnalyzer()
        
        # Capture and analyze screen
        print("📊 Analyzing current screen...")
        screenshot = analyzer.capture_screen()
        
        if screenshot.size > 0:
            print(f"✅ Screen captured: {screenshot.shape}")
            
            # Analyze game state
            game_state = analyzer.analyze_game_state(screenshot)
            print(f"🎮 Game Running: {game_state.is_running}")
            print(f"🎮 Window Focused: {game_state.window_focused}")
            print(f"🎮 FPS: {game_state.fps}")
            print(f"🎮 Generation: {game_state.generation}")
            print(f"🎮 Living Cells: {game_state.living_cells}")
            print(f"🎮 Paused: {game_state.paused}")
            
            # Find UI elements
            ui_elements = analyzer.find_ui_elements(screenshot)
            print(f"🔍 UI Elements Found: {len(ui_elements)}")
            for element_type, elements in ui_elements.items():
                print(f"   • {element_type}: {len(elements)} instances")
            
            # Save analysis
            analysis_path = analyzer.save_analysis_result(
                screenshot, game_state, ui_elements, "demo_analysis"
            )
            print(f"💾 Analysis saved: {analysis_path}")
            
        else:
            print("❌ Failed to capture screen")
        
        print("✅ Screen analyzer demonstration completed!")
        
    except Exception as e:
        print(f"❌ Screen analyzer demo failed: {e}")

def demonstrate_test_scenarios():
    """Demonstrate the test scenarios system"""
    print("\n🧪 TEST SCENARIOS DEMO")
    print("=" * 50)
    
    try:
        # Create controllers
        input_controller = AutonomousInputController()
        screen_analyzer = ScreenAnalyzer()
        
        # Create test scenarios
        test_scenarios = GameOfLifeTestScenarios(input_controller, screen_analyzer)
        
        print(f"📋 Total Scenarios Available: {len(test_scenarios.scenarios)}")
        
        # Group by category
        categories = {}
        for scenario in test_scenarios.scenarios:
            category = scenario.category
            if category not in categories:
                categories[category] = []
            categories[category].append(scenario)
        
        print("\n📊 Scenarios by Category:")
        for category, scenarios in categories.items():
            print(f"   • {category}: {len(scenarios)} scenarios")
            for scenario in scenarios[:2]:  # Show first 2
                print(f"     - {scenario.name} (Priority {scenario.priority})")
            if len(scenarios) > 2:
                print(f"     ... and {len(scenarios) - 2} more")
        
        # Show available test suites
        print("\n🚀 Available Test Suites:")
        suites = [
            ("basic", "Essential functionality tests (~5 min)"),
            ("full", "Comprehensive testing (~30 min)"),  
            ("performance", "Performance analysis (~10 min)"),
            ("game_logic", "Game-specific tests (~15 min)"),
            ("stress", "Stress testing (~45 min)")
        ]
        
        for suite_name, description in suites:
            print(f"   • {suite_name}: {description}")
        
        print("✅ Test scenarios demonstration completed!")
        
    except Exception as e:
        print(f"❌ Test scenarios demo failed: {e}")

def demonstrate_integration():
    """Demonstrate the complete integration"""
    print("\n🔗 INTEGRATION DEMO")
    print("=" * 50)
    
    try:
        # Import the main test runner
        from ux_mirror_autonomous.run_tests import AutonomousTestRunner
        
        print("🤖 Initializing Autonomous Test Runner...")
        runner = AutonomousTestRunner()
        
        print("🔧 Initializing components...")
        if runner.initialize_components():
            print("✅ All components initialized successfully!")
            
            # Show available test suites
            available_suites = runner.get_available_suites()
            print(f"\n📋 Available Test Suites: {len(available_suites)}")
            for suite in available_suites:
                print(f"   • {suite['name']}: {suite['description']}")
            
            # Perform pre-test checks (non-destructive)
            print("\n🔍 Performing pre-test checks...")
            checks_passed = runner.pre_test_checks()
            print(f"📊 Pre-test checks: {'✅ Passed' if checks_passed else '⚠️ Some issues detected'}")
            
        else:
            print("❌ Component initialization failed")
        
        print("✅ Integration demonstration completed!")
        
    except Exception as e:
        print(f"❌ Integration demo failed: {e}")

def main():
    """Main demonstration function"""
    print("🤖 UX-MIRROR AUTONOMOUS TESTING SYSTEM")
    print("Phase 2: Input Automation System - DEMONSTRATION")
    print("=" * 70)
    
    print("\n🎯 This demonstration showcases the capabilities of Phase 2:")
    print("   • Autonomous input simulation with PyAutoGUI")
    print("   • Computer vision-based screen analysis")
    print("   • Comprehensive test scenarios for 3D Game of Life")
    print("   • Safety systems and human-like input patterns")
    print("   • Integrated testing framework")
    
    # Run demonstrations
    demonstrate_input_controller()
    demonstrate_screen_analyzer()
    demonstrate_test_scenarios()
    demonstrate_integration()
    
    print("\n" + "=" * 70)
    print("🎉 PHASE 2 DEMONSTRATION COMPLETED!")
    print("\n💡 Next Steps:")
    print("   • Run 'python launch_ux_mirror.py' and select Autonomous Testing Mode")
    print("   • Choose a test suite (Basic recommended for first run)")
    print("   • Review generated reports in ux_mirror_autonomous/test_results/")
    print("\n🚀 Phase 2 Input Automation System is ready for autonomous testing!")

if __name__ == "__main__":
    main() 