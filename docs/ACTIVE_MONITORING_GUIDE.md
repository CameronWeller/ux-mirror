# Active User Monitoring Guide

## Overview

Active User Monitoring watches users interact with websites/applications in real-time and automatically detects problems they encounter. This is perfect for usability testing, QA sessions, and understanding real user friction points.

## Features

### Real-Time Problem Detection

- **Errors**: JavaScript errors, HTTP errors, console warnings
- **Confusion Points**: User hesitation (detected via inactivity)
- **Unexpected Behavior**: UI issues detected by AI analysis
- **Performance Issues**: Slow requests, timeouts
- **Accessibility Problems**: Issues detected during interaction

### Interaction Tracking

- Monitors clicks, typing, navigation
- Tracks user flow through the application
- Captures screenshots at key moments
- Builds context from interaction history

## Usage

### Python API

```python
from src.integration.playwright_active_monitor import PlaywrightActiveMonitor, ProblemDetected

# Initialize monitor
monitor = PlaywrightActiveMonitor(api_key="your-key")

# Set up callbacks
def handle_problem(problem: ProblemDetected):
    print(f"⚠️  {problem.severity.upper()}: {problem.description}")
    print(f"   Category: {problem.category}")
    if problem.user_action:
        print(f"   Triggered by: {problem.user_action.event_type}")

monitor.on_problem_detected = handle_problem

# Start monitoring (headless=False so user can interact)
await monitor.start_monitoring("https://example.com", headless=False)

# Monitor runs in background
# User interacts with browser window
# Problems detected automatically

# Stop when done
await monitor.stop_monitoring()

# Get summary
summary = monitor.get_summary()
print(f"Total problems: {summary['problems_detected']}")
```

### CLI Usage

```bash
# Basic monitoring
ux-tester playwright monitor https://example.com

# Adjust hesitation threshold (default: 5 seconds)
ux-tester playwright monitor https://example.com --hesitation-threshold 3.0

# Use Anthropic instead of OpenAI
ux-tester playwright monitor https://example.com --provider anthropic
```

## Problem Categories

### 1. Errors (`category: "error"`)
- JavaScript runtime errors
- HTTP 4xx/5xx responses
- Console errors/warnings
- Page crashes

**Example:**
```
⚠️  HIGH: HTTP 500 error: https://api.example.com/data
   Category: error
   Evidence: {"status": 500, "url": "https://api.example.com/data"}
```

### 2. Confusion (`category: "confusion"`)
- User inactive for extended period (hesitation threshold)
- Indicates potential confusion or being stuck
- Detected via inactivity monitoring

**Example:**
```
⚠️  MEDIUM: User inactive for 7.3s - possible confusion or hesitation
   Category: confusion
   Evidence: {"inactive_duration": 7.3, "last_interaction": "click on button.submit"}
```

### 3. Unexpected (`category: "unexpected"`)
- UI issues detected by AI vision analysis
- Problems found during periodic analysis
- Visual inconsistencies or broken states

**Example:**
```
⚠️  HIGH: UI issue detected: Button text not readable
   Category: unexpected
   Evidence: {"location": "top-right", "type": "readability"}
```

### 4. Performance (`category: "performance"`)
- Slow network requests
- Timeouts
- Long page load times

## Configuration

### Hesitation Threshold

The hesitation threshold determines how long a user can be inactive before it's considered a confusion point.

```python
monitor.hesitation_threshold = 5.0  # 5 seconds (default)
```

### Analysis Interval

How often to analyze the current page state:

```python
monitor.analysis_interval = 2.0  # Every 2 seconds (default)
```

### Enable/Disable Features

```python
monitor.error_detection_enabled = True  # Detect errors (default: True)
monitor.performance_monitoring = True   # Monitor performance (default: True)
```

## Callbacks

### Problem Detection Callback

Called whenever a problem is detected:

```python
def on_problem(problem: ProblemDetected):
    # Send to notification system
    send_to_slack(problem)
    
    # Log to database
    log_problem(problem)
    
    # Alert if critical
    if problem.severity == "critical":
        send_alert(problem)

monitor.on_problem_detected = on_problem
```

### Interaction Callback

Called for each user interaction:

