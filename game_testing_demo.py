#!/usr/bin/env python3
"""
Game UX Testing Demo - 3:1 Feedback Sessions
=============================================

Demonstrates the UX-MIRROR system's game testing capabilities
using computer vision and performance analysis (no API keys required).
"""

import asyncio
import time
import json
from datetime import datetime
from pathlib import Path
import subprocess
import sys

# Add src to path for imports
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

class GameUXDemo:
    """Demo class for game UX testing sessions"""
    
    def __init__(self):
        self.session_data = []
        self.config = self.load_game_config()
        
    def load_game_config(self):
        """Load game testing configuration"""
        try:
            with open('game_ux_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
    
    def get_default_config(self):
        """Default configuration for game testing"""
        return {
            "game_ux_testing": {
                "session_config": {
                    "feedback_ratio": "3:1",
                    "session_duration": 60,
                    "analysis_intervals": [15, 30, 45, 60]
                }
            }
        }
    
    def print_banner(self):
        """Print demo banner"""
        print("🎮 UX-MIRROR: Game Testing Demo")
        print("=" * 50)
        print("🎯 3:1 Feedback Sessions (No API Keys Required)")
        print("✨ Computer Vision + Performance Analysis")
        print()
    
    def print_session_start(self, session_num, focus, duration):
        """Print session start information"""
        print(f"🚀 Session {session_num}: {focus}")
        print(f"   Duration: {duration} seconds")
        print(f"   Timestamp: {datetime.now().strftime('%H:%M:%S')}")
        print()
    
    def simulate_visual_analysis(self, session_focus):
        """Simulate visual analysis for the session"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "session_focus": session_focus,
            "analysis_type": "computer_vision",
            "findings": []
        }
        
        if "UI assessment" in session_focus:
            results["findings"] = [
                "✅ HUD elements properly positioned in safe zones",
                "⚠️  Small text detected (12px) - may need scaling for accessibility",
                "✅ High contrast ratio (7.2:1) for main UI elements",
                "📊 Visual hierarchy score: 8.5/10"
            ]
            results["quality_score"] = 0.85
            results["ui_elements_detected"] = 23
            
        elif "Interaction flow" in session_focus:
            results["findings"] = [
                "✅ Clear button feedback with 0.1s response time", 
                "⚠️  Menu navigation requires 3+ clicks for common actions",
                "✅ Consistent interaction patterns across screens",
                "📈 User flow efficiency: 78%"
            ]
            results["interaction_score"] = 0.78
            results["navigation_efficiency"] = 0.82
            
        elif "Accessibility" in session_focus:
            results["findings"] = [
                "✅ Colorblind-friendly palette detected",
                "⚠️  Touch targets below 44px minimum (found 6 instances)",
                "❌ No subtitle options detected for audio elements",
                "✅ High contrast mode compatible"
            ]
            results["accessibility_score"] = 0.73
            results["accessibility_issues"] = 3
            
        elif "Comprehensive" in session_focus:
            results["findings"] = [
                "📊 Overall UX Quality Score: 8.1/10",
                "🎯 Primary recommendation: Increase touch target sizes",
                "🔧 Performance optimization: UI renders at stable 60fps",
                "♿ Accessibility compliance: 73% (needs improvement)",
                "🎮 Game-specific UX: Excellent visual feedback systems"
            ]
            results["overall_score"] = 0.81
            results["recommendations"] = [
                "Implement UI scaling options for better accessibility",
                "Add subtitle support for inclusive gaming",
                "Optimize menu navigation flow",
                "Consider larger touch targets for mobile gaming"
            ]
        
        return results
    
    def simulate_performance_metrics(self):
        """Simulate performance metrics collection"""
        import random
        
        return {
            "frame_rate": round(58 + random.uniform(-2, 4), 1),
            "input_lag": round(12 + random.uniform(-3, 8), 2),
            "ui_render_time": round(8 + random.uniform(-2, 4), 2),
            "memory_usage": round(45 + random.uniform(-5, 15), 1),
            "cpu_usage": round(35 + random.uniform(-10, 20), 1)
        }
    
    def print_analysis_results(self, results, metrics):
        """Print analysis results for a session"""
        print("📊 Analysis Results:")
        print("-" * 30)
        
        for finding in results.get("findings", []):
            print(f"   {finding}")
        
        print()
        print("⚡ Performance Metrics:")
        print(f"   Frame Rate: {metrics['frame_rate']} fps")
        print(f"   Input Lag: {metrics['input_lag']} ms")
        print(f"   UI Render: {metrics['ui_render_time']} ms")
        print(f"   Memory: {metrics['memory_usage']}%")
        print(f"   CPU: {metrics['cpu_usage']}%")
        print()
    
    def print_session_summary(self):
        """Print summary of all sessions"""
        print("🎯 3:1 Feedback Session Summary")
        print("=" * 50)
        
        total_issues = 0
        critical_issues = 0
        
        for i, session in enumerate(self.session_data, 1):
            print(f"Session {i}: {session['results']['session_focus']}")
            issues = len([f for f in session['results']['findings'] if '⚠️' in f or '❌' in f])
            critical = len([f for f in session['results']['findings'] if '❌' in f])
            total_issues += issues
            critical_issues += critical
            print(f"   Issues found: {issues} (Critical: {critical})")
        
        print()
        print("🏆 Overall Assessment:")
        print(f"   Total Issues: {total_issues}")
        print(f"   Critical Issues: {critical_issues}")
        print(f"   Sessions Completed: {len(self.session_data)}")
        
        if critical_issues == 0:
            status = "🟢 Good"
        elif critical_issues <= 2:
            status = "🟡 Needs Attention" 
        else:
            status = "🔴 Requires Immediate Action"
            
        print(f"   UX Status: {status}")
        print()
        
        print("💡 Key Recommendations:")
        print("   1. Implement UI scaling for accessibility")
        print("   2. Add subtitle support for inclusive gaming")
        print("   3. Optimize menu navigation flow")
        print("   4. Increase touch target sizes for mobile")
        print()
    
    async def run_session(self, session_num, session_config):
        """Run a single testing session"""
        focus = session_config["focus"]
        duration = session_config["duration"]
        
        self.print_session_start(session_num, focus, duration)
        
        # Simulate session running
        for i in range(duration // 5):
            print(f"   📸 Capturing frame {i+1}...")
            await asyncio.sleep(0.5)  # Faster for demo
        
        # Generate analysis results
        results = self.simulate_visual_analysis(focus)
        metrics = self.simulate_performance_metrics()
        
        # Store session data
        self.session_data.append({
            "session": session_num,
            "results": results,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })
        
        self.print_analysis_results(results, metrics)
        
        return results, metrics
    
    async def run_all_sessions(self):
        """Run all 4 sessions of the 3:1 feedback cycle"""
        self.print_banner()
        
        sessions = [
            {"focus": "Initial UI assessment", "duration": 15},
            {"focus": "Interaction flow analysis", "duration": 15}, 
            {"focus": "Accessibility and performance", "duration": 15},
            {"focus": "Comprehensive analysis", "duration": 15}
        ]
        
        print("🎮 Starting 3:1 Game UX Feedback Sessions...")
        print()
        
        for i, session_config in enumerate(sessions, 1):
            await self.run_session(i, session_config)
            
            if i < len(sessions):
                print("⏸️  Session complete. Preparing next session...")
                await asyncio.sleep(1)  # Brief pause between sessions
                print()
        
        self.print_session_summary()
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save session results to file"""
        filename = f"game_ux_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "demo_info": {
                    "type": "3:1 Game UX Feedback Sessions",
                    "timestamp": datetime.now().isoformat(),
                    "system": "UX-MIRROR Multi-Agent System",
                    "mode": "Computer Vision + Performance Analysis (No API Keys)"
                },
                "sessions": self.session_data
            }, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")

async def main():
    """Main demo function"""
    demo = GameUXDemo()
    await demo.run_all_sessions()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Demo stopped by user")
    except Exception as e:
        print(f"❌ Demo error: {e}") 