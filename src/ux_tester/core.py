"""
Core UX testing functionality.

This module provides the main UXTester class that orchestrates screenshot capture,
visual analysis, and AI-powered content validation.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from ..capture.screenshot import ScreenshotCapture
from ..analysis.visual_analysis import VisualAnalyzer
from ..analysis.content_validation import ContentValidator
from .utils import load_config, validate_config, setup_logging, ensure_directory

import logging

logger = logging.getLogger(__name__)


class UXTester:
    """
    Core UX testing class that orchestrates all testing functionality.
    
    This class provides a unified interface for:
    - Screenshot capture with metadata
    - Visual analysis and change detection
    - AI-powered content validation
    - Performance metrics and reporting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, output_dir: str = "ux_captures"):
        """
        Initialize the UX tester with configuration.
        
        Args:
            config: Configuration dictionary (optional, will load from config.env if not provided)
            output_dir: Directory for saving screenshots and results
        """
        # Load and validate configuration
        if config is None:
            config = load_config()
        self.config = validate_config(config)
        
        # Set up logging
        setup_logging()
        
        # Create output directory
        self.output_dir = ensure_directory(output_dir)
        
        # Initialize components
        self.screenshot_capture = ScreenshotCapture(
            output_dir=output_dir,
            quality=self.config['screenshot_quality']
        )
        
        self.visual_analyzer = VisualAnalyzer(
            ui_change_threshold=self.config['ui_change_threshold']
        )
        
        self.content_validator = None
        if self.config['content_validation_enabled']:
            self.content_validator = ContentValidator(
                openai_api_key=self.config.get('openai_api_key', ''),
                anthropic_api_key=self.config.get('anthropic_api_key', '')
            )
        
        logger.info("UXTester initialized successfully")
    
    def capture_screenshot(self, label: str = "screenshot") -> Tuple[Path, Dict[str, Any]]:
        """
        Capture a screenshot with timestamp and metadata.
        
        Args:
            label: Label for the screenshot
            
        Returns:
            Tuple of (filepath, metadata)
        """
        return self.screenshot_capture.capture_screenshot(label)
    
    def capture_before(self, expected_content: Optional[str] = None) -> Tuple[Path, Dict[str, Any]]:
        """
        Capture 'before' screenshot with optional content expectation.
        
        Args:
            expected_content: Description of expected content
            
        Returns:
            Tuple of (filepath, metadata)
        """
        return self.screenshot_capture.capture_before(expected_content)
    
    def capture_after(self, expected_content: Optional[str] = None) -> Tuple[Path, Dict[str, Any]]:
        """
        Capture 'after' screenshot with optional content expectation.
        
        Args:
            expected_content: Description of expected content
            
        Returns:
            Tuple of (filepath, metadata)
        """
        return self.screenshot_capture.capture_after(expected_content)
    
    def analyze_screenshots(self, before_path: Optional[Path] = None, after_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Analyze before/after screenshots for UX quality.
        
        Args:
            before_path: Path to before screenshot (optional, will find latest if not provided)
            after_path: Path to after screenshot (optional, will find latest if not provided)
            
        Returns:
            Complete analysis results
        """
        # Find latest pair if paths not provided
        if before_path is None or after_path is None:
            before_path, after_path = self.screenshot_capture.find_latest_pair()
        
        if before_path is None or after_path is None:
            logger.error("Could not find before/after screenshot pair")
            return {
                'error': 'Could not find before/after screenshot pair',
                'instructions': [
                    'Run: capture_before() or capture_screenshot("before")',
                    'Then interact with your UI',
                    'Then: capture_after() or capture_screenshot("after")',
                    'Finally: analyze_screenshots()'
                ]
            }
        
        logger.info(f"Analyzing: {before_path.name} -> {after_path.name}")
        
        # Perform visual analysis
        analysis = self.visual_analyzer.analyze_screenshots(before_path, after_path)
        
        # Add content validation if enabled and expected content is available
        if self.content_validator:
            # Load metadata to check for expected content
            before_metadata = self.screenshot_capture.load_metadata(before_path)
            after_metadata = self.screenshot_capture.load_metadata(after_path)
            
            expected_content = after_metadata.get('expected_content') or before_metadata.get('expected_content')
            
            if expected_content:
                logger.info("Performing AI content validation")
                content_validation = self.content_validator.validate_content(after_path, expected_content)
                analysis['results']['content_validation'] = content_validation
            else:
                logger.debug("No expected content specified, skipping AI validation")
        
        # Save analysis results
        self._save_analysis_results(analysis)
        
        # Print summary
        self._print_analysis_summary(analysis)
        
        return analysis
    
    def validate_content_expectations(self, before_path: Optional[Path] = None, after_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Validate content expectations using AI analysis.
        
        Args:
            before_path: Path to before screenshot
            after_path: Path to after screenshot
            
        Returns:
            Content validation results
        """
        if not self.content_validator:
            return {
                'error': 'Content validation not enabled',
                'suggestion': 'Set content_validation_enabled=True in config'
            }
        
        # Find latest pair if paths not provided
        if before_path is None or after_path is None:
            before_path, after_path = self.screenshot_capture.find_latest_pair()
        
        if before_path is None or after_path is None:
            return {'error': 'Could not find before/after screenshot pair'}
        
        # Load metadata to get expected content
        before_metadata = self.screenshot_capture.load_metadata(before_path)
        after_metadata = self.screenshot_capture.load_metadata(after_path)
        
        expected_content = after_metadata.get('expected_content') or before_metadata.get('expected_content')
        
        if not expected_content:
            return {
                'error': 'No expected content specified',
                'suggestion': 'Provide expected_content when capturing screenshots'
            }
        
        # Validate both before and after screenshots
        results = {
            'expected_content': expected_content,
            'before_validation': self.content_validator.validate_content(before_path, expected_content),
            'after_validation': self.content_validator.validate_content(after_path, expected_content)
        }
        
        return results
    
    def list_captures(self) -> Dict[str, Any]:
        """
        List all captured screenshots with metadata.
        
        Returns:
            Dictionary with capture information
        """
        return self.screenshot_capture.list_captures()
    
    def clean_old_captures(self, keep_count: int = 20) -> int:
        """
        Clean old screenshot captures, keeping the most recent ones.
        
        Args:
            keep_count: Number of recent captures to keep
            
        Returns:
            Number of files deleted
        """
        return self.screenshot_capture.clean_old_captures(keep_count)
    
    def _save_analysis_results(self, analysis: Dict[str, Any]) -> None:
        """
        Save analysis results to JSON file.
        
        Args:
            analysis: Analysis results to save
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            results_file = self.output_dir / f"{timestamp}_analysis.json"
            
            with open(results_file, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            
            logger.info(f"Analysis results saved: {results_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save analysis results: {e}")
    
    def _print_analysis_summary(self, analysis: Dict[str, Any]) -> None:
        """
        Print a human-readable summary of analysis results.
        
        Args:
            analysis: Analysis results to summarize
        """
        print("\n" + "="*60)
        print("📊 UX ANALYSIS SUMMARY")
        print("="*60)
        
        results = analysis.get('results', {})
        
        # Basic info
        print(f"📸 Before: {analysis.get('before_file', 'N/A')}")
        print(f"📸 After:  {analysis.get('after_file', 'N/A')}")
        print(f"⏰ Analysis Time: {analysis.get('timestamp', 'N/A')}")
        
        # Response time
        response_time = results.get('response_time_ms', 0)
        if response_time > 0:
            print(f"⚡ Response Time: {response_time:.1f}ms", end="")
            if response_time < 300:
                print(" ✅ (Good)")
            elif response_time < 500:
                print(" ⚠️  (Acceptable)")
            else:
                print(" ❌ (Slow)")
        
        # UI Changes
        ui_changed = results.get('ui_changed', False)
        ui_change_score = results.get('ui_change_score', 0)
        print(f"🔄 UI Changed: {'Yes' if ui_changed else 'No'} ({ui_change_score:.1%})")
        
        # UX Assessment
        ux_assessment = results.get('ux_assessment', {})
        if ux_assessment:
            overall_score = ux_assessment.get('overall_score', 0)
            print(f"📊 Overall UX Score: {overall_score:.1%}", end="")
            if overall_score >= 0.8:
                print(" ✅ (Excellent)")
            elif overall_score >= 0.6:
                print(" ⚠️  (Good)")
            else:
                print(" ❌ (Needs Improvement)")
            
            # Issues and recommendations
            issues = ux_assessment.get('issues', [])
            if issues:
                print("\n🚨 Issues Found:")
                for i, issue in enumerate(issues, 1):
                    print(f"   {i}. {issue}")
            
            recommendations = ux_assessment.get('recommendations', [])
            if recommendations:
                print("\n💡 Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")
        
        # Content validation
        content_validation = results.get('content_validation', {})
        if content_validation:
            consensus = content_validation.get('consensus', {})
            content_matches = consensus.get('content_matches', False)
            confidence = consensus.get('confidence', 0)
            
            print(f"\n🤖 AI Content Validation:")
            print(f"   Expected Content: {content_validation.get('expected_content', 'N/A')}")
            print(f"   Content Matches: {'Yes' if content_matches else 'No'} ({confidence:.1%} confidence)")
            
            if consensus.get('description'):
                print(f"   AI Description: {consensus['description'][:100]}...")
        
        print("="*60)
        
        # Error handling
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
            if 'instructions' in results:
                print("\n📋 Instructions:")
                for instruction in results['instructions']:
                    print(f"   • {instruction}")
        
        print()  # Empty line for spacing 