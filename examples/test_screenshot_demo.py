#!/usr/bin/env python3
"""
Quick Screenshot Demo

Demonstrates the screenshot capture and analysis functionality
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append('.')

async def demo_screenshot():
    """Demo the screenshot functionality"""
    try:
        from core.screenshot_analyzer import ScreenshotAnalyzer
        
        print("🎯 UX-MIRROR Screenshot Demo")
        print("=" * 40)
        
        # Create analyzer
        analyzer = ScreenshotAnalyzer()
        
        print("📸 Capturing screenshot...")
        screenshot_path = await analyzer.capture_screenshot()
        
        if screenshot_path and os.path.exists(screenshot_path):
            print(f"✅ Screenshot saved: {screenshot_path}")
            
            print("🔍 Analyzing image...")
            analysis = await analyzer.analyze_image(screenshot_path)
            
            if analysis and 'error' not in analysis:
                print(f"📊 Analysis Results:")
                print(f"   • Image dimensions: {analysis['dimensions']['width']}x{analysis['dimensions']['height']}")
                print(f"   • Quality score: {analysis['quality_score']:.1%}")
                print(f"   • UI elements detected: {len(analysis['ui_elements'])}")
                print(f"   • Performance assessment: {analysis['performance_assessment']}")
                
                if analysis['accessibility_issues']:
                    print(f"   • Accessibility issues: {len(analysis['accessibility_issues'])}")
                    for issue in analysis['accessibility_issues'][:3]:
                        print(f"     - {issue}")
                else:
                    print(f"   • ✅ No accessibility issues found")
                
                print(f"   • Analysis time: {analysis['analysis_time']:.3f}s")
                
                if analysis['ui_elements']:
                    print(f"\n🎮 UI Elements Found:")
                    for i, element in enumerate(analysis['ui_elements'], 1):
                        print(f"   {i}. {element['type']} at ({element['x']}, {element['y']}) - {element['width']}x{element['height']}")
                
                print(f"\n💡 Recommendations:")
                for rec in analysis['recommendations']:
                    print(f"   • {rec}")
                    
            else:
                print(f"❌ Analysis failed: {analysis.get('error', 'Unknown error')}")
                
        else:
            print("❌ Failed to capture screenshot")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting screenshot demo...")
    asyncio.run(demo_screenshot())
    print("\nDemo completed!") 