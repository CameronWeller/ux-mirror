#!/usr/bin/env python3
"""
UX-MIRROR Standalone Launcher

One-click startup for intelligent UX analysis of any application.
Features:
- Application detection and targeting
- Non-intrusive background analysis
- Adaptive feedback engine
- Cursor integration ready
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
import psutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import time

# UX-MIRROR imports
try:
    from core.port_manager import get_port_manager, PortManager
    from core.adaptive_feedback import AdaptiveFeedbackEngine, UserEngagementAction
    from agents.core_orchestrator import CoreOrchestrator
    from agents.visual_analysis_agent import VisualAnalysisAgent
    from game_testing_session import GameUXTestingController
except ImportError as e:
    print(f"Warning: Could not import UX-MIRROR modules: {e}")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApplicationDetector:
    """Detects and categorizes running applications for UX analysis"""
    
    def __init__(self):
        self.app_categories = {
            'games': {
                'keywords': ['game', 'unity', 'unreal', 'pygame', 'steam'],
                'extensions': ['.exe'],
                'processes': ['UnityPlayer.dll', 'UE4Game', 'steam.exe']
            },
            'productivity': {
                'keywords': ['office', 'word', 'excel', 'notepad', 'code', 'visual studio'],
                'extensions': ['.exe'],
                'processes': ['winword.exe', 'excel.exe', 'code.exe', 'devenv.exe']
            },
            'web_browsers': {
                'keywords': ['chrome', 'firefox', 'edge', 'safari', 'browser'],
                'extensions': ['.exe'],
                'processes': ['chrome.exe', 'firefox.exe', 'msedge.exe']
            },
            'development': {
                'keywords': ['code', 'studio', 'intellij', 'cursor', 'atom'],
                'extensions': ['.exe'],
                'processes': ['code.exe', 'cursor.exe', 'idea64.exe']
            }
        }
    
    def detect_applications(self) -> List[Dict[str, Any]]:
        """Detect running applications suitable for UX analysis"""
        applications = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'memory_info']):
                try:
                    pinfo = proc.info
                    if not pinfo['name'] or not pinfo['exe']:
                        continue
                    
                    # Skip system processes
                    if pinfo['name'].lower() in ['system', 'svchost.exe', 'dwm.exe', 'explorer.exe']:
                        continue
                    
                    # Categorize the application
                    category = self._categorize_application(pinfo)
                    if category:
                        app_info = {
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'exe_path': pinfo['exe'],
                            'category': category,
                            'memory_mb': pinfo['memory_info'].rss / 1024 / 1024 if pinfo['memory_info'] else 0,
                            'display_name': self._create_display_name(pinfo)
                        }
                        applications.append(app_info)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            logger.error(f"Error detecting applications: {e}")
        
        # Sort by memory usage (larger apps first)
        applications.sort(key=lambda x: x['memory_mb'], reverse=True)
        
        return applications
    
    def _categorize_application(self, pinfo: Dict) -> Optional[str]:
        """Categorize an application based on its properties"""
        name = pinfo['name'].lower()
        exe_path = pinfo['exe'].lower() if pinfo['exe'] else ''
        
        for category, criteria in self.app_categories.items():
            # Check by keywords
            for keyword in criteria['keywords']:
                if keyword in name or keyword in exe_path:
                    return category
            
            # Check by specific process names
            if name in [p.lower() for p in criteria['processes']]:
                return category
        
        # Default category for GUI applications
        if '.exe' in exe_path and 'windows' not in exe_path and 'system32' not in exe_path:
            return 'other'
        
        return None
    
    def _create_display_name(self, pinfo: Dict) -> str:
        """Create a user-friendly display name"""
        name = pinfo['name']
        if name.endswith('.exe'):
            name = name[:-4]
        
        # Capitalize and clean up
        name = name.replace('_', ' ').replace('-', ' ').title()
        
        # Add memory info
        memory_mb = pinfo['memory_info'].rss / 1024 / 1024 if pinfo['memory_info'] else 0
        return f"{name} ({memory_mb:.0f} MB)"

class UXMirrorLauncher:
    """Main launcher window for UX-MIRROR"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("UX-MIRROR - Intelligent UX Analysis")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize components
        self.app_detector = ApplicationDetector()
        self.port_manager = get_port_manager()
        self.adaptive_engine = AdaptiveFeedbackEngine()
        
        # State
        self.selected_app = None
        self.analysis_running = False
        self.orchestrator = None
        self.visual_agent = None
        self.session_controller = None
        
        # Create UI
        self.create_ui()
        
        # Auto-detect applications
        self.refresh_applications()
        
        logger.info("UX-MIRROR Launcher initialized")
    
    def create_ui(self):
        """Create the launcher interface"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🎯 UX-MIRROR", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(header_frame, text="Intelligent UX Analysis for Any Application", 
                                 font=('Arial', 10), foreground='gray')
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Application selection section
        app_frame = ttk.LabelFrame(main_frame, text="Target Application", padding="10")
        app_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        app_frame.columnconfigure(0, weight=1)
        app_frame.rowconfigure(1, weight=1)
        
        # App selection controls
        controls_frame = ttk.Frame(app_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        controls_frame.columnconfigure(1, weight=1)
        
        ttk.Label(controls_frame, text="Select application to analyze:").grid(row=0, column=0, sticky=tk.W)
        
        self.refresh_button = ttk.Button(controls_frame, text="🔄 Refresh", 
                                       command=self.refresh_applications)
        self.refresh_button.grid(row=0, column=2, padx=(10, 0))
        
        # Application list
        list_frame = ttk.Frame(app_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Create treeview for applications
        columns = ('name', 'category', 'memory', 'pid')
        self.app_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=8)
        
        # Configure columns
        self.app_tree.heading('#0', text='Application')
        self.app_tree.heading('name', text='Process Name')
        self.app_tree.heading('category', text='Category')
        self.app_tree.heading('memory', text='Memory')
        self.app_tree.heading('pid', text='PID')
        
        self.app_tree.column('#0', width=200)
        self.app_tree.column('name', width=150)
        self.app_tree.column('category', width=100)
        self.app_tree.column('memory', width=80)
        self.app_tree.column('pid', width=60)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.app_tree.yview)
        self.app_tree.configure(yscrollcommand=scrollbar.set)
        
        self.app_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind selection event
        self.app_tree.bind('<<TreeviewSelect>>', self.on_app_selected)
        
        # Analysis configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Analysis Configuration", padding="10")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        config_frame.columnconfigure(1, weight=1)
        
        # Analysis mode
        ttk.Label(config_frame, text="Analysis Mode:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.analysis_mode = tk.StringVar(value="adaptive")
        mode_frame = ttk.Frame(config_frame)
        mode_frame.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        ttk.Radiobutton(mode_frame, text="Adaptive (Recommended)", 
                       variable=self.analysis_mode, value="adaptive").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Continuous", 
                       variable=self.analysis_mode, value="continuous").pack(side=tk.LEFT, padx=(20, 0))
        ttk.Radiobutton(mode_frame, text="One-Shot", 
                       variable=self.analysis_mode, value="oneshot").pack(side=tk.LEFT, padx=(20, 0))
        
        # Analysis options
        ttk.Label(config_frame, text="Options:").grid(row=1, column=0, sticky=tk.W, pady=(5, 5))
        options_frame = ttk.Frame(config_frame)
        options_frame.grid(row=1, column=1, sticky=tk.W, pady=(5, 5))
        
        self.capture_user_input = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Capture user input", 
                       variable=self.capture_user_input).pack(side=tk.LEFT)
        
        self.show_analysis_overlay = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Show analysis overlay", 
                       variable=self.show_analysis_overlay).pack(side=tk.LEFT, padx=(20, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        self.start_button = ttk.Button(button_frame, text="🚀 Start Analysis", 
                                     command=self.start_analysis, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="🛑 Stop Analysis", 
                                    command=self.stop_analysis, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.feedback_button = ttk.Button(button_frame, text="💬 Provide Feedback", 
                                        command=self.open_feedback_dialog, state='disabled')
        self.feedback_button.pack(side=tk.LEFT)
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Analysis Status", padding="10")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(1, weight=1)
        
        # Status info
        self.status_text = tk.StringVar(value="Ready to start analysis")
        status_label = ttk.Label(status_frame, textvariable=self.status_text)
        status_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log area
        self.log_text = tk.Text(status_frame, height=6, wrap=tk.WORD, 
                               font=('Consolas', 9), bg='#f8f8f8')
        self.log_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_scroll = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        log_scroll.grid(row=2, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(4, weight=1)
        
        # Initial log message
        self.log_message("🎯 UX-MIRROR Launcher ready")
    
    def refresh_applications(self):
        """Refresh the list of available applications"""
        self.log_message("🔄 Detecting applications...")
        
        # Clear existing items
        for item in self.app_tree.get_children():
            self.app_tree.delete(item)
        
        # Get applications
        apps = self.app_detector.detect_applications()
        
        # Populate tree
        category_items = {}
        
        for app in apps:
            category = app['category']
            
            # Create category if not exists
            if category not in category_items:
                category_icon = {'games': '🎮', 'productivity': '💼', 'web_browsers': '🌐', 
                               'development': '💻', 'other': '📱'}.get(category, '📱')
                category_items[category] = self.app_tree.insert('', 'end', 
                    text=f"{category_icon} {category.replace('_', ' ').title()}", 
                    open=True)
            
            # Add application
            app_icon = {'games': '🎯', 'productivity': '📊', 'web_browsers': '🌍', 
                       'development': '⚡', 'other': '🔧'}.get(category, '🔧')
            
            self.app_tree.insert(category_items[category], 'end',
                text=f"{app_icon} {app['display_name']}",
                values=(app['name'], app['category'], f"{app['memory_mb']:.0f} MB", app['pid']),
                tags=(app['pid'],))
        
        self.log_message(f"✅ Found {len(apps)} applications")
    
    def on_app_selected(self, event):
        """Handle application selection"""
        selection = self.app_tree.selection()
        if selection:
            item = self.app_tree.item(selection[0])
            if item['tags']:  # This is an application, not a category
                pid = int(item['tags'][0])
                app_name = item['text'].split(' ', 1)[1]  # Remove emoji
                self.selected_app = {'pid': pid, 'name': app_name}
                self.log_message(f"📱 Selected: {app_name} (PID: {pid})")
                
                # Enable start button
                self.start_button.config(state='normal')
            else:
                self.selected_app = None
                self.start_button.config(state='disabled')
    
    def start_analysis(self):
        """Start UX analysis on selected application"""
        if not self.selected_app:
            messagebox.showerror("Error", "Please select an application first")
            return
        
        if self.analysis_running:
            return
        
        self.analysis_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.feedback_button.config(state='normal')
        self.progress.start()
        
        self.status_text.set("Starting analysis...")
        self.log_message(f"🚀 Starting analysis of {self.selected_app['name']}")
        
        # Start analysis in background thread
        analysis_thread = threading.Thread(target=self._run_analysis, daemon=True)
        analysis_thread.start()
    
    def stop_analysis(self):
        """Stop the current analysis"""
        if not self.analysis_running:
            return
        
        self.analysis_running = False
        self.status_text.set("Stopping analysis...")
        self.log_message("🛑 Stopping analysis...")
        
        # Clean up components
        if self.orchestrator:
            self.orchestrator.running = False
        if self.visual_agent:
            self.visual_agent.running = False
        
        self._reset_ui_state()
    
    def _run_analysis(self):
        """Run analysis in background thread"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Start analysis components
            session_id = f"launcher_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Start adaptive session
            session = self.adaptive_engine.start_session(session_id, {
                'target_app': self.selected_app,
                'analysis_mode': self.analysis_mode.get(),
                'capture_input': self.capture_user_input.get(),
                'show_overlay': self.show_analysis_overlay.get()
            })
            
            # Update status
            self.root.after(0, lambda: self.status_text.set("Analysis running..."))
            self.root.after(0, lambda: self.log_message("✅ Analysis session started"))
            
            # Run analysis loop
            iteration = 0
            while self.analysis_running and iteration < 15:  # Max 15 iterations
                iteration += 1
                
                # Simulate analysis (replace with actual analysis)
                time.sleep(3)  # Simulate analysis time
                
                if not self.analysis_running:
                    break
                
                # Create mock analysis results
                analysis_result = {
                    'quality_score': 0.6 + (iteration * 0.02),
                    'ui_elements_detected': 5 + iteration,
                    'accessibility_issues': ['Issue 1', 'Issue 2'][:max(0, 3-iteration)],
                    'recommendations': [f'Recommendation {i}' for i in range(1, min(4, iteration+1))],
                    'response_time': 0.5 - (iteration * 0.02),
                    'change_score': 0.1 + (iteration * 0.01)
                }
                
                # Update UI
                self.root.after(0, lambda i=iteration: 
                    self.log_message(f"📊 Iteration {i}: Quality {analysis_result['quality_score']:.1%}"))
                
                # Check what action to take based on confidence
                action, context = self.adaptive_engine.determine_action(session_id)
                
                if action == UserEngagementAction.READY_FOR_REVIEW:
                    self.root.after(0, lambda: self._analysis_complete("ready"))
                    break
                elif action == UserEngagementAction.REQUEST_INPUT:
                    self.root.after(0, lambda: self._request_user_input())
                    # Wait for user input or timeout
                    time.sleep(10)  # Simulate waiting
                elif action == UserEngagementAction.IMMEDIATE_ATTENTION:
                    self.root.after(0, lambda: self._analysis_complete("critical"))
                    break
                elif action == UserEngagementAction.SESSION_COMPLETE:
                    self.root.after(0, lambda: self._analysis_complete("complete"))
                    break
            
            if self.analysis_running:
                self.root.after(0, lambda: self._analysis_complete("timeout"))
                
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            self.root.after(0, lambda: self.log_message(f"❌ Analysis error: {e}"))
            self.root.after(0, self._reset_ui_state)
        finally:
            loop.close()
    
    def _analysis_complete(self, reason: str):
        """Handle analysis completion"""
        self.analysis_running = False
        
        messages = {
            'ready': '✅ Analysis complete - Ready for review',
            'critical': '⚠️ Critical issues found - Immediate attention needed',
            'complete': '🏁 Analysis session completed',
            'timeout': '⏰ Analysis completed (max iterations reached)'
        }
        
        self.status_text.set(messages.get(reason, 'Analysis completed'))
        self.log_message(messages.get(reason, 'Analysis completed'))
        
        self._reset_ui_state()
        
        # Show completion dialog
        if reason == 'critical':
            messagebox.showwarning("Critical Issues", 
                "Critical UX issues were detected. Please review the analysis results.")
        else:
            messagebox.showinfo("Analysis Complete", 
                "UX analysis has been completed. Check the log for details.")
    
    def _request_user_input(self):
        """Request user input during analysis"""
        self.log_message("💭 Analysis needs your input - confidence is low")
        self.feedback_button.config(style='Accent.TButton')  # Highlight button
    
    def _reset_ui_state(self):
        """Reset UI to ready state"""
        self.start_button.config(state='normal' if self.selected_app else 'disabled')
        self.stop_button.config(state='disabled')
        self.feedback_button.config(state='disabled', style='TButton')
        self.progress.stop()
        self.status_text.set("Ready to start analysis")
    
    def open_feedback_dialog(self):
        """Open feedback dialog"""
        if not self.analysis_running:
            return
        
        # Simple feedback dialog
        feedback_window = tk.Toplevel(self.root)
        feedback_window.title("Provide Feedback")
        feedback_window.geometry("400x300")
        feedback_window.resizable(False, False)
        
        # Center the window
        feedback_window.transient(self.root)
        feedback_window.grab_set()
        
        ttk.Label(feedback_window, text="How is the UX analysis going?", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Feedback text
        ttk.Label(feedback_window, text="Your feedback:").pack(anchor=tk.W, padx=20)
        feedback_text = tk.Text(feedback_window, height=6, width=45)
        feedback_text.pack(padx=20, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(feedback_window)
        button_frame.pack(pady=10)
        
        def submit_feedback():
            feedback = feedback_text.get(1.0, tk.END).strip()
            if feedback:
                self.log_message(f"💬 Feedback received: {feedback[:50]}...")
                # In real implementation, add to adaptive engine
            feedback_window.destroy()
        
        ttk.Button(button_frame, text="Submit", command=submit_feedback).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=feedback_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def log_message(self, message: str):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Limit log size
        if int(self.log_text.index('end-1c').split('.')[0]) > 100:
            self.log_text.delete(1.0, "10.0")
    
    def run(self):
        """Run the launcher"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        if self.analysis_running:
            if messagebox.askokcancel("Quit", "Analysis is running. Do you want to quit?"):
                self.stop_analysis()
                self.root.after(1000, self.root.quit)  # Give time for cleanup
        else:
            self.root.quit()

def main():
    """Main entry point"""
    try:
        launcher = UXMirrorLauncher()
        launcher.run()
    except Exception as e:
        logger.error(f"Launcher error: {e}")
        messagebox.showerror("Error", f"Failed to start UX-MIRROR Launcher: {e}")

if __name__ == "__main__":
    main() 