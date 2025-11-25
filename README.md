# UX-MIRROR v0.1.0

**Simple AI-powered UX analysis for desktop applications**

UX-MIRROR is a focused tool that captures screenshots of your applications, analyzes them with AI vision, and provides actionable UX feedback and recommendations.

## 🎯 What is UX-MIRROR?

UX-MIRROR helps you improve user interfaces by:
- **Capturing screenshots** of your desktop applications
- **Analyzing UI** with AI vision (Claude/OpenAI)
- **Detecting issues** like poor contrast, spacing problems, accessibility concerns
- **Providing recommendations** with specific, actionable feedback

## ✨ Features

### Core Capabilities
- 📸 **Screenshot Capture** - Capture screenshots of any desktop application
- 🤖 **AI Vision Analysis** - Powered by Anthropic Claude and OpenAI Vision
- 🔍 **UI Element Detection** - Automatic detection of buttons, text, inputs, and more
- 📝 **OCR Text Extraction** - Extract and analyze text from UI elements
- 📊 **Quality Scoring** - Get quality scores and detailed metrics
- 💡 **Actionable Recommendations** - Specific suggestions for improvement

### User Interfaces
- 🖥️ **GUI Launcher** - Easy-to-use graphical interface
- ⌨️ **CLI Tool** - Command-line interface for automation

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/ux-mirror.git
cd ux-mirror

# Install dependencies
pip install -r requirements.txt
```

### Setup

1. **Get an API key** from [Anthropic](https://www.anthropic.com/) or [OpenAI](https://openai.com/)

2. **Set your API key**:
   ```bash
   # Windows PowerShell
   $env:ANTHROPIC_API_KEY = "your_key_here"
   
   # Linux/Mac
   export ANTHROPIC_API_KEY="your_key_here"
   ```

### Usage

#### GUI Launcher (Recommended)
```bash
python ux_mirror_launcher.py
```

1. Select your target application from the list
2. Click "Start Analysis"
3. Review the AI-generated feedback and recommendations

#### CLI Tool
```bash
# Analyze a running application
ux-tester analyze --target "MyApp.exe"

# Game testing mode
ux-tester game --iterations 5
```

## 📖 Examples

### Basic Analysis
```python
from core.screenshot_analyzer import ScreenshotAnalyzer

analyzer = ScreenshotAnalyzer()
result = analyzer.analyze_screenshot("screenshot.png")
print(f"Quality Score: {result['quality_score']}")
print(f"Issues Found: {len(result['issues'])}")
```

### CLI Usage
```bash
# Capture and analyze
ux-tester test --before
# ... perform your UI interaction ...
ux-tester test --after
ux-tester test --analyze
```

## 🎯 Use Cases

- **Game Development** - Analyze game UIs for accessibility and usability
- **Desktop Applications** - Get feedback on desktop app interfaces
- **UI/UX Design** - Validate design decisions with AI analysis
- **Accessibility Testing** - Detect contrast and accessibility issues
- **Quality Assurance** - Automated UI quality checks

## 📋 Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **API Key**: Anthropic Claude or OpenAI Vision API key
- **Dependencies**: See `requirements.txt`

## 🔧 Configuration

Create a `config.env` file or set environment variables:

```env
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
RESPONSE_TIME_THRESHOLD=500
UI_CHANGE_THRESHOLD=0.05
```

## 📁 Project Structure

```
ux-mirror/
├── src/
│   ├── analysis/          # Analysis modules
│   ├── capture/           # Screenshot capture
│   └── ux_tester/         # Core testing logic
├── core/                  # Core functionality
├── cli/                   # CLI interface
├── config/                # Configuration files
├── ux_mirror_launcher.py  # GUI launcher
└── simple_ux_tester.py    # Simple CLI tool
```

## 🐛 Troubleshooting

### "API key not found"
- Make sure you've set the `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` environment variable
- Check that the API key is valid and has credits

### "Application not detected"
- Make sure the target application is running
- Try running UX-MIRROR with administrator privileges (Windows)

### "Analysis failed"
- Check your internet connection (API calls required)
- Verify your API key has sufficient credits
- Check the logs for detailed error messages

## 📚 Documentation

- [Usage Guide](USAGE_GUIDE.md) - Detailed usage instructions
- [Release Notes](CHANGELOG.md) - Version history
- [v0.1.0 Roadmap](v0.1.0_ROADMAP.md) - Development roadmap

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## 📄 License

MIT License - See LICENSE file for details

## 🗺️ Roadmap

### v0.1.0 (Current)
- ✅ Core screenshot capture
- ✅ AI vision analysis
- ✅ UI element detection
- ✅ OCR text extraction
- ✅ CLI and GUI interfaces

### v0.2.0 (Planned)
- Web application support
- Real-time monitoring
- Advanced OCR features

### v1.0.0 (Future)
- Self-programming capabilities
- GPU acceleration
- Multi-platform integrations

## 🙏 Acknowledgments

- Built with [Anthropic Claude](https://www.anthropic.com/) and [OpenAI](https://openai.com/) vision APIs
- Uses [OpenCV](https://opencv.org/) for computer vision
- Uses [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text extraction

---

**Version**: 0.1.0  
**Status**: Beta  
**Last Updated**: 2025-01-XX

