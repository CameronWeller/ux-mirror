# Universal Active Monitoring Guide

## Overview

Universal Active Monitoring works with **ANY application type**:
- 🌐 **Web Applications** (via Playwright)
- 🪟 **Windows Executables** (native capture)
- 🎮 **Games** (Vulkan/DirectX capture + FPS monitoring)
- 📱 **Mobile Applications** (ADB/device capture)

It detects:
- **Performance Issues**: Hitches, stuttering, frame drops, FPS issues
- **Errors**: Application crashes, unexpected behavior
- **User Confusion**: Hesitation points, stuck states
- **Input Lag**: Responsiveness issues

## Key Features

### Performance Monitoring

- **FPS Tracking**: Real-time frame rate monitoring
- **Frame Time Analysis**: Detects stuttering and hitches
- **Stutter Detection**: Identifies frame time spikes
- **Hitch Detection**: Catches severe performance drops
- **FPS Drop Detection**: Alerts on significant FPS decreases

### Universal Application Support

Works across all application types with platform-specific optimizations.

## Usage

### CLI

```bash
# Monitor web application
ux-tester monitor-universal web https://example.com

# Monitor Windows executable
ux-tester monitor-universal windows notepad.exe

# Monitor game with FPS tracking
ux-tester monitor-universal game game.exe --target-fps 60

# Customize thresholds
ux-tester monitor-universal game game.exe \
  --target-fps 60 \
  --stutter-threshold 16.67 \
  --hitch-threshold 50.0
```

### Python API

```python
from src.integration.universal_active_monitor import (
    UniversalActiveMonitor,
    ApplicationType
)

# Monitor web app
monitor = UniversalActiveMonitor(api_key="key", app_type=ApplicationType.WEB)
await monitor.start_monitoring("https://example.com")

# Monitor Windows exe
monitor = UniversalActiveMonitor(api_key="key", app_type=ApplicationType.WINDOWS_EXE)
await monitor.start_monitoring("notepad.exe")

# Monitor game
monitor = UniversalActiveMonitor(api_key="key", app_type=ApplicationType.GAME)
monitor.target_fps = 60.0
monitor.stutter_threshold_ms = 16.67  # 60fps = 16.67ms per frame
await monitor.start_monitoring("game.exe", width=1920, height=1080)
```

## Performance Thresholds

### Stutter Detection

A **stutter** occurs when frame time exceeds the stutter threshold:

```python
monitor.stutter_threshold_ms = 33.0  # Default: 33ms (30fps minimum)
```

At 60fps target, each frame should take ~16.67ms. If a frame takes >33ms, it's a stutter.

### Hitch Detection

A **hitch** is a severe stutter (multiple frames):

```python
monitor.hitch_threshold_ms = 100.0  # Default: 100ms (3+ frames at 60fps)
```

Hitches are more severe and indicate significant performance problems.

### FPS Drop Detection

Detects when FPS drops significantly below target:

```python
monitor.fps_drop_threshold = 0.2  # Default: 20% drop
monitor.target_fps = 60.0
```

If FPS drops below 48fps (20% of 60), it's detected as a problem.

## Application Types

### Web Applications

Uses Playwright for capture and interaction tracking:

```python
monitor = UniversalActiveMonitor(api_key, ApplicationType.WEB)
await monitor.start_monitoring("https://example.com", headless=False)
```

**Detects:**
- Page load performance
- JavaScript errors
- Network issues
- UI responsiveness

### Windows Executables

Uses native Windows capture:

```python
monitor = UniversalActiveMonitor(api_key, ApplicationType.WINDOWS_EXE)
await monitor.start_monitoring("app.exe")
```

**Detects:**
- Application responsiveness
- UI freezes
- Performance degradation
- Error dialogs

### Games

Uses Vulkan/DirectX capture with FPS monitoring:

```python
monitor = UniversalActiveMonitor(api_key, ApplicationType.GAME)
monitor.target_fps = 60.0
monitor.stutter_threshold_ms = 16.67  # Strict for games
await monitor.start_monitoring("game.exe", width=1920, height=1080)
```

**Detects:**
- FPS drops
- Stuttering
- Hitches
- Frame time variance
- Input lag

### Mobile Applications

Uses ADB or device capture (coming soon):

```python
monitor = UniversalActiveMonitor(api_key, ApplicationType.MOBILE)
await monitor.start_monitoring("com.example.app")
```

## Problem Categories

### Performance Problems

- **`stutter`**: Frame time spike (medium severity)
- **`hitch`**: Severe frame time spike (high severity)
- **`performance`**: FPS drop or general performance issue

### Other Problems

- **`error`**: Application errors, crashes
- **`confusion`**: User hesitation, stuck states
- **`unexpected`**: UI issues detected by AI

## Configuration Examples

### Game Monitoring (Strict)