```python
def on_interaction(interaction: InteractionEvent):
    # Track user flow
    log_interaction(interaction)
    
    # Update analytics
    analytics.track(interaction.event_type, interaction.target)

monitor.on_interaction = on_interaction
```

## Session Summary

Get a summary of the monitoring session:

```python
summary = monitor.get_summary()

# Returns:
{
    "monitoring_active": True,
    "current_url": "https://example.com",
    "total_interactions": 42,
    "problems_detected": 5,
    "problems_by_severity": {
        "critical": 1,
        "high": 2,
        "medium": 2,
        "low": 0
    },
    "problems_by_category": {
        "error": 2,
        "confusion": 1,
        "unexpected": 2
    },
    "recent_problems": [...]
}
```

## Best Practices

### 1. Use Non-Headless Mode
Always use `headless=False` for active monitoring so users can actually interact:

```python
await monitor.start_monitoring(url, headless=False)
```

### 2. Set Appropriate Thresholds
Adjust hesitation threshold based on your use case:
- **Fast-paced apps**: 3-5 seconds
- **Complex forms**: 7-10 seconds
- **Reading content**: 10-15 seconds

### 3. Handle Callbacks Efficiently
Keep callbacks lightweight to avoid blocking:

```python
def on_problem(problem):
    # Queue for async processing
    asyncio.create_task(process_problem_async(problem))
```

### 4. Review Session Summaries
Always review the summary after monitoring:

```python
summary = monitor.get_summary()
print(f"Found {summary['problems_detected']} problems")
for category, count in summary['problems_by_category'].items():
    print(f"  {category}: {count}")
```

## Example: Full Monitoring Session

```python
import asyncio
from src.integration.playwright_active_monitor import PlaywrightActiveMonitor

async def monitor_session():
    monitor = PlaywrightActiveMonitor(api_key="your-key")
    
    # Configure
    monitor.hesitation_threshold = 5.0
    
    # Set up callbacks
    problems = []
    
    def collect_problems(problem):
        problems.append(problem)
        print(f"⚠️  {problem.severity}: {problem.description}")
    
    monitor.on_problem_detected = collect_problems
    
    try:
        # Start monitoring
        await monitor.start_monitoring("https://example.com", headless=False)
        
        print("Monitoring active. Interact with the browser...")
        print("Press Ctrl+C to stop")
        
        # Keep running
        while monitor.monitoring:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print("\nStopping...")
    
    finally:
        await monitor.stop_monitoring()
        
        # Print summary
        summary = monitor.get_summary()
        print(f"\nSession complete:")
        print(f"  Interactions: {summary['total_interactions']}")
        print(f"  Problems: {summary['problems_detected']}")
        
        # Export problems
        with open("problems.json", "w") as f:
            import json
            json.dump([p.to_dict() for p in problems], f, indent=2)

asyncio.run(monitor_session())
```

## Integration with Testing

Active monitoring can be integrated into automated testing workflows:

```python
# During a test session
async def run_test_with_monitoring():
    monitor = PlaywrightActiveMonitor(api_key="your-key")
    
    test_problems = []
    monitor.on_problem_detected = lambda p: test_problems.append(p)
    
    await monitor.start_monitoring(test_url, headless=False)
    
    # Run your test
    # ... test code ...
    
    await monitor.stop_monitoring()
    
    # Assert no critical problems
    critical = [p for p in test_problems if p.severity == "critical"]
    assert len(critical) == 0, f"Found {len(critical)} critical problems"
```

## Troubleshooting

### Browser Not Opening
- Ensure `headless=False`
- Check Playwright browser installation: `playwright install chromium`

### No Problems Detected
- Verify API key is set
- Check that user is actually interacting
- Lower hesitation threshold if needed
- Enable error detection: `monitor.error_detection_enabled = True`

### Too Many False Positives
- Increase hesitation threshold
- Adjust analysis interval
- Filter problems by severity in callbacks

## Summary

Active User Monitoring provides real-time visibility into user experience issues. It automatically detects problems as users interact with your application, making it perfect for:

- **Usability Testing**: Watch real users and see where they struggle
- **QA Sessions**: Automatically catch issues during testing
- **Production Monitoring**: Monitor real user sessions (with privacy considerations)
- **A/B Testing**: Compare problem rates between variants

The system builds on Playwright's robust automation and adds AI-powered problem detection to give you comprehensive UX insights.

