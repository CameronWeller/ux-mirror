# 🎯 UX-MIRROR + 3D Game of Life Launcher

This launcher system provides an easy, one-click way to start UX-MIRROR analysis with the target game (3D Game of Life - Vulkan Edition).

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)
1. **Double-click** `setup_launcher.bat`
2. Follow the setup process (installs dependencies, creates shortcuts)
3. **Use the desktop shortcut** created for you

### Option 2: Manual Launch
1. **Double-click** `launch_ux_mirror.bat` for a simple command-line launcher
2. **Run** `python launch_ux_mirror.py` for a GUI launcher with more options

## 📁 Launcher Files

| File | Description |
|------|-------------|
| `setup_launcher.bat` | **One-time setup** - installs dependencies and creates shortcuts |
| `launch_ux_mirror.bat` | **Command-line launcher** - simple batch file launcher |
| `launch_ux_mirror.py` | **GUI launcher** - advanced Python launcher with options |
| `create_desktop_shortcut.py` | Creates desktop/start menu shortcuts |

## 🎮 Launch Modes

The GUI launcher (`launch_ux_mirror.py`) offers three modes:

### 🚀 Integrated Launch (Recommended)
- Launches the 3D Game of Life 
- Automatically starts UX-MIRROR analysis
- Perfect for comprehensive UX testing

### 🎮 Game Only
- Launches only the 3D Game of Life
- For playing without analysis

### 🔍 UX-MIRROR Only  
- Launches the UX-MIRROR system
- Can analyze any running application

## 🎯 Target Game: 3D Game of Life

The current target game is **3D Game of Life - Vulkan Edition**:
- High-performance 3D cellular automata simulation
- GPU-accelerated with Vulkan compute shaders
- Interactive 3D visualization
- Perfect for UX analysis of gaming interfaces

## 🛠️ Requirements

### Core Requirements
- **Python 3.8+** 
- **Required Python packages** (installed automatically):
  - `tkinter` (usually comes with Python)
  - `psutil`
  - `asyncio`
  - All packages from `requirements.txt`

### For Game Building (Optional)
- **CMake 3.20+**
- **Vulkan SDK 1.3.0+**
- **C++ compiler with C++17 support**
- **vcpkg** (for dependency management)

### For Shortcuts (Windows Only)
- `pywin32` and `winshell` (installed automatically)

## 🎮 Game Controls

When the 3D Game of Life launches:

### Camera Controls
- **Mouse**: Look around (hold right-click)
- **WASD**: Move camera position
- **Scroll**: Zoom in/out
- **Shift**: Increase movement speed

### Simulation Controls
- **Space**: Play/pause simulation
- **R**: Reset grid/camera
- **ESC**: Toggle mouse look
- **1**: Fly mode
- **2**: Orbit mode

## 🔍 UX Analysis Features

The UX-MIRROR system will analyze:

- **UI Responsiveness**: Frame rate, input lag, update frequency
- **Visual Clarity**: Text readability, HUD visibility, contrast ratios
- **Accessibility**: Colorblind compatibility, UI scaling, button sizes
- **Engagement Tracking**: Attention heatmaps, interaction flow
- **Performance Impact**: How UI affects game performance
- **Navigation Efficiency**: Menu flow and usability

## 📊 Results and Reports

Analysis results are saved in the `reports/` directory:
- Screenshots with analysis overlays
- JSON data files with metrics
- AI-generated insights and recommendations
- Performance analysis reports

## 🔧 Troubleshooting

### "Python not found"
- Install Python 3.8+ from [python.org](https://python.org)
- Make sure to check "Add to PATH" during installation

### "Game executable not found"
- Click "Build Game" in the GUI launcher
- Or run the build process manually from `game-target/`

### "Dependencies missing"  
- Run `setup_launcher.bat` to install all requirements
- Or manually: `pip install -r requirements.txt`

### Game won't build
- Install CMake from [cmake.org](https://cmake.org)
- Install Vulkan SDK from [vulkan.lunarg.com](https://vulkan.lunarg.com)
- Ensure you have a C++17 compatible compiler

## 🎯 Usage Workflow

1. **Launch** using any of the launcher options
2. **Select mode** (integrated recommended for UX analysis)
3. **Play the game** naturally - UX analysis runs in background
4. **Review results** in the reports directory
5. **Implement improvements** based on AI recommendations

## 🔄 Updates and Maintenance

- Re-run `setup_launcher.bat` after major updates
- Check the `reports/` directory regularly for new insights
- Update Python packages: `pip install -r requirements.txt --upgrade`

## 📞 Support

If you encounter issues:
1. Check this README for troubleshooting steps
2. Review the activity log in the GUI launcher
3. Check the console output from the batch launcher
4. Ensure all requirements are properly installed

---

**Happy UX Testing!** 🎮✨ 