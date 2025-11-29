# UX-MIRROR User Manual
## Comprehensive Guide to UX Testing and Analysis

**Version:** 0.1.0  
**Last Updated:** 2025-01-XX  
**Document Version:** 1.0

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Features Overview](#features-overview)
5. [Usage Guide](#usage-guide)
6. [Screenshots and Examples](#screenshots-and-examples)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Best Practices](#best-practices)
9. [Advanced Usage](#advanced-usage)
10. [FAQ](#faq)
11. [Appendix](#appendix)

---

## 1. Introduction

### 1.1 What is UX-MIRROR?

UX-MIRROR is an intelligent UX testing and analysis tool that helps developers and designers evaluate user interface quality through automated screenshot analysis. It combines computer vision, AI-powered analysis, and OCR to provide comprehensive insights into UI/UX quality.

### 1.2 Key Capabilities

- **Automated Screenshot Capture**: Capture screenshots of your application with metadata tracking
- **AI-Powered Analysis**: Analyze UI using OpenAI and Anthropic Claude Vision APIs
- **UI Element Detection**: Automatically detect buttons, menus, text regions, and other UI elements
- **OCR Text Extraction**: Extract and analyze text content from screenshots
- **Comprehensive Reports**: Generate detailed reports in JSON and HTML formats
- **Cross-Platform Support**: Works on Windows, Linux, and macOS

### 1.3 Use Cases

- **Game UI Testing**: Analyze game interfaces for clutter, readability, and usability
- **Desktop Application Testing**: Evaluate desktop app UIs for accessibility and design quality
- **Web Application Testing**: Test web interfaces for UX issues
- **Design Review**: Get AI-powered feedback on UI designs
- **Accessibility Audits**: Identify accessibility issues in user interfaces

---

## 2. Installation

### 2.1 System Requirements

**Minimum Requirements:**
- Python 3.8 or higher
- 4 GB RAM
- 500 MB free disk space
- Internet connection (for AI analysis features)

**Recommended:**
- Python 3.10 or higher
- 8 GB RAM
- 1 GB free disk space
- Stable internet connection

### 2.2 Installing Dependencies

#### Step 1: Install Python Dependencies

```bash
pip install -r requirements_v0.1.0.txt
```

**Key Dependencies:**
- `opencv-python` - Image processing and UI element detection
- `Pillow` - Screenshot capture
- `pytesseract` - OCR text extraction
- `aiohttp` - Async HTTP requests for AI APIs
- `numpy` - Numerical operations

#### Step 2: Install Tesseract OCR

**Windows:**
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install the executable
3. Add Tesseract to your system PATH, or configure the path in `config.env`

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install libtesseract-dev
```

**macOS:**
```bash
brew install tesseract
```

#### Step 3: Configure API Keys

1. Copy `config.env.example` to `config.env` (if available)
2. Edit `config.env` and add your API keys:

```env
# OpenAI API Key (optional, for OpenAI Vision analysis)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude API Key (optional, for Claude Vision analysis)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Other configuration options
RESPONSE_TIME_THRESHOLD=500
UI_CHANGE_THRESHOLD=0.05
SCREENSHOT_QUALITY=85
```

**Note:** You can use UX-MIRROR without API keys for basic screenshot capture and UI element detection. AI analysis features require API keys.

### 2.3 Verify Installation

Run the test suite to verify installation:

```bash
python tests/v0.1.0_test_suite.py
```

Or test individual components:

```bash
# Test screenshot capture
python -c "from core.screenshot_analyzer import ScreenshotAnalyzer; print('OK')"

# Test OpenCV
python -c "import cv2; print(f'OpenCV {cv2.__version__}')"

# Test Tesseract
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

---

## 3. Quick Start

### 3.1 Basic Screenshot Capture

**Using the CLI:**

```bash
# Capture a screenshot
python simple_ux_tester.py capture --before

# Perform your UI interaction (click button, navigate, etc.)

# Capture after screenshot
python simple_ux_tester.py capture --after

# Analyze the screenshots
python simple_ux_tester.py analyze
```

**Using Python Code:**

```python
from simple_ux_tester import SimpleUXTester

# Initialize tester
tester = SimpleUXTester(output_dir="ux_captures")

# Capture before screenshot
before_path, before_metadata = tester.capture_before()

# Perform your UI interaction...

# Capture after screenshot
after_path, after_metadata = tester.capture_after()

# Analyze
results = tester.analyze_screenshots(before_path, after_path)
```

### 3.2 AI-Powered Analysis

```python
from ai_vision_analyzer import AIVisionAnalyzer
from core.screenshot_analyzer import ScreenshotAnalyzer
import asyncio

async def analyze_ui():
    # Initialize analyzers
    screenshot_analyzer = ScreenshotAnalyzer()
    ai_analyzer = AIVisionAnalyzer(
        api_key="your_api_key",
        provider="anthropic"  # or "openai"
    )
    
    # Capture screenshot
    screenshot_path = await screenshot_analyzer.capture_screenshot()
    
    # Analyze with AI
    analysis = await ai_analyzer.analyze_game_ui(
        image_path=screenshot_path,
        context="Game main menu"
    )
    
    # Print results
    print(f"Overall Assessment: {analysis.overall_assessment}")
    print(f"Issues Found: {len(analysis.issues_found)}")
    print(f"Recommendations: {len(analysis.recommendations)}")

# Run analysis
asyncio.run(analyze_ui())
```

### 3.3 Generate Reports

```python
from ux_report_generator import UXReportGenerator

# Initialize generator
generator = UXReportGenerator(reports_dir="reports")

# Generate comprehensive report
analysis_data = {
    "overall_assessment": "Good UI with minor issues",
    "issues_found": [...],
    "recommendations": [...]
}

report_paths = generator.generate_comprehensive_report(
    analysis_data=analysis_data,
    screenshot_path="screenshot.png",
    app_context={"app_type": "game", "platform": "Windows"}
)

print(f"JSON Report: {report_paths['json']}")
print(f"HTML Report: {report_paths['html']}")
```

---

## 4. Features Overview

### 4.1 Screenshot Capture

**Features:**
- Full-screen capture
- Timestamp-based naming
- Metadata tracking (dimensions, file size, capture time)
- Automatic directory organization
- Cross-platform support (Windows, Linux, macOS)

**Usage:**
```python
from core.screenshot_analyzer import ScreenshotAnalyzer
import asyncio

async def capture():
    analyzer = ScreenshotAnalyzer()
    path = await analyzer.capture_screenshot()
    print(f"Screenshot saved: {path}")

asyncio.run(capture())
```

### 4.2 UI Element Detection

**Detected Elements:**
- Buttons (rectangular regions with edges)
- Menus (horizontal/vertical line patterns)
- Text regions (MSER-based detection)
- UI components (contour-based detection)

**Usage:**
```python
from src.analysis.ui_element_detector import UIElementDetector
import cv2

detector = UIElementDetector()
image = cv2.imread("screenshot.png")

# Detect buttons
buttons = detector.detect_buttons(image)

# Detect menus
menus = detector.detect_menus(image)

# Detect text regions
text_regions = detector.detect_text_regions(image)
```

### 4.3 OCR Text Extraction

**Features:**
- Multi-language support
- Confidence scoring
- Preprocessing options (grayscale, denoising, thresholding)
- Text region detection

**Usage:**
```python
import pytesseract
from PIL import Image

image = Image.open("screenshot.png")

# Extract text
text = pytesseract.image_to_string(image)
print(text)

# Get detailed data with confidence
data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
```

### 4.4 AI Vision Analysis

**Providers:**
- **OpenAI Vision API**: GPT-4 Vision model
- **Anthropic Claude Vision API**: Claude 3 Vision model

**Analysis Includes:**
- Overall UI assessment
- Specific issues found
- Visual hierarchy analysis
- Readability assessment
- Clutter scoring
- Actionable recommendations

**Usage:**
```python
from ai_vision_analyzer import AIVisionAnalyzer
import asyncio

async def analyze():
    analyzer = AIVisionAnalyzer(
        api_key="your_key",
        provider="anthropic"
    )
    
    result = await analyzer.analyze_game_ui(
        image_path="screenshot.png",
        context="Main menu screen"
    )
    
    print(result.overall_assessment)
    print(f"Clutter Score: {result.clutter_score}")
    print(f"Readability: {result.readability_score}")

asyncio.run(analyze())
```

### 4.5 Report Generation

**Report Formats:**
- **JSON**: Machine-readable structured data
- **HTML**: Visual, human-readable report with styling
- **Markdown**: Simple text format (optional)

**Report Contents:**
- Executive summary
- Detailed analysis results
- Issues found (with severity)
- Prioritized recommendations
- Accessibility audit
- Technical metrics
- Screenshot embedding

---

## 5. Usage Guide

### 5.1 Command-Line Interface

**Basic Commands:**

```bash
# Launch GUI launcher
python ux_mirror_launcher.py

# Simple UX tester
python simple_ux_tester.py capture --before
python simple_ux_tester.py capture --after
python simple_ux_tester.py analyze

# List captured screenshots
python simple_ux_tester.py list

# Delete old screenshots
python simple_ux_tester.py clean --days 7
```

**CLI Options:**

```bash
# Capture with expected content
python simple_ux_tester.py capture --before --expected "Button should appear"

# Analyze specific screenshots
python simple_ux_tester.py analyze --before path/to/before.png --after path/to/after.png

# Custom output directory
python simple_ux_tester.py capture --output custom_dir
```

### 5.2 Python API Usage

#### 5.2.1 Simple UX Testing

```python
from simple_ux_tester import SimpleUXTester

tester = SimpleUXTester(output_dir="ux_captures")

# Capture workflow
before_path, before_meta = tester.capture_before(
    expected_content="Login button should be visible"
)

# ... perform interaction ...

after_path, after_meta = tester.capture_after(
    expected_content="Dashboard should load"
)

# Analyze
results = tester.analyze_screenshots(before_path, after_path)

# Check results
if results['results']['ux_quality'] == 'good':
    print("✅ UX quality is good!")
else:
    print("⚠️ Issues found:", results['results']['visual_issues'])
```

#### 5.2.2 Advanced Analysis

```python
from core.screenshot_analyzer import ScreenshotAnalyzer
from ai_vision_analyzer import AIVisionAnalyzer
import asyncio

async def advanced_analysis():
    # Initialize
    screenshot_analyzer = ScreenshotAnalyzer()
    ai_analyzer = AIVisionAnalyzer(
        api_key="your_key",
        provider="anthropic"
    )
    
    # Capture
    screenshot_path = await screenshot_analyzer.capture_screenshot()
    
    # Basic analysis
    basic_analysis = await screenshot_analyzer.analyze_image(screenshot_path)
    print(f"Quality Score: {basic_analysis['quality_score']}")
    print(f"UI Elements: {len(basic_analysis['ui_elements'])}")
    
    # AI analysis
    ai_analysis = await ai_analyzer.analyze_game_ui(
        image_path=screenshot_path,
        context="Game main menu - testing button layout"
    )
    
    # Process results
    print(f"Overall: {ai_analysis.overall_assessment}")
    print(f"Issues: {len(ai_analysis.issues_found)}")
    
    # Generate report
    from ux_report_generator import UXReportGenerator
    generator = UXReportGenerator()
    
    report_data = {
        "overall_assessment": ai_analysis.overall_assessment,
        "issues_found": ai_analysis.issues_found,
        "recommendations": ai_analysis.recommendations,
        "clutter_score": ai_analysis.clutter_score,
        "readability_score": ai_analysis.readability_score
    }
    
    reports = generator.generate_comprehensive_report(
        analysis_data=report_data,
        screenshot_path=screenshot_path,
        app_context={"app": "My Game", "screen": "Main Menu"}
    )
    
    print(f"Reports generated: {reports}")

asyncio.run(advanced_analysis())
```

#### 5.2.3 Game Testing Session

```python
from game_testing_session import GameUXTestingController

# Initialize controller
controller = GameUXTestingController("game_ux_config.json")

# Start session
controller.start_session(
    session_id="test_session_001",
    total_iterations=10,
    feedback_ratio=3  # User feedback every 3 iterations
)

# Run testing loop
await controller.run_testing_cycle()

# Get results
results = controller.get_session_results()
```

### 5.3 GUI Launcher

**Launching the GUI:**

```bash
python ux_mirror_launcher.py
```

**GUI Features:**
- Visual screenshot display
- Real-time analysis results
- Report preview
- Configuration management
- Session management

---

## 6. Screenshots and Examples

### 6.1 Screenshot Locations

**Note:** Actual screenshots should be added to the `docs/screenshots/` directory.

#### 6.1.1 Main GUI Launcher
**File:** `docs/screenshots/gui_launcher.png`
**Description:** Main window showing the UX-MIRROR launcher interface with capture, analyze, and report buttons.

#### 6.1.2 Screenshot Capture
**File:** `docs/screenshots/capture_interface.png`
**Description:** Screenshot capture interface showing before/after capture options and metadata display.

#### 6.1.3 Analysis Results
**File:** `docs/screenshots/analysis_results.png`
**Description:** Analysis results panel showing detected UI elements, quality scores, and identified issues.

#### 6.1.4 HTML Report
**File:** `docs/screenshots/html_report.png`
**Description:** Generated HTML report showing executive summary, issues, recommendations, and embedded screenshot.

#### 6.1.5 JSON Report Structure
**File:** `docs/screenshots/json_report_structure.png`
**Description:** JSON report structure displayed in a code editor, showing the hierarchical data format.

### 6.2 Example Workflows

#### Example 1: Testing a Login Screen

```python
from simple_ux_tester import SimpleUXTester

tester = SimpleUXTester()

# 1. Capture initial state
before, _ = tester.capture_before(
    expected_content="Login form should be visible"
)

# 2. User enters credentials (manual step)
# ... user interaction ...

# 3. Capture after login
after, _ = tester.capture_after(
    expected_content="Dashboard should appear"
)

# 4. Analyze
results = tester.analyze_screenshots(before, after)

# 5. Check results
if results['results']['response_time_ms'] < 500:
    print("✅ Fast response time")
if results['results']['ui_changed']:
    print("✅ UI changed as expected")
```

#### Example 2: Game UI Analysis

```python
from ai_vision_analyzer import AIVisionAnalyzer
from core.screenshot_analyzer import ScreenshotAnalyzer
import asyncio

async def analyze_game_menu():
    screenshot_analyzer = ScreenshotAnalyzer()
    ai_analyzer = AIVisionAnalyzer(
        api_key="your_key",
        provider="anthropic"
    )
    
    # Capture game menu
    screenshot = await screenshot_analyzer.capture_screenshot()
    
    # Analyze
    analysis = await ai_analyzer.analyze_game_ui(
        image_path=screenshot,
        context="Main menu - checking button layout and readability"
    )
    
    # Review results
    print("=== Game UI Analysis ===")
    print(f"Overall: {analysis.overall_assessment}")
    print(f"Clutter Score: {analysis.clutter_score:.2f} (lower is better)")
    print(f"Readability: {analysis.readability_score:.2f} (higher is better)")
    
    print("\nIssues Found:")
    for issue in analysis.issues_found:
        print(f"  - [{issue['severity']}] {issue.get('type', 'Unknown')}: {issue.get('description', '')}")
    
    print("\nTop Recommendations:")
    for i, rec in enumerate(analysis.recommendations[:5], 1):
        print(f"  {i}. {rec}")

asyncio.run(analyze_game_menu())
```

---

## 7. Troubleshooting Guide

### 7.1 Common Issues

#### Issue: "Tesseract not found"

**Symptoms:**
```
TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

**Solutions:**

1. **Windows:**
   - Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add to PATH: `C:\Program Files\Tesseract-OCR`
   - Or set path in code:
     ```python
     import pytesseract
     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
     ```

2. **Linux:**
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr
   ```

3. **macOS:**
   ```bash
   brew install tesseract
   ```

#### Issue: "OpenCV import error"

**Symptoms:**
```
ModuleNotFoundError: No module named 'cv2'
```

**Solutions:**

```bash
# Install OpenCV
pip install opencv-python

# If that fails, try:
pip install opencv-python-headless

# Verify installation
python -c "import cv2; print(cv2.__version__)"
```

#### Issue: "API key not found"

**Symptoms:**
```
ValueError: API key not found
```

**Solutions:**

1. Check `config.env` file exists
2. Verify API key is set:
   ```env
   ANTHROPIC_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ```
3. Or set environment variable:
   ```bash
   # Windows
   set ANTHROPIC_API_KEY=your_key_here
   
   # Linux/macOS
   export ANTHROPIC_API_KEY=your_key_here
   ```

#### Issue: "Screenshot capture fails"

**Symptoms:**
```
Failed to capture screenshot: ...
```

**Solutions:**

1. **Windows:**
   - Ensure you have proper permissions
   - Try running as administrator
   - Check if screen capture is blocked by security software

2. **Linux:**
   - Install required dependencies:
     ```bash
     sudo apt-get install python3-tk python3-dev
     ```
   - For headless systems, use alternative capture methods

3. **macOS:**
   - Grant screen recording permissions in System Preferences > Security & Privacy

#### Issue: "Out of memory during analysis"

**Symptoms:**
```
MemoryError: ...
```

**Solutions:**

1. Reduce image size before analysis:
   ```python
   from PIL import Image
   
   img = Image.open("screenshot.png")
   img = img.resize((1920, 1080))  # Resize if larger
   img.save("screenshot_resized.png")
   ```

2. Process screenshots in batches
3. Close other applications to free memory

#### Issue: "Report generation fails"

**Symptoms:**
```
Failed to generate report: ...
```

**Solutions:**

1. Check output directory permissions:
   ```python
   import os
   os.makedirs("reports", exist_ok=True)
   ```

2. Verify report data structure matches expected format
3. Check disk space availability

### 7.2 Performance Issues

#### Slow Screenshot Capture

**Solutions:**
- Close unnecessary applications
- Reduce screen resolution temporarily
- Use lower quality settings:
  ```python
  tester = SimpleUXTester()
  tester.config['screenshot_quality'] = 70  # Lower quality = faster
  ```

#### Slow AI Analysis

**Solutions:**
- Use smaller images (resize before analysis)
- Check API rate limits
- Use local analysis when possible (UI element detection)
- Cache results to avoid re-analysis

#### High Memory Usage

**Solutions:**
- Process screenshots one at a time
- Delete old screenshots regularly
- Use image compression
- Close analysis objects after use

### 7.3 Platform-Specific Issues

#### Windows

**Issue: COM Error when creating shortcuts**
- Solution: Run as administrator or check COM permissions

**Issue: Path issues with spaces**
- Solution: Use `Path` objects from `pathlib` instead of strings

#### Linux

**Issue: Display not available (headless)**
- Solution: Use `Xvfb` for virtual display:
  ```bash
  sudo apt-get install xvfb
  xvfb-run python your_script.py
  ```

**Issue: Permission denied for screenshot**
- Solution: Check X11 permissions and display access

#### macOS

**Issue: Screen recording permission denied**
- Solution: Grant permission in System Preferences > Security & Privacy > Privacy > Screen Recording

**Issue: Tesseract path not found**
- Solution: Set path explicitly:
  ```python
  pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
  ```

### 7.4 Getting Help

**Resources:**
- Check logs in `logs/` directory (if logging is enabled)
- Review test files in `tests/` for usage examples
- Check `config.env` for configuration options
- Review error messages for specific guidance

**Debug Mode:**
Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 8. Best Practices

### 8.1 Screenshot Capture

**Do:**
- ✅ Capture before and after states for comparison
- ✅ Use descriptive labels for screenshots
- ✅ Include expected content in metadata
- ✅ Organize screenshots by session/feature
- ✅ Clean up old screenshots regularly

**Don't:**
- ❌ Capture during animations or transitions
- ❌ Use very high resolution (unless necessary)
- ❌ Keep all screenshots indefinitely
- ❌ Capture sensitive information

**Example:**
```python
# Good practice
tester.capture_before(
    expected_content="Login button should be visible and enabled"
)

# After interaction
tester.capture_after(
    expected_content="Dashboard should load with user data"
)
```

### 8.2 AI Analysis

**Do:**
- ✅ Provide context about what you're testing
- ✅ Use appropriate API provider for your needs
- ✅ Cache results to avoid redundant API calls
- ✅ Review and validate AI recommendations
- ✅ Combine AI analysis with manual review

**Don't:**
- ❌ Rely solely on AI analysis
- ❌ Make excessive API calls (watch rate limits)
- ❌ Ignore false positives
- ❌ Use AI for sensitive/private content

**Example:**
```python
# Good practice - provide context
analysis = await ai_analyzer.analyze_game_ui(
    image_path=screenshot,
    context="Main menu - testing button visibility and spacing for mobile users"
)

# Review results critically
for issue in analysis.issues_found:
    if issue['severity'] == 'high':
        # Manually verify high-severity issues
        verify_issue_manually(issue)
```

### 8.3 Report Generation

**Do:**
- ✅ Include relevant context in reports
- ✅ Use consistent naming conventions
- ✅ Archive important reports
- ✅ Share reports with team members
- ✅ Review reports before sharing

**Don't:**
- ❌ Generate reports for every single screenshot
- ❌ Include sensitive data in reports
- ❌ Overwrite important reports
- ❌ Generate reports without analysis data

**Example:**
```python
# Good practice - comprehensive context
report_paths = generator.generate_comprehensive_report(
    analysis_data=analysis_data,
    screenshot_path=screenshot_path,
    app_context={
        "app_name": "My Game",
        "version": "1.0.0",
        "screen": "Main Menu",
        "test_date": "2025-01-XX",
        "tester": "John Doe"
    }
)
```

### 8.4 Performance Optimization

**Do:**
- ✅ Resize large images before analysis
- ✅ Process screenshots in batches
- ✅ Use local analysis when AI isn't needed
- ✅ Clean up temporary files
- ✅ Monitor API usage and costs

**Example:**
```python
# Optimize image size
from PIL import Image

img = Image.open("large_screenshot.png")
if img.size[0] > 1920:
    img = img.resize((1920, int(1920 * img.size[1] / img.size[0])))
    img.save("optimized_screenshot.png")
```

### 8.5 Testing Workflow

**Recommended Workflow:**

1. **Setup Phase:**
   - Configure API keys
   - Set up output directories
   - Prepare test scenarios

2. **Capture Phase:**
   - Capture before state
   - Perform interaction
   - Capture after state

3. **Analysis Phase:**
   - Run basic analysis (UI detection, OCR)
   - Run AI analysis (if needed)
   - Review results

4. **Reporting Phase:**
   - Generate reports
   - Review and validate findings
   - Share with team

5. **Cleanup Phase:**
   - Archive important results
   - Clean up temporary files
   - Update documentation

### 8.6 Security Best Practices

**Do:**
- ✅ Store API keys securely (use environment variables)
- ✅ Don't commit API keys to version control
- ✅ Use `.gitignore` for sensitive files
- ✅ Review screenshots for sensitive data
- ✅ Secure report storage

**Don't:**
- ❌ Hardcode API keys in source code
- ❌ Share API keys publicly
- ❌ Capture sensitive user data
- ❌ Store unencrypted sensitive reports

---

## 9. Advanced Usage

### 9.1 Custom UI Element Detection

```python
from src.analysis.ui_element_detector import UIElementDetector
import cv2
import numpy as np

detector = UIElementDetector()

# Custom detection parameters
image = cv2.imread("screenshot.png")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Custom button detection
edges = cv2.Canny(gray, 50, 150)
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

buttons = []
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    if 50 < w < 300 and 20 < h < 100:  # Button size constraints
        buttons.append((x, y, w, h))
```

### 9.2 Batch Processing

```python
import asyncio
from pathlib import Path
from core.screenshot_analyzer import ScreenshotAnalyzer

async def batch_analyze_screenshots(screenshot_dir):
    analyzer = ScreenshotAnalyzer()
    screenshots = list(Path(screenshot_dir).glob("*.png"))
    
    results = []
    for screenshot in screenshots:
        analysis = await analyzer.analyze_image(str(screenshot))
        results.append({
            "screenshot": str(screenshot),
            "analysis": analysis
        })
    
    return results

# Process all screenshots
results = asyncio.run(batch_analyze_screenshots("ux_captures"))
```

### 9.3 Custom Report Templates

```python
from ux_report_generator import UXReportGenerator

class CustomReportGenerator(UXReportGenerator):
    def _generate_custom_report(self, data):
        # Custom report format
        template = """
        Custom Report
        =============
        App: {app_name}
        Date: {date}
        Issues: {issue_count}
        """
        return template.format(
            app_name=data.get('app_name', 'Unknown'),
            date=data.get('date', 'Unknown'),
            issue_count=len(data.get('issues', []))
        )
```

### 9.4 Integration with CI/CD

```python
# Example GitHub Actions integration
import os
import sys

def ci_test():
    """Run UX tests in CI environment"""
    tester = SimpleUXTester()
    
    # Capture and analyze
    before, _ = tester.capture_before()
    # ... automated interaction ...
    after, _ = tester.capture_after()
    results = tester.analyze_screenshots(before, after)
    
    # Check quality thresholds
    if results['results']['ux_quality'] != 'good':
        print("❌ UX quality check failed")
        sys.exit(1)
    
    print("✅ UX quality check passed")

if __name__ == "__main__":
    ci_test()
```

---

## 10. FAQ

### Q1: Do I need API keys to use UX-MIRROR?

**A:** No, you can use basic features without API keys:
- Screenshot capture
- UI element detection (OpenCV)
- OCR text extraction
- Basic analysis

AI-powered analysis requires API keys from OpenAI or Anthropic.

### Q2: Which AI provider should I use?

**A:** Both providers work well:
- **OpenAI**: Faster responses, good for general UI analysis
- **Anthropic Claude**: More detailed analysis, better for complex UIs

You can use both and compare results.

### Q3: How much do API calls cost?

**A:** Costs vary by provider and usage:
- OpenAI Vision: ~$0.01-0.03 per image
- Anthropic Claude Vision: ~$0.01-0.02 per image

Check current pricing on provider websites.

### Q4: Can I use UX-MIRROR for automated testing?

**A:** Yes! UX-MIRROR can be integrated into automated test suites. See Section 9.4 for CI/CD integration examples.

### Q5: What image formats are supported?

**A:** Primarily PNG for screenshots. Analysis supports:
- PNG (recommended)
- JPEG
- BMP
- Other formats supported by PIL

### Q6: How do I handle multiple monitors?

**A:** By default, `ImageGrab.grab()` captures the primary monitor. For multi-monitor support, you may need platform-specific code or use alternative libraries.

### Q7: Can I analyze videos instead of screenshots?

**A:** Currently, UX-MIRROR focuses on static screenshot analysis. For video analysis, you would need to extract frames first.

### Q8: How accurate is the UI element detection?

**A:** Detection accuracy depends on:
- Image quality
- UI complexity
- Element contrast
- Image preprocessing

Typical accuracy: 70-90% for clear, well-contrasted UIs.

### Q9: Can I customize the analysis prompts?

**A:** Yes, you can modify prompts in `ai_vision_analyzer.py` to focus on specific aspects of UI analysis.

### Q10: How do I contribute to the project?

**A:** Check the project repository for contribution guidelines. Common contributions:
- Bug fixes
- Feature additions
- Documentation improvements
- Test coverage

---

## 11. Appendix

### 11.1 Configuration Reference

**config.env Options:**

```env
# API Keys
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# Thresholds
RESPONSE_TIME_THRESHOLD=500  # milliseconds
UI_CHANGE_THRESHOLD=0.05      # 0-1 scale

# Quality Settings
SCREENSHOT_QUALITY=85         # 1-100

# Features
CONTENT_VALIDATION_ENABLED=true
```

### 11.2 File Structure

```
ux-mirror/
├── core/
│   └── screenshot_analyzer.py    # Screenshot capture
├── src/
│   ├── analysis/
│   │   └── ui_element_detector.py  # UI detection
│   ├── capture/
│   └── ux_tester/
├── cli/
│   └── main.py                   # CLI interface
├── tests/                        # Test suite
├── docs/                         # Documentation
├── ux_captures/                  # Screenshot storage
├── reports/                      # Generated reports
├── config.env                    # Configuration
├── simple_ux_tester.py          # Simple testing tool
├── ai_vision_analyzer.py        # AI analysis
└── ux_report_generator.py        # Report generation
```

### 11.3 API Reference

**Key Classes:**

- `ScreenshotAnalyzer`: Screenshot capture and basic analysis
- `AIVisionAnalyzer`: AI-powered UI analysis
- `UIElementDetector`: UI element detection
- `SimpleUXTester`: Simple testing workflow
- `UXReportGenerator`: Report generation
- `GameUXTestingController`: Game-focused testing

### 11.4 Glossary

- **UI Element**: A detectable component in a user interface (button, menu, etc.)
- **Clutter Score**: Measure of UI complexity (0-1, lower is better)
- **Readability Score**: Measure of text readability (0-1, higher is better)
- **Visual Hierarchy**: Organization of UI elements by importance
- **OCR**: Optical Character Recognition - text extraction from images
- **MSER**: Maximally Stable Extremal Regions - text detection algorithm

### 11.5 Additional Resources

- **OpenCV Documentation**: https://docs.opencv.org/
- **Tesseract OCR**: https://github.com/tesseract-ocr/tesseract
- **OpenAI Vision API**: https://platform.openai.com/docs/guides/vision
- **Anthropic Claude API**: https://docs.anthropic.com/

### 11.6 Version History

**v0.1.0 (Current)**
- Initial release
- Basic screenshot capture
- UI element detection
- AI vision analysis
- Report generation
- Cross-platform support

---

## Document Information

**Document Version:** 1.0  
**Last Updated:** 2025-01-XX  
**Maintained By:** UX-MIRROR Development Team  
**Feedback:** Please report issues or suggest improvements via the project repository

---

**End of User Manual**






