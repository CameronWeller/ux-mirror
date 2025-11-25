#!/usr/bin/env python3
"""
Autonomous Input Controller for UX-MIRROR Testing
Phase 2: Input Automation System

Provides human-like mouse and keyboard input simulation with safety features.
"""

import time
import random
import logging
import threading
from typing import Tuple, Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

try:
    import pyautogui
    import cv2
    import numpy as np
    from PIL import Image
    import psutil
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Run: pip install pyautogui opencv-python pillow psutil")
    raise

logger = logging.getLogger(__name__)

class SafetyMonitor:
    """Safety monitoring for autonomous input control"""
    
    def __init__(self):
        self.emergency_stop = False
        self.start_time = None
        self.max_duration = 3600  # 1 hour max
        self.cpu_limit = 80  # Max CPU usage %
        self.memory_limit = 90  # Max memory usage %
        
    def check_safety(self) -> bool:
        """Check if it's safe to continue automation"""
        if self.emergency_stop:
            return False
            
        # Check time limit
        if self.start_time and (time.time() - self.start_time) > self.max_duration:
            logger.warning("Maximum test duration exceeded")
            return False
            
        # Check resource usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent > self.cpu_limit:
            logger.warning(f"CPU usage too high: {cpu_percent}%")
            return False
            
        if memory_percent > self.memory_limit:
            logger.warning(f"Memory usage too high: {memory_percent}%")
            return False
            
        return True
    
    def start_monitoring(self):
        """Start safety monitoring"""
        self.start_time = time.time()
        self.emergency_stop = False
        
    def stop_monitoring(self):
        """Stop safety monitoring"""
        self.emergency_stop = True

