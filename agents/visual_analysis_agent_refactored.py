"""
Visual Analysis Agent - Refactored Version
Demonstrates how to use BaseAgent and common utilities for cleaner code.
This reduces the original ~750 lines to ~250 lines while maintaining functionality.
"""

import numpy as np
from PIL import Image
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import cv2

# Import common components instead of duplicating code
from src.common.base_agent import BaseAgent
from src.common.config_manager import get_config, get_agent_config
from src.common.utils import (
    safe_json_load, safe_json_save, ensure_directory,
    Timer, async_retry, setup_logger, timestamp_now
)
from src.capture.screenshot_handler import get_screenshot_handler
from src.analysis.ui_element_detector import get_ui_detector

logger = setup_logger(__name__)

class VisualAnalysisAgentRefactored(BaseAgent):
    """
    Refactored Visual Analysis Agent using base class and shared utilities.
    Significantly reduced code duplication while maintaining all functionality.
    """
    
    def __init__(self, agent_id: str = "visual_analysis_001"):
        # Initialize base class with agent info
        super().__init__(
            agent_id=agent_id,
            agent_type="visual_analysis",
            capabilities=[
                "screenshot_capture",
                "ui_element_detection", 
                "accessibility_check",
                "quality_assessment",
                "baseline_comparison"
            ]
        )
        
        # Use centralized configuration
        self.config.update(get_agent_config('visual_analysis_agent'))
        
        # Use existing singletons
        self.screenshot_handler = get_screenshot_handler()
        self.ui_detector = get_ui_detector()
        
        # Agent-specific initialization
        self.baseline_dir = ensure_directory("baselines/visual")
        self.current_baseline = None
        
    async def run(self):
        """Main agent logic - much simpler with base class handling infrastructure"""
        logger.info("Visual Analysis Agent started")
        
        while self.running:
            try:
                # Capture and analyze
                with Timer("Visual Analysis Cycle"):
                    screenshot = await self._capture_screenshot()
                    if screenshot:
                        analysis = await self._analyze_screenshot(screenshot)
                        await self._process_results(analysis)
                
                # Wait for next cycle
                await asyncio.sleep(self.config.get('analysis_interval', 5.0))
                
            except Exception as e:
                await self.log_error(e, "Visual analysis cycle failed")
    
    @async_retry(max_attempts=3)
    async def _capture_screenshot(self) -> Optional[np.ndarray]:
        """Capture screenshot using shared handler"""
        return self.screenshot_handler.capture()
    
    async def _analyze_screenshot(self, screenshot: np.ndarray) -> Dict[str, Any]:
        """Perform visual analysis using shared components"""
        analysis = {
            'timestamp': timestamp_now(),
            'resolution': screenshot.shape[:2]
        }
        
        # Use shared UI detector
        ui_elements = self.ui_detector.detect_elements(screenshot)
        analysis['ui_elements'] = len(ui_elements)
        analysis['element_types'] = self._categorize_elements(ui_elements)
        
        # Quality assessment
        analysis['quality_score'] = self._assess_quality(screenshot)
        
        # Accessibility check
        analysis['accessibility_issues'] = self._check_accessibility(
            screenshot, ui_elements
        )
        
        # Baseline comparison if available
        if self.current_baseline is not None:
            analysis['baseline_comparison'] = self._compare_to_baseline(
                screenshot, self.current_baseline
            )
        
        return analysis
    
    async def _process_results(self, analysis: Dict[str, Any]):
        """Process and report analysis results"""
        # Determine severity based on findings
        severity = self._determine_severity(analysis)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis)
        
        # Report using base class method
        await self.report_insight(
            insight_type="visual_analysis",
            severity=severity,
            description=self._create_summary(analysis),
            recommendations=recommendations,
            data=analysis
        )
        
        # Update metrics
        self.metrics.custom_metrics['analyses_completed'] = \
            self.metrics.custom_metrics.get('analyses_completed', 0) + 1
    
    def _categorize_elements(self, elements: List[Any]) -> Dict[str, int]:
        """Categorize UI elements by type"""
        categories = {}
        for element in elements:
            element_type = element.get('type', 'unknown')
            categories[element_type] = categories.get(element_type, 0) + 1
        return categories
    
    def _assess_quality(self, image: np.ndarray) -> float:
        """Assess image quality (simplified)"""
        # Check contrast
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contrast = gray.std()
        
        # Check sharpness
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        
        # Normalize to 0-1 score
        quality_score = min(1.0, (contrast / 100 + sharpness / 1000) / 2)
        return quality_score
    
    def _check_accessibility(self, image: np.ndarray, 
                           elements: List[Any]) -> List[str]:
        """Check for accessibility issues"""
        issues = []
        
        # Check color contrast
        if self._has_low_contrast(image):
            issues.append("Low color contrast detected")
        
        # Check element sizes
        small_elements = [e for e in elements 
                         if e.get('width', 0) < 44 or e.get('height', 0) < 44]
        if small_elements:
            issues.append(f"{len(small_elements)} touch targets below minimum size")
        
        # Check for missing alt text (simplified)
        images_without_text = [e for e in elements 
                              if e.get('type') == 'image' and not e.get('text')]
        if images_without_text:
            issues.append(f"{len(images_without_text)} images may lack alt text")
        
        return issues
    
    def _compare_to_baseline(self, current: np.ndarray, 
                           baseline: np.ndarray) -> Dict[str, Any]:
        """Compare current screenshot to baseline"""
        # Resize if needed
        if current.shape != baseline.shape:
            baseline = cv2.resize(baseline, (current.shape[1], current.shape[0]))
        
        # Calculate difference
        diff = cv2.absdiff(current, baseline)
        change_score = np.mean(diff) / 255.0
        
        return {
            'change_score': float(change_score),
            'significant_change': change_score > self.config.get('change_threshold', 0.1)
        }
    
    def _has_low_contrast(self, image: np.ndarray) -> bool:
        """Check if image has low contrast areas"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray.std() < 30
    
    def _determine_severity(self, analysis: Dict[str, Any]) -> str:
        """Determine issue severity"""
        if len(analysis.get('accessibility_issues', [])) > 3:
            return 'high'
        elif analysis.get('quality_score', 1.0) < 0.5:
            return 'high'
        elif len(analysis.get('accessibility_issues', [])) > 0:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if analysis.get('quality_score', 1.0) < 0.7:
            recommendations.append("Improve image quality and contrast")
        
        for issue in analysis.get('accessibility_issues', []):
            if 'contrast' in issue.lower():
                recommendations.append("Increase color contrast for better readability")
            elif 'touch targets' in issue:
                recommendations.append("Increase size of interactive elements to 44x44px minimum")
            elif 'alt text' in issue:
                recommendations.append("Add descriptive alt text to images")
        
        return recommendations
    
    def _create_summary(self, analysis: Dict[str, Any]) -> str:
        """Create analysis summary"""
        ui_count = analysis.get('ui_elements', 0)
        quality = analysis.get('quality_score', 1.0)
        issues = len(analysis.get('accessibility_issues', []))
        
        summary = f"Detected {ui_count} UI elements, quality score: {quality:.2f}"
        if issues > 0:
            summary += f", {issues} accessibility issues found"
        
        return summary
    
    async def update_custom_metrics(self):
        """Update agent-specific metrics"""
        # This is called periodically by the base class
        if hasattr(self, 'ui_detector'):
            self.metrics.custom_metrics['cache_size'] = len(self.ui_detector._cache)
    
    async def cleanup(self):
        """Cleanup when agent stops"""
        logger.info("Visual Analysis Agent cleanup")
        # Any agent-specific cleanup here

# Example usage showing the simplicity:
async def main():
    agent = VisualAnalysisAgentRefactored()
    await agent.start()  # Base class handles all the infrastructure!

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())