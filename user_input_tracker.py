#!/usr/bin/env python3
"""
UX Mirror - User Input Tracker
Tracks mouse and keyboard input to provide context for UI analysis
"""

import json
import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Platform-specific imports
try:
    from pynput import keyboard, mouse
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logging.warning("pynput not available. Install with: pip install pynput")

logger = logging.getLogger(__name__)

@dataclass
class InputEvent:
    """Represents a user input event"""
    timestamp: float
    event_type: str  # 'click', 'key', 'move', 'scroll'
    data: Dict
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'event_type': self.event_type,
            'data': self.data
        }

class UserInputTracker:
    """Tracks user mouse and keyboard input for game UI analysis"""
    
    def __init__(self, max_events: int = 1000):
        self.max_events = max_events
        self.events = deque(maxlen=max_events)
        self.tracking_enabled = False
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Activity summary
        self.click_heatmap = {}  # Position -> count
        self.key_frequency = {}   # Key -> count
        self.last_activity = time.time()
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info("User input tracker initialized")
    
    def start_tracking(self):
        """Start tracking user input"""
        if not PYNPUT_AVAILABLE:
            logger.error("Cannot start tracking - pynput not available")
            return False
        
        if self.tracking_enabled:
            logger.warning("Tracking already enabled")
            return True
        
        self.tracking_enabled = True
        
        # Start mouse listener
        self.mouse_listener = mouse.Listener(
            on_click=self._on_click,
            on_move=self._on_move,
            on_scroll=self._on_scroll
        )
        self.mouse_listener.start()
        
        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.start()
        
        logger.info("User input tracking started")
        return True
    
    def stop_tracking(self):
        """Stop tracking user input"""
        self.tracking_enabled = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        logger.info("User input tracking stopped")
    
    def _add_event(self, event: InputEvent):
        """Add event to history (thread-safe)"""
        with self.lock:
            self.events.append(event)
            self.last_activity = event.timestamp
    
    def _on_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if not self.tracking_enabled:
            return
        
        self._add_event(InputEvent(
            timestamp=time.time(),
            event_type='click',
            data={
                'x': x,
                'y': y,
                'button': str(button),
                'pressed': pressed
            }
        ))
        
        # Update heatmap for pressed events
        if pressed:
            self._update_click_heatmap(x, y)
    
    def _update_click_heatmap(self, x: int, y: int):
        """Update click position heatmap"""
        grid_x, grid_y = x // 50, y // 50  # 50px grid
        key = f"{grid_x},{grid_y}"
        
        with self.lock:
            self.click_heatmap[key] = self.click_heatmap.get(key, 0) + 1
    
    def _on_move(self, x, y):
        """Handle mouse move events (sampled)"""
        if not self.tracking_enabled:
            return
        
        # Sample movement (don't record every pixel)
        current_time = time.time()
        if hasattr(self, '_last_move_time') and current_time - self._last_move_time < 0.1:
            return
        
        self._last_move_time = current_time
        self._add_event(InputEvent(
            timestamp=current_time,
            event_type='move',
            data={'x': x, 'y': y}
        ))
    
    def _on_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events"""
        if not self.tracking_enabled:
            return
        
        self._add_event(InputEvent(
            timestamp=time.time(),
            event_type='scroll',
            data={'x': x, 'y': y, 'dx': dx, 'dy': dy}
        ))
    
    def _handle_key_event(self, key, action: str):
        """Handle keyboard events"""
        if not self.tracking_enabled:
            return
        
        try:
            key_name = key.char if hasattr(key, 'char') else str(key)
        except AttributeError:
            key_name = str(key)
        
        self._add_event(InputEvent(
            timestamp=time.time(),
            event_type='key',
            data={'key': key_name, 'action': action}
        ))
        
        # Update frequency for press events
        if action == 'press':
            with self.lock:
                self.key_frequency[key_name] = self.key_frequency.get(key_name, 0) + 1
    
    def _on_key_press(self, key):
        """Handle key press events"""
        self._handle_key_event(key, 'press')
    
    def _on_key_release(self, key):
        """Handle key release events"""
        self._handle_key_event(key, 'release')
    
    def get_recent_activity(self, seconds: float = 10.0) -> Dict:
        """Get summary of recent user activity"""
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - seconds
            
            recent_events = [
                e.to_dict() for e in self.events 
                if e.timestamp > cutoff_time
            ]
            
            # Calculate activity metrics
            click_count = sum(1 for e in recent_events 
                            if e['event_type'] == 'click' and 
                            e['data'].get('pressed', False))
            
            key_count = sum(1 for e in recent_events 
                          if e['event_type'] == 'key' and 
                          e['data'].get('action') == 'press')
            
            # Find most clicked area
            recent_clicks = {}
            for e in recent_events:
                if e['event_type'] == 'click' and e['data'].get('pressed'):
                    x, y = e['data']['x'], e['data']['y']
                    grid_x, grid_y = x // 50, y // 50
                    key = f"{grid_x},{grid_y}"
                    recent_clicks[key] = recent_clicks.get(key, 0) + 1
            
            hotspot = max(recent_clicks.items(), key=lambda x: x[1])[0] if recent_clicks else None
            
            return {
                'time_window': seconds,
                'total_events': len(recent_events),
                'click_count': click_count,
                'key_count': key_count,
                'activity_rate': len(recent_events) / seconds if seconds > 0 else 0,
                'last_activity': current_time - self.last_activity,
                'click_hotspot': hotspot,
                'most_used_keys': self._get_top_keys(5),
                'events_summary': self._summarize_events(recent_events)
            }
    
    def _get_top_keys(self, n: int = 5) -> List[Tuple[str, int]]:
        """Get most frequently used keys"""
        with self.lock:
            sorted_keys = sorted(
                self.key_frequency.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            return sorted_keys[:n]
    
    def _summarize_events(self, events: List[Dict]) -> Dict:
        """Create a summary of event patterns"""
        if not events:
            return {}
        
        # Group events by type
        event_groups = {}
        for e in events:
            event_type = e['event_type']
            if event_type not in event_groups:
                event_groups[event_type] = []
            event_groups[event_type].append(e)
        
        summary = {}
        
        # Analyze click patterns
        if 'click' in event_groups:
            clicks = event_groups['click']
            double_clicks = self._detect_double_clicks(clicks)
            summary['double_clicks'] = double_clicks
            summary['click_locations'] = [
                {'x': c['data']['x'], 'y': c['data']['y']} 
                for c in clicks if c['data'].get('pressed')
            ][:10]  # Last 10 clicks
        
        # Analyze key patterns
        if 'key' in event_groups:
            keys = event_groups['key']
            summary['key_combos'] = self._detect_key_combos(keys)
        
        return summary
    
    def _detect_double_clicks(self, clicks: List[Dict]) -> int:
        """Detect double-click patterns"""
        double_clicks = 0
        for i in range(1, len(clicks)):
            if (clicks[i]['data'].get('pressed') and 
                clicks[i-1]['data'].get('pressed') and
                clicks[i]['timestamp'] - clicks[i-1]['timestamp'] < 0.5):
                double_clicks += 1
        return double_clicks
    
    def _detect_key_combos(self, keys: List[Dict]) -> List[str]:
        """Detect common key combinations"""
        combos = []
        # Simple detection for ctrl/cmd combinations
        ctrl_held = False
        
        for k in keys:
            key_name = k['data']['key']
            action = k['data']['action']
            
            if 'ctrl' in key_name.lower() or 'cmd' in key_name.lower():
                ctrl_held = action == 'press'
            elif ctrl_held and action == 'press':
                combos.append(f"Ctrl+{key_name}")
        
        return list(set(combos))[:5]  # Top 5 unique combos
    
    def get_click_heatmap(self) -> Dict[str, int]:
        """Get click position heatmap"""
        with self.lock:
            return self.click_heatmap.copy()
    
    def clear_history(self):
        """Clear event history"""
        with self.lock:
            self.events.clear()
            self.click_heatmap.clear()
            self.key_frequency.clear()
        
        logger.info("Input history cleared")
    
    def export_data(self, filepath: str):
        """Export tracking data to file"""
        with self.lock:
            data = {
                'events': [e.to_dict() for e in self.events],
                'click_heatmap': self.click_heatmap,
                'key_frequency': self.key_frequency,
                'export_time': datetime.now().isoformat()
            }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Tracking data exported to {filepath}")

# Singleton instance for easy access
_tracker_instance = None

def get_tracker() -> UserInputTracker:
    """Get singleton tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = UserInputTracker()
    return _tracker_instance

if __name__ == "__main__":
    # Test the tracker
    tracker = get_tracker()
    
    print("Starting input tracking for 10 seconds...")
    print("Press Ctrl+C to stop early")
    tracker.start_tracking()
    
    try:
        # More responsive sleep with progress indication
        for i in range(10):
            time.sleep(1)
            print(f"Tracking... {10-i} seconds remaining")
    except KeyboardInterrupt:
        print("\nStopped by user")
    
    tracker.stop_tracking()
    
    # Get activity summary
    activity = tracker.get_recent_activity()
    print("\nActivity Summary:")
    print(json.dumps(activity, indent=2))
    
    # Export data
    tracker.export_data("input_tracking_test.json")
    print("\nData exported to input_tracking_test.json") 