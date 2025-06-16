#!/usr/bin/env python3
"""
Screen Analysis and Computer Vision for UX-MIRROR Autonomous Testing
Phase 2: Input Automation System

Provides screen capture, UI element detection, and game state analysis.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List, Dict, Any, NamedTuple
from pathlib import Path
from datetime import datetime
import logging
import time
import json

try:
    import pyautogui
    from PIL import Image, ImageEnhance
    import pytesseract
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Run: pip install pyautogui pillow pytesseract opencv-python")
    raise

logger = logging.getLogger(__name__)

class DetectedElement(NamedTuple):
    """Represents a detected UI element"""
    name: str
    confidence: float
    position: Tuple[int, int]  # (x, y) center coordinates
    bounds: Tuple[int, int, int, int]  # (left, top, width, height)
    element_type: str  # button, text, window, etc.

class GameState(NamedTuple):
    """Represents the current game state"""
    is_running: bool
    fps: Optional[float]
    generation: Optional[int]
    living_cells: Optional[int]
    paused: bool
    window_focused: bool
    performance_metrics: Dict[str, Any]

class ScreenAnalyzer:
    """Analyzes screen content for autonomous testing"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.template_cache = {}
        self.results_dir = Path(__file__).parent.parent / "test_results" / "analysis"
        self.templates_dir = Path(__file__).parent.parent / "templates"
        
        # Create directories
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Game-specific detection patterns
        self.game_patterns = self._load_game_patterns()
        
        logger.info("ScreenAnalyzer initialized")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "template_matching_threshold": 0.8,
            "text_detection_enabled": True,
            "color_detection_enabled": True,
            "debug_mode": True,
            "save_analysis_images": True,
            "fps_detection_method": "ocr",  # ocr, pattern, color
            "performance_monitoring": True
        }
    
    def _load_game_patterns(self) -> Dict[str, Any]:
        """Load game-specific detection patterns"""
        patterns_file = self.templates_dir / "game_patterns.json"
        
        default_patterns = {
            "3d_game_of_life": {
                "window_title": "3D Game of Life",
                "ui_elements": {
                    "play_button": {"color_range": [(0, 255, 0), (50, 255, 50)]},
                    "pause_button": {"color_range": [(255, 255, 0), (255, 255, 50)]},
                    "reset_button": {"color_range": [(255, 0, 0), (255, 50, 50)]},
                    "settings_button": {"color_range": [(128, 128, 128), (200, 200, 200)]}
                },
                "text_regions": {
                    "fps_counter": {"region": (10, 10, 200, 50)},
                    "generation_counter": {"region": (10, 60, 200, 100)},
                    "cell_count": {"region": (10, 110, 200, 150)}
                },
                "performance_indicators": {
                    "fps_good": 60,
                    "fps_acceptable": 30,
                    "fps_poor": 15
                }
            }
        }
        
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load game patterns: {e}")
        
        # Save default patterns
        try:
            with open(patterns_file, 'w') as f:
                json.dump(default_patterns, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save default patterns: {e}")
        
        return default_patterns
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Capture screen or specific region as OpenCV image"""
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            # Convert PIL to OpenCV format
            opencv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            return opencv_image
            
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            return np.array([])
    
    def find_template(self, template_path: str, screenshot: Optional[np.ndarray] = None,
                     threshold: Optional[float] = None) -> List[DetectedElement]:
        """Find template matches in screenshot"""
        if screenshot is None:
            screenshot = self.capture_screen()
        
        if screenshot.size == 0:
            return []
        
        threshold = threshold or self.config["template_matching_threshold"]
        
        try:
            # Load template (with caching)
            if template_path not in self.template_cache:
                template = cv2.imread(template_path, cv2.IMREAD_COLOR)
                if template is None:
                    logger.error(f"Failed to load template: {template_path}")
                    return []
                self.template_cache[template_path] = template
            else:
                template = self.template_cache[template_path]
            
            # Perform template matching
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)
            
            detected_elements = []
            h, w = template.shape[:2]
            
            for pt in zip(*locations[::-1]):  # Switch x and y
                confidence = result[pt[1], pt[0]]
                center_x = pt[0] + w // 2
                center_y = pt[1] + h // 2
                
                element = DetectedElement(
                    name=Path(template_path).stem,
                    confidence=float(confidence),
                    position=(center_x, center_y),
                    bounds=(pt[0], pt[1], w, h),
                    element_type="template_match"
                )
                detected_elements.append(element)
            
            if self.config["debug_mode"] and detected_elements:
                logger.info(f"Found {len(detected_elements)} matches for {template_path}")
            
            return detected_elements
            
        except Exception as e:
            logger.error(f"Template matching failed: {e}")
            return []
    
    def detect_text_regions(self, screenshot: Optional[np.ndarray] = None,
                           regions: Optional[Dict[str, Tuple[int, int, int, int]]] = None) -> Dict[str, str]:
        """Detect text in specified regions using OCR"""
        if not self.config["text_detection_enabled"]:
            return {}
        
        if screenshot is None:
            screenshot = self.capture_screen()
        
        if screenshot.size == 0:
            return {}
        
        detected_text = {}
        
        try:
            # Use default regions for 3D Game of Life if none specified
            if regions is None:
                game_patterns = self.game_patterns.get("3d_game_of_life", {})
                regions = game_patterns.get("text_regions", {})
            
            for region_name, (x, y, w, h) in regions.items():
                try:
                    # Extract region
                    roi = screenshot[y:y+h, x:x+w]
                    
                    # Preprocess for better OCR
                    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                    
                    # Enhance contrast
                    enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(gray)
                    
                    # Threshold for better text recognition
                    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    
                    # OCR
                    text = pytesseract.image_to_string(thresh, config='--psm 8').strip()
                    
                    if text:
                        detected_text[region_name] = text
                        if self.config["debug_mode"]:
                            logger.info(f"Detected text in {region_name}: '{text}'")
                    
                    # Save debug images if enabled
                    if self.config["save_analysis_images"]:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        debug_path = self.results_dir / f"ocr_{region_name}_{timestamp}.png"
                        cv2.imwrite(str(debug_path), thresh)
                
                except Exception as e:
                    logger.warning(f"OCR failed for region {region_name}: {e}")
            
            return detected_text
            
        except Exception as e:
            logger.error(f"Text detection failed: {e}")
            return {}
    
    def detect_colors(self, screenshot: Optional[np.ndarray] = None,
                     color_ranges: Optional[Dict[str, List[Tuple[int, int, int]]]] = None) -> Dict[str, List[Tuple[int, int]]]:
        """Detect specific colors and return their positions"""
        if not self.config["color_detection_enabled"]:
            return {}
        
        if screenshot is None:
            screenshot = self.capture_screen()
        
        if screenshot.size == 0:
            return {}
        
        detected_colors = {}
        
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
            
            # Use default color ranges if none specified
            if color_ranges is None:
                game_patterns = self.game_patterns.get("3d_game_of_life", {})
                ui_elements = game_patterns.get("ui_elements", {})
                color_ranges = {}
                
                for element, props in ui_elements.items():
                    if "color_range" in props:
                        color_ranges[element] = props["color_range"]
            
            for color_name, (lower_color, upper_color) in color_ranges.items():
                try:
                    # Convert RGB to HSV
                    lower_hsv = cv2.cvtColor(np.uint8([[lower_color]]), cv2.COLOR_RGB2HSV)[0][0]
                    upper_hsv = cv2.cvtColor(np.uint8([[upper_color]]), cv2.COLOR_RGB2HSV)[0][0]
                    
                    # Create mask
                    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
                    
                    # Find contours
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    positions = []
                    for contour in contours:
                        # Filter small contours
                        if cv2.contourArea(contour) > 100:  # Minimum area threshold
                            # Get center point
                            M = cv2.moments(contour)
                            if M["m00"] != 0:
                                cx = int(M["m10"] / M["m00"])
                                cy = int(M["m01"] / M["m00"])
                                positions.append((cx, cy))
                    
                    if positions:
                        detected_colors[color_name] = positions
                        if self.config["debug_mode"]:
                            logger.info(f"Detected {len(positions)} instances of {color_name}")
                
                except Exception as e:
                    logger.warning(f"Color detection failed for {color_name}: {e}")
            
            return detected_colors
            
        except Exception as e:
            logger.error(f"Color detection failed: {e}")
            return {}
    
    def extract_fps(self, text_data: Dict[str, str]) -> Optional[float]:
        """Extract FPS from detected text"""
        try:
            # Look for FPS in various text regions
            for region_name, text in text_data.items():
                if "fps" in region_name.lower() or "frame" in text.lower():
                    # Extract numbers from text
                    import re
                    numbers = re.findall(r'\d+\.?\d*', text)
                    
                    for num_str in numbers:
                        try:
                            fps = float(num_str)
                            # Validate FPS range (reasonable values)
                            if 1 <= fps <= 300:
                                return fps
                        except ValueError:
                            continue
            
            return None
            
        except Exception as e:
            logger.error(f"FPS extraction failed: {e}")
            return None
    
    def extract_generation(self, text_data: Dict[str, str]) -> Optional[int]:
        """Extract generation count from detected text"""
        try:
            for region_name, text in text_data.items():
                if "generation" in region_name.lower() or "gen" in text.lower():
                    import re
                    numbers = re.findall(r'\d+', text)
                    
                    for num_str in numbers:
                        try:
                            generation = int(num_str)
                            # Validate generation range
                            if 0 <= generation <= 1000000:
                                return generation
                        except ValueError:
                            continue
            
            return None
            
        except Exception as e:
            logger.error(f"Generation extraction failed: {e}")
            return None
    
    def extract_cell_count(self, text_data: Dict[str, str]) -> Optional[int]:
        """Extract living cell count from detected text"""
        try:
            for region_name, text in text_data.items():
                if "cell" in region_name.lower() or "live" in text.lower():
                    import re
                    numbers = re.findall(r'\d+', text)
                    
                    for num_str in numbers:
                        try:
                            cells = int(num_str)
                            # Validate cell count range
                            if 0 <= cells <= 1000000:
                                return cells
                        except ValueError:
                            continue
            
            return None
            
        except Exception as e:
            logger.error(f"Cell count extraction failed: {e}")
            return None
    
    def analyze_game_state(self, screenshot: Optional[np.ndarray] = None) -> GameState:
        """Analyze current game state"""
        if screenshot is None:
            screenshot = self.capture_screen()
        
        if screenshot.size == 0:
            return GameState(False, None, None, None, True, False, {})
        
        try:
            # Detect text regions
            text_data = self.detect_text_regions(screenshot)
            
            # Detect UI colors
            color_data = self.detect_colors(screenshot)
            
            # Extract game metrics
            fps = self.extract_fps(text_data)
            generation = self.extract_generation(text_data)
            living_cells = self.extract_cell_count(text_data)
            
            # Determine if game is running (has FPS > 0)
            is_running = fps is not None and fps > 0
            
            # Determine if paused (look for pause indicators)
            paused = False
            if "pause_button" in color_data or fps == 0:
                paused = True
            
            # Check if window is focused (simple heuristic)
            window_focused = len(text_data) > 0 or len(color_data) > 0
            
            # Performance metrics
            performance_metrics = {
                "fps_category": self._categorize_fps(fps),
                "text_regions_detected": len(text_data),
                "ui_elements_detected": len(color_data),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            game_state = GameState(
                is_running=is_running,
                fps=fps,
                generation=generation,
                living_cells=living_cells,
                paused=paused,
                window_focused=window_focused,
                performance_metrics=performance_metrics
            )
            
            if self.config["debug_mode"]:
                logger.info(f"Game State: Running={is_running}, FPS={fps}, Gen={generation}, Cells={living_cells}")
            
                # Save annotated analysis image for easier inspection
                try:
                    detected_elements = self.find_ui_elements(screenshot)
                    self.save_analysis_result(
                        screenshot,
                        game_state,
                        detected_elements,
                        session_name="debug"
                    )
                except Exception as e:
                    logger.warning(f"Failed to save debug analysis image: {e}")
            
            return game_state
            
        except Exception as e:
            logger.error(f"Game state analysis failed: {e}")
            return GameState(False, None, None, None, True, False, {"error": str(e)})
    
    def _categorize_fps(self, fps: Optional[float]) -> str:
        """Categorize FPS performance"""
        if fps is None:
            return "unknown"
        
        patterns = self.game_patterns.get("3d_game_of_life", {}).get("performance_indicators", {})
        
        if fps >= patterns.get("fps_good", 60):
            return "excellent"
        elif fps >= patterns.get("fps_acceptable", 30):
            return "good"
        elif fps >= patterns.get("fps_poor", 15):
            return "acceptable"
        else:
            return "poor"
    
    def find_ui_elements(self, screenshot: Optional[np.ndarray] = None) -> Dict[str, List[DetectedElement]]:
        """Find all UI elements in the current screen"""
        if screenshot is None:
            screenshot = self.capture_screen()
        
        all_elements = {}
        
        # Template matching for known UI elements
        template_dir = self.templates_dir / "ui_elements"
        if template_dir.exists():
            for template_file in template_dir.glob("*.png"):
                elements = self.find_template(str(template_file), screenshot)
                if elements:
                    all_elements[template_file.stem] = elements
        
        # Color-based detection
        color_positions = self.detect_colors(screenshot)
        for element_name, positions in color_positions.items():
            color_elements = []
            for pos in positions:
                element = DetectedElement(
                    name=element_name,
                    confidence=0.8,  # Default confidence for color detection
                    position=pos,
                    bounds=(pos[0]-10, pos[1]-10, 20, 20),  # Default bounds
                    element_type="color_detection"
                )
                color_elements.append(element)
            
            if color_elements:
                all_elements[element_name] = color_elements
        
        return all_elements
    
    def save_analysis_result(self, screenshot: np.ndarray, game_state: GameState, 
                           detected_elements: Dict[str, List[DetectedElement]], 
                           session_name: str = "analysis") -> str:
        """Save comprehensive analysis results"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save annotated screenshot
            annotated = screenshot.copy()
            
            # Draw detected elements
            for element_type, elements in detected_elements.items():
                for element in elements:
                    x, y = element.position
                    left, top, width, height = element.bounds
                    
                    # Draw bounding box
                    cv2.rectangle(annotated, (left, top), (left + width, top + height), (0, 255, 0), 2)
                    
                    # Draw center point
                    cv2.circle(annotated, (x, y), 5, (0, 0, 255), -1)
                    
                    # Add label
                    label = f"{element.name} ({element.confidence:.2f})"
                    cv2.putText(annotated, label, (left, top - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Add game state info
            info_text = [
                f"FPS: {game_state.fps}",
                f"Generation: {game_state.generation}",
                f"Living Cells: {game_state.living_cells}",
                f"Running: {game_state.is_running}",
                f"Paused: {game_state.paused}"
            ]
            
            for i, text in enumerate(info_text):
                cv2.putText(annotated, text, (10, 30 + i * 20), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # Save annotated image
            image_path = self.results_dir / f"{session_name}_{timestamp}_analysis.png"
            cv2.imwrite(str(image_path), annotated)
            
            # Save JSON data
            analysis_data = {
                "timestamp": timestamp,
                "session_name": session_name,
                "game_state": game_state._asdict(),
                "detected_elements": {
                    element_type: [elem._asdict() for elem in elements]
                    for element_type, elements in detected_elements.items()
                }
            }
            
            json_path = self.results_dir / f"{session_name}_{timestamp}_analysis.json"
            with open(json_path, 'w') as f:
                json.dump(analysis_data, f, indent=2, default=str)
            
            logger.info(f"Analysis results saved: {image_path}")
            return str(image_path)
            
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            return ""

def main():
    """Test the screen analyzer"""
    print("🔍 Testing Screen Analyzer...")
    
    analyzer = ScreenAnalyzer()
    
    print("Capturing screen...")
    screenshot = analyzer.capture_screen()
    
    print("Analyzing game state...")
    game_state = analyzer.analyze_game_state(screenshot)
    
    print("Finding UI elements...")
    ui_elements = analyzer.find_ui_elements(screenshot)
    
    print("Saving analysis results...")
    result_path = analyzer.save_analysis_result(screenshot, game_state, ui_elements, "test_analysis")
    
    print(f"✅ Screen analysis test completed!")
    print(f"📁 Results saved to: {result_path}")
    print(f"🎮 Game State: {game_state}")

if __name__ == "__main__":
    main() 