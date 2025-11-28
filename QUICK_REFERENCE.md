# UX-MIRROR Quick Reference Guide

## Installation

```bash
# Install dependencies
pip install -r requirements_v0.1.0.txt

# Install Tesseract OCR (platform-specific)
# Windows: Download from GitHub
# Linux: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract

# Configure API keys in config.env
```

## Basic Usage

### CLI Commands

```bash
# Capture screenshots
python simple_ux_tester.py capture --before
python simple_ux_tester.py capture --after

# Analyze
python simple_ux_tester.py analyze

# List screenshots
python simple_ux_tester.py list

# Clean old files
python simple_ux_tester.py clean --days 7
```

### Python API

```python
# Simple testing
from simple_ux_tester import SimpleUXTester
tester = SimpleUXTester()
before, _ = tester.capture_before()
after, _ = tester.capture_after()
results = tester.analyze_screenshots(before, after)

# AI Analysis
from ai_vision_analyzer import AIVisionAnalyzer
from core.screenshot_analyzer import ScreenshotAnalyzer
import asyncio

async def analyze():
    screenshot_analyzer = ScreenshotAnalyzer()
    ai_analyzer = AIVisionAnalyzer(api_key="key", provider="anthropic")
    
    screenshot = await screenshot_analyzer.capture_screenshot()
    analysis = await ai_analyzer.analyze_game_ui(screenshot, "context")
    print(analysis.overall_assessment)

asyncio.run(analyze())
```

## Common Tasks

### Capture Screenshot
```python
from core.screenshot_analyzer import ScreenshotAnalyzer
import asyncio

async def capture():
    analyzer = ScreenshotAnalyzer()
    path = await analyzer.capture_screenshot()
    return path
```

### Detect UI Elements
```python
from src.analysis.ui_element_detector import UIElementDetector
import cv2

detector = UIElementDetector()
image = cv2.imread("screenshot.png")
buttons = detector.detect_buttons(image)
menus = detector.detect_menus(image)
```

### Extract Text (OCR)
```python
import pytesseract
from PIL import Image

image = Image.open("screenshot.png")
text = pytesseract.image_to_string(image)
```

### Generate Report
```python
from ux_report_generator import UXReportGenerator

generator = UXReportGenerator()
reports = generator.generate_comprehensive_report(
    analysis_data={...},
    screenshot_path="screenshot.png"
)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tesseract not found | Install Tesseract, add to PATH |
| OpenCV import error | `pip install opencv-python` |
| API key error | Check `config.env` or environment variables |
| Screenshot fails | Check permissions, try running as admin |
| Out of memory | Resize images, process in batches |

## Configuration

**config.env:**
```env
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
RESPONSE_TIME_THRESHOLD=500
UI_CHANGE_THRESHOLD=0.05
SCREENSHOT_QUALITY=85
```

## File Locations

- Screenshots: `ux_captures/`
- Reports: `reports/`
- Config: `config.env`
- Logs: `logs/` (if enabled)

## Best Practices

✅ Do:
- Capture before/after states
- Provide context for AI analysis
- Organize screenshots by session
- Review AI recommendations critically

❌ Don't:
- Capture during animations
- Rely solely on AI analysis
- Keep all screenshots indefinitely
- Hardcode API keys

## Support

- Full Manual: See `USER_MANUAL.md`
- Examples: Check `tests/` directory
- Issues: Report via project repository



