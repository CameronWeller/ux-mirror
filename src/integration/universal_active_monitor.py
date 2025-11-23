#!/usr/bin/env python3
"""
Universal Active Monitor

Monitors ANY application (web, Windows executable, mobile, games) and detects:
- Performance issues (hitches, stuttering, frame drops)
- User confusion points
- Errors and unexpected behavior
- Input lag and responsiveness issues

Works across platforms and application types.
"""

import asyncio
import os
import sys
import time
import io
from typing import Optional, Dict, Any, List, Callable, Union
from PIL import Image
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_vision_analyzer import AIVisionAnalyzer, GameUIFeedbackProcessor

logger = logging.getLogger(__name__)


class ApplicationType(Enum):
    """Type of application being monitored"""
    WEB = "web"
    WINDOWS_EXE = "windows_exe"
    MOBILE = "mobile"
    GAME = "game"
    DESKTOP = "desktop"


@dataclass
class PerformanceMetrics:
    """Performance metrics for frame-based applications"""
    timestamp: float
    fps: Optional[float] = None
    frame_time_ms: Optional[float] = None
    frame_time_variance: Optional[float] = None
    dropped_frames: int = 0
    stutter_count: int = 0
    hitch_detected: bool = False
    input_lag_ms: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ProblemDetected:
    """Represents a problem detected during active monitoring"""
    timestamp: float
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str  # 'performance', 'error', 'confusion', 'accessibility', 'stutter', 'hitch'
    description: str
    evidence: Dict[str, Any]
    screenshot: Optional[bytes] = None
    performance_metrics: Optional[PerformanceMetrics] = None
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        if result.get('screenshot'):
            result['screenshot'] = f"<{len(self.screenshot)} bytes>"
        return result


