#!/usr/bin/env python3
"""
Test script to demonstrate UX-MIRROR integration with C++ game
This simulates the complete workflow including Anthropic API usage
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add the UX-MIRROR modules to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from ux_mirror_launcher import UXMirrorLauncher, ApplicationDetector
    from core.adaptive_feedback import AdaptiveFeedbackEngine
    from core.port_manager import PortManager
    print("✓ UX-MIRROR modules imported successfully")
except ImportError as e:
    print(f"✗ Failed to import UX-MIRROR modules: {e}")
    sys.exit(1)

def check_api_key():
    """Check if Anthropic API key is available"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠ ANTHROPIC_API_KEY not found in environment variables")
        print("Please set it with: set ANTHROPIC_API_KEY=your_key_here (Windows)")
        print("Or: export ANTHROPIC_API_KEY=your_key_here (Linux/Mac)")
        return False
    else:
        print(f"✓ Anthropic API key found (length: {len(api_key)} chars)")
        return True

def simulate_cpp_game_analysis():
    """Simulate analyzing our C++ game concept"""
    print("\n=== UX-MIRROR C++ Game Analysis Simulation ===")
    
    # 1. Check API key
    if not check_api_key():
        print("⚠ Continuing with simulation (API calls will be mocked)")
    
    # 2. Initialize systems
    print("\n1. Initializing UX-MIRROR systems...")
    
    try:
        port_manager = PortManager()
        allocated_port = port_manager.allocate_port("ux_test_game")
        print(f"✓ Port allocated: {allocated_port}")
        
        feedback_engine = AdaptiveFeedbackEngine()
        print("✓ Adaptive feedback engine initialized")
        
        app_detector = ApplicationDetector()
        print("✓ Application detector initialized")
        
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False
    
    # 3. Simulate game detection
    print("\n2. Simulating C++ game detection...")
    
    # Mock our C++ game as a detected application
    mock_cpp_game = {
        'name': 'UX Test Game - C++ Edition',
        'executable': 'ux_test_game.exe',
        'path': str(Path.cwd() / 'ux_test_game.exe'),
        'category': 'Game',
        'ui_elements': [
            'Menu System',
            'Settings Panel', 
            'HUD Elements',
            'Button Interactions',
            'Score Display',
            'Health Bar',
            'Mini-map'
        ]
    }
    
    print(f"✓ Target game: {mock_cpp_game['name']}")
    print(f"✓ UI elements to analyze: {len(mock_cpp_game['ui_elements'])}")
    for element in mock_cpp_game['ui_elements']:
        print(f"  - {element}")
    
    # 4. Simulate adaptive feedback analysis
    print("\n3. Running adaptive feedback analysis...")
    
    # Mock analysis results for different UI elements
    mock_analysis_results = {
        'Menu System': {
            'confidence': 0.85,
            'issues': ['Button spacing could be improved', 'Color contrast needs work'],
            'suggestions': ['Increase button padding by 10px', 'Use higher contrast colors']
        },
        'HUD Elements': {
            'confidence': 0.75,
            'issues': ['Information overload', 'Mini-map too small'],
            'suggestions': ['Group related information', 'Increase mini-map size by 50%']
        },
        'Settings Panel': {
            'confidence': 0.90,
            'issues': ['Volume controls unclear'],
            'suggestions': ['Add visual slider for volume']
        }
    }
    
    total_confidence = 0
    analysis_count = 0
    
    for element, analysis in mock_analysis_results.items():
        confidence = analysis['confidence']
        total_confidence += confidence
        analysis_count += 1
        
        print(f"\n  Analyzing {element}:")
        print(f"    Confidence: {confidence:.2f}")
        print(f"    Issues found: {len(analysis['issues'])}")
        for issue in analysis['issues']:
            print(f"      - {issue}")
        print(f"    Suggestions: {len(analysis['suggestions'])}")
        for suggestion in analysis['suggestions']:
            print(f"      + {suggestion}")
    
    # 5. Determine if more analysis is needed
    avg_confidence = total_confidence / analysis_count
    print(f"\n4. Adaptive feedback decision:")
    print(f"   Average confidence: {avg_confidence:.2f}")
    
    # Start a session and add iterations to test adaptive feedback
    session = feedback_engine.start_session("cpp_game_test")
    
    # Add mock iterations
    for i, (element, analysis) in enumerate(mock_analysis_results.items()):
        iteration_data = {
            'quality_score': analysis['confidence'],
            'ui_elements_detected': 1,
            'accessibility_issues': analysis['issues'],
            'recommendations': analysis['suggestions'],
            'response_time': 0.5 + i * 0.1,
            'metadata': {'element': element}
        }
        feedback_engine.add_iteration("cpp_game_test", iteration_data)
    
    action, context = feedback_engine.determine_action("cpp_game_test")
    
    print(f"   Recommended action: {action}")
    print(f"   Analysis context: {context['confidence_level']}")
    print(f"   Session iterations: {context['iterations']}")
    
    # 6. Generate improvement suggestions
    print("\n5. Generated improvement plan:")
    print("   Priority improvements for C++ game:")
    print("   🎯 High Priority:")
    print("     - Improve button spacing in menu system")
    print("     - Add visual volume slider in settings")
    print("   📊 Medium Priority:")
    print("     - Increase mini-map size for better visibility")
    print("     - Group HUD information more logically")
    print("   🎨 Low Priority:")
    print("     - Enhance color contrast throughout UI")
    
    # 7. Show how to implement improvements
    print("\n6. Implementation guide:")
    print("   To implement these improvements in your C++ game:")
    print("   1. Edit test_cpp_game.cpp")
    print("   2. Modify the DrawHUD() function for HUD improvements")
    print("   3. Update UpdateSettings() for better volume controls")
    print("   4. Adjust button spacing in UpdateMenu()")
    print("   5. Recompile with: g++ test_cpp_game.cpp -o ux_test_game")
    print("   6. Re-run UX-MIRROR analysis to validate improvements")
    
    # 8. Port cleanup
    print(f"\n7. Cleaning up port allocation...")
    port_manager.release_port(allocated_port)
    print("✓ Port released")
    
    return True

def main():
    """Main test function"""
    print("UX-MIRROR C++ Game Integration Test")
    print("====================================")
    
    # Check if we're in the right directory
    if not Path('ux_mirror_launcher.py').exists():
        print("✗ Please run this script from the UX-MIRROR root directory")
        return False
    
    # Run the simulation
    success = simulate_cpp_game_analysis()
    
    if success:
        print("\n✅ Integration test completed successfully!")
        print("\nNext steps:")
        print("1. Install a C++ compiler (MinGW for Windows)")
        print("2. Run: .\\build_game.bat")
        print("3. Launch: python ux_mirror_launcher.py")
        print("4. Select the compiled C++ game for real analysis")
        return True
    else:
        print("\n❌ Integration test failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 