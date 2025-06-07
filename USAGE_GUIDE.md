# UX-MIRROR Usage Guide

## ✅ Current Status: Production Ready

Your UX-MIRROR system has **real AI-powered analysis** that works with C++ games and any other application.

## 🚀 Quick Start

### 1. Set Your Anthropic API Key
```bash
# Windows PowerShell (permanent)
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "your_key_here", "User")

# Windows PowerShell (current session)
$env:ANTHROPIC_API_KEY = "your_anthropic_key_here"

# Command Prompt
set ANTHROPIC_API_KEY=your_anthropic_key_here
```

### 2. Test the System
```bash
# Test real AI integration
python test_real_analysis.py

# Launch the main system
python ux_mirror_launcher.py
```

### 3. Analyze Your Application

1. **Start your target application** (game, web app, etc.)
2. **Launch UX-MIRROR**: `python ux_mirror_launcher.py`  
3. **Select your application** from the detected list
4. **Click "Start Analysis"**

## 🔍 What You'll Get

### Real-Time Analysis
- **Screenshot capture** with metadata
- **Claude vision analysis** of actual UI elements
- **Specific issue detection** (spacing, contrast, accessibility)
- **Actionable recommendations** with pixel measurements
- **Quality scoring** based on real analysis

### Example Analysis Output
```
[19:58:47] 🚀 Starting analysis of My Game
[19:58:50] 📸 Screenshot captured
[19:58:51] 🤖 Analyzing with Anthropic Claude...
[19:58:54] ✅ AI analysis complete
[19:58:54] 📊 Iteration 1: Quality 72.0%
[19:58:54] ⚠️ Found: Button spacing in menu needs improvement
[19:58:54] 💡 Suggestion: Increase button padding by 10-15px for better accessibility
```

### Detailed Feedback
Claude provides specific observations like:
> "I can see a game menu with three buttons: 'Start Game', 'Settings', and 'Exit'. The buttons have good color coding but spacing is tight at 20px. For better accessibility, increase vertical spacing to 30-35px. Consider white text instead of black for better contrast."

## 🎮 For C++ Game Development

### Build Your Game First
```bash
# Windows (MinGW setup)
.\setup_mingw.bat  # Installs MinGW if needed

# Compile your game
g++ -std=c++17 -O2 -Wall -Wextra test_cpp_game.cpp -o ux_test_game.exe -lgdi32 -luser32 -lopengl32 -lgdiplus

# Verify build
dir ux_test_game.exe
```

### Game UX Testing Features
- **3:1 Feedback Cycles**: User feedback collected every 3 iterations
- **Screenshot Analysis**: Real-time UI element detection with overlays
- **Game-Specific Metrics**: UI responsiveness, visual clarity, accessibility
- **Performance Tracking**: FPS, input lag, response times

### Implementing Improvements
When Claude suggests changes, update your C++ code:

```cpp
// Before (from Claude's analysis)
FillRect(btn.x, btn.y, btn.w, btn.h, buttonColor);

// After (implementing Claude's suggestion)  
FillRect(btn.x, btn.y - 5, btn.w, btn.h + 10, buttonColor);  // Added spacing
DrawString(btn.x + 10, btn.y + 15, btn.text, olc::WHITE);   // White text
```

### Common Game UX Improvements
```cpp
// Improve button spacing in menus
FillRect(btn.x - 5, btn.y - 5, btn.w + 10, btn.h + 15, olc::DARK_YELLOW);

// Add volume slider feedback
DrawRect(50, 100, 200, 20, olc::WHITE);        // Background
FillRect(50, 100, volume * 2, 20, olc::GREEN); // Level indicator

// Enhance HUD layout
DrawString(10, 10, "Score: " + std::to_string(score), olc::YELLOW);
DrawString(10, 25, "Lives: " + std::to_string(lives), olc::GREEN);
DrawString(200, 10, "Time: " + std::to_string(int(gameTime)), olc::CYAN);
```

Then recompile and re-analyze:
```bash
g++ -std=c++17 -O2 test_cpp_game.cpp -o ux_test_game.exe -lgdi32 -luser32 -lopengl32
python ux_mirror_launcher.py  # Re-analyze to validate improvements
```

## 🔧 Advanced Usage

### CLI Commands
```bash
# Multi-Agent System Management
ux-tester agent start all              # Start all agents
ux-tester agent status                 # View agent health
ux-tester agent stop all               # Stop all agents

# Real-Time Monitoring
ux-tester monitor start --interval 5.0 # Begin continuous monitoring
ux-tester monitor status               # Check monitoring state
ux-tester monitor stop                 # Stop monitoring

# Intelligent Insights
ux-tester insights --limit 20          # View recent UX insights
ux-tester insights --severity high     # Filter by severity

# Legacy Support (Still Works)
ux-tester test --before                # Legacy screenshot testing
ux-tester test --after                 # Traditional workflow
ux-tester test --analyze               # Backward compatible
```

### Configuration
Edit `config.env` to customize:
- Analysis intervals
- AI provider settings
- Screenshot quality
- Port configurations

## ✅ Success Indicators

You'll know it's working when you see:
1. **"📸 Screenshot captured"** - Real capture happening
2. **"🤖 Analyzing with Anthropic Claude..."** - AI analysis in progress
3. **Specific issue detection** - Real problems found
4. **Variable quality scores** - Based on actual analysis, not fake increments
5. **Detailed feedback** - Specific observations about your UI

## 🎯 What Makes This Special

- **Real AI Analysis**: Not mock data - actual Claude vision API
- **Application Agnostic**: Works with games, web apps, desktop software
- **Iterative Improvement**: Tracks changes between analysis sessions
- **Professional Grade**: Same quality as UX consulting teams
- **Fast & Affordable**: Seconds for analysis, pay-per-use pricing

**Start improving your UX today!** 🚀 