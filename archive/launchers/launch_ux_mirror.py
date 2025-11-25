#!/usr/bin/env python3
"""
UX-MIRROR + Game Launcher
One-click launcher for UX-MIRROR analysis with target game integration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
import time
from pathlib import Path
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UXMirrorGameLauncher:
    """Enhanced launcher for UX-MIRROR with integrated game launching"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("UX-MIRROR + 3D Game of Life Launcher")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        # Paths
        self.base_path = Path.cwd()
        self.game_path = self.base_path / "game-target"
        self.game_exe = self.game_path / "build_minimal" / "x64" / "Release" / "minimal_vulkan_app.exe"
        self.ux_launcher = self.base_path / "ux_mirror_launcher.py"
        self.config_file = self.base_path / "game_ux_config.json"
        
        # State
        self.game_process = None
        self.ux_process = None
        self.is_analyzing = False
        
        self.create_ui()
        self.check_requirements()
        
    def create_ui(self):
        """Create the launcher interface"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for dark theme
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2E86AB')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10), foreground='#666666')
        style.configure('Status.TLabel', font=('Segoe UI', 9), foreground='#28A745')
        style.configure('Warning.TLabel', font=('Segoe UI', 9), foreground='#DC3545')
        style.configure('Action.TButton', font=('Segoe UI', 10, 'bold'))
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🎯 UX-MIRROR + 3D Game of Life", style="Title.TLabel")
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Intelligent UX Analysis for Gaming Experiences", style="Subtitle.TLabel")
        subtitle_label.pack(pady=(5, 0))
        
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="15")
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.python_status = ttk.Label(status_frame, text="⏳ Checking Python...", style="Status.TLabel")
        self.python_status.pack(anchor=tk.W)
        
        self.deps_status = ttk.Label(status_frame, text="⏳ Checking dependencies...", style="Status.TLabel")
        self.deps_status.pack(anchor=tk.W)
        
        self.game_status = ttk.Label(status_frame, text="⏳ Checking target game...", style="Status.TLabel")
        self.game_status.pack(anchor=tk.W)
        
        self.ux_status = ttk.Label(status_frame, text="⏳ Checking UX-MIRROR...", style="Status.TLabel")
        self.ux_status.pack(anchor=tk.W)
        
        # Launch Options
        options_frame = ttk.LabelFrame(main_frame, text="Launch Options", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Target game info
        game_info_frame = ttk.Frame(options_frame)
        game_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(game_info_frame, text="Target Game:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W)
        ttk.Label(game_info_frame, text="3D Game of Life - Vulkan Edition", style="Status.TLabel").pack(anchor=tk.W, padx=(20, 0))
        ttk.Label(game_info_frame, text="High-performance 3D cellular automata with GPU acceleration", style="Subtitle.TLabel").pack(anchor=tk.W, padx=(20, 0))
        
        # Launch modes
        mode_frame = ttk.LabelFrame(options_frame, text="Launch Modes", padding="10")
        mode_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.launch_mode = tk.StringVar(value="integrated")
        
        # Integrated Mode
        ttk.Radiobutton(mode_frame, text="🚀 Integrated Mode (Recommended)", 
                       variable=self.launch_mode, value="integrated").pack(anchor=tk.W)
        ttk.Label(mode_frame, text="    • Real-time analysis of user interactions", 
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        ttk.Label(mode_frame, text="    • Best for: Active development and live testing", 
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        
        # Game Only Mode
        ttk.Radiobutton(mode_frame, text="🎮 Game Only Mode", 
                       variable=self.launch_mode, value="game").pack(anchor=tk.W, pady=(10, 0))
        ttk.Label(mode_frame, text="    • Launches only the 3D Game of Life", 
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        ttk.Label(mode_frame, text="    • Best for: Pure gaming/application use", 
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        
        # UX Analysis Only Mode
        ttk.Radiobutton(mode_frame, text="🔍 Analysis Only Mode", 
                       variable=self.launch_mode, value="ux").pack(anchor=tk.W, pady=(10, 0))
        ttk.Label(mode_frame, text="    • Launches UX-MIRROR for any application", 
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        ttk.Label(mode_frame, text="    • Best for: Analyzing existing running applications", 
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        
        # Autonomous Testing Mode - Now Available!
        autonomous_radio = ttk.Radiobutton(mode_frame, text="🤖 Autonomous Testing Mode", 
                                         variable=self.launch_mode, value="autonomous")
        autonomous_radio.pack(anchor=tk.W, pady=(10, 0))
        ttk.Label(mode_frame, text="    • VM environment with automated testing", 
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        ttk.Label(mode_frame, text="    • Best for: Continuous integration, overnight testing", 
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        
        # VM Settings (for autonomous mode)
        vm_frame = ttk.LabelFrame(options_frame, text="VM Settings (Autonomous Mode)", padding="10")
        vm_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(vm_frame, text="VM Memory (GB):").pack(anchor=tk.W)
        self.vm_memory = tk.StringVar(value="4")
        memory_frame = ttk.Frame(vm_frame)
        memory_frame.pack(anchor=tk.W, pady=(2, 5))
        ttk.Entry(memory_frame, textvariable=self.vm_memory, width=10).pack(side=tk.LEFT)
        ttk.Label(memory_frame, text="GB (Configurable: 2-8 GB)", style="Subtitle.TLabel").pack(side=tk.LEFT, padx=(5, 0))
        
        # Action Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.launch_button = ttk.Button(button_frame, text="🚀 Launch", 
                                       command=self.launch_action, style="Action.TButton")
        self.launch_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Stop All", 
                                     command=self.stop_all, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="⚙️ Build Game", 
                  command=self.build_game).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📁 Open Reports", 
                  command=self.open_reports).pack(side=tk.RIGHT)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial log message
        self.log("🎯 UX-MIRROR + 3D Game of Life Launcher initialized")
        self.log("📍 Working directory: " + str(self.base_path))
        
    def check_requirements(self):
        """Check system requirements in background"""
        threading.Thread(target=self._check_requirements_thread, daemon=True).start()
        
    def _check_requirements_thread(self):
        """Background thread to check requirements"""
        # Check Python
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.python_status.config(text=f"✅ {version}", style="Status.TLabel")
                self.log(f"✅ Python found: {version}")
            else:
                self.python_status.config(text="❌ Python not working", style="Warning.TLabel")
                self.log("❌ Python check failed")
        except Exception as e:
            self.python_status.config(text="❌ Python error", style="Warning.TLabel")
            self.log(f"❌ Python error: {e}")
        
        # Check dependencies
        try:
            import tkinter, psutil, asyncio
            self.deps_status.config(text="✅ Dependencies OK", style="Status.TLabel")
            self.log("✅ Core dependencies available")
        except ImportError as e:
            self.deps_status.config(text="❌ Missing dependencies", style="Warning.TLabel")
            self.log(f"❌ Missing dependency: {e}")
        
        # Check game
        if self.game_exe.exists():
            self.game_status.config(text="✅ Game ready", style="Status.TLabel")
            self.log("✅ 3D Game of Life executable found")
        else:
            self.game_status.config(text="⚠️ Game needs building", style="Warning.TLabel")
            self.log("⚠️ Game executable not found, build required")
        
        # Check UX-MIRROR
        if self.ux_launcher.exists():
            self.ux_status.config(text="✅ UX-MIRROR ready", style="Status.TLabel")
            self.log("✅ UX-MIRROR launcher found")
        else:
            self.ux_status.config(text="❌ UX-MIRROR missing", style="Warning.TLabel")
            self.log("❌ UX-MIRROR launcher not found")
    
    def launch_action(self):
        """Handle launch button click"""
        mode = self.launch_mode.get()
        
        if mode == "integrated":
            self.launch_integrated()
        elif mode == "game":
            self.launch_game_only()
        elif mode == "ux":
            self.launch_ux_only()
        elif mode == "autonomous":
            self.launch_autonomous()
        else:
            messagebox.showwarning("Unknown Mode", 
                                 "Selected launch mode is not recognized.")
            return
            
        self.launch_button.config(state='disabled')
        self.stop_button.config(state='normal')
    
    def launch_integrated(self):
        """Launch both game and UX-MIRROR in integrated mode"""
        self.log("🚀 Starting integrated launch...")
        
        # First launch the game
        threading.Thread(target=self._launch_game_thread, daemon=True).start()
        
        # Wait a moment then launch UX-MIRROR
        threading.Thread(target=self._launch_ux_delayed, daemon=True).start()
    
    def launch_game_only(self):
        """Launch only the game"""
        self.log("🎮 Launching 3D Game of Life...")
        threading.Thread(target=self._launch_game_thread, daemon=True).start()
    
    def launch_ux_only(self):
        """Launch only UX-MIRROR"""
        self.log("🔍 Launching UX-MIRROR...")
        threading.Thread(target=self._launch_ux_thread, daemon=True).start()
    
    def launch_autonomous(self):
        """Launch autonomous testing mode"""
        self.log("🤖 Starting Autonomous Testing Mode...")
        
        # Check if autonomous framework exists
        autonomous_path = Path("ux_mirror_autonomous")
        if not autonomous_path.exists():
            messagebox.showerror("Autonomous Testing Error", 
                               "Autonomous testing framework not found!\n"
                               "Please run the setup script first.")
            self.launch_button.config(state='normal')
            self.stop_button.config(state='disabled')
            return
        
        # Show test options dialog
        self.show_autonomous_options()
    
    def _launch_game_thread(self):
        """Launch game in background thread"""
        try:
            if not self.game_exe.exists():
                self.log("❌ Game executable not found. Building first...")
                self.build_game()
                return
            
            self.log(f"🎮 Starting: {self.game_exe}")
            self.game_process = subprocess.Popen([str(self.game_exe)], 
                                               cwd=str(self.game_path))
            self.log("✅ 3D Game of Life started successfully")
            
        except Exception as e:
            self.log(f"❌ Failed to launch game: {e}")
    
    def _launch_ux_thread(self):
        """Launch UX-MIRROR in background thread"""
        try:
            if not self.ux_launcher.exists():
                self.log("❌ UX-MIRROR launcher not found")
                return
            
            self.log(f"🔍 Starting UX-MIRROR: {self.ux_launcher}")
            self.ux_process = subprocess.Popen([sys.executable, str(self.ux_launcher)])
            self.log("✅ UX-MIRROR started successfully")
            
        except Exception as e:
            self.log(f"❌ Failed to launch UX-MIRROR: {e}")
    
    def _launch_ux_delayed(self):
        """Launch UX-MIRROR with a delay for integrated mode"""
        time.sleep(3)  # Wait for game to initialize
        self._launch_ux_thread()
    
    def show_autonomous_options(self):
        """Show autonomous testing options dialog"""
        options_window = tk.Toplevel(self.root)
        options_window.title("Autonomous Testing Options")
        options_window.geometry("500x400")
        options_window.resizable(False, False)
        options_window.transient(self.root)
        options_window.grab_set()
        
        # Center the window
        options_window.update_idletasks()
        x = (options_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (options_window.winfo_screenheight() // 2) - (400 // 2)
        options_window.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(options_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="🤖 Autonomous Testing Options", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Test suite options
        self.test_suite_var = tk.StringVar(value="basic")
        
        ttk.Label(main_frame, text="Select Test Suite:", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        
        ttk.Radiobutton(main_frame, text="🧪 Basic Test Suite (Quick - ~5 minutes)", 
                       variable=self.test_suite_var, value="basic").pack(anchor=tk.W, pady=2)
        ttk.Label(main_frame, text="    • Essential functionality tests", 
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        
        ttk.Radiobutton(main_frame, text="🚀 Full Test Suite (Comprehensive - ~30 minutes)", 
                       variable=self.test_suite_var, value="full").pack(anchor=tk.W, pady=2)
        ttk.Label(main_frame, text="    • All test categories, detailed analysis", 
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        
        ttk.Radiobutton(main_frame, text="⚡ Performance Tests Only (~10 minutes)", 
                       variable=self.test_suite_var, value="performance").pack(anchor=tk.W, pady=2)
        ttk.Label(main_frame, text="    • FPS, memory, response time analysis", 
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        
        ttk.Radiobutton(main_frame, text="🎮 Game Logic Tests Only (~15 minutes)", 
                       variable=self.test_suite_var, value="game_logic").pack(anchor=tk.W, pady=2)
        ttk.Label(main_frame, text="    • 3D Game of Life specific testing", 
                 style="Subtitle.TLabel").pack(anchor=tk.W)
        
        # VM Settings frame
        vm_frame = ttk.LabelFrame(main_frame, text="VM Configuration", padding="10")
        vm_frame.pack(fill=tk.X, pady=(20, 10))
        
        memory_frame = ttk.Frame(vm_frame)
        memory_frame.pack(fill=tk.X)
        
        ttk.Label(memory_frame, text="Memory:").pack(side=tk.LEFT)
        memory_spinbox = ttk.Spinbox(memory_frame, from_=2, to=8, 
                                   textvariable=self.vm_memory, width=5)
        memory_spinbox.pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(memory_frame, text="GB").pack(side=tk.LEFT)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Testing Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(10, 20))
        
        ttk.Label(status_frame, text="🔍 Framework: Phase 2 Input Automation", 
                 style="Status.TLabel").pack(anchor=tk.W)
        ttk.Label(status_frame, text="🖥️ Target: 3D Game of Life (Vulkan)", 
                 style="Status.TLabel").pack(anchor=tk.W)
        ttk.Label(status_frame, text="⚙️ Features: PyAutoGUI, Computer Vision", 
                 style="Status.TLabel").pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="🚀 Start Testing", 
                  command=lambda: self.start_autonomous_testing(options_window)).pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="📊 View Previous Results", 
                  command=self.view_autonomous_results).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.cancel_autonomous).pack(side=tk.RIGHT)
    
    def start_autonomous_testing(self, options_window):
        """Start the autonomous testing process"""
        options_window.destroy()
        
        test_suite = self.test_suite_var.get()
        vm_memory = self.vm_memory.get()
        
        self.log(f"🤖 Starting {test_suite} test suite with {vm_memory}GB VM memory...")
        
        # Start autonomous testing in background thread
        threading.Thread(target=self._run_autonomous_tests, 
                        args=(test_suite, vm_memory), daemon=True).start()
    
    def _run_autonomous_tests(self, test_suite, vm_memory):
        """Run autonomous tests in background thread"""
        try:
            # Import autonomous testing framework
            import sys
            sys.path.append(str(Path("ux_mirror_autonomous")))
            
            from ux_mirror_autonomous.run_tests import main as run_autonomous_tests
            
            # Configure test parameters
            test_config = {
                "test_suite": test_suite,
                "vm_memory": vm_memory,
                "target_application": "3d_game_of_life"
            }
            
            self.log("📋 Autonomous testing configuration:")
            self.log(f"   • Test Suite: {test_suite}")
            self.log(f"   • VM Memory: {vm_memory}GB")
            self.log(f"   • Target: 3D Game of Life")
            
            # Run the tests
            result = run_autonomous_tests(test_config)
            
            if result and result.get("success"):
                self.log("✅ Autonomous testing completed successfully!")
                self.log(f"📊 Results: {result.get('pass_count', 0)}/{result.get('total_count', 0)} tests passed")
                
                # Show results dialog
                self.root.after(0, self.show_test_results, result)
            else:
                self.log("❌ Autonomous testing failed or was interrupted")
                
        except ImportError as e:
            self.log(f"❌ Failed to import autonomous testing framework: {e}")
            self.log("💡 Please ensure Phase 2 dependencies are installed")
        except Exception as e:
            self.log(f"❌ Autonomous testing error: {e}")
        finally:
            # Re-enable launch button
            self.root.after(0, lambda: (
                self.launch_button.config(state='normal'),
                self.stop_button.config(state='disabled')
            ))
    
    def show_test_results(self, results):
        """Show autonomous test results in a dialog"""
        results_window = tk.Toplevel(self.root)
        results_window.title("Autonomous Test Results")
        results_window.geometry("600x500")
        results_window.resizable(True, True)
        
        main_frame = ttk.Frame(results_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results summary
        ttk.Label(main_frame, text="🧪 Test Results Summary", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=(0, 15))
        
        summary_frame = ttk.LabelFrame(main_frame, text="Summary", padding="10")
        summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        pass_count = results.get('pass_count', 0)
        total_count = results.get('total_count', 0)
        pass_rate = (pass_count / total_count * 100) if total_count > 0 else 0
        
        ttk.Label(summary_frame, text=f"✅ Passed: {pass_count}/{total_count} ({pass_rate:.1f}%)", 
                 style="Status.TLabel").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"⏱️ Duration: {results.get('total_duration', 0):.1f} seconds", 
                 style="Status.TLabel").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"📸 Screenshots: {results.get('total_screenshots', 0)}", 
                 style="Status.TLabel").pack(anchor=tk.W)
        
        if results.get('average_fps'):
            ttk.Label(summary_frame, text=f"🎮 Average FPS: {results['average_fps']:.1f}", 
                     style="Status.TLabel").pack(anchor=tk.W)
        
        # Detailed results
        details_frame = ttk.LabelFrame(main_frame, text="Detailed Results", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for detailed results
        tree = ttk.Treeview(details_frame, columns=('result', 'duration'), show='tree headings')
        tree.heading('#0', text='Test')
        tree.heading('result', text='Result')
        tree.heading('duration', text='Duration (s)')
        
        scrollbar_tree = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar_tree.set)
        
        # Populate results
        for test_result in results.get('test_results', []):
            result_icon = "✅" if test_result['result'] == 'pass' else "❌"
            tree.insert('', 'end', 
                       text=f"{result_icon} {test_result['scenario_name']}", 
                       values=(test_result['result'], f"{test_result['metrics']['duration']:.2f}"))
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_tree.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(button_frame, text="📁 Open Full Report", 
                  command=lambda: self.open_autonomous_reports()).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close", 
                  command=results_window.destroy).pack(side=tk.RIGHT)
    
    def view_autonomous_results(self):
        """View previous autonomous test results"""
        self.log("📊 Opening autonomous test results...")
        reports_dir = Path("ux_mirror_autonomous") / "test_results"
        reports_dir.mkdir(exist_ok=True, parents=True)
        
        try:
            import os
            os.startfile(str(reports_dir))  # Windows
        except AttributeError:
            import subprocess
            try:
                subprocess.run(["open", str(reports_dir)])  # macOS
            except:
                subprocess.run(["xdg-open", str(reports_dir)])  # Linux
    
    def open_autonomous_reports(self):
        """Open autonomous testing reports directory"""
        self.view_autonomous_results()
    
    def cancel_autonomous(self):
        """Cancel autonomous testing setup"""
        self.launch_button.config(state='normal')
        self.stop_button.config(state='disabled')
    
    def stop_all(self):
        """Stop all launched processes"""
        self.log("⏹️ Stopping all processes...")
        
        stopped = False
        
        if self.game_process:
            try:
                self.game_process.terminate()
                self.game_process = None
                self.log("✅ Game process stopped")
                stopped = True
            except Exception as e:
                self.log(f"⚠️ Error stopping game: {e}")
        
        if self.ux_process:
            try:
                self.ux_process.terminate()
                self.ux_process = None
                self.log("✅ UX-MIRROR process stopped")
                stopped = True
            except Exception as e:
                self.log(f"⚠️ Error stopping UX-MIRROR: {e}")
        
        if not stopped:
            self.log("ℹ️ No processes to stop")
        
        self.launch_button.config(state='normal')
        self.stop_button.config(state='disabled')
    
    def build_game(self):
        """Build the target game"""
        self.log("🔨 Building 3D Game of Life...")
        threading.Thread(target=self._build_game_thread, daemon=True).start()
    
    def _build_game_thread(self):
        """Build game in background thread"""
        try:
            if not self.game_path.exists():
                self.log("❌ Game source directory not found")
                return
            
            build_dir = self.game_path / "build_minimal"
            build_dir.mkdir(exist_ok=True)
            
            # Configure
            self.log("📝 Configuring CMake...")
            cmake_cmd = [
                "cmake", "-S", str(self.game_path), "-B", str(build_dir),
                "-DCMAKE_BUILD_TYPE=Release"
            ]
            
            vcpkg_toolchain = self.game_path / "vcpkg" / "scripts" / "buildsystems" / "vcpkg.cmake"
            if vcpkg_toolchain.exists():
                cmake_cmd.extend(["-DCMAKE_TOOLCHAIN_FILE", str(vcpkg_toolchain)])
            
            result = subprocess.run(cmake_cmd, cwd=str(build_dir), 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log(f"❌ CMake configure failed: {result.stderr}")
                return
            
            # Build
            self.log("🔨 Building project...")
            build_cmd = ["cmake", "--build", ".", "--config", "Release"]
            result = subprocess.run(build_cmd, cwd=str(build_dir),
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Game built successfully")
                self.game_status.config(text="✅ Game ready", style="Status.TLabel")
            else:
                self.log(f"❌ Build failed: {result.stderr}")
                
        except Exception as e:
            self.log(f"❌ Build error: {e}")
    
    def open_reports(self):
        """Open the reports directory"""
        reports_dir = self.base_path / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        try:
            os.startfile(str(reports_dir))  # Windows
        except AttributeError:
            subprocess.run(["open", str(reports_dir)])  # macOS
        except:
            subprocess.run(["xdg-open", str(reports_dir)])  # Linux
    
    def log(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # Update UI in main thread
        self.root.after(0, self._append_log, log_message)
        
        # Also log to console
        logger.info(message)
    
    def _append_log(self, message):
        """Append message to log text widget"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
    
    def run(self):
        """Start the launcher"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_all()
        self.root.destroy()


def main():
    """Main entry point"""
    try:
        launcher = UXMirrorGameLauncher()
        launcher.run()
    except Exception as e:
        print(f"Error starting launcher: {e}")
        messagebox.showerror("Launcher Error", f"Failed to start launcher:\n{e}")


if __name__ == "__main__":
    main() 