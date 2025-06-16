# UX-MIRROR GUI Application

## 🎯 Overview

The UX-MIRROR GUI is a standalone launcher that provides intelligent UX analysis for any application. It features:

- 🔍 Automatic application detection and targeting
- 📊 Non-intrusive background analysis
- 🤖 Adaptive feedback engine
- 🎨 Modern dark theme interface
- 🔒 Secure configuration management

## 🚀 Quick Start

### Windows Users

1. **Double-click `run_gui.bat`** in the project folder
   
   OR

2. Open Command Prompt/PowerShell and run:
   ```bash
   cd C:\Dev\ux-mirror
   python run_gui.py
   ```

### macOS/Linux Users

1. Open Terminal and run:
   ```bash
   cd /path/to/ux-mirror
   python3 run_gui.py
   ```

## 📋 Prerequisites

### Required
- Python 3.8 or higher
- Tkinter (usually included with Python)
  - **Ubuntu/Debian**: `sudo apt-get install python3-tk`
  - **Windows/macOS**: Included with Python

### Installation

1. **Minimal Installation** (GUI only):
   ```bash
   pip install -r requirements_gui.txt
   ```

2. **Full Installation** (all features):
   ```bash
   pip install -r requirements.txt
   ```

## 🔧 Troubleshooting

### "No pyvenv.cfg file" Error

This indicates a virtual environment issue. Solutions:

1. **Use system Python directly**:
   ```bash
   # Windows
   py -m pip install -r requirements_gui.txt
   py run_gui.py
   
   # macOS/Linux
   python3 -m pip install -r requirements_gui.txt
   python3 run_gui.py
   ```

2. **Create a fresh virtual environment**:
   ```bash
   # Windows
   python -m venv new_venv
   new_venv\Scripts\activate
   pip install -r requirements_gui.txt
   python run_gui.py
   
   # macOS/Linux
   python3 -m venv new_venv
   source new_venv/bin/activate
   pip install -r requirements_gui.txt
   python run_gui.py
   ```

### Tkinter Not Found

- **Windows**: Reinstall Python with tkinter option checked
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **macOS**: Use Python from python.org (not Homebrew)

### Testing Components

Run the test script to verify everything works:
```bash
python test_gui_simple.py
```

## 🎮 Using the GUI

1. **Launch the Application**
   - Run `run_gui.py` or `run_gui.bat`

2. **Select Target Application**
   - The GUI will automatically detect running applications
   - Click "🔄 Refresh Apps" to update the list
   - Select the application you want to analyze

3. **Configure Analysis**
   - Choose analysis mode:
     - 🎯 **Adaptive** (Recommended): Adjusts based on user behavior
     - 🔄 **Continuous**: Ongoing analysis
     - ⚡ **One-Shot**: Single analysis pass
   
   - Select options:
     - 📝 Capture user input
     - 👁️ Show analysis overlay

4. **Start Analysis**
   - Click "🚀 Start Analysis"
   - Monitor progress in the status window
   - Use "💬 Provide Feedback" to improve analysis

5. **Settings**
   - Click "⚙️ Settings" to configure:
     - API keys (for AI analysis)
     - Analysis parameters
     - Security settings

## 📁 Project Structure

```
ux-mirror/
├── run_gui.py              # GUI launcher script
├── run_gui.bat             # Windows batch launcher
├── ux_mirror_launcher.py   # Main GUI application
├── requirements_gui.txt    # Minimal dependencies
├── requirements.txt        # Full dependencies
├── test_gui_simple.py      # Component test script
├── ui/
│   └── dark_theme.py       # Dark theme styling
├── core/
│   ├── port_manager.py     # Port management
│   ├── adaptive_feedback.py # Feedback engine
│   └── secure_config.py    # Configuration management
└── agents/
    ├── core_orchestrator.py # Analysis orchestration
    └── visual_analysis_agent.py # Visual analysis
```

## 🛡️ Security

- API keys are stored securely using the system keyring
- All analysis runs in a sandboxed environment
- No data is sent without explicit permission

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run `test_gui_simple.py` to diagnose problems
3. Check the log output in the GUI status window
4. Ensure all dependencies are installed

## 🎨 Features

### Application Detection
- Automatically finds running applications
- Categorizes by type (games, productivity, browsers, etc.)
- Shows memory usage and process information

### Analysis Modes
- **Adaptive**: Learns from user behavior
- **Continuous**: Ongoing monitoring
- **One-Shot**: Quick analysis

### Dark Theme
- Modern, eye-friendly interface
- Consistent styling across all components
- Responsive layout

### Feedback System
- Provide real-time feedback during analysis
- Helps improve AI understanding
- Adaptive learning from user input

## 🚧 Known Limitations

- Windows: May require administrator privileges for some applications
- macOS: May need accessibility permissions
- Linux: X11 support required for screenshot capture

---

For more information, see the main [README.md](README.md) file. 