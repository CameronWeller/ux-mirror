#!/usr/bin/env python3
"""
Temporal Screenshot Analysis Agent
=================================

Enhanced version that focuses on temporal patterns and change detection
across different generation ranges. Provides minimal security metadata
while maximizing timing analysis capabilities.

Author: UX-Mirror System
"""

import os
import base64
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import anthropic
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TemporalScreenshotAnalyzer:
    def __init__(self, api_key: str = None):
        """Initialize the temporal screenshot analyzer"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables or .env file")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.screenshot_dir = "game_screenshots"
        
    def get_all_screenshots(self) -> List[Dict[str, Any]]:
        """Get all screenshots with full temporal metadata"""
        if not os.path.exists(self.screenshot_dir):
            return []
        
        files = []
        for filename in os.listdir(self.screenshot_dir):
            if filename.endswith('.png'):
                metadata = self.parse_screenshot_metadata(filename)
                if metadata:
                    files.append(metadata)
        
        # Sort by generation
        files.sort(key=lambda x: x['generation'])
        
        # Calculate temporal relationships
        if files:
            start_time = files[0]['timestamp']
            for i, file_meta in enumerate(files):
                file_meta['relative_time'] = (file_meta['timestamp'] - start_time).total_seconds()
                file_meta['sequence_index'] = i
                
                # Generation interval analysis
                if i > 0:
                    file_meta['generation_interval'] = file_meta['generation'] - files[i-1]['generation']
                    file_meta['time_interval'] = file_meta['relative_time'] - files[i-1]['relative_time']
                else:
                    file_meta['generation_interval'] = 0
                    file_meta['time_interval'] = 0.0
        
        return files
    
    def parse_screenshot_metadata(self, filename: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from screenshot filename"""
        # Parse filename: game_of_life_gen_XXX_YYYYMMDD_HHMMSS.png
        match = re.match(r'game_of_life_gen_(\d+)_(\d{8})_(\d{6})\.png', filename)
        if not match:
            return None
            
        generation = int(match.group(1))
        date_str = match.group(2)
        time_str = match.group(3)
        
        # Parse datetime
        timestamp = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
        
        # Calculate file stats for additional metadata
        filepath = os.path.join(self.screenshot_dir, filename)
        file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        
        return {
            "generation": generation,
            "timestamp": timestamp,
            "filename": filename,
            "filepath": filepath,
            "file_size": file_size,
            "relative_time": None,  # Will be calculated later
            "sequence_index": None,
            "generation_interval": None,
            "time_interval": None
        }
    
    def select_representative_screenshots(self, screenshots: List[Dict], 
                                       analysis_type: str = "temporal") -> List[Dict]:
        """Select screenshots for analysis based on different strategies"""
        
        if not screenshots:
            return []
        
        if analysis_type == "temporal":
            # Select evenly spaced across time
            max_images = 8
            if len(screenshots) <= max_images:
                return screenshots
            
            step = len(screenshots) // max_images
            return [screenshots[i] for i in range(0, len(screenshots), step)][:max_images]
            
        elif analysis_type == "generation_focused":
            # Select based on generation intervals
            max_images = 6
            if len(screenshots) <= max_images:
                return screenshots
            
            # Include first, last, and evenly distributed middle ones
            selected = [screenshots[0]]  # First
            if len(screenshots) > 2:
                mid_count = max_images - 2
                mid_step = (len(screenshots) - 2) // mid_count if mid_count > 0 else 1
                for i in range(1, len(screenshots) - 1, mid_step):
                    if len(selected) < max_images - 1:
                        selected.append(screenshots[i])
            selected.append(screenshots[-1])  # Last
            return selected
            
        elif analysis_type == "change_detection":
            # Select screenshots that might show significant changes
            max_images = 6
            if len(screenshots) <= max_images:
                return screenshots
            
            # Select based on time intervals (detect periods of activity)
            selected = []
            interval_threshold = 10  # seconds
            
            selected.append(screenshots[0])  # Always include first
            
            for i, shot in enumerate(screenshots[1:-1], 1):
                if shot['time_interval'] > interval_threshold or len(selected) < max_images - 1:
                    selected.append(shot)
                    if len(selected) >= max_images - 1:
                        break
            
            selected.append(screenshots[-1])  # Always include last
            return selected
            
        return screenshots[:6]  # Default fallback
    
    def analyze_temporal_sequence(self, screenshots: List[Dict], 
                                analysis_type: str = "temporal") -> Dict[str, Any]:
        """Analyze screenshot sequence with temporal focus"""
        
        if not screenshots:
            return {"error": "No screenshots provided"}
        
        selected_shots = self.select_representative_screenshots(screenshots, analysis_type)
        
        # Build temporal analysis context
        temporal_context = self.build_temporal_context(selected_shots, screenshots)
        
        # Prepare API content
        content = [
            {
                "type": "text",
                "text": f"""Analyze this temporal sequence of {len(selected_shots)} screenshots from a 3D Game of Life simulation.

TEMPORAL ANALYSIS FOCUS:
{temporal_context}

ANALYSIS OBJECTIVES:
1. Temporal pattern detection - How does the simulation change over time?
2. Population dynamics evolution - Trace cell population changes
3. Spatial pattern emergence - Identify recurring or evolving structures
4. Stability assessment - Is the simulation stable, oscillating, or chaotic?
5. Visual consistency - Are there rendering or display issues over time?
6. Generation-to-generation changes - What happens between captures?

Please focus on temporal patterns and provide insights into the simulation's behavior over time."""
            }
        ]
        
        # Add images with temporal context
        for i, shot in enumerate(selected_shots):
            try:
                image_data = base64.b64encode(open(shot['filepath'], 'rb').read()).decode('utf-8')
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data
                    }
                })
                
                # Rich temporal context for each image
                context_text = (f"Screenshot {i+1}/{len(selected_shots)}: "
                              f"Gen {shot['generation']}, "
                              f"Time +{shot['relative_time']:.0f}s")
                
                if shot['generation_interval'] > 0:
                    context_text += f", Δgen +{shot['generation_interval']}"
                if shot['time_interval'] > 0:
                    context_text += f", Δtime +{shot['time_interval']:.1f}s"
                
                content.append({
                    "type": "text", 
                    "text": context_text
                })
                
            except Exception as e:
                print(f"Failed to encode {shot['filename']}: {e}")
        
        try:
            # Send to Anthropic
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": content
                }]
            )
            
            return {
                "analysis": response.content[0].text,
                "analysis_type": analysis_type,
                "images_analyzed": len(selected_shots),
                "total_screenshots": len(screenshots),
                "generation_range": [screenshots[0]['generation'], screenshots[-1]['generation']],
                "time_span_seconds": screenshots[-1]['relative_time'],
                "temporal_metrics": self.calculate_temporal_metrics(screenshots)
            }
            
        except Exception as e:
            return {"error": f"API call failed: {e}"}
    
    def build_temporal_context(self, selected_shots: List[Dict], 
                             all_shots: List[Dict]) -> str:
        """Build rich temporal context for analysis"""
        context_lines = []
        
        # Overall temporal scope
        total_time = all_shots[-1]['relative_time']
        total_generations = all_shots[-1]['generation'] - all_shots[0]['generation']
        avg_gen_time = total_time / total_generations if total_generations > 0 else 0
        
        context_lines.append(f"Total timespan: {total_time:.0f} seconds across {total_generations} generations")
        context_lines.append(f"Average time per generation: {avg_gen_time:.1f} seconds")
        context_lines.append(f"Total screenshots available: {len(all_shots)}")
        context_lines.append(f"Selected for analysis: {len(selected_shots)}")
        
        # Temporal distribution of selected shots
        context_lines.append("\nSelected screenshots temporal distribution:")
        for i, shot in enumerate(selected_shots):
            line = f"  {i+1}. Gen {shot['generation']:3d} at +{shot['relative_time']:3.0f}s"
            if i > 0:
                time_gap = shot['relative_time'] - selected_shots[i-1]['relative_time']
                gen_gap = shot['generation'] - selected_shots[i-1]['generation']
                line += f" (gap: {time_gap:.0f}s, {gen_gap} gen)"
            context_lines.append(line)
        
        return "\n".join(context_lines)
    
    def calculate_temporal_metrics(self, screenshots: List[Dict]) -> Dict[str, Any]:
        """Calculate temporal analysis metrics (privacy-safe)"""
        if not screenshots:
            return {}
        
        generation_intervals = [s['generation_interval'] for s in screenshots[1:]]
        time_intervals = [s['time_interval'] for s in screenshots[1:]]
        
        return {
            "total_screenshots": len(screenshots),
            "generation_span": screenshots[-1]['generation'] - screenshots[0]['generation'],
            "time_span_seconds": screenshots[-1]['relative_time'],
            "avg_generation_interval": sum(generation_intervals) / len(generation_intervals) if generation_intervals else 0,
            "avg_time_interval": sum(time_intervals) / len(time_intervals) if time_intervals else 0,
            "max_generation_gap": max(generation_intervals) if generation_intervals else 0,
            "max_time_gap": max(time_intervals) if time_intervals else 0,
            "screenshot_frequency": len(screenshots) / (screenshots[-1]['relative_time'] / 60) if screenshots[-1]['relative_time'] > 0 else 0,  # per minute
        }
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run multiple types of temporal analysis"""
        screenshots = self.get_all_screenshots()
        
        if not screenshots:
            return {"error": "No screenshots found"}
        
        print(f"Found {len(screenshots)} screenshots")
        print(f"Generation range: {screenshots[0]['generation']} - {screenshots[-1]['generation']}")
        print(f"Time span: {screenshots[-1]['relative_time']:.0f} seconds")
        
        results = {
            "metadata": {
                "analysis_timestamp": datetime.now().isoformat(),
                "total_screenshots": len(screenshots),
                "source": "3D_Game_of_Life_Demo"
            }
        }
        
        # Run different analysis types
        analysis_types = ["temporal", "generation_focused", "change_detection"]
        
        for analysis_type in analysis_types:
            print(f"\nRunning {analysis_type} analysis...")
            try:
                result = self.analyze_temporal_sequence(screenshots, analysis_type)
                results[f"{analysis_type}_analysis"] = result
                
                if "error" not in result:
                    print(f"✓ {analysis_type} analysis completed ({result['images_analyzed']} images)")
                else:
                    print(f"✗ {analysis_type} analysis failed: {result['error']}")
                    
            except Exception as e:
                print(f"✗ {analysis_type} analysis error: {e}")
                results[f"{analysis_type}_analysis"] = {"error": str(e)}
        
        return results

def main():
    """Main function for comprehensive temporal analysis"""
    try:
        analyzer = TemporalScreenshotAnalyzer()
        
        print("Temporal Screenshot Analysis Agent")
        print("=" * 50)
        print("Running comprehensive temporal analysis...")
        
        # Run all analysis types
        results = analyzer.run_comprehensive_analysis()
        
        if "error" in results:
            print(f"Error: {results['error']}")
            return
        
        # Save comprehensive results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"temporal_analysis_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nComprehensive analysis saved to: {output_file}")
        
        # Print summary
        print("\nAnalysis Summary:")
        print("=" * 50)
        for analysis_type in ["temporal", "generation_focused", "change_detection"]:
            key = f"{analysis_type}_analysis"
            if key in results and "error" not in results[key]:
                result = results[key]
                print(f"\n{analysis_type.upper()} ANALYSIS:")
                print(f"  Images analyzed: {result['images_analyzed']}")
                print(f"  Generation range: {result['generation_range']}")
                print(f"  Time span: {result['time_span_seconds']:.0f}s")
                
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nTo fix this:")
        print("1. Create a .env file in the project root")
        print("2. Add your Anthropic API key: ANTHROPIC_API_KEY=your_key_here")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 