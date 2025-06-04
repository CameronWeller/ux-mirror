"""
Visual analysis functionality for UX testing.

This module handles image comparison, change detection, and visual quality assessment.
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class VisualAnalyzer:
    """Handles visual analysis of screenshots."""
    
    def __init__(self, ui_change_threshold: float = 0.05):
        """
        Initialize visual analyzer.
        
        Args:
            ui_change_threshold: Threshold for detecting UI changes (0.0-1.0)
        """
        self.ui_change_threshold = ui_change_threshold
    
    def detect_ui_changes(self, before_img: np.ndarray, after_img: np.ndarray) -> float:
        """
        Detect changes between two screenshots.
        
        Args:
            before_img: Before screenshot as numpy array
            after_img: After screenshot as numpy array
            
        Returns:
            Change score (0.0 = no change, 1.0 = complete change)
        """
        try:
            # Ensure images are the same size
            if before_img.shape != after_img.shape:
                height, width = min(before_img.shape[0], after_img.shape[0]), min(before_img.shape[1], after_img.shape[1])
                before_img = cv2.resize(before_img, (width, height))
                after_img = cv2.resize(after_img, (width, height))
            
            # Convert to grayscale for comparison
            before_gray = cv2.cvtColor(before_img, cv2.COLOR_BGR2GRAY)
            after_gray = cv2.cvtColor(after_img, cv2.COLOR_BGR2GRAY)
            
            # Calculate structural similarity
            diff = cv2.absdiff(before_gray, after_gray)
            non_zero_count = np.count_nonzero(diff)
            total_pixels = diff.size
            
            change_score = non_zero_count / total_pixels
            
            logger.debug(f"UI change detection: {change_score:.3f} (threshold: {self.ui_change_threshold})")
            return change_score
            
        except Exception as e:
            logger.error(f"Error detecting UI changes: {e}")
            return 0.0
    
    def calculate_response_time(self, before_path: Path, after_path: Path) -> float:
        """
        Calculate response time between before and after screenshots.
        
        Args:
            before_path: Path to before screenshot
            after_path: Path to after screenshot
            
        Returns:
            Response time in milliseconds
        """
        try:
            # Extract timestamps from filenames
            before_timestamp = before_path.stem.split('_')[0]
            after_timestamp = after_path.stem.split('_')[0]
            
            # Convert to datetime
            before_time = datetime.strptime(before_timestamp, "%Y%m%d_%H%M%S_%f")
            after_time = datetime.strptime(after_timestamp, "%Y%m%d_%H%M%S_%f")
            
            # Calculate difference in milliseconds
            time_diff = (after_time - before_time).total_seconds() * 1000
            
            logger.debug(f"Response time calculated: {time_diff:.2f}ms")
            return time_diff
            
        except Exception as e:
            logger.error(f"Error calculating response time: {e}")
            return 0.0
    
    def check_visual_quality(self, img: np.ndarray) -> Dict[str, Any]:
        """
        Assess visual quality of a screenshot.
        
        Args:
            img: Screenshot as numpy array
            
        Returns:
            Dictionary with visual quality metrics
        """
        quality_metrics = {
            'blur_score': 0.0,
            'brightness': 0.0,
            'contrast': 0.0,
            'color_diversity': 0.0,
            'is_blurry': False,
            'is_too_dark': False,
            'is_too_bright': False
        }
        
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 1. Blur detection using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_metrics['blur_score'] = float(laplacian_var)
            quality_metrics['is_blurry'] = laplacian_var < 100.0
            
            # 2. Brightness assessment
            brightness = np.mean(gray)
            quality_metrics['brightness'] = float(brightness)
            quality_metrics['is_too_dark'] = brightness < 50
            quality_metrics['is_too_bright'] = brightness > 200
            
            # 3. Contrast assessment
            contrast = gray.std()
            quality_metrics['contrast'] = float(contrast)
            
            # 4. Color diversity (using histogram)
            hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            color_diversity = np.count_nonzero(hist) / hist.size
            quality_metrics['color_diversity'] = float(color_diversity)
            
            logger.debug(f"Visual quality metrics calculated: {quality_metrics}")
            
        except Exception as e:
            logger.error(f"Error checking visual quality: {e}")
        
        return quality_metrics
    
    def assess_ux_quality(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess overall UX quality based on analysis results.
        
        Args:
            analysis_results: Results from visual analysis
            
        Returns:
            UX quality assessment
        """
        assessment = {
            'overall_score': 0.0,
            'responsiveness': 'unknown',
            'visual_feedback': 'unknown',
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Score components
            responsiveness_score = 0.0
            visual_feedback_score = 0.0
            quality_score = 0.0
            
            # 1. Responsiveness assessment
            response_time = analysis_results.get('response_time_ms', 0)
            if response_time > 0:
                if response_time < 100:
                    responsiveness_score = 1.0
                    assessment['responsiveness'] = 'excellent'
                elif response_time < 300:
                    responsiveness_score = 0.8
                    assessment['responsiveness'] = 'good'
                elif response_time < 500:
                    responsiveness_score = 0.6
                    assessment['responsiveness'] = 'acceptable'
                elif response_time < 1000:
                    responsiveness_score = 0.4
                    assessment['responsiveness'] = 'slow'
                    assessment['issues'].append(f"Slow response time: {response_time:.0f}ms")
                else:
                    responsiveness_score = 0.2
                    assessment['responsiveness'] = 'very_slow'
                    assessment['issues'].append(f"Very slow response time: {response_time:.0f}ms")
            
            # 2. Visual feedback assessment
            ui_change_score = analysis_results.get('ui_change_score', 0)
            if ui_change_score >= self.ui_change_threshold:
                visual_feedback_score = 1.0
                assessment['visual_feedback'] = 'clear'
            elif ui_change_score >= self.ui_change_threshold * 0.5:
                visual_feedback_score = 0.6
                assessment['visual_feedback'] = 'subtle'
                assessment['recommendations'].append("Consider more prominent visual feedback")
            else:
                visual_feedback_score = 0.2
                assessment['visual_feedback'] = 'minimal'
                assessment['issues'].append("Little to no visual feedback detected")
            
            # 3. Visual quality assessment
            visual_quality = analysis_results.get('visual_quality', {})
            if visual_quality:
                quality_issues = 0
                
                if visual_quality.get('is_blurry', False):
                    assessment['issues'].append("Screenshot appears blurry")
                    quality_issues += 1
                
                if visual_quality.get('is_too_dark', False):
                    assessment['issues'].append("Screenshot is too dark")
                    quality_issues += 1
                
                if visual_quality.get('is_too_bright', False):
                    assessment['issues'].append("Screenshot is too bright")
                    quality_issues += 1
                
                if visual_quality.get('contrast', 0) < 30:
                    assessment['issues'].append("Low contrast detected")
                    quality_issues += 1
                
                quality_score = max(0.0, 1.0 - (quality_issues * 0.2))
            
            # Calculate overall score
            scores = [s for s in [responsiveness_score, visual_feedback_score, quality_score] if s > 0]
            if scores:
                assessment['overall_score'] = sum(scores) / len(scores)
            
            # Add recommendations based on score
            if assessment['overall_score'] < 0.6:
                assessment['recommendations'].append("Consider UX improvements for better user experience")
            
            logger.debug(f"UX quality assessment: {assessment}")
            
        except Exception as e:
            logger.error(f"Error assessing UX quality: {e}")
        
        return assessment
    
    def analyze_screenshots(self, before_path: Path, after_path: Path) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of before/after screenshots.
        
        Args:
            before_path: Path to before screenshot
            after_path: Path to after screenshot
            
        Returns:
            Complete analysis results
        """
        analysis = {
            'before_file': before_path.name,
            'after_file': after_path.name,
            'timestamp': datetime.now().isoformat(),
            'results': {}
        }
        
        try:
            # Load images
            before_img = cv2.imread(str(before_path))
            after_img = cv2.imread(str(after_path))
            
            if before_img is None or after_img is None:
                raise ValueError("Could not load screenshot images")
            
            # 1. UI Change Detection
            ui_change_score = self.detect_ui_changes(before_img, after_img)
            analysis['results']['ui_change_score'] = ui_change_score
            analysis['results']['ui_changed'] = ui_change_score >= self.ui_change_threshold
            
            # 2. Response Time Analysis
            response_time = self.calculate_response_time(before_path, after_path)
            analysis['results']['response_time_ms'] = response_time
            
            # 3. Visual Quality Assessment
            before_quality = self.check_visual_quality(before_img)
            after_quality = self.check_visual_quality(after_img)
            analysis['results']['visual_quality'] = {
                'before': before_quality,
                'after': after_quality
            }
            
            # 4. Overall UX Quality Assessment
            ux_assessment = self.assess_ux_quality(analysis['results'])
            analysis['results']['ux_assessment'] = ux_assessment
            
            logger.info(f"Screenshot analysis completed: {analysis['results']['ux_assessment']['overall_score']:.2f} score")
            
        except Exception as e:
            logger.error(f"Error analyzing screenshots: {e}")
            analysis['results']['error'] = str(e)
        
        return analysis
    
    def create_diff_image(self, before_path: Path, after_path: Path, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Create a difference image highlighting changes between screenshots.
        
        Args:
            before_path: Path to before screenshot
            after_path: Path to after screenshot
            output_path: Optional output path for difference image
            
        Returns:
            Path to difference image or None if failed
        """
        try:
            # Load images
            before_img = cv2.imread(str(before_path))
            after_img = cv2.imread(str(after_path))
            
            if before_img is None or after_img is None:
                return None
            
            # Ensure same size
            if before_img.shape != after_img.shape:
                height, width = min(before_img.shape[0], after_img.shape[0]), min(before_img.shape[1], after_img.shape[1])
                before_img = cv2.resize(before_img, (width, height))
                after_img = cv2.resize(after_img, (width, height))
            
            # Create difference image
            diff = cv2.absdiff(before_img, after_img)
            
            # Enhance differences for visibility
            diff_enhanced = cv2.convertScaleAbs(diff, alpha=3.0, beta=0)
            
            # Set output path if not provided
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = before_path.parent / f"{timestamp}_diff.png"
            
            # Save difference image
            cv2.imwrite(str(output_path), diff_enhanced)
            
            logger.info(f"Difference image created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating difference image: {e}")
            return None 