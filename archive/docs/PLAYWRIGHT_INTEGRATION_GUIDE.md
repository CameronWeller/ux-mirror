# Playwright Integration Guide for UX-Mirror

## Overview

This guide outlines how to integrate Playwright with UX-Mirror's existing image recognition and AI vision analysis system. The goal is to **build on top of Playwright** rather than duplicating its features.

## Architecture Philosophy

### What Playwright Provides (Don't Duplicate)
- **Web automation**: Navigation, clicking, typing, form filling
- **Screenshot capture**: Built-in screenshot capabilities for web pages
- **Element interaction**: Finding and interacting with DOM elements
- **Network monitoring**: Request/response interception
- **Browser context management**: Multiple contexts, incognito mode
- **Waiting strategies**: Auto-waiting for elements, network idle, etc.

### What UX-Mirror Adds (Our Value)
- **AI Vision Analysis**: Deep analysis of screenshots using OpenAI/Anthropic
- **UX Intelligence**: Clutter scores, readability metrics, visual hierarchy
- **Game/App Analysis**: Specialized prompts for game UI analysis
- **Feedback Processing**: Developer-friendly feedback and code suggestions
- **Cross-platform**: Works with games, desktop apps, not just web

## Integration Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    UX-Mirror Layer                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  AI Vision Analyzer (OpenAI/Anthropic)              │  │
│  │  - Screenshot analysis                               │  │
│  │  - UX metrics calculation                            │  │
│  │  - Issue detection                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Feedback Processor                                   │  │
│  │  - Priority ranking                                  │  │
│  │  - Code suggestions                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │ Uses screenshots from
                          │
┌─────────────────────────────────────────────────────────────┐
│              Playwright (Web Automation)                    │
│  - Navigate pages                                          │
│  - Interact with elements                                  │
│  - Capture screenshots                                     │
│  - Monitor network                                         │
└─────────────────────────────────────────────────────────────┘
```

## Implementation

### 1. Playwright Screenshot Adapter

Create a bridge between Playwright screenshots and UX-Mirror's AI analyzer:

```python
# src/integration/playwright_adapter.py

import asyncio
from typing import Optional, Dict, Any
from PIL import Image
import io
from playwright.async_api import async_playwright, Page, Browser
from ai_vision_analyzer import AIVisionAnalyzer, GameUIFeedbackProcessor
import logging

logger = logging.getLogger(__name__)

