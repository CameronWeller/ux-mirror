#!/usr/bin/env python3
"""
UX Mirror - Game Integration Example
Combines Visual Analysis with Vulkan capture for game UI feedback
"""

import asyncio
import logging
from pathlib import Path
import time

# Import the key components
from agents.visual_analysis import VisualAnalysisAgent
from vulkan_screenshot_capture import VulkanScreenshotCapture, VulkanFrame
from user_input_tracker import get_tracker, UserInputTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameUIAnalyzer:
    """Integrates screenshot capture, input tracking, and AI analysis for games"""
    
    def __init__(self, openai_api_key: str = None):
        # Initialize components
        self.vulkan_capture = VulkanScreenshotCapture()
        self.input_tracker = get_tracker()
        self.visual_agent = VisualAnalysisAgent()
        
        # Configure OpenAI API if provided
        if openai_api_key:
            self.visual_agent.config['vision_apis']['openai_vision']['api_key'] = openai_api_key
        
        self.analysis_results = []
        
    async def start(self):
        """Start the integrated analysis system"""
        logger.info("Starting Game UI Analyzer...")
        
        # Start visual analysis agent
        await self.visual_agent.start()
        
        # Start input tracking
        self.input_tracker.start_tracking()
        
        # Setup Vulkan capture (1920x1080 default)
        if self.vulkan_capture.setup_shared_memory(1920, 1080):
            logger.info("Vulkan shared memory setup complete")
        else:
            logger.error("Failed to setup Vulkan shared memory")
            return False
        
        return True
    
    async def analyze_current_frame(self):
        """Capture and analyze current game frame"""
        # Capture frame from Vulkan
        frame = self.vulkan_capture.capture_frame()
        if not frame:
            logger.error("Failed to capture Vulkan frame")
            return None
        
        # Get recent user activity for context
        user_activity = self.input_tracker.get_recent_activity(seconds=5.0)
        
        # Convert frame to format for visual analysis
        screenshot_data = {
            'image_data': frame.to_pil_image().tobytes(),
            'resolution': (frame.width, frame.height),
            'timestamp': frame.timestamp,
            'platform': 'vulkan_game',
            'user_context': {
                'recent_clicks': user_activity.get('click_count', 0),
                'recent_keys': user_activity.get('key_count', 0),
                'click_hotspot': user_activity.get('click_hotspot'),
                'activity_rate': user_activity.get('activity_rate', 0)
            }
        }
        
        # Send to visual analysis agent
        analysis_request = {
            'type': 'analyze_screenshot',
            'data': screenshot_data,
            'analysis_config': {
                'check_game_ui': True,
                'check_accessibility': True,
                'check_performance': True,
                'context_prompt': f"""
                Analyze this game UI screenshot for:
                1. UI clarity and readability
                2. Button and control visibility
                3. Visual glitches or rendering issues
                4. General game UI/UX quality
                
                User activity context:
                - Recent clicks: {user_activity.get('click_count', 0)}
                - Activity rate: {user_activity.get('activity_rate', 0):.2f} events/sec
                - Click hotspot: {user_activity.get('click_hotspot', 'None')}
                """
            }
        }
        
        # Process analysis
        result = await self.visual_agent._handle_screenshot_analysis_request(analysis_request)
        
        # Store result
        self.analysis_results.append({
            'timestamp': time.time(),
            'frame_timestamp': frame.timestamp,
            'analysis': result,
            'user_activity': user_activity
        })
        
        return result
    
    async def continuous_analysis(self, interval_seconds: float = 3.0):
        """Continuously analyze game frames at specified interval"""
        logger.info(f"Starting continuous analysis every {interval_seconds} seconds")
        
        while True:
            try:
                result = await self.analyze_current_frame()
                if result:
                    self._log_analysis_summary(result)
                
                await asyncio.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Stopping continuous analysis...")
                break
            except Exception as e:
                logger.error(f"Error in continuous analysis: {e}")
                await asyncio.sleep(interval_seconds)
    
    def _log_analysis_summary(self, result: dict):
        """Log a summary of the analysis results"""
        if 'issues' in result:
            issue_count = len(result['issues'])
            if issue_count > 0:
                logger.info(f"Found {issue_count} UI/UX issues:")
                for issue in result['issues'][:3]:  # Log first 3 issues
                    logger.info(f"  - {issue.get('issue_type')}: {issue.get('description')}")
            else:
                logger.info("No UI/UX issues detected")
        
        if 'ui_elements' in result:
            logger.info(f"Detected {len(result['ui_elements'])} UI elements")
    
    async def analyze_specific_scenario(self, scenario_name: str, duration_seconds: float = 10.0):
        """Analyze a specific game scenario"""
        logger.info(f"Analyzing scenario: {scenario_name} for {duration_seconds} seconds")
        
        start_time = time.time()
        scenario_results = []
        
        while time.time() - start_time < duration_seconds:
            result = await self.analyze_current_frame()
            if result:
                scenario_results.append(result)
            await asyncio.sleep(1.0)  # 1 FPS for scenario analysis
        
        # Summarize scenario results
        summary = {
            'scenario_name': scenario_name,
            'duration': duration_seconds,
            'frames_analyzed': len(scenario_results),
            'total_issues': sum(len(r.get('issues', [])) for r in scenario_results),
            'unique_issue_types': set()
        }
        
        for result in scenario_results:
            for issue in result.get('issues', []):
                summary['unique_issue_types'].add(issue.get('issue_type'))
        
        summary['unique_issue_types'] = list(summary['unique_issue_types'])
        
        return summary
    
    def cleanup(self):
        """Cleanup resources"""
        self.input_tracker.stop_tracking()
        self.vulkan_capture.cleanup()
        logger.info("Cleanup complete")

async def main():
    """Example usage for 3DGameOfLife integration"""
    # Initialize analyzer (set your OpenAI API key here or in environment)
    analyzer = GameUIAnalyzer(openai_api_key="your-openai-api-key")
    
    # Start the system
    if await analyzer.start():
        try:
            # Example 1: Analyze current frame
            logger.info("Analyzing single frame...")
            result = await analyzer.analyze_current_frame()
            if result:
                logger.info(f"Analysis complete: {result}")
            
            # Example 2: Analyze specific scenario
            logger.info("Analyzing game menu scenario...")
            menu_summary = await analyzer.analyze_specific_scenario("main_menu", duration_seconds=5.0)
            logger.info(f"Menu analysis: {menu_summary}")
            
            # Example 3: Continuous monitoring
            logger.info("Starting continuous monitoring...")
            await analyzer.continuous_analysis(interval_seconds=3.0)
            
        finally:
            analyzer.cleanup()
    else:
        logger.error("Failed to start analyzer")

if __name__ == "__main__":
    asyncio.run(main()) 