```python
monitor = UniversalActiveMonitor(api_key, ApplicationType.GAME)
monitor.target_fps = 60.0
monitor.stutter_threshold_ms = 16.67  # 60fps = 16.67ms
monitor.hitch_threshold_ms = 50.0     # 3 frames
monitor.fps_drop_threshold = 0.1      # 10% drop
```

### Desktop App Monitoring (Moderate)

```python
monitor = UniversalActiveMonitor(api_key, ApplicationType.WINDOWS_EXE)
monitor.target_fps = 60.0
monitor.stutter_threshold_ms = 33.0   # 30fps minimum
monitor.hitch_threshold_ms = 100.0    # 6 frames
monitor.fps_drop_threshold = 0.2      # 20% drop
```

### Web App Monitoring (Flexible)

```python
monitor = UniversalActiveMonitor(api_key, ApplicationType.WEB)
monitor.target_fps = 30.0  # Lower target for web
monitor.stutter_threshold_ms = 50.0
monitor.hitch_threshold_ms = 200.0
```

## Callbacks

### Problem Detection

```python
def on_problem(problem: ProblemDetected):
    if problem.category in ['stutter', 'hitch']:
        print(f"Performance issue: {problem.description}")
        metrics = problem.performance_metrics
        print(f"  FPS: {metrics.fps:.1f}")
        print(f"  Frame Time: {metrics.frame_time_ms:.2f}ms")

monitor.on_problem_detected = on_problem
```

### Performance Updates

```python
def on_performance(metrics: PerformanceMetrics):
    if metrics.hitch_detected:
        print(f"🚨 HITCH! Frame time: {metrics.frame_time_ms:.1f}ms")
    elif metrics.fps < monitor.target_fps * 0.9:
        print(f"⚠️  Low FPS: {metrics.fps:.1f}")

monitor.on_performance_update = on_performance
```

## Session Summary

Get comprehensive session statistics:

```python
summary = monitor.get_summary()

# Returns:
{
    "monitoring_active": True,
    "app_type": "game",
    "total_problems": 15,
    "problems_by_severity": {
        "critical": 0,
        "high": 3,
        "medium": 8,
        "low": 4
    },
    "problems_by_category": {
        "stutter": 5,
        "hitch": 2,
        "performance": 3,
        "error": 1
    },
    "performance": {
        "fps": 58.3,
        "frame_time_ms": 17.15,
        "stutter_count": 5,
        "hitch_detected": True
    },
    "fps_stats": {
        "current": 58.3,
        "average": 59.1,
        "min": 45.2,
        "max": 60.0
    }
}
```

## Best Practices

### 1. Set Appropriate Thresholds

- **Games**: Strict thresholds (16.67ms for 60fps)
- **Desktop Apps**: Moderate (33ms for 30fps minimum)
- **Web Apps**: Flexible (50ms+ acceptable)

### 2. Monitor Target FPS

Set realistic target FPS:
- Games: 60fps or 144fps
- Desktop: 60fps
- Web: 30fps

### 3. Use Callbacks Efficiently

Keep callbacks lightweight:

```python
def on_problem(problem):
    # Queue for async processing
    asyncio.create_task(process_problem_async(problem))
```

### 4. Review Performance Metrics

Always check FPS stats and frame time variance:

```python
summary = monitor.get_summary()
fps_stats = summary['fps_stats']
if fps_stats['min'] < target_fps * 0.8:
    print("Significant FPS drops detected")
```

## Example: Game Performance Monitoring

```python
import asyncio
from src.integration.universal_active_monitor import (
    UniversalActiveMonitor,
    ApplicationType
)

async def monitor_game():
    monitor = UniversalActiveMonitor(api_key, ApplicationType.GAME)
    
    # Configure for 60fps game
    monitor.target_fps = 60.0
    monitor.stutter_threshold_ms = 16.67
    monitor.hitch_threshold_ms = 50.0
    
    problems = []
    def collect_problems(p):
        if p.category in ['stutter', 'hitch']:
            problems.append(p)
    
    monitor.on_problem_detected = collect_problems
    
    await monitor.start_monitoring("game.exe", width=1920, height=1080)
    
    try:
        while monitor.monitoring:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        await monitor.stop_monitoring()
        
        summary = monitor.get_summary()
        print(f"Stutters: {summary['problems_by_category'].get('stutter', 0)}")
        print(f"Hitches: {summary['problems_by_category'].get('hitch', 0)}")
        print(f"Avg FPS: {summary['fps_stats']['average']:.1f}")

asyncio.run(monitor_game())
```

## Summary

Universal Active Monitoring provides comprehensive performance and UX monitoring for **any application type**. It automatically detects:

- ✅ **Hitches** - Severe frame time spikes
- ✅ **Stuttering** - Frame time variance
- ✅ **FPS Drops** - Performance degradation
- ✅ **Errors** - Application issues
- ✅ **Confusion** - User friction points

Perfect for:
- Game performance testing
- Desktop application QA
- Web application monitoring
- Mobile app testing
- Cross-platform UX analysis