class PlaywrightUXMirrorAdapter:
    """
    Adapter that integrates Playwright web automation with UX-Mirror AI analysis.
    
    Uses Playwright for:
    - Web navigation and interaction
    - Screenshot capture
    
    Uses UX-Mirror for:
    - AI vision analysis of screenshots
    - UX metrics and feedback generation
    """
    
    def __init__(self, api_key: str, provider: str = "openai"):
        self.api_key = api_key
        self.provider = provider
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.analyzer: Optional[AIVisionAnalyzer] = None
        self.feedback_processor = GameUIFeedbackProcessor()
    
    async def start(self, headless: bool = True):
        """Start Playwright browser and initialize AI analyzer"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=headless)
        self.page = await self.browser.new_page()
        
        # Initialize AI analyzer
        self.analyzer = AIVisionAnalyzer(self.api_key, self.provider)
        await self.analyzer.__aenter__()
        
        logger.info("Playwright UX-Mirror adapter started")
    
    async def stop(self):
        """Stop browser and cleanup"""
        if self.analyzer:
            await self.analyzer.__aexit__(None, None, None)
        if self.browser:
            await self.browser.close()
        logger.info("Playwright UX-Mirror adapter stopped")
    
    async def navigate_and_analyze(
        self, 
        url: str, 
        wait_for: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Navigate to a URL, capture screenshot, and analyze with AI.
        
        Args:
            url: URL to navigate to
            wait_for: Optional selector to wait for before screenshot
            context: Additional context for AI analysis
            
        Returns:
            Analysis results with UX feedback
        """
        if not self.page:
            raise RuntimeError("Adapter not started. Call start() first.")
        
        # Use Playwright for navigation
        await self.page.goto(url, wait_until="networkidle")
        
        # Wait for specific element if provided
        if wait_for:
            await self.page.wait_for_selector(wait_for)
        
        # Capture screenshot using Playwright
        screenshot_bytes = await self.page.screenshot(full_page=True)
        
        # Convert to PIL Image for AI analyzer
        image = Image.open(io.BytesIO(screenshot_bytes))
        
        # Use UX-Mirror AI analyzer
        analysis = await self.analyzer.analyze_screenshot(
            image,
            context=context or f"Web page analysis: {url}"
        )
        
        # Process feedback
        feedback = self.feedback_processor.process_analysis(analysis)
        
        return {
            "url": url,
            "screenshot_captured": True,
            "analysis": analysis,
            "feedback": feedback
        }
    
    async def interact_and_analyze(
        self,
        action: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform an interaction (click, type, etc.) and analyze the result.
        
        Args:
            action: Dict with 'type' (click/type/fill) and 'selector' or 'text'
            context: Context for AI analysis
            
        Example:
            await adapter.interact_and_analyze({
                "type": "click",
                "selector": "button.submit"
            })
        """
        if not self.page:
            raise RuntimeError("Adapter not started. Call start() first.")
        
        # Use Playwright for interaction
        action_type = action.get("type")
        
        if action_type == "click":
            await self.page.click(action["selector"])
        elif action_type == "type":
            await self.page.fill(action["selector"], action["text"])
        elif action_type == "fill":
            await self.page.fill(action["selector"], action["value"])
        else:
            raise ValueError(f"Unknown action type: {action_type}")
        
        # Wait for page to settle
        await self.page.wait_for_load_state("networkidle")
        
        # Capture screenshot after interaction
        screenshot_bytes = await self.page.screenshot(full_page=True)
        image = Image.open(io.BytesIO(screenshot_bytes))
        
        # Analyze with UX-Mirror
        analysis = await self.analyzer.analyze_screenshot(
            image,
            context=context or f"After {action_type} on {action.get('selector', 'element')}"
        )
        
        feedback = self.feedback_processor.process_analysis(analysis)
        
        return {
            "action": action,
            "screenshot_captured": True,
            "analysis": analysis,
            "feedback": feedback
        }
    
    async def analyze_element(
        self,
        selector: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a specific element by capturing its screenshot.
        
        Uses Playwright to:
        - Locate the element
        - Capture element screenshot
        
        Uses UX-Mirror to:
        - Analyze the element's visual design
        """
        if not self.page:
            raise RuntimeError("Adapter not started. Call start() first.")
        
        # Wait for element
        element = await self.page.wait_for_selector(selector)
        
        # Capture element screenshot using Playwright
        screenshot_bytes = await element.screenshot()
        image = Image.open(io.BytesIO(screenshot_bytes))
        
        # Analyze with UX-Mirror
        analysis = await self.analyzer.analyze_screenshot(
            image,
            context=context or f"Element analysis: {selector}"
        )
        
        feedback = self.feedback_processor.process_analysis(analysis)
        
        return {
            "selector": selector,
            "element_captured": True,
            "analysis": analysis,
            "feedback": feedback
        }
    
    async def run_ux_test_flow(
        self,
        test_steps: list[Dict[str, Any]],
        analyze_after_each: bool = True
    ) -> Dict[str, Any]:
        """
        Run a sequence of interactions and analyze UX at each step.
        
        Args:
            test_steps: List of actions to perform
            analyze_after_each: Whether to analyze after each step
            
        Returns:
            Complete test results with analysis at each step
        """
        results = {
            "steps": [],
            "overall_analysis": None,
            "recommendations": []
        }
        
        for i, step in enumerate(test_steps):
            step_result = {
                "step_number": i + 1,
                "action": step
            }
            
            # Perform action using Playwright
            action_type = step.get("type")
            if action_type == "navigate":
                await self.page.goto(step["url"], wait_until="networkidle")
            elif action_type == "click":
                await self.page.click(step["selector"])
            elif action_type == "type":
                await self.page.fill(step["selector"], step["text"])
            # Add more action types as needed
            
            # Analyze if requested
            if analyze_after_each:
                screenshot_bytes = await self.page.screenshot(full_page=True)
                image = Image.open(io.BytesIO(screenshot_bytes))
                
                analysis = await self.analyzer.analyze_screenshot(
                    image,
                    context=f"Step {i+1}: {step.get('description', action_type)}"
                )
                
                step_result["analysis"] = analysis
                step_result["feedback"] = self.feedback_processor.process_analysis(analysis)
            
            results["steps"].append(step_result)
        
        # Final overall analysis
        final_screenshot = await self.page.screenshot(full_page=True)
        final_image = Image.open(io.BytesIO(final_screenshot))
        final_analysis = await self.analyzer.analyze_screenshot(
            final_image,
            context="Final state after all test steps"
        )
        
        results["overall_analysis"] = final_analysis
        results["recommendations"] = final_analysis.recommendations
        
        return results
```

### 2. Usage Examples

#### Basic Web Page Analysis

```python
import asyncio
from src.integration.playwright_adapter import PlaywrightUXMirrorAdapter

async def analyze_web_page():
    adapter = PlaywrightUXMirrorAdapter(
        api_key=os.getenv("OPENAI_API_KEY"),
        provider="openai"
    )
    
    await adapter.start(headless=True)
    
    try:
        # Navigate and analyze
        results = await adapter.navigate_and_analyze(
            url="https://example.com",
            context="Analyzing homepage UX"
        )
        
        print("Analysis Summary:", results["feedback"]["summary"])
        print("Top Issues:")
        for issue in results["feedback"]["priority_fixes"]:
            print(f"  - {issue['description']} ({issue['severity']})")
        
    finally:
        await adapter.stop()

asyncio.run(analyze_web_page())
```

#### Interactive UX Testing Flow

```python
async def test_user_registration_flow():
    adapter = PlaywrightUXMirrorAdapter(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    await adapter.start(headless=False)  # Visible browser
    
    try:
        test_steps = [
            {
                "type": "navigate",
                "url": "https://example.com/signup",
                "description": "Navigate to signup page"
            },
            {
                "type": "type",
                "selector": "input[name='email']",
                "text": "test@example.com",
                "description": "Enter email"
            },
            {
                "type": "click",
                "selector": "button[type='submit']",
                "description": "Submit form"
            }
        ]
        
        results = await adapter.run_ux_test_flow(
            test_steps,
            analyze_after_each=True
        )
        
        # Print analysis for each step
        for step in results["steps"]:
            if "feedback" in step:
                print(f"\nStep {step['step_number']}:")
                print(step["feedback"]["summary"])
        
        # Overall recommendations
        print("\n=== Overall Recommendations ===")
        for rec in results["recommendations"]:
            print(f"  - {rec}")
        
    finally:
        await adapter.stop()
```

#### Element-Specific Analysis

```python
async def analyze_button_design():
    adapter = PlaywrightUXMirrorAdapter(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    await adapter.start()
    
    try:
        await adapter.page.goto("https://example.com")
        
        # Analyze specific button
        results = await adapter.analyze_element(
            selector="button.primary-cta",
            context="Analyzing primary call-to-action button design"
        )
        
        print("Button Analysis:")
        print(results["feedback"]["summary"])
        print("\nCode Suggestions:")
        for suggestion in results["feedback"]["code_suggestions"]:
            print(f"  {suggestion}")
        
    finally:
        await adapter.stop()
```

### 3. Integration with Existing Systems

#### Using with Screenshot Handler

```python
# Integrate with existing screenshot_handler.py
from src.capture.screenshot_handler import ScreenshotHandler
from src.integration.playwright_adapter import PlaywrightUXMirrorAdapter

class HybridScreenshotManager:
    """
    Manages screenshots from both Playwright (web) and native capture (games/apps)
    """
    
    def __init__(self, api_key: str):
        self.playwright_adapter = PlaywrightUXMirrorAdapter(api_key)
        self.native_handler = ScreenshotHandler()
        self.ai_analyzer = None
    
    async def analyze_web_page(self, url: str):
        """Use Playwright for web pages"""
        await self.playwright_adapter.start()
        return await self.playwright_adapter.navigate_and_analyze(url)
    
    async def analyze_game_screenshot(self, screenshot_path: str):
        """Use native capture for games"""
        # Use existing screenshot handler
        screenshot = self.native_handler.load_screenshot(screenshot_path)
        
        # Use AI analyzer
        if not self.ai_analyzer:
            self.ai_analyzer = AIVisionAnalyzer(api_key)
            await self.ai_analyzer.__aenter__()
        
        image = Image.fromarray(screenshot)
        analysis = await self.ai_analyzer.analyze_screenshot(image)
        
        return self.feedback_processor.process_analysis(analysis)
```

## Key Principles

### ✅ DO: Build on Playwright
- Use Playwright's screenshot capabilities for web pages
- Leverage Playwright's navigation and interaction features
- Use Playwright's element selectors and waiting strategies
- Integrate Playwright's network monitoring for performance insights

### ❌ DON'T: Duplicate Playwright Features
- Don't reimplement web automation (Playwright does this)
- Don't create custom screenshot capture for web (use Playwright's)
- Don't build element finders (Playwright has robust selectors)
- Don't implement network monitoring (Playwright provides this)

### ✅ DO: Add UX-Mirror Value
- Apply AI vision analysis to Playwright screenshots
- Generate UX metrics and scores
- Provide developer-friendly feedback
- Create code suggestions based on analysis
- Support non-web platforms (games, desktop apps)

## Installation

```bash
# Install Playwright for Python
pip install playwright

# Install Playwright browsers
playwright install chromium

# UX-Mirror dependencies (already installed)
# - ai_vision_analyzer.py
# - PIL, numpy, aiohttp
```

## Testing

```python
# tests/test_playwright_integration.py

import pytest
from src.integration.playwright_adapter import PlaywrightUXMirrorAdapter

@pytest.mark.asyncio
async def test_playwright_adapter_basic():
    adapter = PlaywrightUXMirrorAdapter(
        api_key="test-key",
        provider="openai"
    )
    
    await adapter.start(headless=True)
    
    try:
        results = await adapter.navigate_and_analyze(
            url="https://example.com"
        )
        
        assert results["screenshot_captured"] == True
        assert "analysis" in results
        assert "feedback" in results
        
    finally:
        await adapter.stop()
```

## Active User Monitoring

UX-Mirror includes an **Active Monitoring Mode** that watches users interact with websites in real-time and detects problems they encounter.

### Features

- **Real-time Problem Detection**: Detects errors, confusion points, and unexpected behavior
- **Interaction Tracking**: Monitors clicks, typing, navigation
- **Hesitation Detection**: Identifies when users pause (potential confusion)
- **Performance Monitoring**: Tracks slow requests and errors
- **AI-Powered Analysis**: Analyzes screenshots at key moments

### Usage

```python
from src.integration.playwright_active_monitor import PlaywrightActiveMonitor

monitor = PlaywrightActiveMonitor(api_key="your-key")

# Set up callbacks
def on_problem(problem):
    print(f"Problem: {problem.description} ({problem.severity})")

monitor.on_problem_detected = on_problem

# Start monitoring (headless=False so user can interact)
await monitor.start_monitoring("https://example.com", headless=False)

# Monitor runs in background, detects problems automatically
# Press Ctrl+C to stop
```

### CLI Usage

```bash
# Watch user interact and detect problems
ux-tester playwright monitor https://example.com

# Adjust hesitation threshold (default: 5 seconds)
ux-tester playwright monitor https://example.com --hesitation-threshold 3.0
```

### Detected Problem Types

- **Errors**: JavaScript errors, HTTP errors, console errors
- **Confusion**: User hesitation (inactive for threshold time)
- **Unexpected**: UI issues detected by AI analysis
- **Performance**: Slow requests, timeouts
- **Accessibility**: Issues detected during interaction

## Next Steps

1. ✅ **Create the adapter module** (`src/integration/playwright_adapter.py`)
2. ✅ **Add tests** for Playwright integration
3. ✅ **Update documentation** with Playwright examples
4. ✅ **Create CLI commands** for web UX testing
5. ✅ **Add active monitoring** for real-time problem detection
6. ⏭️ **Integrate with visual analysis components** (core/screenshot_analyzer.py)

## Summary

This integration allows UX-Mirror to:
- **Leverage Playwright** for robust web automation and screenshot capture
- **Add AI intelligence** on top of Playwright's capabilities
- **Maintain separation** between automation (Playwright) and analysis (UX-Mirror)
- **Extend beyond web** to games and desktop applications

The result is a powerful combination: Playwright's reliable web automation + UX-Mirror's AI-powered UX analysis.