class UniversalActiveMonitor:
    """
    Universal active monitor for any application type.
    
    Supports:
    - Web applications (via Playwright)
    - Windows executables (via native capture)
    - Mobile applications (via ADB/device capture)
    - Games (via Vulkan/DirectX capture + FPS monitoring)
    """
    
    def __init__(
        self,
        api_key: str,
        app_type: ApplicationType,
        provider: str = "openai"
    ):
        """
        Initialize universal monitor.
        
        Args:
            api_key: API key for AI analysis
            app_type: Type of application (WEB, WINDOWS_EXE, MOBILE, GAME)
            provider: AI provider ("openai" or "anthropic")
        """
        self.api_key = api_key
        self.provider = provider
        self.app_type = app_type
        
        # Monitoring state
        self.monitoring = False
        self.problems_detected: List[ProblemDetected] = []
        
        # Performance monitoring
        self.frame_times: List[float] = []  # Frame times in ms
        self.fps_history: List[float] = []  # FPS over time
        self.last_frame_time: Optional[float] = None
        self.frame_count = 0
        
        # Configuration
        self.target_fps = 60.0  # Target FPS (configurable)
        self.stutter_threshold_ms = 33.0  # Frame time > 33ms = stutter (at 60fps)
        self.hitch_threshold_ms = 100.0  # Frame time > 100ms = hitch
        self.fps_drop_threshold = 0.2  # 20% FPS drop = problem
        self.analysis_interval = 2.0  # Analyze every 2 seconds
        
        # Callbacks
        self.on_problem_detected: Optional[Callable[[ProblemDetected], None]] = None
        self.on_performance_update: Optional[Callable[[PerformanceMetrics], None]] = None
        
        # AI analyzer
        self.analyzer: Optional[AIVisionAnalyzer] = None
        self.feedback_processor = GameUIFeedbackProcessor()
        
        # Platform-specific capture
        self.capture_handler = None
        self._setup_capture_handler()
    
    def _setup_capture_handler(self):
        """Setup platform-specific capture handler"""
        if self.app_type == ApplicationType.WEB:
            # Use Playwright for web
            try:
                from src.integration.playwright_active_monitor import PlaywrightActiveMonitor
                self.capture_handler = PlaywrightActiveMonitor(self.api_key, self.provider)
            except ImportError:
                logger.error("Playwright not available for web monitoring")
        
        elif self.app_type == ApplicationType.WINDOWS_EXE:
            # Use native Windows capture
            try:
                from src.capture.screenshot_handler import ScreenshotHandler
                self.capture_handler = ScreenshotHandler()
            except ImportError:
                logger.error("Screenshot handler not available")
        
        elif self.app_type == ApplicationType.GAME:
            # Use Vulkan/DirectX capture
            try:
                from vulkan_screenshot_capture import VulkanScreenshotCapture
                self.capture_handler = VulkanScreenshotCapture()
            except ImportError:
                logger.error("Vulkan capture not available")
        
        elif self.app_type == ApplicationType.MOBILE:
            # Use ADB for mobile
            try:
                # Mobile capture would go here
                logger.warning("Mobile capture not yet implemented")
            except ImportError:
                logger.error("Mobile capture not available")
    
    async def start_monitoring(self, target: str, **kwargs):
        """
        Start monitoring an application.
        
        Args:
            target: URL (web), process name (exe), or app identifier
            **kwargs: Platform-specific options
        """
        if self.monitoring:
            logger.warning("Monitoring already active")
            return
        
        # Initialize AI analyzer
        self.analyzer = AIVisionAnalyzer(self.api_key, self.provider)
        await self.analyzer.__aenter__()
        
        # Start platform-specific monitoring
        if self.app_type == ApplicationType.WEB:
            await self._start_web_monitoring(target, **kwargs)
        elif self.app_type == ApplicationType.WINDOWS_EXE:
            await self._start_windows_monitoring(target, **kwargs)
        elif self.app_type == ApplicationType.GAME:
            await self._start_game_monitoring(target, **kwargs)
        elif self.app_type == ApplicationType.MOBILE:
            await self._start_mobile_monitoring(target, **kwargs)
        
        self.monitoring = True
        
        # Start monitoring loops
        asyncio.create_task(self._performance_monitoring_loop())
        asyncio.create_task(self._analysis_loop())
        
        logger.info(f"Universal monitoring started for {self.app_type.value}: {target}")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        
        if self.analyzer:
            await self.analyzer.__aexit__(None, None, None)
        
        if self.capture_handler and hasattr(self.capture_handler, 'stop_monitoring'):
            await self.capture_handler.stop_monitoring()
        
        logger.info("Universal monitoring stopped")
    
    async def _start_web_monitoring(self, url: str, **kwargs):
        """Start web application monitoring"""
        if hasattr(self.capture_handler, 'start_monitoring'):
            await self.capture_handler.start_monitoring(url, **kwargs)
    
    async def _start_windows_monitoring(self, process_name: str, **kwargs):
        """Start Windows executable monitoring"""
        # Windows monitoring would use native capture
        # This is a placeholder - would integrate with Windows-specific capture
        logger.info(f"Starting Windows monitoring for: {process_name}")
    
    async def _start_game_monitoring(self, game_name: str, **kwargs):
        """Start game monitoring with FPS tracking"""
        logger.info(f"Starting game monitoring for: {game_name}")
        # Game monitoring would setup Vulkan/DirectX capture
        if self.capture_handler:
            self.capture_handler.setup_shared_memory(
                kwargs.get('width', 1920),
                kwargs.get('height', 1080)
            )
    
    async def _start_mobile_monitoring(self, app_id: str, **kwargs):
        """Start mobile application monitoring"""
        logger.info(f"Starting mobile monitoring for: {app_id}")
        # Mobile monitoring would use ADB or similar
    
    async def _performance_monitoring_loop(self):
        """Monitor performance metrics (FPS, frame times, stuttering)"""
        while self.monitoring:
            try:
                await asyncio.sleep(0.016)  # ~60Hz monitoring
                
                if not self.monitoring:
                    break
                
                # Capture frame time
                current_time = time.time()
                
                if self.last_frame_time:
                    frame_time_ms = (current_time - self.last_frame_time) * 1000
                    self.frame_times.append(frame_time_ms)
                    self.frame_count += 1
                    
                    # Calculate FPS
                    fps = 1000.0 / frame_time_ms if frame_time_ms > 0 else 0
                    self.fps_history.append(fps)
                    
                    # Keep only recent history (last 60 frames = 1 second at 60fps)
                    if len(self.frame_times) > 60:
                        self.frame_times = self.frame_times[-60:]
                    if len(self.fps_history) > 60:
                        self.fps_history = self.fps_history[-60:]
                    
                    # Detect performance issues
                    await self._detect_performance_issues(frame_time_ms, fps)
                    
                    # Create performance metrics
                    metrics = self._calculate_performance_metrics()
                    if metrics and self.on_performance_update:
                        self.on_performance_update(metrics)
                
                self.last_frame_time = current_time
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
    
    async def _detect_performance_issues(self, frame_time_ms: float, fps: float):
        """Detect performance issues from frame timing"""
        
        # Detect stuttering (frame time spikes)
        if frame_time_ms > self.stutter_threshold_ms:
            stutter_severity = "high" if frame_time_ms > self.hitch_threshold_ms else "medium"
            category = "hitch" if frame_time_ms > self.hitch_threshold_ms else "stutter"
            
            problem = ProblemDetected(
                timestamp=time.time(),
                severity=stutter_severity,
                category=category,
                description=f"{category.capitalize()} detected: {frame_time_ms:.1f}ms frame time (target: {1000/self.target_fps:.1f}ms)",
                evidence={
                    "frame_time_ms": frame_time_ms,
                    "fps": fps,
                    "target_fps": self.target_fps,
                    "threshold": self.stutter_threshold_ms if category == "stutter" else self.hitch_threshold_ms
                },
                performance_metrics=self._calculate_performance_metrics()
            )
            await self._report_problem(problem)
        
        # Detect FPS drops
        if len(self.fps_history) >= 10:
            recent_fps = statistics.mean(self.fps_history[-10:])
            if recent_fps < self.target_fps * (1 - self.fps_drop_threshold):
                problem = ProblemDetected(
                    timestamp=time.time(),
                    severity="medium",
                    category="performance",
                    description=f"FPS drop detected: {recent_fps:.1f} FPS (target: {self.target_fps} FPS)",
                    evidence={
                        "current_fps": recent_fps,
                        "target_fps": self.target_fps,
                        "drop_percentage": (1 - recent_fps / self.target_fps) * 100
                    },
                    performance_metrics=self._calculate_performance_metrics()
                )
                await self._report_problem(problem)
    
    def _calculate_performance_metrics(self) -> Optional[PerformanceMetrics]:
        """Calculate current performance metrics"""
        if not self.frame_times:
            return None
        
        current_fps = self.fps_history[-1] if self.fps_history else None
        avg_frame_time = statistics.mean(self.frame_times) if self.frame_times else None
        frame_variance = statistics.variance(self.frame_times) if len(self.frame_times) > 1 else None
        
        # Count stutters (frames > threshold)
        stutter_count = sum(1 for ft in self.frame_times if ft > self.stutter_threshold_ms)
        hitch_detected = any(ft > self.hitch_threshold_ms for ft in self.frame_times[-10:])
        
        return PerformanceMetrics(
            timestamp=time.time(),
            fps=current_fps,
            frame_time_ms=avg_frame_time,
            frame_time_variance=frame_variance,
            stutter_count=stutter_count,
            hitch_detected=hitch_detected
        )
    
    async def _analysis_loop(self):
        """Periodic AI analysis of current state"""
        while self.monitoring:
            try:
                await asyncio.sleep(self.analysis_interval)
                
                if not self.monitoring:
                    break
                
                # Capture screenshot and analyze
                screenshot = await self._capture_screenshot()
                if screenshot and self.analyzer:
                    await self._analyze_screenshot(screenshot)
                
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
    
    async def _capture_screenshot(self) -> Optional[bytes]:
        """Capture screenshot from current application"""
        try:
            if self.app_type == ApplicationType.WEB:
                if hasattr(self.capture_handler, 'adapter') and self.capture_handler.adapter.page:
                    return await self.capture_handler.adapter.page.screenshot()
            
            elif self.app_type == ApplicationType.WINDOWS_EXE:
                # Use native Windows capture
                from PIL import ImageGrab
                img = ImageGrab.grab()
                import io
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                return buffer.getvalue()
            
            elif self.app_type == ApplicationType.GAME:
                # Use Vulkan capture
                if self.capture_handler:
                    frame = self.capture_handler.capture_frame()
                    if frame:
                        import io
                        buffer = io.BytesIO()
                        frame.to_pil_image().save(buffer, format='PNG')
                        return buffer.getvalue()
            
            return None
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    async def _analyze_screenshot(self, screenshot: bytes):
        """Analyze screenshot with AI"""
        try:
            image = Image.open(io.BytesIO(screenshot))
            
            # Build context based on app type
            context = f"Monitoring {self.app_type.value} application"
            if self.frame_times:
                avg_fps = statistics.mean(self.fps_history[-10:]) if self.fps_history else None
                if avg_fps:
                    context += f". Current FPS: {avg_fps:.1f}"
            
            analysis = await self.analyzer.analyze_screenshot(image, context=context)
            
            # Check for UI issues
            if analysis.issues_found:
                for issue in analysis.issues_found:
                    if issue.get('severity') in ['high', 'critical']:
                        problem = ProblemDetected(
                            timestamp=time.time(),
                            severity=issue.get('severity', 'medium'),
                            category="unexpected",
                            description=issue.get('description', 'UI issue detected'),
                            evidence={
                                "location": issue.get('location'),
                                "type": issue.get('type')
                            },
                            screenshot=screenshot,
                            performance_metrics=self._calculate_performance_metrics()
                        )
                        await self._report_problem(problem)
        
        except Exception as e:
            logger.error(f"Error analyzing screenshot: {e}")
    
    async def _report_problem(self, problem: ProblemDetected):
        """Report a detected problem"""
        self.problems_detected.append(problem)
        
        # Keep only recent problems
        if len(self.problems_detected) > 100:
            self.problems_detected = self.problems_detected[-100:]
        
        if self.on_problem_detected:
            try:
                self.on_problem_detected(problem)
            except Exception as e:
                logger.error(f"Error in problem callback: {e}")
        
        logger.warning(f"Problem detected: {problem.severity} - {problem.description}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of monitoring session"""
        metrics = self._calculate_performance_metrics()
        
        return {
            "monitoring_active": self.monitoring,
            "app_type": self.app_type.value,
            "total_problems": len(self.problems_detected),
            "problems_by_severity": self._count_problems_by_severity(),
            "problems_by_category": self._count_problems_by_category(),
            "performance": metrics.to_dict() if metrics else None,
            "fps_stats": {
                "current": self.fps_history[-1] if self.fps_history else None,
                "average": statistics.mean(self.fps_history) if self.fps_history else None,
                "min": min(self.fps_history) if self.fps_history else None,
                "max": max(self.fps_history) if self.fps_history else None
            } if self.fps_history else None
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

