#!/usr/bin/env python3
"""
Vulkan Game of Life Viewer
- Captures frames from Vulkan Game of Life
- Displays them in an interactive window
- Takes screenshots with '1' key
- Analyzes UI/UX in real-time
"""

import pygame
import sys
import time
import asyncio
import logging
from pathlib import Path
from typing import Optional, Tuple

from vulkan_screenshot_capture import VulkanScreenshotCapture, VulkanFrame
from agents.visual_analysis import VisualAnalysisAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VulkanGameViewer:
    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
        self.vulkan_capture = VulkanScreenshotCapture()
        self.visual_agent = VisualAnalysisAgent()
        self.last_frame: Optional[VulkanFrame] = None
        self.last_analysis = None
        self.analysis_results = []
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Vulkan Game of Life Viewer")
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.clock = pygame.time.Clock()
        
    async def start(self):
        """Start the viewer and capture system"""
        logger.info("Starting Vulkan Game Viewer...")
        
        # Start visual analysis agent
        await self.visual_agent.start()
        
        # Setup Vulkan capture
        if self.vulkan_capture.setup_shared_memory(self.width, self.height):
            logger.info("Vulkan shared memory setup complete")
            return True
        else:
            logger.error("Failed to setup Vulkan shared memory")
            return False
    
    def draw_ui(self, fps: float):
        """Draw UI overlays"""
        # Title
        pygame.draw.rect(self.screen, (42, 42, 42), (self.width//2-120, 10, 240, 40), border_radius=8)
        text = self.font.render("Vulkan Game of Life", True, (255,255,255))
        self.screen.blit(text, (self.width//2-100, 15))
        
        # Stats
        pygame.draw.rect(self.screen, (42,42,42), (20, 20, 180, 100), border_radius=8)
        self.screen.blit(self.small_font.render(f"FPS: {int(fps)}", True, (255,255,255)), (30, 30))
        if self.last_frame:
            self.screen.blit(self.small_font.render(f"Frame: {self.last_frame.timestamp:.2f}", True, (255,255,255)), (30, 50))
        
        # Controls
        pygame.draw.rect(self.screen, (42,42,42), (20, self.height-160, 180, 130), border_radius=8)
        controls = [
            ("1", "Screenshot"),
            ("Space", "Pause/Resume"),
            ("R", "Reset"),
            ("Q", "Quit")
        ]
        y = self.height-150
        for key, action in controls:
            self.screen.blit(self.small_font.render(f"{key}:", True, (0,255,0)), (30, y))
            self.screen.blit(self.small_font.render(action, True, (255,255,255)), (90, y))
            y += 20
        
        # Analysis results
        if self.last_analysis:
            pygame.draw.rect(self.screen, (42,42,42), (self.width-320, 20, 300, 200), border_radius=8)
            self.screen.blit(self.small_font.render("UI Analysis:", True, (255,255,255)), (self.width-310, 30))
            y = 50
            for issue in self.last_analysis.get('issues', [])[:5]:  # Show first 5 issues
                self.screen.blit(self.small_font.render(f"• {issue.get('description', '')}", True, (255,100,100)), (self.width-300, y))
                y += 20
    
    async def analyze_frame(self, frame: VulkanFrame):
        """Analyze the current frame"""
        screenshot_data = {
            'image_data': frame.to_pil_image().tobytes(),
            'resolution': (frame.width, frame.height),
            'timestamp': frame.timestamp,
            'platform': 'vulkan_game'
        }
        
        analysis_request = {
            'type': 'analyze_screenshot',
            'data': screenshot_data,
            'analysis_config': {
                'check_game_ui': True,
                'check_accessibility': True,
                'check_performance': True,
                'context_prompt': """
                Analyze this game UI screenshot for:
                1. UI clarity and readability
                2. Button and control visibility
                3. Visual glitches or rendering issues
                4. General game UI/UX quality
                """
            }
        }
        
        result = await self.visual_agent._handle_screenshot_analysis_request(analysis_request)
        self.last_analysis = result
        self.analysis_results.append({
            'timestamp': time.time(),
            'frame_timestamp': frame.timestamp,
            'analysis': result
        })
        return result
    
    def run(self):
        """Main viewer loop"""
        running = True
        paused = False
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        # Take screenshot
                        fname = f"vulkan_game_screenshot_{int(time.time())}.png"
                        pygame.image.save(self.screen, fname)
                        logger.info(f"Screenshot saved: {fname}")
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_r:
                        # Reset analysis
                        self.last_analysis = None
                    elif event.key == pygame.K_q:
                        running = False
            
            if not paused:
                # Capture frame
                frame = self.vulkan_capture.capture_frame()
                if frame:
                    self.last_frame = frame
                    # Convert frame to pygame surface
                    frame_surface = pygame.image.fromstring(
                        frame.data.tobytes(),
                        (frame.width, frame.height),
                        'RGBA'
                    )
                    # Draw frame
                    self.screen.blit(frame_surface, (0, 0))
                    
                    # Analyze frame (every 3 seconds)
                    if not hasattr(self, '_last_analysis_time') or time.time() - self._last_analysis_time > 3:
                        asyncio.create_task(self.analyze_frame(frame))
                        self._last_analysis_time = time.time()
            
            # Draw UI
            fps = self.clock.get_fps()
            self.draw_ui(fps)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        # Cleanup
        self.vulkan_capture.cleanup()
        pygame.quit()
        sys.exit()

async def main():
    viewer = VulkanGameViewer()
    if await viewer.start():
        viewer.run()
    else:
        logger.error("Failed to start viewer")

if __name__ == "__main__":
    asyncio.run(main()) 