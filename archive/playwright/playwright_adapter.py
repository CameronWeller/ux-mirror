#!/usr/bin/env python3
"""
Playwright UX-Mirror Adapter

Integrates Playwright web automation with UX-Mirror's AI vision analysis.
This adapter builds ON TOP OF Playwright rather than duplicating its features.

Playwright provides:
- Web navigation and interaction
- Screenshot capture
- Element selection and waiting

UX-Mirror adds:
- AI vision analysis of screenshots
- UX metrics and feedback
- Developer-friendly recommendations
"""

import asyncio
import os
import sys
from typing import Optional, Dict, Any, List
from PIL import Image
import io
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not installed. Install with: pip install playwright")

from ai_vision_analyzer import AIVisionAnalyzer, GameUIFeedbackProcessor

logger = logging.getLogger(__name__)

class PlaywrightUXMirrorAdapter:
    """
    Adapter that integrates Playwright web automation with UX-Mirror AI analysis.
    
    Architecture:
    - Uses Playwright for web automation (navigation, interaction, screenshots)
    - Uses UX-Mirror AI analyzer for vision analysis and UX feedback
    - Does NOT duplicate Playwright features - builds on top of them
    """
    
    def __init__(self, api_key: str, provider: str = "openai"):
        """
        Initialize the adapter.
        
        Args:
            api_key: API key for OpenAI or Anthropic
            provider: "openai" or "anthropic"
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright is required. Install with: pip install playwright && playwright install chromium"
            )
        
        self.api_key = api_key
        self.provider = provider
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.analyzer: Optional[AIVisionAnalyzer] = None
        self.feedback_processor = GameUIFeedbackProcessor()
        self._playwright = None
    
    async def start(self, headless: bool = True, browser_type: str = "chromium"):
        """
        Start Playwright browser and initialize AI analyzer.
        
        Args:
            headless: Run browser in headless mode
            browser_type: "chromium", "firefox", or "webkit"
        """
        self._playwright = await async_playwright().start()
        
        # Launch browser based on type
        if browser_type == "chromium":
            self.browser = await self._playwright.chromium.launch(headless=headless)
        elif browser_type == "firefox":
            self.browser = await self._playwright.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            self.browser = await self._playwright.webkit.launch(headless=headless)
        else:
            raise ValueError(f"Unknown browser type: {browser_type}")
        
        self.page = await self.browser.new_page()
        
        # Initialize AI analyzer
        self.analyzer = AIVisionAnalyzer(self.api_key, self.provider)
        await self.analyzer.__aenter__()
        
        logger.info(f"Playwright UX-Mirror adapter started ({browser_type}, headless={headless})")
    
    async def stop(self):
        """Stop browser and cleanup resources"""
        if self.analyzer:
            await self.analyzer.__aexit__(None, None, None)
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Playwright UX-Mirror adapter stopped")
    
    async def navigate_and_analyze(
        self, 
        url: str, 
        wait_for: Optional[str] = None,
        context: Optional[str] = None,
        full_page: bool = True
    ) -> Dict[str, Any]:
        """
        Navigate to a URL, capture screenshot using Playwright, and analyze with UX-Mirror AI.
        
        Args:
            url: URL to navigate to
            wait_for: Optional CSS selector to wait for before screenshot
            context: Additional context for AI analysis
            full_page: Capture full page or just viewport
            
        Returns:
            Dict with analysis results and UX feedback
        """
        if not self.page:
            raise RuntimeError("Adapter not started. Call start() first.")
        
        # Use Playwright for navigation
        await self.page.goto(url, wait_until="networkidle")
        
        # Wait for specific element if provided
        if wait_for:
            await self.page.wait_for_selector(wait_for)
        
        # Capture screenshot using Playwright (don't duplicate this!)
        screenshot_bytes = await self.page.screenshot(full_page=full_page)
        
        # Convert to PIL Image for AI analyzer
        image = Image.open(io.BytesIO(screenshot_bytes))
        
        # Use UX-Mirror AI analyzer (our value-add)
        analysis = await self.analyzer.analyze_screenshot(
            image,
            context=context or f"Web page analysis: {url}"
        )
        
        # Process feedback
        feedback = self.feedback_processor.process_analysis(analysis)
        
        return {
            "url": url,
            "screenshot_captured": True,
            "screenshot_size": image.size,
            "analysis": analysis,
            "feedback": feedback
        }
    
    async def interact_and_analyze(
        self,
        action: Dict[str, Any],
        context: Optional[str] = None,
        wait_after: bool = True
    ) -> Dict[str, Any]:
        """
        Perform an interaction using Playwright and analyze the result with UX-Mirror.
        
        Args:
            action: Dict with 'type' and action-specific params
                - type: "click", "type", "fill", "select", "hover"
                - selector: CSS selector for element
                - text/value: Text to type or value to fill
            context: Context for AI analysis
            wait_after: Wait for network idle after interaction
            
        Returns:
            Dict with action results and analysis
        """
        if not self.page:
            raise RuntimeError("Adapter not started. Call start() first.")
        
        # Use Playwright for interaction (don't duplicate!)
        action_type = action.get("type")
        selector = action.get("selector")
        
        if action_type == "click":
            await self.page.click(selector)
        elif action_type == "type":
            await self.page.fill(selector, action.get("text", ""))
        elif action_type == "fill":
            await self.page.fill(selector, action.get("value", ""))
        elif action_type == "select":
            await self.page.select_option(selector, action.get("value"))
        elif action_type == "hover":
            await self.page.hover(selector)
        else:
            raise ValueError(f"Unknown action type: {action_type}")
        
        # Wait for page to settle (Playwright feature)
        if wait_after:
            await self.page.wait_for_load_state("networkidle")
        
        # Capture screenshot using Playwright
        screenshot_bytes = await self.page.screenshot(full_page=True)
        image = Image.open(io.BytesIO(screenshot_bytes))
        
        # Analyze with UX-Mirror AI (our value-add)
        analysis = await self.analyzer.analyze_screenshot(
            image,
            context=context or f"After {action_type} on {selector}"
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
        Analyze a specific element by capturing its screenshot with Playwright.
        
        Uses Playwright to:
        - Locate and wait for element
        - Capture element screenshot
        
        Uses UX-Mirror to:
        - Analyze element's visual design
        - Generate UX feedback
        
        Args:
            selector: CSS selector for element
            context: Context for AI analysis
            
        Returns:
            Dict with element analysis and feedback
        """
        if not self.page:
            raise RuntimeError("Adapter not started. Call start() first.")
        
        # Use Playwright to wait for and locate element
        element = await self.page.wait_for_selector(selector)
        
        # Capture element screenshot using Playwright
        screenshot_bytes = await element.screenshot()
        image = Image.open(io.BytesIO(screenshot_bytes))
        
        # Analyze with UX-Mirror AI
        analysis = await self.analyzer.analyze_screenshot(
            image,
            context=context or f"Element analysis: {selector}"
        )
        
        feedback = self.feedback_processor.process_analysis(analysis)
        
        return {
            "selector": selector,
            "element_captured": True,
            "element_size": image.size,
            "analysis": analysis,
            "feedback": feedback
        }
    
    async def run_ux_test_flow(
        self,
        test_steps: List[Dict[str, Any]],
        analyze_after_each: bool = True
    ) -> Dict[str, Any]:
        """
        Run a sequence of interactions and analyze UX at each step.
        
        Uses Playwright for all automation, UX-Mirror for all analysis.
        
        Args:
            test_steps: List of action dicts
                - type: "navigate", "click", "type", etc.
                - url/selector/text: Action-specific params
                - description: Optional description for context
            analyze_after_each: Whether to analyze after each step
            
        Returns:
            Complete test results with analysis at each step
        """
        if not self.page:
            raise RuntimeError("Adapter not started. Call start() first.")
        
        results = {
            "steps": [],
            "overall_analysis": None,
            "recommendations": []
        }
        
        for i, step in enumerate(test_steps):
            step_result = {
                "step_number": i + 1,
                "action": step,
                "description": step.get("description", step.get("type", "unknown"))
            }
            
            # Perform action using Playwright (don't duplicate!)
            action_type = step.get("type")
            
            try:
                if action_type == "navigate":
                    await self.page.goto(step["url"], wait_until="networkidle")
                elif action_type == "click":
                    await self.page.click(step["selector"])
                elif action_type == "type":
                    await self.page.fill(step["selector"], step.get("text", ""))
                elif action_type == "fill":
                    await self.page.fill(step["selector"], step.get("value", ""))
                elif action_type == "wait":
                    await self.page.wait_for_timeout(step.get("timeout", 1000))
                else:
                    logger.warning(f"Unknown action type: {action_type}")
                
                step_result["success"] = True
                
            except Exception as e:
                logger.error(f"Step {i+1} failed: {e}")
                step_result["success"] = False
                step_result["error"] = str(e)
            
            # Analyze if requested (UX-Mirror value-add)
            if analyze_after_each and step_result.get("success"):
                try:
                    screenshot_bytes = await self.page.screenshot(full_page=True)
                    image = Image.open(io.BytesIO(screenshot_bytes))
                    
                    analysis = await self.analyzer.analyze_screenshot(
                        image,
                        context=f"Step {i+1}: {step_result['description']}"
                    )
                    
                    step_result["analysis"] = analysis
                    step_result["feedback"] = self.feedback_processor.process_analysis(analysis)
                    
                except Exception as e:
                    logger.error(f"Analysis failed for step {i+1}: {e}")
                    step_result["analysis_error"] = str(e)
            
            results["steps"].append(step_result)
        
        # Final overall analysis
        try:
            final_screenshot = await self.page.screenshot(full_page=True)
            final_image = Image.open(io.BytesIO(final_screenshot))
            final_analysis = await self.analyzer.analyze_screenshot(
                final_image,
                context="Final state after all test steps"
            )
            
            results["overall_analysis"] = final_analysis
            results["recommendations"] = final_analysis.recommendations
            
        except Exception as e:
            logger.error(f"Final analysis failed: {e}")
            results["overall_analysis_error"] = str(e)
        
        return results
    
    async def get_page_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics from Playwright (don't duplicate this!).
        
        Returns:
            Dict with page metrics
        """
        if not self.page:
            raise RuntimeError("Adapter not started. Call start() first.")
        
        # Use Playwright's built-in metrics
        metrics = await self.page.evaluate("""() => {
            return {
                loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
                domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0,
                firstContentfulPaint: performance.getEntriesByType('paint')[1]?.startTime || 0
            };
        }""")
        
        return metrics


# Example usage
async def main():
    """Example usage of the adapter"""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return
    
    adapter = PlaywrightUXMirrorAdapter(api_key, provider="openai")
    
    try:
        await adapter.start(headless=True)
        
        # Analyze a web page
        results = await adapter.navigate_and_analyze(
            url="https://example.com",
            context="Analyzing homepage UX"
        )
        
        print("Analysis Summary:", results["feedback"]["summary"])
        print("\nTop Issues:")
        for issue in results["feedback"]["priority_fixes"]:
            print(f"  - {issue['description']} ({issue['severity']})")
        
    finally:
        await adapter.stop()


if __name__ == "__main__":
    asyncio.run(main())

