#!/usr/bin/env python3
"""
UX-MIRROR Visual Analysis Agent
===============================

Specialized agent for real-time computer vision analysis, UI change detection,
and visual quality assessment. Works with GPU acceleration when available.

Author: UX-MIRROR System
Version: 1.0.0
"""

import asyncio
import logging
import json
import time
import numpy as np
import cv2
from PIL import Image, ImageGrab
import base64
from io import BytesIO
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import websockets

# Import screenshot handler
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from capture.screenshot_handler import get_screenshot_handler

# Make PyTorch import optional
try:
    import torch
    import torchvision.transforms as transforms
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    transforms = None
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available - using OpenCV fallback")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class VisualAnalysisResult:
    """Result of visual analysis"""
    timestamp: datetime
    change_score: float
    quality_score: float
    ui_elements_detected: int
    response_time: Optional[float]
    attention_areas: List[Tuple[int, int, int, int]]  # Bounding boxes (x, y, w, h)
    accessibility_issues: List[str]
    performance_impact: str
    recommendations: List[str]

@dataclass
class UIElement:
    """Detected UI element"""
    element_type: str  # 'button', 'input', 'text', 'image', 'menu'
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float
    text_content: Optional[str]
    color_analysis: Dict[str, Any]
    accessibility_score: float

