# UX Mirror - Game Integration Quick Start Guide

## Setting Up Visual Analysis for 3DGameOfLife-Vulkan-Edition

This guide will help you integrate UX Mirror's visual analysis capabilities with your Vulkan game project.

## Prerequisites

1. **3DGameOfLife-Vulkan-Edition** running on your system
2. Python 3.11+ installed
3. OpenAI API key (for vision analysis)
4. Windows 10/11 with Vulkan support

## Step 1: Clone the 3DGameOfLife Project

```bash
# Clone the game project as a submodule
git submodule add https://github.com/CameronWeller/3DGameOfLife-Vulkan-Edition.git game-target/3DGameOfLife
cd game-target/3DGameOfLife
git checkout main
cd ../..
```

## Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install required packages
pip install -r requirements.txt
pip install -r requirements-vm.txt

# Install additional game integration dependencies
pip install pynput pillow numpy aiohttp
```

## Step 3: Configure the Visual Analysis Agent

Create a configuration file `.env` in the project root:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Vulkan Capture Settings
VULKAN_CAPTURE_WIDTH=1920
VULKAN_CAPTURE_HEIGHT=1080
VULKAN_SHARED_MEMORY_NAME=UXMirrorVulkanCapture

# Analysis Settings
ANALYSIS_INTERVAL_SECONDS=3.0
SCREENSHOT_QUALITY=high
```

## Step 4: Modify the Game for Screenshot Capture

Add the Vulkan capture layer to your game. In your game's main rendering loop, add:

```cpp
// In your Vulkan render loop (e.g., in present queue)
void PresentFrame(VkQueue queue, VkPresentInfoKHR* pPresentInfo) {
    // Add UX Mirror capture hook
    if (uxMirrorEnabled) {
        CaptureFrameToSharedMemory(swapchainImage);
    }
    
    // Continue with normal present
    vkQueuePresentKHR(queue, pPresentInfo);
}
```

## Step 5: Run the Visual Analysis Agent

```bash
# Start the visual analysis agent
python game_integration_example.py
```

Or use the provided integration script:

```python
import asyncio
import os
from game_integration_example import GameUIAnalyzer

async def analyze_game():
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Create analyzer
    analyzer = GameUIAnalyzer(openai_api_key=api_key)
    
    # Start analysis
    if await analyzer.start():
        print("Visual analysis started! Press Ctrl+C to stop.")
        
        # Run continuous analysis
        await analyzer.continuous_analysis(interval_seconds=3.0)

if __name__ == "__main__":
    asyncio.run(analyze_game())
```

## Step 6: Integration with Cursor AI

To feed the analysis results back to your AI coding assistant:

1. **Real-time Feedback Mode**:
   ```python
   # In your game_integration_example.py
   async def send_to_cursor(analysis_result):
       # Format the result for Cursor
       feedback = {
           "ui_issues": analysis_result.get('issues', []),
           "suggestions": analysis_result.get('suggestions', []),
           "screenshot_context": "Current game state analysis"
       }
       
       # Write to a file that Cursor can monitor
       with open("ui_feedback.json", "w") as f:
           json.dump(feedback, f, indent=2)
   ```

2. **Batch Analysis Mode**:
   ```bash
   # Run analysis for specific duration
   python -m agents.visual_analysis --game-mode --duration 60 --output game_ui_report.json
   ```

## Expected Output

When running successfully, you should see:

```
INFO - Starting Game UI Analyzer...
INFO - Vulkan shared memory setup complete
INFO - User input tracking started
INFO - Starting continuous analysis every 3.0 seconds
INFO - Found 2 UI/UX issues:
  - low_contrast_text: Game score text has insufficient contrast
  - small_clickable_elements: Menu buttons below recommended touch size
INFO - Detected 15 UI elements
```

## Troubleshooting

### Issue: "Failed to setup Vulkan shared memory"
- Ensure the game is running before starting the analyzer
- Check that the shared memory name matches in both applications
- Verify Vulkan drivers are up to date

### Issue: "No frames captured"
- Confirm the game is using the correct present mode
- Check Windows Defender/antivirus isn't blocking memory access
- Try running both applications as Administrator

### Issue: "OpenAI API errors"
- Verify your API key is correct and has vision model access
- Check your OpenAI account has sufficient credits
- Ensure internet connectivity

## Next Steps

1. **Train Custom Recognizers**: Use the visual analysis agent's training features to detect game-specific UI patterns
2. **Integrate with CI/CD**: Add automated UI testing to your build pipeline
3. **Create Custom Prompts**: Tailor the AI analysis for your specific game genre

## Example Analysis Results

Here's what a typical analysis might return:

```json
{
  "timestamp": 1704243621.5,
  "issues": [
    {
      "issue_type": "low_contrast_text",
      "severity": "medium",
      "description": "Score display text lacks sufficient contrast against game background",
      "location": [10, 10, 200, 50],
      "suggested_fix": "Increase text contrast or add background panel"
    },
    {
      "issue_type": "ui_overlap",
      "severity": "high", 
      "description": "Game menu overlaps with gameplay elements",
      "location": [860, 540, 200, 400],
      "suggested_fix": "Add semi-transparent background or reposition menu"
    }
  ],
  "ui_elements": [
    {"type": "button", "text": "Start Game", "confidence": 0.95},
    {"type": "text", "text": "Score: 1234", "confidence": 0.89}
  ],
  "performance_metrics": {
    "frame_capture_time": 0.023,
    "analysis_time": 1.245
  }
}
```

## Support

For issues specific to:
- **Vulkan Integration**: Check the Vulkan capture logs in `logs/vulkan_capture.log`
- **Visual Analysis**: Review `logs/visual_analysis.log`
- **API Issues**: Ensure your OpenAI API key has proper permissions

Happy game UI development! 🎮✨ 