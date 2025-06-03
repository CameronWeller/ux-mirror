#!/usr/bin/env python3
"""
UX Mirror - Advanced UX Heuristics
Implements sophisticated UX analysis heuristics for web and game interfaces
"""

import numpy as np
from PIL import Image, ImageDraw
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
import colorsys
from scipy.spatial import distance
import cv2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VisualElement:
    """Represents a detected visual element in the UI"""
    type: str
    bounds: Dict[str, int]  # x, y, width, height
    confidence: float
    properties: Dict[str, Any]
    color: Optional[Tuple[int, int, int]] = None
    text: Optional[str] = None
    font_size: Optional[int] = None

@dataclass
class UXIssue:
    """Represents a detected UX issue"""
    type: str
    severity: str  # high, medium, low
    description: str
    location: Dict[str, int]  # x, y coordinates
    element: Optional[VisualElement] = None
    fix: Optional[str] = None
    confidence: float = 1.0
    metrics: Optional[Dict[str, float]] = None

class AdvancedUXAnalyzer:
    """Implements sophisticated UX analysis heuristics"""
    
    def __init__(self):
        # Constants for analysis
        self.MIN_TOUCH_TARGET = 48  # Minimum touch target size in pixels
        self.MIN_CONTRAST_RATIO = 4.5  # WCAG AA standard
        self.MIN_TEXT_SIZE = 16  # Minimum readable text size
        self.MAX_CLUTTER_DENSITY = 0.4  # Maximum element density
        self.OPTIMAL_SPACING = 8  # Optimal spacing between elements
        
    def analyze_layout(self, elements: List[VisualElement], 
                      image_size: Tuple[int, int]) -> List[UXIssue]:
        """Analyze layout and spacing of UI elements"""
        issues = []
        
        # Check element density
        density = self._calculate_element_density(elements, image_size)
        if density > self.MAX_CLUTTER_DENSITY:
            issues.append(UXIssue(
                type="layout",
                severity="high",
                description="UI appears cluttered with too many elements",
                location={"x": 0, "y": 0},
                fix="Consider reducing the number of visible elements or increasing spacing",
                metrics={"density": density}
            ))
        
        # Check spacing between elements
        spacing_issues = self._check_element_spacing(elements)
        issues.extend(spacing_issues)
        
        # Check visual hierarchy
        hierarchy_issues = self._analyze_visual_hierarchy(elements)
        issues.extend(hierarchy_issues)
        
        return issues
    
    def analyze_accessibility(self, elements: List[VisualElement]) -> List[UXIssue]:
        """Analyze accessibility aspects of UI elements"""
        issues = []
        
        for element in elements:
            # Check text contrast
            if element.text and element.color:
                contrast_ratio = self._calculate_contrast_ratio(
                    element.color, 
                    self._get_background_color(element)
                )
                if contrast_ratio < self.MIN_CONTRAST_RATIO:
                    issues.append(UXIssue(
                        type="accessibility",
                        severity="high",
                        description=f"Low contrast text ({contrast_ratio:.1f}:1)",
                        location=element.bounds,
                        element=element,
                        fix="Increase text contrast to meet WCAG AA standards",
                        metrics={"contrast_ratio": contrast_ratio}
                    ))
            
            # Check touch target size
            if element.type in ["button", "link", "input"]:
                area = element.bounds["width"] * element.bounds["height"]
                if area < self.MIN_TOUCH_TARGET * self.MIN_TOUCH_TARGET:
                    issues.append(UXIssue(
                        type="accessibility",
                        severity="medium",
                        description="Touch target too small",
                        location=element.bounds,
                        element=element,
                        fix=f"Increase size to at least {self.MIN_TOUCH_TARGET}x{self.MIN_TOUCH_TARGET} pixels",
                        metrics={"current_area": area}
                    ))
        
        return issues
    
    def analyze_readability(self, elements: List[VisualElement]) -> List[UXIssue]:
        """Analyze text readability aspects"""
        issues = []
        
        for element in elements:
            if element.text and element.font_size:
                # Check font size
                if element.font_size < self.MIN_TEXT_SIZE:
                    issues.append(UXIssue(
                        type="readability",
                        severity="medium",
                        description="Text size may be too small to read",
                        location=element.bounds,
                        element=element,
                        fix=f"Increase font size to at least {self.MIN_TEXT_SIZE}px",
                        metrics={"current_size": element.font_size}
                    ))
                
                # Check line length
                if len(element.text) > 75:  # Optimal line length
                    issues.append(UXIssue(
                        type="readability",
                        severity="low",
                        description="Text line may be too long",
                        location=element.bounds,
                        element=element,
                        fix="Consider breaking text into shorter lines",
                        metrics={"line_length": len(element.text)}
                    ))
        
        return issues
    
    def _calculate_element_density(self, elements: List[VisualElement], 
                                 image_size: Tuple[int, int]) -> float:
        """Calculate the density of UI elements"""
        total_area = image_size[0] * image_size[1]
        element_area = sum(
            elem.bounds["width"] * elem.bounds["height"] 
            for elem in elements
        )
        return element_area / total_area
    
    def _check_element_spacing(self, elements: List[VisualElement]) -> List[UXIssue]:
        """Check spacing between UI elements"""
        issues = []
        
        for i, elem1 in enumerate(elements):
            for elem2 in elements[i+1:]:
                distance = self._calculate_element_distance(elem1, elem2)
                if distance < self.OPTIMAL_SPACING:
                    issues.append(UXIssue(
                        type="spacing",
                        severity="medium",
                        description="Elements too close together",
                        location=elem1.bounds,
                        element=elem1,
                        fix=f"Increase spacing to at least {self.OPTIMAL_SPACING} pixels",
                        metrics={"current_spacing": distance}
                    ))
        
        return issues
    
    def _analyze_visual_hierarchy(self, elements: List[VisualElement]) -> List[UXIssue]:
        """Analyze visual hierarchy of UI elements"""
        issues = []
        
        # Group elements by type
        buttons = [e for e in elements if e.type == "button"]
        text_elements = [e for e in elements if e.type == "text"]
        
        # Check if primary actions are prominent
        if buttons:
            primary_buttons = [b for b in buttons if "primary" in b.properties.get("role", "")]
            if not primary_buttons:
                issues.append(UXIssue(
                    type="hierarchy",
                    severity="medium",
                    description="No clear primary action button",
                    location=buttons[0].bounds,
                    element=buttons[0],
                    fix="Add visual emphasis to primary action buttons"
                ))
        
        # Check text hierarchy
        if text_elements:
            heading_sizes = [t.font_size for t in text_elements if t.font_size]
            if heading_sizes:
                size_variation = max(heading_sizes) - min(heading_sizes)
                if size_variation < 8:  # Minimum size difference for hierarchy
                    issues.append(UXIssue(
                        type="hierarchy",
                        severity="low",
                        description="Insufficient text size variation",
                        location=text_elements[0].bounds,
                        element=text_elements[0],
                        fix="Increase size difference between headings and body text"
                    ))
        
        return issues
    
    def _calculate_contrast_ratio(self, color1: Tuple[int, int, int], 
                                color2: Tuple[int, int, int]) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        def get_luminance(color):
            # Convert RGB to relative luminance
            r, g, b = [c/255 for c in color]
            r = r/12.92 if r <= 0.03928 else ((r + 0.055)/1.055) ** 2.4
            g = g/12.92 if g <= 0.03928 else ((g + 0.055)/1.055) ** 2.4
            b = b/12.92 if b <= 0.03928 else ((b + 0.055)/1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        l1 = get_luminance(color1)
        l2 = get_luminance(color2)
        
        # Ensure l1 is the lighter color
        if l1 < l2:
            l1, l2 = l2, l1
            
        return (l1 + 0.05) / (l2 + 0.05)
    
    def _get_background_color(self, element: VisualElement) -> Tuple[int, int, int]:
        """Get the background color for an element"""
        # This is a simplified version - in practice, you'd need to analyze the image
        return (255, 255, 255)  # Default to white
    
    def _calculate_element_distance(self, elem1: VisualElement, 
                                  elem2: VisualElement) -> float:
        """Calculate the minimum distance between two elements"""
        # Get element centers
        center1 = (
            elem1.bounds["x"] + elem1.bounds["width"]/2,
            elem1.bounds["y"] + elem1.bounds["height"]/2
        )
        center2 = (
            elem2.bounds["x"] + elem2.bounds["width"]/2,
            elem2.bounds["y"] + elem2.bounds["height"]/2
        )
        
        # Calculate Euclidean distance
        return distance.euclidean(center1, center2)

def analyze_image(image: Image.Image) -> List[UXIssue]:
    """Main function to analyze an image using all heuristics"""
    analyzer = AdvancedUXAnalyzer()
    
    # Convert image to numpy array for OpenCV processing
    img_array = np.array(image)
    
    # Detect elements (simplified version - in practice, use ML models)
    elements = detect_elements(img_array)
    
    # Run all analyses
    layout_issues = analyzer.analyze_layout(elements, image.size)
    accessibility_issues = analyzer.analyze_accessibility(elements)
    readability_issues = analyzer.analyze_readability(elements)
    
    # Combine all issues
    all_issues = layout_issues + accessibility_issues + readability_issues
    
    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    all_issues.sort(key=lambda x: severity_order[x.severity])
    
    return all_issues

def detect_elements(img_array: np.ndarray) -> List[VisualElement]:
    """Detect UI elements in the image (placeholder implementation)"""
    # In practice, this would use computer vision or ML models
    # For now, return some example elements
    return [
        VisualElement(
            type="button",
            bounds={"x": 100, "y": 200, "width": 120, "height": 40},
            confidence=0.85,
            properties={"role": "primary"},
            color=(0, 123, 255),
            text="Submit",
            font_size=16
        ),
        VisualElement(
            type="text",
            bounds={"x": 50, "y": 50, "width": 300, "height": 30},
            confidence=0.92,
            properties={},
            color=(0, 0, 0),
            text="Welcome to our site",
            font_size=24
        )
    ] 