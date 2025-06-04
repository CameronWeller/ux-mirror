# Simple UX Tester

A straightforward manual testing tool to answer two critical questions:
1. **"Did this UI interaction work as expected?"** (timing, visual changes)
2. **"Is what's showing on screen what we expected?"** (AI-powered content validation)

## Quick Start

### 1. Test a Button Click with Content Validation

```bash
# Capture before clicking with expectation
python simple_ux_tester.py capture --before --expect "login screen with username field visible"

# Click your button/UI element
# (do this manually)

# Capture after clicking with expectation  
python simple_ux_tester.py capture --after --expect "dashboard showing welcome message"

# Analyze the results
python simple_ux_tester.py analyze
```

### 2. View Results

The tool will tell you:
- ✅ **Did the UI change?** (Something actually happened)
- ⚡ **How fast was the response?** (Under 500ms is good)
- 🎨 **Any visual issues?** (Loading problems, blank screens)
- 🤖 **Content matches expectations?** (AI validates what's displayed)
- 📊 **Overall UX quality score** (0-100)

## What It Checks

### Response Time
- Measures time between before/after screenshots
- Flags anything over 500ms as slow
- Helps identify sluggish interactions

### Visual Changes
- Compares before/after images pixel by pixel
- Detects if UI actually updated
- Catches "broken" buttons that don't do anything

### Content Validation (NEW!)
- **Uses AI vision** to understand what's displayed
- **Validates expectations** against actual content
- **Supports both Claude and OpenAI** (tries Claude first, OpenAI as fallback)
- Catches issues like:
  - Wrong page loaded
  - Missing content
  - Error messages instead of expected content
  - Loading screens that never finish

### Basic Quality Issues
- Mostly black/white screens (loading problems)
- Empty interfaces (missing content)
- Very low UI element density

## Commands

```bash
# Capture screenshots with content expectations
python simple_ux_tester.py capture --before --expect "description of what should be visible"
python simple_ux_tester.py capture --after --expect "description of expected result"

# Basic capture without content validation
python simple_ux_tester.py capture --before
python simple_ux_tester.py capture --after

# Analyze latest pair
python simple_ux_tester.py analyze

# List all captures
python simple_ux_tester.py list

# Clean up old screenshots
python simple_ux_tester.py clean --keep 10
```

## Configuration

Edit `config.env` to set up AI APIs and adjust settings:

```bash
# AI Vision APIs (you only need one)
ANTHROPIC_API_KEY=your_anthropic_key_here    # Preferred - Claude vision
OPENAI_API_KEY=your_openai_key_here          # Fallback - GPT-4 vision

# Enable/disable content validation
CONTENT_VALIDATION_ENABLED=true

# Sensitivity settings
UI_CHANGE_THRESHOLD=0.05              # Visual change sensitivity
RESPONSE_TIME_THRESHOLD=500           # Response time threshold (ms)
SCREENSHOT_QUALITY=85                 # Image quality (1-100)
```

## Example Output with Content Validation

```
==================================================
UX ANALYSIS SUMMARY
==================================================
Overall Quality: EXCELLENT (95/100)

Response Time: 234ms ✓ GOOD
UI Changed: 0.127 ✓ YES

Content Validation:
  ✓ Content matches expectations
  Before: Login screen with username field and login button visible
  After: Dashboard showing welcome message and navigation menu

✅ No major issues detected!

==================================================
```

## AI Vision Support

### Anthropic Claude (Preferred)
- Uses Claude 3.5 Sonnet with vision
- Excellent at understanding UI context
- More reliable for content validation

### OpenAI GPT-4 Vision (Fallback)
- Automatic fallback if Claude fails
- Good general vision capabilities
- Useful as backup option

### No API Key? No Problem!
- Tool works without AI APIs
- Still provides timing and visual change detection
- Content validation simply reports "unavailable"

## Use Cases

- **Login Flow Testing**: "Does clicking login actually show the dashboard?"
- **Form Validation**: "Do error messages appear correctly?"
- **Navigation Testing**: "Does the menu link go to the right page?"
- **Game UI Testing**: "Does the settings button open settings menu?"
- **E-commerce**: "Does add to cart show the cart page?"
- **Error Handling**: "Does invalid input show proper error messages?"

## Privacy & Security

- 🔒 **Manual only**: No automatic screenshots
- 🛡️ **Privacy-focused**: Only sends images you explicitly capture
- 🎯 **Targeted**: Test specific interactions you care about
- 📁 **Local storage**: Screenshots stored locally
- 🤖 **Optional AI**: Content validation can be disabled

## Dependencies

```bash
pip install opencv-python pillow numpy anthropic  # For Claude vision
pip install openai  # Optional, for OpenAI fallback
```

Simple computer vision + optional AI vision for comprehensive UX testing! 