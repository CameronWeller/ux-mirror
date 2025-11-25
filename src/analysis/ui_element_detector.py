"""
UI Element Detection Component for UX-MIRROR
===========================================

Handles detection and analysis of UI elements in screenshots.
Extracted from visual analysis agent for better modularity.

Task: REFACTOR-006A - Create ui_element_detector.py with detection and classification
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Make PyTorch import optional for GPU acceleration
try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    from PIL import Image
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    transforms = None
    TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)

class UIElementType(Enum):
    """Enumeration of UI element types"""
    BUTTON = "button"
    INPUT = "input"
    TEXT = "text"
    IMAGE = "image"
    MENU = "menu"
    CONTAINER = "container"
    LINK = "link"
    ICON = "icon"
    UNKNOWN = "unknown"

@dataclass
class UIElement:
    """Detected UI element with properties"""
    element_type: UIElementType
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float
    text_content: Optional[str] = None
    text_confidence: Optional[float] = None  # OCR confidence for extracted text
    color_analysis: Optional[Dict[str, Any]] = None
    accessibility_score: float = 0.0
    is_interactive: bool = False
    is_visible: bool = True

class UIElementDetector:
    """
    Detects and classifies UI elements in screenshots using both
    traditional computer vision and optional GPU-accelerated deep learning.
    Now includes OCR for text extraction from detected elements.
    """
    
    def __init__(self, 
                 use_gpu: bool = False,  # v0.1.0: GPU disabled by default 
                 confidence_threshold: float = 0.3,
                 enable_ocr: bool = True,
                 ocr_language: str = "eng"):
        """
        Initialize the UI Element Detector
        
        Args:
            use_gpu: Whether to use GPU acceleration if available
            confidence_threshold: Minimum confidence score for detections
            enable_ocr: Enable OCR for text extraction from detected elements
            ocr_language: Language code for OCR (e.g., 'eng', 'eng+spa')
        """
        self.confidence_threshold = confidence_threshold
        # v0.1.0: GPU disabled for MVP
        self.use_gpu = False  # Disable GPU for v0.1.0 MVP
        self.enable_ocr = enable_ocr
        
        if self.use_gpu:
            self.device = torch.device("cuda")
            self.model = self._init_detection_model()
            self.transform = self._init_transforms()
            logger.info("UI Element Detector initialized with GPU acceleration")
        else:
            self.device = None
            self.model = None
            self.transform = None
            logger.info("UI Element Detector initialized with OpenCV fallback")
        
        # Initialize OCR engine if enabled
        self.ocr_engine = None
        if self.enable_ocr:
            try:
                from .ocr_engine import get_ocr_engine
                self.ocr_engine = get_ocr_engine(language=ocr_language, preprocessing=True)
                logger.info(f"OCR engine initialized (language: {ocr_language})")
            except Exception as e:
                logger.warning(f"OCR engine not available: {e}. Text extraction will be disabled.")
                self.enable_ocr = False
        
        # Initialize traditional CV detectors
        self._init_opencv_detectors()
    
    def detect_elements(self, image: np.ndarray) -> List[UIElement]:
        """
        Detect UI elements in the given image
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            List of detected UI elements
        """
        # v0.1.0: GPU detection disabled - always use OpenCV
        # if self.use_gpu and self.model is not None:
        #     return self._gpu_detect_elements(image)
        return self._opencv_detect_elements(image)
    
    def _gpu_detect_elements(self, image: np.ndarray) -> List[UIElement]:
        """GPU-accelerated UI element detection"""
        try:
            # Convert to PIL and preprocess
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            tensor_image = self.transform(pil_image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                predictions = self.model(tensor_image)
            
            # Convert predictions to UI elements
            elements = self._process_gpu_predictions(predictions, image)
            
            # Combine with OpenCV detections for better coverage
            opencv_elements = self._opencv_detect_elements(image)
            elements.extend(opencv_elements)
            
            # Remove duplicates and filter by confidence
            elements = self._filter_and_deduplicate(elements)
            
            # Extract text from elements if OCR is enabled
            if self.enable_ocr and self.ocr_engine:
                elements = self._extract_text_from_elements(elements, image)
            
            logger.debug(f"GPU detection found {len(elements)} UI elements")
            return elements
            
        except Exception as e:
            logger.error(f"GPU detection failed, falling back to OpenCV: {e}")
            return self._opencv_detect_elements(image)
    
    def _opencv_detect_elements(self, image: np.ndarray) -> List[UIElement]:
        """Traditional OpenCV-based UI element detection"""
        elements = []
        
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect button-like elements
            elements.extend(self._detect_buttons(image, gray))
            
            # Detect text regions
            elements.extend(self._detect_text_regions(image, gray))
            
            # Detect input fields
            elements.extend(self._detect_input_fields(image, gray))
            
            # Detect containers/panels
            elements.extend(self._detect_containers(image, gray))
            
            # Detect clickable elements
            elements.extend(self._detect_clickable_elements(image, gray))
            
            # Filter and enhance detected elements
            elements = self._enhance_detections(elements, image)
            
            logger.debug(f"OpenCV detection found {len(elements)} UI elements")
            return elements
            
        except Exception as e:
            logger.error(f"OpenCV detection failed: {e}")
            return []
    
    def _detect_buttons(self, image: np.ndarray, gray: np.ndarray) -> List[UIElement]:
        """Detect button-like UI elements"""
        elements = []
        
        # Edge detection for rectangular shapes
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            
            # Filter potential buttons by size and aspect ratio
            if 30 <= w <= 300 and 20 <= h <= 80 and area > 600:
                aspect_ratio = w / h
                
                # Buttons typically have specific aspect ratios
                if 1.2 <= aspect_ratio <= 8.0:
                    # Check if region has button-like characteristics
                    roi = image[y:y+h, x:x+w]
                    if self._is_button_like(roi):
                        confidence = min(1.0, area / (w * h))
                        
                        elements.append(UIElement(
                            element_type=UIElementType.BUTTON,
                            bbox=(x, y, w, h),
                            confidence=confidence,
                            color_analysis=self._analyze_colors(roi),
                            accessibility_score=self._assess_accessibility(roi),
                            is_interactive=True
                        ))
        
        return elements
    
    def _detect_text_regions(self, image: np.ndarray, gray: np.ndarray) -> List[UIElement]:
        """Detect text regions using MSER and morphological operations"""
        elements = []
        
        # Use MSER for text detection
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        for region in regions:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(region)
            
            # Filter text regions by size
            if w > 10 and h > 8 and w < 500 and h < 100:
                # Check text-like characteristics
                roi = gray[y:y+h, x:x+w]
                if self._is_text_like(roi):
                    confidence = 0.7  # Base confidence for text regions
                    
                    elements.append(UIElement(
                        element_type=UIElementType.TEXT,
                        bbox=(x, y, w, h),
                        confidence=confidence,
                        color_analysis=self._analyze_colors(image[y:y+h, x:x+w]),
                        accessibility_score=self._assess_text_accessibility(roi),
                        is_interactive=False
                    ))
        
        return elements
    
    def _detect_input_fields(self, image: np.ndarray, gray: np.ndarray) -> List[UIElement]:
        """Detect input field elements"""
        elements = []
        
        # Look for rectangular regions that could be input fields
        edges = cv2.Canny(gray, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Input fields are typically wider than they are tall
            if w > 50 and h > 15 and w/h > 2.0 and w < 400 and h < 60:
                roi = image[y:y+h, x:x+w]
                
                # Check if it looks like an input field
                if self._is_input_field_like(roi):
                    confidence = 0.6
                    
                    elements.append(UIElement(
                        element_type=UIElementType.INPUT,
                        bbox=(x, y, w, h),
                        confidence=confidence,
                        color_analysis=self._analyze_colors(roi),
                        accessibility_score=self._assess_input_accessibility(roi),
                        is_interactive=True
                    ))
        
        return elements
    
    def _detect_containers(self, image: np.ndarray, gray: np.ndarray) -> List[UIElement]:
        """Detect container/panel elements"""
        elements = []
        
        # Look for large rectangular regions
        edges = cv2.Canny(gray, 20, 60)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            
            # Containers are typically large
            if w > 100 and h > 100 and area > 10000:
                roi = image[y:y+h, x:x+w]
                confidence = min(0.8, area / (image.shape[0] * image.shape[1]))
                
                elements.append(UIElement(
                    element_type=UIElementType.CONTAINER,
                    bbox=(x, y, w, h),
                    confidence=confidence,
                    color_analysis=self._analyze_colors(roi),
                    accessibility_score=0.5,
                    is_interactive=False
                ))
        
        return elements
    
    def _detect_clickable_elements(self, image: np.ndarray, gray: np.ndarray) -> List[UIElement]:
        """Detect potentially clickable elements"""
        elements = []
        
        # Use template matching for common UI patterns
        # This is a simplified approach - in practice, you'd use trained templates
        
        # Harris corner detection for clickable elements
        corners = cv2.cornerHarris(gray, 2, 3, 0.04)
        corners = cv2.dilate(corners, None)
        
        # Find corner coordinates
        corner_coords = np.where(corners > 0.01 * corners.max())
        
        # Group nearby corners into potential clickable regions
        for y, x in zip(corner_coords[0], corner_coords[1]):
            # Simple region around corner
            region_size = 40
            x1, y1 = max(0, x - region_size//2), max(0, y - region_size//2)
            x2, y2 = min(image.shape[1], x + region_size//2), min(image.shape[0], y + region_size//2)
            
            if x2 - x1 > 20 and y2 - y1 > 20:
                elements.append(UIElement(
                    element_type=UIElementType.ICON,
                    bbox=(x1, y1, x2-x1, y2-y1),
                    confidence=0.4,
                    is_interactive=True
                ))
        
        return elements
    
    def _is_button_like(self, roi: np.ndarray) -> bool:
        """Check if a region looks like a button"""
        if roi.size == 0:
            return False
        
        # Check color uniformity (buttons often have solid colors)
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        std_dev = np.std(gray_roi)
        
        # Buttons often have low color variation
        return std_dev < 30
    
    def _is_text_like(self, roi: np.ndarray) -> bool:
        """Check if a region looks like text"""
        if roi.size == 0:
            return False
        
        # Text regions have specific characteristics
        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Text has moderate edge density
        return 0.05 < edge_density < 0.3
    
    def _is_input_field_like(self, roi: np.ndarray) -> bool:
        """Check if a region looks like an input field"""
        if roi.size == 0:
            return False
        
        # Input fields often have borders
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_roi, 50, 150)
        
        # Check for rectangular border
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
            if len(approx) == 4:  # Rectangular shape
                return True
        
        return False
    
    def _analyze_colors(self, roi: np.ndarray) -> Dict[str, Any]:
        """Analyze color properties of a region"""
        if roi.size == 0:
            return {"dominant_color": [0, 0, 0], "contrast_ratio": 0.0}
        
        # Calculate dominant color
        roi_reshaped = roi.reshape(-1, 3)
        dominant_color = np.mean(roi_reshaped, axis=0).astype(int).tolist()
        
        # Simple contrast ratio calculation
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        contrast_ratio = np.std(gray_roi) / 255.0
        
        return {
            "dominant_color": dominant_color,
            "contrast_ratio": contrast_ratio,
            "brightness": np.mean(gray_roi) / 255.0
        }
    
    def _assess_accessibility(self, roi: np.ndarray) -> float:
        """Assess accessibility score for a UI element"""
        if roi.size == 0:
            return 0.0
        
        color_analysis = self._analyze_colors(roi)
        contrast = color_analysis["contrast_ratio"]
        
        # Base accessibility on contrast and size
        h, w = roi.shape[:2]
        size_score = min(1.0, (w * h) / (44 * 44))  # 44px is minimum touch target
        contrast_score = min(1.0, contrast * 3.0)  # Scale contrast
        
        return (size_score + contrast_score) / 2.0
    
    def _assess_text_accessibility(self, roi: np.ndarray) -> float:
        """Assess accessibility specifically for text elements"""
        if roi.size == 0:
            return 0.0
        
        # Text accessibility depends heavily on contrast
        std_dev = np.std(roi)
        contrast_score = min(1.0, std_dev / 50.0)
        
        return contrast_score
    
    def _assess_input_accessibility(self, roi: np.ndarray) -> float:
        """Assess accessibility for input field elements"""
        if roi.size == 0:
            return 0.0
        
        # Input fields need good contrast and sufficient size
        color_analysis = self._analyze_colors(roi)
        contrast = color_analysis["contrast_ratio"]
        
        h, w = roi.shape[:2]
        size_score = min(1.0, h / 30.0)  # Minimum height for input fields
        contrast_score = min(1.0, contrast * 2.0)
        
        return (size_score + contrast_score) / 2.0
    
    def _filter_and_deduplicate(self, elements: List[UIElement]) -> List[UIElement]:
        """Filter elements by confidence and remove duplicates"""
        # Filter by confidence threshold
        filtered = [elem for elem in elements if elem.confidence >= self.confidence_threshold]
        
        # Remove overlapping elements (keep higher confidence)
        deduplicated = []
        for elem in sorted(filtered, key=lambda x: x.confidence, reverse=True):
            is_duplicate = False
            for existing in deduplicated:
                if self._elements_overlap(elem, existing, threshold=0.5):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduplicated.append(elem)
        
        return deduplicated
    
    def _elements_overlap(self, elem1: UIElement, elem2: UIElement, threshold: float = 0.5) -> bool:
        """Check if two elements overlap significantly"""
        x1, y1, w1, h1 = elem1.bbox
        x2, y2, w2, h2 = elem2.bbox
        
        # Calculate intersection
        xi1, yi1 = max(x1, x2), max(y1, y2)
        xi2, yi2 = min(x1 + w1, x2 + w2), min(y1 + h1, y2 + h2)
        
        if xi2 <= xi1 or yi2 <= yi1:
            return False
        
        intersection = (xi2 - xi1) * (yi2 - yi1)
        union = w1 * h1 + w2 * h2 - intersection
        
        return (intersection / union) > threshold
    
    def _enhance_detections(self, elements: List[UIElement], image: np.ndarray) -> List[UIElement]:
        """Enhance detected elements with additional analysis"""
        enhanced = []
        
        for elem in elements:
            # Extract region of interest
            x, y, w, h = elem.bbox
            roi = image[y:y+h, x:x+w]
            
            # Update color analysis if not present
            if elem.color_analysis is None:
                elem.color_analysis = self._analyze_colors(roi)
            
            # Update accessibility score if not set
            if elem.accessibility_score == 0.0:
                elem.accessibility_score = self._assess_accessibility(roi)
            
            enhanced.append(elem)
        
        return enhanced
    
    def _extract_text_from_elements(self, elements: List[UIElement], image: np.ndarray) -> List[UIElement]:
        """
        Extract text from detected UI elements using OCR.
        
        Args:
            elements: List of detected UI elements
            image: Full image
            
        Returns:
            Elements with text_content and text_confidence populated
        """
        if not self.ocr_engine:
            return elements
        
        enhanced = []
        
        for elem in elements:
            # Only extract text from elements that might contain text
            if elem.element_type in [UIElementType.TEXT, UIElementType.BUTTON, 
                                     UIElementType.INPUT, UIElementType.LINK]:
                try:
                    # Extract region
                    x, y, w, h = elem.bbox
                    
                    # Ensure region is valid
                    if w > 10 and h > 8:  # Minimum size for OCR
                        # Extract text using OCR
                        ocr_result = self.ocr_engine.extract_text(image, elem.bbox)
                        
                        if ocr_result.text and ocr_result.confidence >= 0.5:
                            elem.text_content = ocr_result.text
                            elem.text_confidence = ocr_result.confidence
                            logger.debug(f"Extracted text from {elem.element_type.value}: '{ocr_result.text[:50]}'")
                except Exception as e:
                    logger.warning(f"OCR failed for {elem.element_type.value} element: {e}")
            
            enhanced.append(elem)
        
        return enhanced
    
    def _init_detection_model(self):
        """Initialize the GPU detection model"""
        if not self.use_gpu:
            return None
        
        # Simple CNN model for UI element classification
        model = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((7, 7)),
            nn.Flatten(),
            nn.Linear(128 * 7 * 7, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, len(UIElementType))
        ).to(self.device)
        
        return model
    
    def _init_transforms(self):
        """Initialize image transforms for GPU processing"""
        if not self.use_gpu:
            return None
        
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def _init_opencv_detectors(self):
        """Initialize OpenCV-based detectors"""
        # Initialize any OpenCV-specific detectors here
        pass
    
    def _process_gpu_predictions(self, predictions: torch.Tensor, image: np.ndarray) -> List[UIElement]:
        """Process GPU model predictions into UI elements"""
        # This is a simplified version - in practice you'd have a proper object detection model
        # For now, we'll combine GPU classification with OpenCV detection
        elements = []
        
        # Apply softmax to get probabilities
        probs = torch.softmax(predictions, dim=1)
        max_prob, predicted_class = torch.max(probs, 1)
        
        # This is a placeholder - real implementation would use object detection
        # to get bounding boxes along with classifications
        
        return elements

# Global instance for easy access
_ui_detector_instance: Optional[UIElementDetector] = None

def get_ui_detector() -> UIElementDetector:
    """
    Get the global UIElementDetector instance
    
    Returns:
        Global UIElementDetector instance
    """
    global _ui_detector_instance
    if _ui_detector_instance is None:
        _ui_detector_instance = UIElementDetector()