class GPUAcceleratedVision:
    """GPU-accelerated computer vision processing"""
    
    def __init__(self, device=None):
        if TORCH_AVAILABLE and torch.cuda.is_available():
            self.device = torch.device("cuda")
            self.use_gpu = True
            self.ui_detector = self._init_ui_detection_model()
            self.quality_assessor = self._init_quality_model()
            self.change_detector = self._init_change_detection_model()
            logger.info("Using GPU-accelerated visual analysis")
        else:
            self.device = None
            self.use_gpu = False
            logger.info("Using OpenCV fallback for visual analysis")
        
        # Image preprocessing pipeline
        if TORCH_AVAILABLE:
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
    
    def _init_ui_detection_model(self):
        """Initialize UI element detection model"""
        if not self.use_gpu:
            return None
        # Simple CNN for UI element classification
        model = torch.nn.Sequential(
            torch.nn.Conv2d(3, 32, kernel_size=3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
            torch.nn.Conv2d(32, 64, kernel_size=3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
            torch.nn.Conv2d(64, 128, kernel_size=3, padding=1),
            torch.nn.ReLU(),
            torch.nn.AdaptiveAvgPool2d((7, 7)),
            torch.nn.Flatten(),
            torch.nn.Linear(128 * 7 * 7, 256),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.5),
            torch.nn.Linear(256, 6)  # 6 UI element types
        ).to(self.device)
        return model
    
    def _init_quality_model(self):
        """Initialize visual quality assessment model"""
        if not self.use_gpu:
            return None
        model = torch.nn.Sequential(
            torch.nn.Conv2d(3, 64, kernel_size=5, padding=2),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
            torch.nn.Conv2d(64, 128, kernel_size=3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
            torch.nn.AdaptiveAvgPool2d((1, 1)),
            torch.nn.Flatten(),
            torch.nn.Linear(128, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, 1),
            torch.nn.Sigmoid()
        ).to(self.device)
        return model
    
    def _init_change_detection_model(self):
        """Initialize change detection model"""
        if not self.use_gpu:
            return None
        model = torch.nn.Sequential(
            torch.nn.Conv2d(6, 64, kernel_size=3, padding=1),  # 6 channels for before/after
            torch.nn.ReLU(),
            torch.nn.Conv2d(64, 128, kernel_size=3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
            torch.nn.Conv2d(128, 256, kernel_size=3, padding=1),
            torch.nn.ReLU(),
            torch.nn.AdaptiveAvgPool2d((1, 1)),
            torch.nn.Flatten(),
            torch.nn.Linear(256, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 1),
            torch.nn.Sigmoid()
        ).to(self.device)
        return model
    
    def detect_ui_elements(self, image: np.ndarray) -> List[UIElement]:
        """Detect UI elements in screenshot"""
        if self.use_gpu and self.ui_detector is not None:
            return self._gpu_detect_ui_elements(image)
        else:
            return self._opencv_detect_ui_elements(image)
    
    def _gpu_detect_ui_elements(self, image: np.ndarray) -> List[UIElement]:
        """GPU-based UI element detection"""
        # Convert to PIL and preprocess
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        tensor_image = self.transform(pil_image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            predictions = self.ui_detector(tensor_image)
            
        # Convert predictions to UI elements
        # This is a simplified version - in practice you'd use object detection
        elements = []
        height, width = image.shape[:2]
        
        # Generate some mock detections based on image analysis
        # In real implementation, this would be proper object detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i, contour in enumerate(contours[:10]):  # Limit to top 10
            x, y, w, h = cv2.boundingRect(contour)
            if w > 20 and h > 20:  # Filter small elements
                confidence = min(1.0, cv2.contourArea(contour) / (w * h))
                elements.append(UIElement(
                    element_type="unknown",
                    bbox=(x, y, w, h),
                    confidence=confidence,
                    text_content=None,
                    color_analysis=self._analyze_colors(image[y:y+h, x:x+w]),
                    accessibility_score=0.5
                ))
        
        return elements
    
    def _opencv_detect_ui_elements(self, image: np.ndarray) -> List[UIElement]:
        """OpenCV-based UI element detection"""
        elements = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection for UI elements
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            
            # Filter elements by size and area
            if w > 30 and h > 20 and area > 600:
                confidence = min(1.0, area / (w * h))
                
                # Simple element type classification
                aspect_ratio = w / h
                if aspect_ratio > 3 and h < 50:
                    element_type = "button"
                elif aspect_ratio < 0.5 and w < 100:
                    element_type = "input"
                elif area > 5000:
                    element_type = "container"
                else:
                    element_type = "element"
                
                elements.append(UIElement(
                    element_type=element_type,
                    bbox=(x, y, w, h),
                    confidence=confidence,
                    text_content=None,
                    color_analysis=self._analyze_colors(image[y:y+h, x:x+w]),
                    accessibility_score=self._assess_accessibility(image[y:y+h, x:x+w])
                ))
        
        return elements
    
    def _analyze_colors(self, region: np.ndarray) -> Dict[str, Any]:
        """Analyze color properties of a region"""
        if region.size == 0:
            return {"dominant_color": [0, 0, 0], "contrast_ratio": 0.0}
            
        # Calculate dominant color
        pixels = region.reshape(-1, 3)
        dominant_color = np.mean(pixels, axis=0).astype(int).tolist()
        
        # Simple contrast estimation
        gray_region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        contrast = np.std(gray_region) / 255.0
        
        return {
            "dominant_color": dominant_color,
            "contrast_ratio": contrast,
            "brightness": np.mean(gray_region) / 255.0
        }
    
    def _assess_accessibility(self, region: np.ndarray) -> float:
        """Assess accessibility of a UI region"""
        if region.size == 0:
            return 0.0
            
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        
        # Basic accessibility metrics
        contrast = np.std(gray) / 255.0
        brightness = np.mean(gray) / 255.0
        
        # Simple accessibility score
        score = min(1.0, contrast + (0.5 - abs(brightness - 0.5)) * 2)
        return score
    
    def detect_changes(self, before_img: np.ndarray, after_img: np.ndarray) -> Tuple[float, np.ndarray]:
        """Detect changes between before and after images"""
        if self.use_gpu and self.change_detector is not None:
            return self._gpu_detect_changes(before_img, after_img)
        else:
            return self._opencv_detect_changes(before_img, after_img)
    
    def _gpu_detect_changes(self, before_img: np.ndarray, after_img: np.ndarray) -> Tuple[float, np.ndarray]:
        """GPU-based change detection"""
        # Resize images to same size
        height = min(before_img.shape[0], after_img.shape[0])
        width = min(before_img.shape[1], after_img.shape[1])
        
        before_resized = cv2.resize(before_img, (width, height))
        after_resized = cv2.resize(after_img, (width, height))
        
        # Convert to tensors
        before_tensor = torch.tensor(before_resized).permute(2, 0, 1).float() / 255.0
        after_tensor = torch.tensor(after_resized).permute(2, 0, 1).float() / 255.0
        
        # Concatenate for change detection model
        combined = torch.cat([before_tensor, after_tensor], dim=0).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            change_score = self.change_detector(combined).item()
        
        # Generate difference map
        diff = cv2.absdiff(before_resized, after_resized)
        
        return change_score, diff
    
    def _opencv_detect_changes(self, before_img: np.ndarray, after_img: np.ndarray) -> Tuple[float, np.ndarray]:
        """OpenCV-based change detection"""
        # Resize to same dimensions
        if before_img.shape != after_img.shape:
            height = min(before_img.shape[0], after_img.shape[0])
            width = min(before_img.shape[1], after_img.shape[1])
            before_img = cv2.resize(before_img, (width, height))
            after_img = cv2.resize(after_img, (width, height))
        
        # Calculate difference
        diff = cv2.absdiff(before_img, after_img)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Calculate change score
        total_pixels = gray_diff.shape[0] * gray_diff.shape[1]
        changed_pixels = np.count_nonzero(gray_diff > 30)  # Threshold for significant change
        change_score = changed_pixels / total_pixels
        
        return change_score, diff
    
    def assess_visual_quality(self, image: np.ndarray) -> float:
        """Assess overall visual quality of screenshot"""
        if self.use_gpu and self.quality_assessor is not None:
            return self._gpu_assess_quality(image)
        else:
            return self._opencv_assess_quality(image)
    
    def _gpu_assess_quality(self, image: np.ndarray) -> float:
        """GPU-based quality assessment"""
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        tensor_image = self.transform(pil_image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            quality_score = self.quality_assessor(tensor_image).item()
        
        return quality_score
    
    def _opencv_assess_quality(self, image: np.ndarray) -> float:
        """OpenCV-based quality assessment"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Multiple quality metrics
        # 1. Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(1.0, laplacian_var / 1000.0)
        
        # 2. Contrast
        contrast_score = np.std(gray) / 255.0
        
        # 3. Brightness distribution
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_norm = hist / hist.sum()
        entropy = -np.sum(hist_norm * np.log2(hist_norm + 1e-10))
        brightness_score = min(1.0, entropy / 8.0)
        
        # Combined quality score
        quality_score = (sharpness_score * 0.4 + contrast_score * 0.3 + brightness_score * 0.3)
        return min(1.0, quality_score)

class VisualAnalysisAgent:
    """
    Visual Analysis Agent for real-time computer vision processing.
    
    Capabilities:
    - Real-time screenshot analysis
    - UI element detection and tracking
    - Visual change detection
    - Quality assessment
    - Accessibility analysis
    """
    
    def __init__(self, orchestrator_host: str = "localhost", orchestrator_port: int = 8765):
        self.orchestrator_host = orchestrator_host
        self.orchestrator_port = orchestrator_port
        self.running = False
        self.websocket = None
        
        # Initialize GPU-accelerated vision
        self.vision_processor = GPUAcceleratedVision()
        
        # Initialize screenshot handler
        self.screenshot_handler = get_screenshot_handler()
        
        # Analysis state (keeping for backward compatibility)
        self.last_screenshot = None
        self.last_analysis = None
        self.baseline_screenshot = None
        
        # Performance tracking
        self.analysis_times = []
        self.total_analyses = 0
        
        # Continuous monitoring
        self.monitoring_interval = 5.0  # seconds
        self.auto_monitor = False
        
        logger.info("Visual Analysis Agent initialized with ScreenshotHandler")
    
    async def start(self):
        """Start the Visual Analysis Agent"""
        self.running = True
        logger.info("Starting Visual Analysis Agent...")
        
        # Connect to orchestrator
        await self._connect_to_orchestrator()
        
        # Start concurrent tasks
        tasks = [
            self._handle_orchestrator_messages(),
            self._continuous_monitoring(),
            self._send_heartbeat()
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Agent error: {e}")
        finally:
            self.running = False
    
    async def _connect_to_orchestrator(self):
        """Connect to the orchestrator via WebSocket"""
        try:
            self.websocket = await websockets.connect(
                f"ws://{self.orchestrator_host}:{self.orchestrator_port}"
            )
            
            # Send registration message
            await self._send_to_orchestrator({
                "type": "agent_registration",
                "agent_id": "visual_analysis_agent",
                "capabilities": [
                    "screenshot_analysis",
                    "ui_element_detection", 
                    "change_detection",
                    "quality_assessment",
                    "accessibility_analysis"
                ],
                "status": "online"
            })
            
            logger.info("Connected to orchestrator")
            
        except Exception as e:
            logger.error(f"Failed to connect to orchestrator: {e}")
            # Continue running in standalone mode
            self.websocket = None
    
    async def _handle_orchestrator_messages(self):
        """Handle messages from orchestrator"""
        if not self.websocket:
            return
            
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self._process_orchestrator_command(data)
        except Exception as e:
            logger.error(f"Error handling orchestrator messages: {e}")
    
    async def _process_orchestrator_command(self, command: Dict[str, Any]):
        """Process commands from orchestrator"""
        command_type = command.get("type")
        
        if command_type == "analyze_screenshot":
            await self._analyze_specific_screenshot(command.get("screenshot_path"))
        elif command_type == "start_monitoring":
            self.auto_monitor = True
            self.monitoring_interval = command.get("interval", 5.0)
        elif command_type == "stop_monitoring":
            self.auto_monitor = False
        elif command_type == "set_baseline":
            await self._set_baseline_screenshot()
        elif command_type == "compare_with_baseline":
            await self._compare_with_baseline()
        else:
            logger.warning(f"Unknown command type: {command_type}")
    
    async def _continuous_monitoring(self):
        """Continuously monitor screen for changes"""
        while self.running:
            if self.auto_monitor:
                try:
                    await self._capture_and_analyze()
                except Exception as e:
                    logger.error(f"Error in continuous monitoring: {e}")
            
            await asyncio.sleep(self.monitoring_interval)
    
    async def _capture_and_analyze(self) -> VisualAnalysisResult:
        """Capture screenshot and perform full analysis"""
        start_time = time.time()
        
        # Capture screenshot using screenshot handler
        screenshot_bgr = self.screenshot_handler.capture_screenshot()
        if screenshot_bgr is None:
            logger.error("Failed to capture screenshot")
            return None
        
        # Perform analysis
        analysis_result = await self._analyze_screenshot(screenshot_bgr)
        
        # Track performance
        analysis_time = time.time() - start_time
        self.analysis_times.append(analysis_time)
        self.total_analyses += 1
        
        # Keep only recent analysis times
        if len(self.analysis_times) > 100:
            self.analysis_times.pop(0)
        
        # Store for comparison
        self.last_screenshot = screenshot_bgr
        self.last_analysis = analysis_result
        
        # Send results to orchestrator
        if self.websocket:
            await self._send_to_orchestrator({
                "type": "visual_analysis_result",
                "agent_id": "visual_analysis_agent",
                "analysis": {
                    "timestamp": analysis_result.timestamp.isoformat(),
                    "change_score": analysis_result.change_score,
                    "quality_score": analysis_result.quality_score,
                    "ui_elements_detected": analysis_result.ui_elements_detected,
                    "response_time": analysis_result.response_time,
                    "accessibility_issues": analysis_result.accessibility_issues,
                    "performance_impact": analysis_result.performance_impact,
                    "recommendations": analysis_result.recommendations,
                    "analysis_time": analysis_time
                }
            })
        
        return analysis_result
    
    async def _analyze_screenshot(self, image: np.ndarray, previous_image: np.ndarray = None) -> VisualAnalysisResult:
        """Perform comprehensive analysis of a screenshot"""
        timestamp = datetime.now()
        
        # UI Element Detection
        ui_elements = self.vision_processor.detect_ui_elements(image)
        
        # Visual Quality Assessment
        quality_score = self.vision_processor.assess_visual_quality(image)
        
        # Change Detection (if previous image available)
        change_score = 0.0
        response_time = None
        if previous_image is not None:
            change_score, diff_image = self.vision_processor.detect_changes(previous_image, image)
            # Estimate response time based on change detection
            if change_score > 0.1:
                response_time = 1.0  # Mock response time
        
        # Accessibility Analysis
        accessibility_issues = self._analyze_accessibility(ui_elements)
        
        # Performance Impact Assessment
        performance_impact = self._assess_performance_impact(len(ui_elements), quality_score)
        
        # Generate Recommendations
        recommendations = self._generate_recommendations(ui_elements, quality_score, accessibility_issues)
        
        # Extract attention areas from UI elements
        attention_areas = [(elem.bbox[0], elem.bbox[1], elem.bbox[2], elem.bbox[3]) 
                          for elem in ui_elements if elem.confidence > 0.7]
        
        return VisualAnalysisResult(
            timestamp=timestamp,
            change_score=change_score,
            quality_score=quality_score,
            ui_elements_detected=len(ui_elements),
            response_time=response_time,
            attention_areas=attention_areas,
            accessibility_issues=accessibility_issues,
            performance_impact=performance_impact,
            recommendations=recommendations
        )
    
    def _analyze_accessibility(self, ui_elements: List[UIElement]) -> List[str]:
        """Analyze accessibility issues"""
        issues = []
        
        for element in ui_elements:
            if element.accessibility_score < 0.5:
                if element.color_analysis["contrast_ratio"] < 0.3:
                    issues.append(f"Low contrast in {element.element_type} element")
                
                if element.bbox[2] < 44 or element.bbox[3] < 44:  # Minimum touch target size
                    issues.append(f"Small touch target: {element.element_type}")
        
        return issues
    
    def _assess_performance_impact(self, element_count: int, quality_score: float) -> str:
        """Assess performance impact based on UI complexity"""
        if element_count > 50:
            return "high"
        elif element_count > 25 or quality_score < 0.6:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, ui_elements: List[UIElement], 
                                quality_score: float, accessibility_issues: List[str]) -> List[str]:
        """Generate UX improvement recommendations"""
        recommendations = []
        
        if quality_score < 0.7:
            recommendations.append("Consider improving visual clarity and contrast")
        
        if len(accessibility_issues) > 0:
            recommendations.append("Address accessibility issues for better inclusivity")
        
        if len(ui_elements) > 30:
            recommendations.append("Consider simplifying the interface to reduce cognitive load")
        
        # Check for overlapping elements
        overlapping = self._detect_overlapping_elements(ui_elements)
        if overlapping > 0:
            recommendations.append("Fix overlapping UI elements for better usability")
        
        return recommendations
    
    def _detect_overlapping_elements(self, ui_elements: List[UIElement]) -> int:
        """Detect overlapping UI elements"""
        overlapping_count = 0
        
        for i, elem1 in enumerate(ui_elements):
            for elem2 in ui_elements[i+1:]:
                if self._boxes_overlap(elem1.bbox, elem2.bbox):
                    overlapping_count += 1
        
        return overlapping_count
    
    def _boxes_overlap(self, box1: Tuple[int, int, int, int], 
                      box2: Tuple[int, int, int, int]) -> bool:
        """Check if two bounding boxes overlap"""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)
    
    async def _set_baseline_screenshot(self):
        """Set current screenshot as baseline for comparisons"""
        success = self.screenshot_handler.set_baseline()
        if success:
            self.baseline_screenshot = self.screenshot_handler.get_baseline()
            logger.info("Baseline screenshot set using ScreenshotHandler")
        else:
            logger.error("Failed to set baseline screenshot")
    
    async def _compare_with_baseline(self):
        """Compare current screenshot with baseline"""
        try:
            comparison_result = self.screenshot_handler.compare_with_baseline()
            if comparison_result is None:
                logger.warning("Baseline comparison failed")
                return
            
            await self._send_to_orchestrator({
                "type": "baseline_comparison",
                "agent_id": "visual_analysis_agent",
                "change_score": comparison_result["change_percentage"] / 100.0,
                "change_percentage": comparison_result["change_percentage"],
                "has_significant_change": comparison_result["has_significant_change"],
                "mse": comparison_result["mse"],
                "timestamp": comparison_result["timestamp"]
            })
            
            logger.info(f"Baseline comparison completed: {comparison_result['change_percentage']:.2f}% change")
            
        except Exception as e:
            logger.error(f"Error during baseline comparison: {e}")
    
    async def _analyze_specific_screenshot(self, screenshot_path: str):
        """Analyze a specific screenshot file"""
        try:
            image = cv2.imread(screenshot_path)
            if image is None:
                logger.error(f"Could not load screenshot: {screenshot_path}")
                return
            
            analysis_result = await self._analyze_screenshot(image)
            
            if self.websocket:
                await self._send_to_orchestrator({
                    "type": "screenshot_analysis_complete",
                    "agent_id": "visual_analysis_agent",
                    "screenshot_path": screenshot_path,
                    "analysis": {
                        "timestamp": analysis_result.timestamp.isoformat(),
                        "change_score": analysis_result.change_score,
                        "quality_score": analysis_result.quality_score,
                        "ui_elements_detected": analysis_result.ui_elements_detected,
                        "accessibility_issues": analysis_result.accessibility_issues,
                        "recommendations": analysis_result.recommendations
                    }
                })
        except Exception as e:
            logger.error(f"Error analyzing screenshot {screenshot_path}: {e}")
    
    async def _send_heartbeat(self):
        """Send periodic heartbeat to orchestrator"""
        while self.running:
            if self.websocket:
                try:
                    avg_analysis_time = np.mean(self.analysis_times) if self.analysis_times else 0
                    
                    await self._send_to_orchestrator({
                        "type": "agent_heartbeat",
                        "agent_id": "visual_analysis_agent",
                        "status": "online",
                        "performance": {
                            "total_analyses": self.total_analyses,
                            "avg_analysis_time": avg_analysis_time,
                            "gpu_enabled": self.vision_processor.use_gpu,
                            "monitoring_active": self.auto_monitor
                        },
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error sending heartbeat: {e}")
            
            await asyncio.sleep(30)  # Heartbeat every 30 seconds
    
    async def _send_to_orchestrator(self, message: Dict[str, Any]):
        """Send message to orchestrator"""
        if self.websocket is not None:
            try:
                # Check if websocket is still open before sending
                if self.websocket.closed:
                    logger.warning("WebSocket connection is closed, cannot send message")
                    self.websocket = None
                    return
                
                await self.websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed during send")
                self.websocket = None
            except Exception as e:
                logger.error(f"Error sending message to orchestrator: {e}")
                # Don't set websocket to None for other errors, may be temporary

def main():
    """Run the Visual Analysis Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="UX-MIRROR Visual Analysis Agent")
    parser.add_argument("--orchestrator-host", default="localhost", 
                       help="Orchestrator host address")
    parser.add_argument("--orchestrator-port", type=int, default=8765,
                       help="Orchestrator port")
    parser.add_argument("--auto-monitor", action="store_true",
                       help="Start with automatic monitoring enabled")
    parser.add_argument("--monitor-interval", type=float, default=5.0,
                       help="Monitoring interval in seconds")
    
    args = parser.parse_args()
    
    # Create and start agent
    agent = VisualAnalysisAgent(args.orchestrator_host, args.orchestrator_port)
    
    if args.auto_monitor:
        agent.auto_monitor = True
        agent.monitoring_interval = args.monitor_interval
    
    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        logger.info("Visual Analysis Agent stopped by user")
    except Exception as e:
        logger.error(f"Agent failed: {e}")

if __name__ == "__main__":
    main() 