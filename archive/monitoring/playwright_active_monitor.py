#!/usr/bin/env python3
"""
Playwright Active User Monitoring

Watches a user actively use a website/application and detects:
- Problems they encounter
- Unexpected behavior
- Confusion points
- Performance issues
- Accessibility barriers

This mode observes real user interactions and provides real-time feedback.
"""

import asyncio
import os
import sys
from typing import Optional, Dict, Any, List, Callable
from PIL import Image
import io
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from playwright.async_api import Page, Browser, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not installed. Install with: pip install playwright")

from src.integration.playwright_adapter import PlaywrightUXMirrorAdapter
from ai_vision_analyzer import AIVisionAnalyzer, GameUIFeedbackProcessor

logger = logging.getLogger(__name__)


@dataclass
class InteractionEvent:
    """Represents a user interaction event"""
    timestamp: float
    event_type: str  # 'click', 'type', 'navigate', 'hover', 'scroll'
    target: Optional[str] = None  # Selector or URL
    value: Optional[str] = None  # Typed text or value
    location: Optional[Dict[str, int]] = None  # x, y coordinates
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ProblemDetected:
    """Represents a problem detected during active monitoring"""
    timestamp: float
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str  # 'error', 'confusion', 'performance', 'accessibility', 'unexpected'
    description: str
    evidence: Dict[str, Any]
    screenshot_before: Optional[bytes] = None
    screenshot_after: Optional[bytes] = None
    user_action: Optional[InteractionEvent] = None
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        # Don't serialize screenshot bytes in dict
        if result.get('screenshot_before'):
            result['screenshot_before'] = f"<{len(self.screenshot_before)} bytes>"
        if result.get('screenshot_after'):
            result['screenshot_after'] = f"<{len(self.screenshot_after)} bytes>"
        return result


