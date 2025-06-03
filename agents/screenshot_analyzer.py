#!/usr/bin/env python3
"""
Screenshot Analysis Agent
========================

Analyzes screenshots over time by sending them to Anthropic for visual analysis.
Focuses on timing patterns and change detection while maintaining privacy.

Author: UX-Mirror System
"""

import os
import base64
import json
import re
from datetime import datetime
from typing import List, Dict, Any
import anthropic
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ScreenshotAnalyzer:
    def __init__(self, api_key: str = None):
        """Initialize the screenshot analyzer"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables or .env file")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.screenshot_dir = "game_screenshots"
        
    def get_screenshot_metadata(self, filename: str) -> Dict[str, Any]:
        """Extract metadata from screenshot filename"""
        # Parse filename: game_of_life_gen_XXX_YYYYMMDD_HHMMSS.png
        match = re.match(r'game_of_life_gen_(\d+)_(\d{8})_(\d{6})\.png', filename)
        if not match:
            return None
            
        generation = int(match.group(1))
        date_str = match.group(2)
        time_str = match.group(3)
        
        # Parse datetime
        timestamp = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
        
        return {
            "generation": generation,
            "timestamp": timestamp,
            "filename": filename,
            "relative_time": None  # Will be calculated later
        }
    
    def get_screenshot_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get screenshot files with metadata, sorted by generation"""
        if not os.path.exists(self.screenshot_dir):
            return []
        
        files = []
        for filename in os.listdir(self.screenshot_dir):
            if filename.endswith('.png'):
                metadata = self.get_screenshot_metadata(filename)
                if metadata:
                    files.append(metadata)
        
        # Sort by generation and take most recent ones
        files.sort(key=lambda x: x['generation'])
        files = files[-limit:] if len(files) > limit else files
        
        # Calculate relative timing
        if files:
            start_time = files[0]['timestamp']
            for file_meta in files:
                file_meta['relative_time'] = (file_meta['timestamp'] - start_time).total_seconds()
        
        return files
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_screenshot_sequence(self, screenshot_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send screenshots to Anthropic for temporal analysis"""
        
        if not screenshot_files:
            return {"error": "No screenshots found"}
        
        # Prepare images for analysis (limit to prevent large requests)
        max_images = 6
        step = max(1, len(screenshot_files) // max_images)
        selected_files = screenshot_files[::step][:max_images]
        
        # Build the message content
        content = [
            {
                "type": "text",
                "text": f"""Analyze this sequence of {len(selected_files)} screenshots from a 3D Game of Life simulation.

Context:
- These are auto-captured screenshots showing evolution over time
- Each screenshot shows a 3D grid with colored cubes representing living cells
- The simulation follows Conway's Game of Life rules adapted for 3D space
- Screenshots span from generation {selected_files[0]['generation']} to {selected_files[-1]['generation']}

Timeline:
{self._format_timeline(selected_files)}

Please analyze:
1. Visual changes over time
2. Population dynamics (increase/decrease in cube density)
3. Spatial patterns and structures
4. Color distribution and changes
5. Overall simulation health and stability
6. Any interesting emergent behaviors

Focus on temporal patterns and change detection."""
            }
        ]
        
        # Add images
        for i, file_meta in enumerate(selected_files):
            image_path = os.path.join(self.screenshot_dir, file_meta['filename'])
            try:
                image_data = self.encode_image(image_path)
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data
                    }
                })
                content.append({
                    "type": "text", 
                    "text": f"Screenshot {i+1}: Generation {file_meta['generation']}, Time +{file_meta['relative_time']:.0f}s"
                })
            except Exception as e:
                print(f"Failed to encode {file_meta['filename']}: {e}")
        
        try:
            # Send to Anthropic
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": content
                }]
            )
            
            return {
                "analysis": response.content[0].text,
                "images_analyzed": len(selected_files),
                "generation_range": [selected_files[0]['generation'], selected_files[-1]['generation']],
                "time_span_seconds": selected_files[-1]['relative_time']
            }
            
        except Exception as e:
            return {"error": f"API call failed: {e}"}
    
    def _format_timeline(self, files: List[Dict[str, Any]]) -> str:
        """Format timeline for context"""
        timeline = []
        for file_meta in files:
            timeline.append(f"Gen {file_meta['generation']:3d}: +{file_meta['relative_time']:3.0f}s")
        return "\n".join(timeline)
    
    def analyze_latest_screenshots(self, count: int = 8) -> Dict[str, Any]:
        """Analyze the most recent screenshots"""
        screenshot_files = self.get_screenshot_files(limit=count)
        
        if not screenshot_files:
            return {"error": "No screenshots found in directory"}
        
        print(f"Found {len(screenshot_files)} screenshots")
        print(f"Generation range: {screenshot_files[0]['generation']} - {screenshot_files[-1]['generation']}")
        print(f"Time span: {screenshot_files[-1]['relative_time']:.0f} seconds")
        
        # Perform analysis
        result = self.analyze_screenshot_sequence(screenshot_files)
        
        # Add summary metadata (privacy-safe)
        result['metadata'] = {
            "analysis_timestamp": datetime.now().isoformat(),
            "screenshots_available": len(screenshot_files),
            "generation_span": screenshot_files[-1]['generation'] - screenshot_files[0]['generation'],
            "time_span_seconds": screenshot_files[-1]['relative_time'],
            "source": "3D_Game_of_Life_Demo"
        }
        
        return result

def main():
    """Main function for testing"""
    try:
        analyzer = ScreenshotAnalyzer()
        
        print("Screenshot Analysis Agent")
        print("=" * 40)
        print("Analyzing Game of Life screenshots...")
        
        # Analyze recent screenshots
        result = analyzer.analyze_latest_screenshots(count=10)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        # Display results
        print("\nAnalysis Results:")
        print("=" * 40)
        print(f"Images analyzed: {result['images_analyzed']}")
        print(f"Generation range: {result['generation_range'][0]} - {result['generation_range'][1]}")
        print(f"Time span: {result['time_span_seconds']:.0f} seconds")
        print("\nVisual Analysis:")
        print("-" * 40)
        print(result['analysis'])
        
        # Save results
        output_file = f"screenshot_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nResults saved to: {output_file}")
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nTo fix this:")
        print("1. Create a .env file in the project root")
        print("2. Add your Anthropic API key: ANTHROPIC_API_KEY=your_key_here")
        print("3. Or set the environment variable: export ANTHROPIC_API_KEY=your_key_here")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 