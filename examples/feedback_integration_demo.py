#!/usr/bin/env python3
"""
Feedback Integration Demo

Shows how manual feedback from the monitoring window
gets integrated into the game testing feedback cycles.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def demo_feedback_integration():
    """Demo the feedback integration system"""
    print("🔗 UX-MIRROR Feedback Integration Demo")
    print("=" * 50)
    
    # Check for existing manual feedback
    feedback_file = Path("game_screenshots") / "manual_feedback_log.json"
    
    if feedback_file.exists():
        print(f"📋 Loading manual feedback from: {feedback_file}")
        
        with open(feedback_file, 'r') as f:
            manual_feedback = json.load(f)
        
        if manual_feedback:
            print(f"✅ Found {len(manual_feedback)} manual feedback entries:")
            print()
            
            for i, feedback in enumerate(manual_feedback, 1):
                timestamp = feedback.get('timestamp', 'Unknown')
                message = feedback.get('message', 'No message')
                screenshot = feedback.get('screenshot_path', 'No screenshot')
                analysis = feedback.get('analysis', {})
                
                quality = analysis.get('quality_score', 0) * 100
                ui_elements = len(analysis.get('ui_elements', []))
                
                print(f"📝 Entry #{i}:")
                print(f"   ⏰ Time: {timestamp[:19]}")
                print(f"   💬 Message: \"{message}\"")
                print(f"   📸 Screenshot: {os.path.basename(screenshot)}")
                print(f"   📊 Quality: {quality:.1f}% | UI Elements: {ui_elements}")
                
                if analysis.get('accessibility_issues'):
                    print(f"   ♿ Accessibility Issues: {len(analysis['accessibility_issues'])}")
                
                print()
            
            # Show how this would be integrated into game testing
            print("🎮 Game Testing Integration:")
            print("-" * 30)
            print("When a 3:1 feedback cycle occurs, the system will:")
            print(f"   1. ✅ Load {len(manual_feedback)} manual feedback entries")
            print(f"   2. 📊 Include recent entries in feedback summary")
            print(f"   3. 🔗 Correlate manual feedback with automated analysis")
            print(f"   4. 💾 Store everything in session summary")
            
            # Show recent feedback format for integration
            recent_feedback = [
                {
                    'timestamp': fb.get('timestamp'),
                    'message': fb.get('message'),
                    'quality_score': fb.get('analysis', {}).get('quality_score', 0)
                }
                for fb in manual_feedback[-3:]  # Last 3 entries
            ]
            
            print(f"\n📋 Recent feedback (last 3 entries):")
            for entry in recent_feedback:
                print(f"   • [{entry['timestamp'][:19]}] {entry['message']} (Q: {entry['quality_score']:.1%})")
            
        else:
            print("📝 No manual feedback entries found")
    else:
        print("📝 No manual feedback file found")
        print("\n💡 To create manual feedback:")
        print("   1. Run: python monitoring_window.py")
        print("   2. Enter a message in the 'Manual Feedback' section")
        print("   3. Click '📸 Screenshot + Log'")
        print("   4. Run this demo again to see the integration")
    
    print("\n" + "=" * 50)

def simulate_game_feedback_cycle():
    """Simulate how manual feedback gets included in game testing"""
    print("\n🎯 Simulating Game Testing Feedback Cycle")
    print("=" * 45)
    
    # Simulate loading manual feedback (as game testing would do)
    feedback_file = Path("game_screenshots") / "manual_feedback_log.json"
    
    if feedback_file.exists():
        with open(feedback_file, 'r') as f:
            manual_feedback = json.load(f)
        
        print(f"📋 Found {len(manual_feedback)} manual feedback entries:")
        for i, feedback in enumerate(manual_feedback[-3:], 1):  # Show last 3
            timestamp = feedback.get('timestamp', 'Unknown time')
            message = feedback.get('message', 'No message')
            print(f"   {i}. [{timestamp[:19]}] {message}")
        
        # Simulate structured feedback collection
        print(f"\n💭 Simulated User Feedback Collection:")
        print(f"   UI Responsiveness: 4/5")
        print(f"   Visual Clarity: 3/5") 
        print(f"   Navigation Ease: 4/5")
        print(f"   Manual Feedback Entries: {len(manual_feedback)}")
        
        # Show how it would be stored
        combined_feedback = {
            "ui_responsiveness": 4,
            "visual_clarity": 3,
            "navigation_ease": 4,
            "manual_feedback_entries": len(manual_feedback),
            "recent_manual_feedback": [
                {
                    'timestamp': fb.get('timestamp'),
                    'message': fb.get('message'),
                    'quality_score': fb.get('analysis', {}).get('quality_score', 0)
                }
                for fb in manual_feedback[-3:]
            ]
        }
        
        print(f"\n💾 Combined Feedback Structure:")
        print(json.dumps(combined_feedback, indent=2))
        
    else:
        print("📝 No manual feedback available for integration")

if __name__ == "__main__":
    demo_feedback_integration()
    simulate_game_feedback_cycle()
    
    print(f"\n🚀 Try the full workflow:")
    print(f"   1. Start monitoring window: python monitoring_window.py")
    print(f"   2. Start test game: cd test_game\\pygame && python pygame1.py")
    print(f"   3. Use '📸 Screenshot + Log' to capture feedback")
    print(f"   4. Start game testing: python cli\\main.py game --iterations 6")
    print(f"   5. See manual feedback integrated in feedback cycles!") 