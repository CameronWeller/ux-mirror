#!/usr/bin/env python3
"""
Example: Active User Monitoring with Playwright

This example demonstrates watching a user actively use a website
and detecting problems they encounter in real-time.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integration.playwright_active_monitor import PlaywrightActiveMonitor, ProblemDetected, InteractionEvent


def print_problem(problem: ProblemDetected):
    """Callback to print detected problems"""
    print("\n" + "=" * 60)
    print(f"⚠️  PROBLEM DETECTED - {problem.severity.upper()}")
    print("=" * 60)
    print(f"Category: {problem.category}")
    print(f"Description: {problem.description}")
    print(f"Time: {datetime.fromtimestamp(problem.timestamp).strftime('%H:%M:%S')}")
    if problem.user_action:
        print(f"User Action: {problem.user_action.event_type} on {problem.user_action.target}")
    print("=" * 60)


def print_interaction(interaction: InteractionEvent):
    """Callback to print user interactions"""
    print(f"👆 {interaction.event_type}: {interaction.target or 'unknown'}")


async def monitor_user_session():
    """Monitor an active user session"""
    print("=" * 60)
    print("Active User Monitoring - UX-Mirror")
    print("=" * 60)
    print("\nThis will watch you use a website and detect:")
    print("  • Problems you encounter")
    print("  • Unexpected behavior")
    print("  • Confusion points")
    print("  • Performance issues")
    print("\nPress Ctrl+C to stop monitoring\n")
    
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return
    
    monitor = PlaywrightActiveMonitor(api_key, provider="openai")
    
    # Set up callbacks
    monitor.on_problem_detected = print_problem
    monitor.on_interaction = print_interaction
    
    try:
        # Start monitoring (headless=False so user can interact)
        url = input("Enter URL to monitor (or press Enter for example.com): ").strip()
        if not url:
            url = "https://example.com"
        
        print(f"\n🌐 Starting monitoring on {url}...")
        print("💡 Use the browser window to interact with the site")
        print("📊 Problems will be detected and reported in real-time\n")
        
        await monitor.start_monitoring(url, headless=False)
        
        # Keep monitoring until interrupted
        try:
            while monitor.monitoring:
                await asyncio.sleep(1)
                
                # Print summary every 10 seconds
                if len(monitor.problems_detected) > 0:
                    summary = monitor.get_summary()
                    print(f"\n📈 Session Summary:")
                    print(f"   Interactions: {summary['total_interactions']}")
                    print(f"   Problems: {summary['problems_detected']}")
                    print(f"   By Severity: {summary['problems_by_severity']}")
                    print(f"   By Category: {summary['problems_by_category']}")
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping monitoring...")
        
    finally:
        await monitor.stop_monitoring()
        
        # Print final summary
        summary = monitor.get_summary()
        print("\n" + "=" * 60)
        print("📊 Final Session Summary")
        print("=" * 60)
        print(f"Total Interactions: {summary['total_interactions']}")
        print(f"Problems Detected: {summary['problems_detected']}")
        print(f"\nBy Severity:")
        for severity, count in summary['problems_by_severity'].items():
            if count > 0:
                print(f"  {severity}: {count}")
        print(f"\nBy Category:")
        for category, count in summary['problems_by_category'].items():
            if count > 0:
                print(f"  {category}: {count}")
        
        if summary['recent_problems']:
            print(f"\n🔍 Recent Problems:")
            for problem in summary['recent_problems'][-5:]:
                print(f"  • [{problem['severity']}] {problem['description']}")
        
        print("=" * 60)


async def monitor_with_custom_detection():
    """Example with custom problem detection logic"""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return
    
    monitor = PlaywrightActiveMonitor(api_key)
    
    # Custom callback that filters and processes problems
    def custom_problem_handler(problem: ProblemDetected):
        # Only alert on high/critical problems
        if problem.severity in ['high', 'critical']:
            print(f"🚨 CRITICAL: {problem.description}")
            
            # You could send to a notification system, log to database, etc.
            # send_to_slack(problem)
            # log_to_database(problem)
    
    monitor.on_problem_detected = custom_problem_handler
    
    try:
        await monitor.start_monitoring("https://example.com", headless=False)
        
        # Monitor for a specific duration
        await asyncio.sleep(60)  # Monitor for 60 seconds
        
    finally:
        await monitor.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(monitor_user_session())

