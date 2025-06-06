#!/usr/bin/env python3
"""
UX-MIRROR Monitoring Window

Small GUI window that:
- Shows active processes and containers status
- Provides clean shutdown functionality
- Displays recent screenshots with analysis (future feature)
- Non-intrusive monitoring interface
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import subprocess
import psutil
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UXMirrorMonitor:
    """Small monitoring window for UX-MIRROR system"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("UX-MIRROR Monitor")
        self.root.geometry("400x300")
        self.root.resizable(True, True)
        
        # Configure window to stay on top but not always
        self.root.attributes('-topmost', False)
        
        # Tracking variables
        self.running_processes = {}
        self.monitoring_active = False
        self.screenshots_dir = "game_screenshots"
        
        # Create UI
        self.create_ui()
        
        # Start monitoring thread
        self.start_monitoring()
        
        logger.info("UX-MIRROR Monitor initialized")
    
    def create_ui(self):
        """Create the monitoring interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎯 UX-MIRROR Monitor", 
                               font=('Arial', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="5")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Status indicators
        ttk.Label(status_frame, text="Orchestrator:").grid(row=0, column=0, sticky=tk.W)
        self.orchestrator_status = ttk.Label(status_frame, text="⚪ Checking...", foreground="gray")
        self.orchestrator_status.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(status_frame, text="Visual Agent:").grid(row=1, column=0, sticky=tk.W)
        self.visual_status = ttk.Label(status_frame, text="⚪ Checking...", foreground="gray")
        self.visual_status.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(status_frame, text="Game Session:").grid(row=2, column=0, sticky=tk.W)
        self.game_status = ttk.Label(status_frame, text="⚪ Not Started", foreground="gray")
        self.game_status.grid(row=2, column=1, sticky=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="🚀 Start Agents", 
                                      command=self.start_agents)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="🛑 Stop All", 
                                     command=self.stop_all_processes)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.game_button = ttk.Button(button_frame, text="🎮 Start Game Test", 
                                     command=self.start_game_testing)
        self.game_button.pack(side=tk.LEFT)
        
        # Recent activity log
        log_frame = ttk.LabelFrame(main_frame, text="Recent Activity", padding="5")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.activity_log = scrolledtext.ScrolledText(log_frame, height=8, width=50)
        self.activity_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(3, weight=1)
        
        # Add initial log message
        self.log_activity("🎯 UX-MIRROR Monitor started")
    
    def start_monitoring(self):
        """Start the background monitoring thread"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        self.monitor_thread.start()
    
    def monitor_processes(self):
        """Background thread to monitor running processes"""
        while self.monitoring_active:
            try:
                # Check for UX-MIRROR related processes
                self.check_process_status()
                time.sleep(2)  # Check every 2 seconds
            except Exception as e:
                logger.error(f"Error in monitoring: {e}")
                time.sleep(5)
    
    def check_process_status(self):
        """Check status of UX-MIRROR processes"""
        try:
            # Check for orchestrator process
            orchestrator_running = self.is_process_running("core_orchestrator.py")
            self.update_status_indicator(self.orchestrator_status, orchestrator_running, "Orchestrator")
            
            # Check for visual agent process
            visual_running = self.is_process_running("visual_analysis_agent.py")
            self.update_status_indicator(self.visual_status, visual_running, "Visual Agent")
            
            # Check for game testing process
            game_running = self.is_process_running("game_testing_session.py")
            self.update_status_indicator(self.game_status, game_running, "Game Session")
            
        except Exception as e:
            logger.error(f"Error checking process status: {e}")
    
    def is_process_running(self, script_name: str) -> bool:
        """Check if a specific Python script is running"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if script_name in cmdline and 'python' in cmdline.lower():
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception:
            return False
    
    def update_status_indicator(self, label_widget, is_running: bool, component_name: str):
        """Update status indicator for a component"""
        if is_running:
            label_widget.config(text="🟢 Running", foreground="green")
        else:
            label_widget.config(text="⚪ Stopped", foreground="gray")
    
    def start_agents(self):
        """Start the multi-agent system"""
        try:
            self.log_activity("🚀 Starting multi-agent system...")
            
            # Start orchestrator
            subprocess.Popen([
                'python', 'agents/core_orchestrator.py',
                '--host', 'localhost', '--port', '8765'
            ], cwd=os.getcwd())
            
            # Wait a moment then start visual agent
            self.root.after(3000, self.start_visual_agent)
            
        except Exception as e:
            self.log_activity(f"❌ Error starting agents: {e}")
    
    def start_visual_agent(self):
        """Start the visual analysis agent"""
        try:
            subprocess.Popen([
                'python', 'agents/visual_analysis_agent.py',
                '--orchestrator-host', 'localhost',
                '--orchestrator-port', '8765'
            ], cwd=os.getcwd())
            
            self.log_activity("✅ Agents started successfully")
            
        except Exception as e:
            self.log_activity(f"❌ Error starting visual agent: {e}")
    
    def start_game_testing(self):
        """Start game testing session"""
        try:
            self.log_activity("🎮 Starting game testing session...")
            
            # Start game testing in separate process
            subprocess.Popen([
                'python', 'cli/main.py', 'game', 
                '--iterations', '6', '--feedback-ratio', '3'
            ], cwd=os.getcwd())
            
            self.log_activity("✅ Game testing session started")
            
        except Exception as e:
            self.log_activity(f"❌ Error starting game testing: {e}")
    
    def stop_all_processes(self):
        """Stop all UX-MIRROR related processes"""
        try:
            self.log_activity("🛑 Stopping all processes...")
            
            processes_stopped = 0
            
            # Find and terminate UX-MIRROR processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        ux_mirror_scripts = [
                            'core_orchestrator.py',
                            'visual_analysis_agent.py', 
                            'game_testing_session.py',
                            'metrics_intelligence.py'
                        ]
                        
                        for script in ux_mirror_scripts:
                            if script in cmdline and 'python' in cmdline.lower():
                                proc.terminate()
                                processes_stopped += 1
                                self.log_activity(f"🔄 Stopped {script}")
                                break
                                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if processes_stopped > 0:
                self.log_activity(f"✅ Stopped {processes_stopped} processes")
            else:
                self.log_activity("ℹ️ No UX-MIRROR processes found")
                
            # Wait a moment for processes to clean up
            self.root.after(2000, self.verify_cleanup)
            
        except Exception as e:
            self.log_activity(f"❌ Error stopping processes: {e}")
    
    def verify_cleanup(self):
        """Verify that processes have been cleaned up"""
        remaining = []
        try:
            for proc in psutil.process_iter(['pid', 'cmdline']):
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    ux_mirror_scripts = [
                        'core_orchestrator.py',
                        'visual_analysis_agent.py',
                        'game_testing_session.py'
                    ]
                    for script in ux_mirror_scripts:
                        if script in cmdline and 'python' in cmdline.lower():
                            remaining.append(script)
                            
            if remaining:
                self.log_activity(f"⚠️ Some processes still running: {', '.join(remaining)}")
            else:
                self.log_activity("✅ All processes cleaned up successfully")
                
        except Exception as e:
            self.log_activity(f"Error verifying cleanup: {e}")
    
    def log_activity(self, message: str):
        """Add message to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # Update UI in main thread
        self.root.after(0, lambda: self.append_to_log(log_message))
    
    def append_to_log(self, message: str):
        """Append message to log widget"""
        self.activity_log.insert(tk.END, message)
        self.activity_log.see(tk.END)
        
        # Keep log size manageable (last 100 lines)
        lines = self.activity_log.get("1.0", tk.END).split('\n')
        if len(lines) > 100:
            self.activity_log.delete("1.0", f"{len(lines)-100}.0")
    
    def on_closing(self):
        """Handle window closing"""
        try:
            self.log_activity("🔄 Shutting down monitor...")
            self.monitoring_active = False
            
            # Stop all processes when closing
            self.stop_all_processes()
            
            # Give processes time to clean up
            self.root.after(2000, self.root.destroy)
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.root.destroy()
    
    def run(self):
        """Start the monitoring window"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

# Future extension for screenshot display
class ScreenshotViewer:
    """Future feature: Display recent screenshots with analysis"""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.screenshots_dir = Path("game_screenshots")
        
    def update_screenshot_display(self):
        """Update the screenshot display with latest analysis"""
        # Future implementation:
        # - Load latest screenshot
        # - Show AI analysis description
        # - Display metrics overlay
        pass
    
    def get_latest_screenshot(self) -> Optional[Path]:
        """Get the most recent screenshot"""
        if not self.screenshots_dir.exists():
            return None
            
        screenshots = list(self.screenshots_dir.glob("*.png"))
        if not screenshots:
            return None
            
        return max(screenshots, key=os.path.getctime)

def main():
    """Run the monitoring window"""
    try:
        monitor = UXMirrorMonitor()
        monitor.run()
    except KeyboardInterrupt:
        print("Monitor interrupted by user")
    except Exception as e:
        print(f"Error running monitor: {e}")

if __name__ == "__main__":
    main() 