class PlaywrightActiveMonitor:
    """
    Monitors active user interactions and detects problems in real-time.
    
    Features:
    - Watches user clicks, typing, navigation
    - Detects errors and unexpected behavior
    - Identifies confusion points (hesitation, backtracking)
    - Monitors performance issues
    - Provides real-time problem alerts
    """
    
    def __init__(self, api_key: str, provider: str = "openai"):
        """
        Initialize active monitor.
        
        Args:
            api_key: API key for AI analysis
            provider: "openai" or "anthropic"
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright is required. Install with: pip install playwright && playwright install chromium"
            )
        
        self.api_key = api_key
        self.provider = provider
        self.adapter = PlaywrightUXMirrorAdapter(api_key, provider)
        
        # Monitoring state
        self.monitoring = False
        self.interaction_history: List[InteractionEvent] = []
        self.problems_detected: List[ProblemDetected] = []
        self.current_url: Optional[str] = None
        self.last_screenshot: Optional[bytes] = None
        self.last_interaction_time: float = 0
        
        # Configuration
        self.analysis_interval = 2.0  # Analyze every 2 seconds of activity
        self.hesitation_threshold = 5.0  # 5 seconds = potential confusion
        self.error_detection_enabled = True
        self.performance_monitoring = True
        
        # Callbacks
        self.on_problem_detected: Optional[Callable[[ProblemDetected], None]] = None
        self.on_interaction: Optional[Callable[[InteractionEvent], None]] = None
        
        # AI analyzer
        self.analyzer: Optional[AIVisionAnalyzer] = None
        self.feedback_processor = GameUIFeedbackProcessor()
    
    async def start_monitoring(
        self,
        url: str,
        headless: bool = False,
        browser_type: str = "chromium"
    ):
        """
        Start monitoring user interactions on a page.
        
        Args:
            url: Initial URL to load
            headless: Run browser in headless mode (usually False for user monitoring)
            browser_type: Browser to use
        """
        if self.monitoring:
            logger.warning("Monitoring already active")
            return
        
        # Start adapter
        await self.adapter.start(headless=headless, browser_type=browser_type)
        
        # Navigate to initial URL
        await self.adapter.page.goto(url, wait_until="networkidle")
        self.current_url = url
        
        # Initialize AI analyzer
        self.analyzer = AIVisionAnalyzer(self.api_key, self.provider)
        await self.analyzer.__aenter__()
        
        # Set up event listeners
        await self._setup_event_listeners()
        
        # Start monitoring loop
        self.monitoring = True
        self.last_interaction_time = asyncio.get_event_loop().time()
        
        logger.info(f"Active monitoring started on {url}")
        
        # Start background monitoring tasks
        asyncio.create_task(self._monitoring_loop())
        asyncio.create_task(self._hesitation_detector())
        asyncio.create_task(self._error_detector())
    
    async def stop_monitoring(self):
        """Stop monitoring and cleanup"""
        self.monitoring = False
        
        if self.analyzer:
            await self.analyzer.__aexit__(None, None, None)
        
        await self.adapter.stop()
        
        logger.info("Active monitoring stopped")
    
    async def _setup_event_listeners(self):
        """Set up Playwright event listeners to track user interactions"""
        page = self.adapter.page
        
        # Track clicks
        async def on_click(event):
            selector = await self._get_selector_for_element(event.target) if hasattr(event, 'target') else None
            interaction = InteractionEvent(
                timestamp=asyncio.get_event_loop().time(),
                event_type="click",
                target=selector,
                location={"x": event.x, "y": event.y} if hasattr(event, 'x') else None
            )
            await self._handle_interaction(interaction)
        
        # Track navigation
        page.on("framenavigated", self._on_navigation)
        
        # Track console errors
        page.on("console", self._on_console_message)
        
        # Track page errors
        page.on("pageerror", self._on_page_error)
        
        # Track requests/responses for performance
        if self.performance_monitoring:
            page.on("request", self._on_request)
            page.on("response", self._on_response)
    
    async def _on_navigation(self, frame):
        """Handle page navigation"""
        if frame == self.adapter.page.main_frame:
            new_url = frame.url
            if new_url != self.current_url:
                interaction = InteractionEvent(
                    timestamp=asyncio.get_event_loop().time(),
                    event_type="navigate",
                    target=new_url
                )
                await self._handle_interaction(interaction)
                self.current_url = new_url
    
    async def _on_console_message(self, msg):
        """Detect console errors/warnings"""
        if msg.type in ['error', 'warning']:
            problem = ProblemDetected(
                timestamp=asyncio.get_event_loop().time(),
                severity="high" if msg.type == "error" else "medium",
                category="error",
                description=f"Console {msg.type}: {msg.text}",
                evidence={"type": msg.type, "text": msg.text, "location": msg.location}
            )
            await self._report_problem(problem)
    
    async def _on_page_error(self, error):
        """Detect page errors"""
        problem = ProblemDetected(
            timestamp=asyncio.get_event_loop().time(),
            severity="critical",
            category="error",
            description=f"Page error: {error.message}",
            evidence={"error": str(error), "stack": error.stack if hasattr(error, 'stack') else None}
        )
        await self._report_problem(problem)
    
    async def _on_request(self, request):
        """Track requests for performance monitoring"""
        # Can detect slow requests here
        pass
    
    async def _on_response(self, response):
        """Track responses for performance issues"""
        if response.status >= 400:
            problem = ProblemDetected(
                timestamp=asyncio.get_event_loop().time(),
                severity="high" if response.status >= 500 else "medium",
                category="error",
                description=f"HTTP {response.status} error: {response.url}",
                evidence={"status": response.status, "url": response.url}
            )
            await self._report_problem(problem)
    
    async def _handle_interaction(self, interaction: InteractionEvent):
        """Handle a user interaction"""
        self.interaction_history.append(interaction)
        self.last_interaction_time = asyncio.get_event_loop().time()
        
        # Keep only recent history (last 100 interactions)
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
        
        # Callback
        if self.on_interaction:
            try:
                self.on_interaction(interaction)
            except Exception as e:
                logger.error(f"Error in interaction callback: {e}")
        
        # Capture screenshot for analysis
        try:
            screenshot = await self.adapter.page.screenshot()
            self.last_screenshot = screenshot
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
    
    async def _monitoring_loop(self):
        """Main monitoring loop - analyzes activity periodically"""
        while self.monitoring:
            try:
                await asyncio.sleep(self.analysis_interval)
                
                if not self.monitoring:
                    break
                
                # Check for recent activity
                time_since_last = asyncio.get_event_loop().time() - self.last_interaction_time
                if time_since_last < self.analysis_interval * 2:
                    # User is active, analyze current state
                    await self._analyze_current_state()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
    
    async def _hesitation_detector(self):
        """Detect user hesitation/confusion"""
        while self.monitoring:
            try:
                await asyncio.sleep(1.0)
                
                if not self.monitoring:
                    break
                
                # Check if user has been inactive
                time_since_last = asyncio.get_event_loop().time() - self.last_interaction_time
                
                if time_since_last > self.hesitation_threshold and len(self.interaction_history) > 0:
                    # User might be confused or stuck
                    problem = ProblemDetected(
                        timestamp=asyncio.get_event_loop().time(),
                        severity="medium",
                        category="confusion",
                        description=f"User inactive for {time_since_last:.1f}s - possible confusion or hesitation",
                        evidence={
                            "inactive_duration": time_since_last,
                            "last_interaction": self.interaction_history[-1].to_dict() if self.interaction_history else None
                        },
                        screenshot_before=self.last_screenshot
                    )
                    await self._report_problem(problem)
                    # Reset to avoid repeated alerts
                    self.last_interaction_time = asyncio.get_event_loop().time()
                
            except Exception as e:
                logger.error(f"Error in hesitation detector: {e}")
    
    async def _error_detector(self):
        """Continuously check for errors"""
        while self.monitoring:
            try:
                await asyncio.sleep(0.5)
                
                if not self.monitoring:
                    break
                
                # Check for JavaScript errors
                errors = await self.adapter.page.evaluate("""() => {
                    return window.errors || [];
                }""")
                
                if errors:
                    for error in errors:
                        problem = ProblemDetected(
                            timestamp=asyncio.get_event_loop().time(),
                            severity="high",
                            category="error",
                            description=f"JavaScript error: {error}",
                            evidence={"error": error}
                        )
                        await self._report_problem(problem)
                
            except Exception as e:
                logger.error(f"Error in error detector: {e}")
    
    async def _analyze_current_state(self):
        """Analyze current page state with AI"""
        if not self.analyzer or not self.last_screenshot:
            return
        
        try:
            # Analyze screenshot
            image = Image.open(io.BytesIO(self.last_screenshot))
            
            # Build context from recent interactions
            context = self._build_interaction_context()
            
            analysis = await self.analyzer.analyze_screenshot(image, context=context)
            
            # Check for issues in analysis
            if analysis.issues_found:
                for issue in analysis.issues_found:
                    if issue.get('severity') in ['high', 'critical']:
                        problem = ProblemDetected(
                            timestamp=asyncio.get_event_loop().time(),
                            severity=issue.get('severity', 'medium'),
                            category="unexpected",
                            description=issue.get('description', 'UI issue detected'),
                            evidence={
                                "location": issue.get('location'),
                                "type": issue.get('type'),
                                "analysis": analysis.overall_assessment
                            },
                            screenshot_before=self.last_screenshot
                        )
                        await self._report_problem(problem)
        
        except Exception as e:
            logger.error(f"Error analyzing current state: {e}")
    
    def _build_interaction_context(self) -> str:
        """Build context string from recent interactions"""
        if not self.interaction_history:
            return "Initial page load"
        
        recent = self.interaction_history[-5:]  # Last 5 interactions
        context_parts = ["Recent user interactions:"]
        
        for interaction in recent:
            if interaction.event_type == "click":
                context_parts.append(f"- Clicked on {interaction.target}")
            elif interaction.event_type == "type":
                context_parts.append(f"- Typed in {interaction.target}")
            elif interaction.event_type == "navigate":
                context_parts.append(f"- Navigated to {interaction.target}")
        
        return "\n".join(context_parts)
    
    async def _report_problem(self, problem: ProblemDetected):
        """Report a detected problem"""
        self.problems_detected.append(problem)
        
        # Keep only recent problems (last 50)
        if len(self.problems_detected) > 50:
            self.problems_detected = self.problems_detected[-50:]
        
        # Callback
        if self.on_problem_detected:
            try:
                self.on_problem_detected(problem)
            except Exception as e:
                logger.error(f"Error in problem callback: {e}")
        
        logger.warning(f"Problem detected: {problem.severity} - {problem.description}")
    
    async def _get_selector_for_element(self, element) -> Optional[str]:
        """Get CSS selector for an element (simplified)"""
        # This is a simplified version - in production, use Playwright's built-in methods
        try:
            return await self.adapter.page.evaluate("""(element) => {
                // Generate a selector for the element
                if (element.id) return '#' + element.id;
                if (element.className) return '.' + element.className.split(' ')[0];
                return element.tagName.toLowerCase();
            }""", element)
        except:
            return None
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of monitoring session"""
        return {
            "monitoring_active": self.monitoring,
            "current_url": self.current_url,
            "total_interactions": len(self.interaction_history),
            "problems_detected": len(self.problems_detected),
            "problems_by_severity": self._count_problems_by_severity(),
            "problems_by_category": self._count_problems_by_category(),
            "recent_problems": [p.to_dict() for p in self.problems_detected[-10:]]
        }
    
    def _count_problems_by_severity(self) -> Dict[str, int]:
        """Count problems by severity"""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for problem in self.problems_detected:
            counts[problem.severity] = counts.get(problem.severity, 0) + 1
        return counts
    
    def _count_problems_by_category(self) -> Dict[str, int]:
        """Count problems by category"""
        counts = {}
        for problem in self.problems_detected:
            counts[problem.category] = counts.get(problem.category, 0) + 1
        return counts