class HumanLikeInput:
    """Generates human-like input patterns"""
    
    @staticmethod
    def add_movement_variation(duration: float) -> float:
        """Add natural variation to movement duration"""
        variation = random.uniform(0.8, 1.2)
        return duration * variation
    
    @staticmethod
    def add_pause_variation(base_pause: float = 0.1) -> float:
        """Add natural pause variation"""
        return base_pause + random.uniform(0.05, 0.3)
    
    @staticmethod
    def generate_bezier_path(start: Tuple[int, int], end: Tuple[int, int], 
                           points: int = 10) -> List[Tuple[int, int]]:
        """Generate a smooth Bezier curve path between two points"""
        def bezier_point(t: float, p0: Tuple[int, int], p1: Tuple[int, int], 
                        p2: Tuple[int, int], p3: Tuple[int, int]) -> Tuple[int, int]:
            x = (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
            y = (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
            return (int(x), int(y))
        
        # Control points for curve
        mid_x = (start[0] + end[0]) // 2
        mid_y = (start[1] + end[1]) // 2
        
        # Add some randomness to control points
        offset_x = random.randint(-50, 50)
        offset_y = random.randint(-50, 50)
        
        p0 = start
        p1 = (start[0] + offset_x, start[1] + offset_y)
        p2 = (end[0] - offset_x, end[1] - offset_y) 
        p3 = end
        
        path = []
        for i in range(points + 1):
            t = i / points
            point = bezier_point(t, p0, p1, p2, p3)
            path.append(point)
            
        return path

class AutonomousInputController:
    """Main input controller for autonomous testing"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.safety_monitor = SafetyMonitor()
        self.human_input = HumanLikeInput()
        self.screenshot_count = 0
        self.test_results_dir = Path(__file__).parent.parent / "test_results"
        
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Create results directories
        self.screenshots_dir = self.test_results_dir / "screenshots"
        self.videos_dir = self.test_results_dir / "videos"
        self.logs_dir = self.test_results_dir / "logs"
        
        for dir_path in [self.screenshots_dir, self.videos_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Setup logging
        self._setup_logging()
        
        logger.info("AutonomousInputController initialized")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "mouse_speed": "human_like",  # slow, medium, fast, human_like
            "click_timing": "realistic",   # immediate, realistic, slow
            "error_simulation": 0.02,      # 2% chance of simulated errors
            "screenshot_on_action": True,
            "video_recording": False,
            "safety_enabled": True
        }
    
    def _setup_logging(self):
        """Setup logging for input controller"""
        log_file = self.logs_dir / f"input_controller_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
    
    def start_session(self, session_name: str = "autonomous_test"):
        """Start an autonomous testing session"""
        if self.config["safety_enabled"]:
            self.safety_monitor.start_monitoring()
        
        logger.info(f"Starting autonomous session: {session_name}")
        
        if self.config["screenshot_on_action"]:
            self.take_screenshot(f"{session_name}_start")
    
    def end_session(self, session_name: str = "autonomous_test"):
        """End an autonomous testing session"""
        if self.config["safety_enabled"]:
            self.safety_monitor.stop_monitoring()
        
        logger.info(f"Ending autonomous session: {session_name}")
        
        if self.config["screenshot_on_action"]:
            self.take_screenshot(f"{session_name}_end")
    
    def check_safety(self) -> bool:
        """Check if it's safe to continue automation"""
        if not self.config["safety_enabled"]:
            return True
        return self.safety_monitor.check_safety()
    
    def take_screenshot(self, name: Optional[str] = None) -> str:
        """Take a screenshot and save it"""
        if not name:
            name = f"screenshot_{self.screenshot_count:04d}"
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{name}.png"
        filepath = self.screenshots_dir / filename
        
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            self.screenshot_count += 1
            logger.info(f"Screenshot saved: {filepath}")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return ""
    
    def move_mouse(self, x: int, y: int, duration: float = 1.0, 
                   human_like: bool = True) -> bool:
        """Move mouse to specified coordinates with human-like movement"""
        if not self.check_safety():
            return False
        
        try:
            current_pos = pyautogui.position()
            target_pos = (x, y)
            
            if human_like:
                # Generate curved path
                path = self.human_input.generate_bezier_path(current_pos, target_pos)
                
                # Move along the path
                total_duration = self.human_input.add_movement_variation(duration)
                step_duration = total_duration / len(path)
                
                for point in path:
                    if not self.check_safety():
                        return False
                    
                    pyautogui.moveTo(point[0], point[1], duration=step_duration)
                    time.sleep(0.01)  # Small pause between steps
            else:
                # Direct movement
                pyautogui.moveTo(x, y, duration=duration)
            
            logger.info(f"Mouse moved to ({x}, {y})")
            
            if self.config["screenshot_on_action"]:
                self.take_screenshot(f"mouse_move_{x}_{y}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to move mouse: {e}")
            return False
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
              button: str = 'left', clicks: int = 1, interval: float = 0.0) -> bool:
        """Click at specified coordinates or current position"""
        if not self.check_safety():
            return False
        
        try:
            # Move to position if specified
            if x is not None and y is not None:
                if not self.move_mouse(x, y):
                    return False
            
            # Add realistic timing
            if self.config["click_timing"] == "realistic":
                time.sleep(self.human_input.add_pause_variation(0.1))
            elif self.config["click_timing"] == "slow":
                time.sleep(self.human_input.add_pause_variation(0.3))
            
            # Simulate occasional misclicks
            if (self.config["error_simulation"] > 0 and 
                random.random() < self.config["error_simulation"]):
                # Slight offset for misclick
                offset_x = random.randint(-3, 3)
                offset_y = random.randint(-3, 3)
                current_pos = pyautogui.position()
                pyautogui.click(current_pos.x + offset_x, current_pos.y + offset_y, 
                              button=button, clicks=clicks, interval=interval)
                logger.info(f"Simulated misclick at offset ({offset_x}, {offset_y})")
            else:
                # Normal click
                pyautogui.click(button=button, clicks=clicks, interval=interval)
            
            position = pyautogui.position()
            logger.info(f"Clicked {button} button at ({position.x}, {position.y})")
            
            if self.config["screenshot_on_action"]:
                self.take_screenshot(f"click_{button}_{position.x}_{position.y}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to click: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.1) -> bool:
        """Type text with human-like timing"""
        if not self.check_safety():
            return False
        
        try:
            # Add variation to typing speed
            base_interval = self.human_input.add_pause_variation(interval)
            
            for char in text:
                if not self.check_safety():
                    return False
                
                # Variable typing speed
                char_interval = base_interval + random.uniform(-0.05, 0.1)
                pyautogui.write(char, interval=char_interval)
            
            logger.info(f"Typed text: {text}")
            
            if self.config["screenshot_on_action"]:
                self.take_screenshot(f"text_input")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False
    
    def key_press(self, key: str, presses: int = 1, interval: float = 0.1) -> bool:
        """Press a key with human-like timing"""
        if not self.check_safety():
            return False
        
        try:
            for _ in range(presses):
                if not self.check_safety():
                    return False
                
                pyautogui.press(key)
                
                if presses > 1:
                    time.sleep(self.human_input.add_pause_variation(interval))
            
            logger.info(f"Pressed key '{key}' {presses} times")
            
            if self.config["screenshot_on_action"]:
                self.take_screenshot(f"key_press_{key}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to press key: {e}")
            return False
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Scroll with mouse wheel"""
        if not self.check_safety():
            return False
        
        try:
            if x is not None and y is not None:
                pyautogui.scroll(clicks, x=x, y=y)
            else:
                pyautogui.scroll(clicks)
            
            logger.info(f"Scrolled {clicks} clicks")
            
            if self.config["screenshot_on_action"]:
                self.take_screenshot(f"scroll_{clicks}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll: {e}")
            return False
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             duration: float = 1.0, button: str = 'left') -> bool:
        """Drag from start to end position"""
        if not self.check_safety():
            return False
        
        try:
            # Move to start position
            if not self.move_mouse(start_x, start_y):
                return False
            
            # Start drag
            pyautogui.mouseDown(button=button)
            
            # Add small pause
            time.sleep(self.human_input.add_pause_variation(0.1))
            
            # Move to end position
            if not self.move_mouse(end_x, end_y, duration=duration):
                pyautogui.mouseUp(button=button)  # Release if movement fails
                return False
            
            # End drag
            pyautogui.mouseUp(button=button)
            
            logger.info(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            
            if self.config["screenshot_on_action"]:
                self.take_screenshot(f"drag_{start_x}_{start_y}_to_{end_x}_{end_y}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to drag: {e}")
            # Make sure mouse is released
            try:
                pyautogui.mouseUp(button=button)
            except:
                pass
            return False
    
    def wait_for_element(self, image_path: str, timeout: float = 10.0, 
                        confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """Wait for a UI element to appear and return its center coordinates"""
        if not self.check_safety():
            return None
        
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if not self.check_safety():
                    return None
                
                try:
                    # Try to find the element
                    location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                    if location:
                        center = pyautogui.center(location)
                        logger.info(f"Found element at ({center.x}, {center.y})")
                        return (center.x, center.y)
                except pyautogui.ImageNotFoundException:
                    pass
                
                time.sleep(0.5)  # Check every 0.5 seconds
            
            logger.warning(f"Element not found within {timeout} seconds: {image_path}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to wait for element: {e}")
            return None
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get current screen size"""
        return pyautogui.size()
    
    def emergency_stop(self):
        """Emergency stop all automation"""
        self.safety_monitor.emergency_stop = True
        logger.warning("Emergency stop activated!")
        
        # Move mouse to failsafe position (top-left corner)
        try:
            pyautogui.moveTo(0, 0, duration=0.1)
        except:
            pass

def main():
    """Test the input controller"""
    print("🤖 Testing Autonomous Input Controller...")
    
    controller = AutonomousInputController()
    
    print(f"Screen size: {controller.get_screen_size()}")
    print("Taking screenshot...")
    
    controller.start_session("test_session")
    controller.take_screenshot("test_screenshot")
    controller.end_session("test_session")
    
    print("✅ Input controller test completed!")
    print(f"📁 Results saved to: {controller.test_results_dir}")

if __name__ == "__main__":
    main() 