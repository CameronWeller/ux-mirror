#!/usr/bin/env python3
"""
Visual Analysis Pipeline Stages for UX Testing
=============================================

Refactored visual analysis using the new pipeline framework with improved
error handling, GPU acceleration, and configuration management.

Author: UX-MIRROR System
Version: 2.0.0
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime
import logging

from src.analysis.pipeline import AnalysisStage, PipelineContext, Pipeline, PipelineBuilder
from core.exceptions import AnalysisError, ValidationError
from core.error_handler import retry, RetryConfig, with_error_handling
from core.gpu_manager import get_gpu_manager
from core.configuration_manager import get_configuration_manager

logger = logging.getLogger(__name__)


class ImageLoadingStage(AnalysisStage):
    """Stage for loading and validating images"""
    
    def __init__(self):
        super().__init__("image_loading", cache_enabled=True, cache_ttl=3600)
        self.gpu_manager = get_gpu_manager()
    
    async def process(self, context: PipelineContext) -> Dict[str, Any]:
        """Load before and after images"""
        input_data = context.input_data
        
        if not isinstance(input_data, dict) or 'before_path' not in input_data or 'after_path' not in input_data:
            raise ValidationError(
                "Input must contain 'before_path' and 'after_path'",
                field='input_data'
            )
        
        before_path = Path(input_data['before_path'])
        after_path = Path(input_data['after_path'])
        
        # Load images with retry
        @retry(RetryConfig(max_attempts=3))
        def load_image(path: Path) -> np.ndarray:
            img = cv2.imread(str(path))
            if img is None:
                raise AnalysisError(f"Failed to load image: {path}")
            return img
        
        before_img = load_image(before_path)
        after_img = load_image(after_path)
        
        # Store metadata
        context.add_metadata('image_shape_before', before_img.shape)
        context.add_metadata('image_shape_after', after_img.shape)
        
        return {
            'before_img': before_img,
            'after_img': after_img,
            'before_path': before_path,
            'after_path': after_path
        }
    
    def validate_input(self, context: PipelineContext) -> bool:
        """Validate input paths exist"""
        input_data = context.input_data
        
        if not isinstance(input_data, dict):
            raise ValidationError("Input must be a dictionary")
        
        for key in ['before_path', 'after_path']:
            if key not in input_data:
                raise ValidationError(f"Missing required field: {key}")
            
            path = Path(input_data[key])
            if not path.exists():
                raise ValidationError(f"File not found: {path}", field=key)
        
        return True


class ImagePreprocessingStage(AnalysisStage):
    """Stage for preprocessing images (resize, normalize, etc.)"""
    
    def __init__(self):
        super().__init__("image_preprocessing", cache_enabled=True)
        self.gpu_manager = get_gpu_manager()
    
    async def process(self, context: PipelineContext) -> Dict[str, Any]:
        """Preprocess images for analysis"""
        images = context.get_previous_result("image_loading")
        if not images:
            raise ValidationError("No image data available from loading stage")
        
        before_img = images['before_img']
        after_img = images['after_img']
        
        # Ensure images are the same size
        if before_img.shape != after_img.shape:
            height = min(before_img.shape[0], after_img.shape[0])
            width = min(before_img.shape[1], after_img.shape[1])
            before_img = cv2.resize(before_img, (width, height))
            after_img = cv2.resize(after_img, (width, height))
            
            context.add_metadata('images_resized', True)
            context.add_metadata('final_shape', (height, width))
        
        # Convert to grayscale versions for certain analyses
        before_gray = cv2.cvtColor(before_img, cv2.COLOR_BGR2GRAY)
        after_gray = cv2.cvtColor(after_img, cv2.COLOR_BGR2GRAY)
        
        # Move to GPU if available
        if self.gpu_manager.device and self.gpu_manager.device.backend != 'cpu':
            # Create GPU tensors for faster processing
            before_tensor = self.gpu_manager.create_tensor(before_img)
            after_tensor = self.gpu_manager.create_tensor(after_img)
            context.add_metadata('gpu_accelerated', True)
        else:
            before_tensor = before_img
            after_tensor = after_img
            context.add_metadata('gpu_accelerated', False)
        
        return {
            'before_img': before_img,
            'after_img': after_img,
            'before_gray': before_gray,
            'after_gray': after_gray,
            'before_tensor': before_tensor,
            'after_tensor': after_tensor
        }


class UIChangeDetectionStage(AnalysisStage):
    """Stage for detecting UI changes between screenshots"""
    
    def __init__(self, threshold: float = 0.05):
        super().__init__("ui_change_detection")
        self.threshold = self.config.get('threshold', threshold)
    
    @with_error_handling("ui_change_detection")
    async def process(self, context: PipelineContext) -> Dict[str, Any]:
        """Detect UI changes between images"""
        images = context.get_previous_result("image_preprocessing")
        if not images:
            raise ValidationError("No preprocessed image data available")
        
        before_gray = images['before_gray']
        after_gray = images['after_gray']
        
        # Calculate difference
        diff = cv2.absdiff(before_gray, after_gray)
        non_zero_count = np.count_nonzero(diff)
        total_pixels = diff.size
        
        change_score = non_zero_count / total_pixels
        
        # Create difference visualization
        diff_enhanced = cv2.convertScaleAbs(diff, alpha=3.0, beta=0)
        
        # Identify changed regions
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        changed_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            if area > 100:  # Filter out noise
                changed_regions.append({
                    'x': int(x), 'y': int(y),
                    'width': int(w), 'height': int(h),
                    'area': float(area)
                })
        
        return {
            'change_score': float(change_score),
            'ui_changed': change_score >= self.threshold,
            'changed_regions': changed_regions,
            'diff_image': diff_enhanced,
            'threshold': self.threshold
        }


class ResponseTimeAnalysisStage(AnalysisStage):
    """Stage for analyzing response time between screenshots"""
    
    def __init__(self):
        super().__init__("response_time_analysis", cache_enabled=False)
    
    async def process(self, context: PipelineContext) -> Dict[str, Any]:
        """Calculate response time from timestamps"""
        images = context.get_previous_result("image_loading")
        if not images:
            raise ValidationError("No image loading data available")
        
        before_path = images['before_path']
        after_path = images['after_path']
        
        try:
            # Extract timestamps from filenames
            before_timestamp = before_path.stem.split('_')[0]
            after_timestamp = after_path.stem.split('_')[0]
            
            # Try multiple timestamp formats
            formats = ["%Y%m%d_%H%M%S_%f", "%Y%m%d_%H%M%S", "%Y%m%d%H%M%S"]
            
            before_time = None
            after_time = None
            
            for fmt in formats:
                try:
                    before_time = datetime.strptime(before_timestamp, fmt)
                    after_time = datetime.strptime(after_timestamp, fmt)
                    break
                except ValueError:
                    continue
            
            if not before_time or not after_time:
                raise ValueError("Could not parse timestamps from filenames")
            
            # Calculate difference in milliseconds
            time_diff = (after_time - before_time).total_seconds() * 1000
            
            # Categorize response time
            if time_diff < 100:
                category = 'excellent'
            elif time_diff < 300:
                category = 'good'
            elif time_diff < 500:
                category = 'acceptable'
            elif time_diff < 1000:
                category = 'slow'
            else:
                category = 'very_slow'
            
            return {
                'response_time_ms': float(time_diff),
                'response_category': category,
                'before_timestamp': before_time.isoformat(),
                'after_timestamp': after_time.isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Could not calculate response time: {e}")
            return {
                'response_time_ms': None,
                'response_category': 'unknown',
                'error': str(e)
            }


class VisualQualityAssessmentStage(AnalysisStage):
    """Stage for assessing visual quality of screenshots"""
    
    def __init__(self):
        super().__init__("visual_quality_assessment")
    
    async def process(self, context: PipelineContext) -> Dict[str, Any]:
        """Assess visual quality metrics"""
        images = context.get_previous_result("image_preprocessing")
        if not images:
            raise ValidationError("No preprocessed image data available")
        
        results = {}
        
        for img_type in ['before', 'after']:
            img = images[f'{img_type}_img']
            gray = images[f'{img_type}_gray']
            
            # Blur detection using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            is_blurry = laplacian_var < 100.0
            
            # Brightness assessment
            brightness = np.mean(gray)
            is_too_dark = brightness < 50
            is_too_bright = brightness > 200
            
            # Contrast assessment
            contrast = gray.std()
            
            # Color diversity using histogram
            hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            color_diversity = np.count_nonzero(hist) / hist.size
            
            results[img_type] = {
                'blur_score': float(laplacian_var),
                'brightness': float(brightness),
                'contrast': float(contrast),
                'color_diversity': float(color_diversity),
                'is_blurry': bool(is_blurry),
                'is_too_dark': bool(is_too_dark),
                'is_too_bright': bool(is_too_bright),
                'quality_issues': []
            }
            
            # Compile quality issues
            if is_blurry:
                results[img_type]['quality_issues'].append('blurry')
            if is_too_dark:
                results[img_type]['quality_issues'].append('too_dark')
            if is_too_bright:
                results[img_type]['quality_issues'].append('too_bright')
            if contrast < 30:
                results[img_type]['quality_issues'].append('low_contrast')
        
        return results


class UXQualityAssessmentStage(AnalysisStage):
    """Stage for overall UX quality assessment"""
    
    def __init__(self):
        super().__init__("ux_quality_assessment", cache_enabled=False)
    
    async def process(self, context: PipelineContext) -> Dict[str, Any]:
        """Assess overall UX quality based on all analysis results"""
        # Gather results from previous stages
        ui_changes = context.get_previous_result("ui_change_detection") or {}
        response_time = context.get_previous_result("response_time_analysis") or {}
        visual_quality = context.get_previous_result("visual_quality_assessment") or {}
        
        assessment = {
            'overall_score': 0.0,
            'responsiveness': response_time.get('response_category', 'unknown'),
            'visual_feedback': 'unknown',
            'issues': [],
            'recommendations': [],
            'component_scores': {}
        }
        
        # Score components
        scores = []
        
        # 1. Responsiveness score
        responsiveness_map = {
            'excellent': 1.0,
            'good': 0.8,
            'acceptable': 0.6,
            'slow': 0.4,
            'very_slow': 0.2,
            'unknown': 0.5
        }
        responsiveness_score = responsiveness_map.get(assessment['responsiveness'], 0.5)
        scores.append(responsiveness_score)
        assessment['component_scores']['responsiveness'] = responsiveness_score
        
        # Add issues for slow response
        if assessment['responsiveness'] in ['slow', 'very_slow']:
            time_ms = response_time.get('response_time_ms', 0)
            assessment['issues'].append(f"Slow response time: {time_ms:.0f}ms")
            assessment['recommendations'].append("Optimize UI response time to under 300ms")
        
        # 2. Visual feedback score
        change_score = ui_changes.get('change_score', 0)
        threshold = ui_changes.get('threshold', 0.05)
        
        if change_score >= threshold:
            visual_feedback_score = 1.0
            assessment['visual_feedback'] = 'clear'
        elif change_score >= threshold * 0.5:
            visual_feedback_score = 0.6
            assessment['visual_feedback'] = 'subtle'
            assessment['recommendations'].append("Consider more prominent visual feedback")
        else:
            visual_feedback_score = 0.2
            assessment['visual_feedback'] = 'minimal'
            assessment['issues'].append("Little to no visual feedback detected")
            assessment['recommendations'].append("Add clear visual feedback for user interactions")
        
        scores.append(visual_feedback_score)
        assessment['component_scores']['visual_feedback'] = visual_feedback_score
        
        # 3. Visual quality score
        quality_scores = []
        for img_type in ['before', 'after']:
            if img_type in visual_quality:
                quality_data = visual_quality[img_type]
                issues_count = len(quality_data.get('quality_issues', []))
                quality_score = max(0.0, 1.0 - (issues_count * 0.25))
                quality_scores.append(quality_score)
                
                # Report quality issues
                for issue in quality_data.get('quality_issues', []):
                    assessment['issues'].append(f"{img_type.capitalize()} image: {issue}")
        
        if quality_scores:
            avg_quality_score = sum(quality_scores) / len(quality_scores)
            scores.append(avg_quality_score)
            assessment['component_scores']['visual_quality'] = avg_quality_score
        
        # Calculate overall score
        if scores:
            assessment['overall_score'] = sum(scores) / len(scores)
        
        # Add general recommendations based on overall score
        if assessment['overall_score'] < 0.6:
            assessment['recommendations'].append("Consider comprehensive UX improvements")
        elif assessment['overall_score'] < 0.8:
            assessment['recommendations'].append("Minor UX improvements recommended")
        
        # Add metadata
        assessment['analysis_timestamp'] = datetime.now().isoformat()
        assessment['changed_regions_count'] = len(ui_changes.get('changed_regions', []))
        
        return assessment


# Factory function to create the visual analysis pipeline
def create_visual_analysis_pipeline(
    ui_change_threshold: float = 0.05,
    enable_gpu: bool = True,
    progress_callback: Optional[callable] = None
) -> Pipeline:
    """
    Create a configured visual analysis pipeline.
    
    Args:
        ui_change_threshold: Threshold for UI change detection
        enable_gpu: Whether to enable GPU acceleration
        progress_callback: Optional callback for progress updates
        
    Returns:
        Configured Pipeline instance
    """
    builder = PipelineBuilder("visual_analysis_pipeline")
    
    # Add stages in order
    builder.add_stage(ImageLoadingStage())
    builder.add_stage(ImagePreprocessingStage())
    builder.add_stage(UIChangeDetectionStage(threshold=ui_change_threshold))
    builder.add_stage(ResponseTimeAnalysisStage())
    builder.add_stage(VisualQualityAssessmentStage())
    builder.add_stage(UXQualityAssessmentStage())
    
    # Configure execution
    builder.with_sequential_execution()  # Stages depend on each other
    builder.stop_on_error()  # Stop if any stage fails
    
    # Add progress callback if provided
    if progress_callback:
        builder.with_progress_callback(progress_callback)
    
    return builder.build()


# Example usage
async def analyze_screenshots_with_pipeline(
    before_path: str,
    after_path: str,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze screenshots using the pipeline framework.
    
    Args:
        before_path: Path to before screenshot
        after_path: Path to after screenshot
        config: Optional configuration overrides
        
    Returns:
        Analysis results
    """
    # Create pipeline
    pipeline = create_visual_analysis_pipeline(
        ui_change_threshold=config.get('ui_change_threshold', 0.05) if config else 0.05,
        progress_callback=lambda p: logger.info(f"Analysis progress: {p['percentage']:.1f}%")
    )
    
    # Execute pipeline
    input_data = {
        'before_path': before_path,
        'after_path': after_path
    }
    
    context = await pipeline.execute(input_data, metadata=config)
    
    # Extract final results
    results = {
        'ux_assessment': context.get_previous_result('ux_quality_assessment'),
        'ui_changes': context.get_previous_result('ui_change_detection'),
        'response_time': context.get_previous_result('response_time_analysis'),
        'visual_quality': context.get_previous_result('visual_quality_assessment'),
        'metadata': context.metadata
    }
    
    return results