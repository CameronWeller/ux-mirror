#!/usr/bin/env python3
"""
Example: Using Playwright with UX-Mirror for Web UX Analysis

This example demonstrates how to:
1. Use Playwright for web automation (navigation, interaction)
2. Use UX-Mirror AI for analyzing screenshots
3. Build on top of Playwright rather than duplicating features
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integration.playwright_adapter import PlaywrightUXMirrorAdapter


async def example_basic_analysis():
    """Basic example: Analyze a single web page"""
    print("=== Example 1: Basic Web Page Analysis ===\n")
    
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        return
    
    adapter = PlaywrightUXMirrorAdapter(api_key, provider="openai")
    
    try:
        await adapter.start(headless=True)
        
        # Navigate and analyze
        results = await adapter.navigate_and_analyze(
            url="https://example.com",
            context="Analyzing homepage UX and design"
        )
        
        print("✅ Screenshot captured and analyzed")
        print(f"\n📊 Analysis Summary:")
        print(results["feedback"]["summary"])
        
        print(f"\n🎯 Top Issues:")
        for issue in results["feedback"]["priority_fixes"][:3]:
            print(f"  • {issue['description']} ({issue['severity']})")
        
        print(f"\n💡 Recommendations:")
        for rec in results["feedback"].get("recommendations", [])[:3]:
            print(f"  • {rec}")
        
    finally:
        await adapter.stop()


async def example_interactive_flow():
    """Example: Test a user interaction flow"""
    print("\n=== Example 2: Interactive UX Testing Flow ===\n")
    
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        return
    
    adapter = PlaywrightUXMirrorAdapter(api_key, provider="openai")
    
    try:
        await adapter.start(headless=False)  # Visible browser for demo
        
        # Define test steps
        test_steps = [
            {
                "type": "navigate",
                "url": "https://example.com",
                "description": "Navigate to homepage"
            },
            {
                "type": "click",
                "selector": "a",  # Click first link
                "description": "Click navigation link"
            }
        ]
        
        print("Running UX test flow...")
        results = await adapter.run_ux_test_flow(
            test_steps,
            analyze_after_each=True
        )
        
        print(f"\n✅ Completed {len(results['steps'])} steps")
        
        # Show analysis for each step
        for step in results["steps"]:
            if "feedback" in step:
                print(f"\n📝 Step {step['step_number']}: {step['description']}")
                print(f"   {step['feedback']['summary'][:100]}...")
        
        # Overall recommendations
        if results.get("recommendations"):
            print(f"\n🎯 Overall Recommendations:")
            for rec in results["recommendations"][:3]:
                print(f"  • {rec}")
        
    finally:
        await adapter.stop()


async def example_element_analysis():
    """Example: Analyze a specific UI element"""
    print("\n=== Example 3: Element-Specific Analysis ===\n")
    
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        return
    
    adapter = PlaywrightUXMirrorAdapter(api_key, provider="openai")
    
    try:
        await adapter.start(headless=True)
        
        # Navigate first
        await adapter.page.goto("https://example.com")
        
        # Analyze a specific element
        print("Analyzing button element...")
        results = await adapter.analyze_element(
            selector="a",  # Analyze first link/button
            context="Analyzing primary call-to-action button design"
        )
        
        print("✅ Element captured and analyzed")
        print(f"\n📊 Element Analysis:")
        print(results["feedback"]["summary"])
        
        if results["feedback"].get("code_suggestions"):
            print(f"\n💻 Code Suggestions:")
            for suggestion in results["feedback"]["code_suggestions"][:2]:
                print(f"  {suggestion}")
        
    finally:
        await adapter.stop()


async def main():
    """Run all examples"""
    print("=" * 60)
    print("Playwright + UX-Mirror Integration Examples")
    print("=" * 60)
    print("\nThis demonstrates building on top of Playwright")
    print("rather than duplicating its features.\n")
    
    # Run examples
    await example_basic_analysis()
    # Uncomment to run more examples:
    # await example_interactive_flow()
    # await example_element_analysis()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

