#!/usr/bin/env python3
"""
UX Mirror API - Visual Feedback for AI Game Development
Main interface for AI agents to get visual feedback on their game builds
"""

import os
import sys
import asyncio
import json
import argparse
from typing import Dict, Optional, List, Any
from datetime import datetime
import logging
from pathlib import Path
from dataclasses import dataclass
import base64

# Import our modules
from vulkan_screenshot_capture import VulkanScreenshotCapture, VulkanFrame
from ai_vision_analyzer import AIVisionAnalyzer, GameUIFeedbackProcessor
from user_input_tracker import UserInputTracker

# FastAPI for the API server
try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Models
if API_AVAILABLE:
    class ScreenshotRequest(BaseModel):
        """Request model for screenshot analysis"""
        game_window_name: Optional[str] = None
        context: Optional[str] = None
        include_user_input: bool = True
        specific_concern: Optional[str] = None
    
    class FeedbackResponse(BaseModel):
        """Response model for AI feedback"""
        timestamp: str
        summary: str
        issues: List[Dict[str, Any]]
        recommendations: List[str]
        code_suggestions: List[str]
        metrics: Dict[str, float]
        user_input_summary: Optional[Dict[str, Any]] = None

class UXMirrorAPI:
    """Main API class for UX Mirror"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.capture = VulkanScreenshotCapture()
        self.input_tracker = UserInputTracker()
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.provider = "openai" if os.getenv("OPENAI_API_KEY") else "anthropic"
        
        if not self.api_key:
            logger.warning("No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        
        # Initialize FastAPI if available
        if API_AVAILABLE:
            self.app = FastAPI(
                title="UX Mirror API",
                description="Visual feedback for AI game developers",
                version="1.0.0"
            )
            self._setup_routes()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration"""
        default_config = {
            "capture": {
                "width": 1920,
                "height": 1080,
                "fps": 1
            },
            "analysis": {
                "provider": "openai",
                "model": "gpt-4-vision-preview",
                "max_issues": 10
            },
            "api": {
                "port": 8888,
                "host": "localhost"
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "name": "UX Mirror API",
                "status": "running",
                "endpoints": [
                    "/analyze",
                    "/capture",
                    "/feedback",
                    "/health"
                ]
            }
        
        @self.app.post("/analyze", response_model=FeedbackResponse)
        async def analyze_current_screen(request: ScreenshotRequest):
            """Analyze current game screen and return feedback"""
            try:
                # Capture screenshot
                frame = await self._capture_screenshot_async()
                if not frame:
                    raise HTTPException(status_code=500, detail="Failed to capture screenshot")
                
                # Get user input data if requested
                user_input_data = None
                if request.include_user_input:
                    user_input_data = self.input_tracker.get_recent_activity()
                
                # Analyze with AI
                feedback = await self._analyze_frame_async(
                    frame,
                    context=request.context,
                    specific_concern=request.specific_concern,
                    user_input=user_input_data
                )
                
                return FeedbackResponse(
                    timestamp=datetime.now().isoformat(),
                    summary=feedback['summary'],
                    issues=feedback['priority_fixes'],
                    recommendations=feedback.get('recommendations', []),
                    code_suggestions=feedback.get('code_suggestions', []),
                    metrics=feedback.get('metrics', {}),
                    user_input_summary=user_input_data
                )
                
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "capture_available": self.capture.shared_memory is not None,
                "api_key_configured": self.api_key is not None,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _capture_screenshot_async(self) -> Optional[VulkanFrame]:
        """Capture screenshot asynchronously"""
        return await asyncio.to_thread(self._capture_screenshot_sync)
    
    def _capture_screenshot_sync(self) -> Optional[VulkanFrame]:
        """Capture screenshot synchronously"""
        try:
            # Setup shared memory if not already done
            if not self.capture.shared_memory:
                width = self.config['capture']['width']
                height = self.config['capture']['height']
                if not self.capture.setup_shared_memory(width, height):
                    logger.error("Failed to setup shared memory")
                    return None
            
            # Capture frame
            return self.capture.capture_frame()
            
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return None
    
    async def _analyze_frame_async(self, frame: VulkanFrame, 
                                  context: Optional[str] = None,
                                  specific_concern: Optional[str] = None,
                                  user_input: Optional[Dict] = None) -> Dict:
        """Analyze frame with AI vision"""
        if not self.api_key:
            return {
                'summary': 'No API key configured',
                'priority_fixes': [],
                'code_suggestions': [],
                'metrics': {}
            }
        
        # Convert frame to PIL image
        image = frame.to_pil_image()
        
        # Build context
        full_context = context or ""
        if specific_concern:
            full_context += f"\nSpecific concern: {specific_concern}"
        if user_input:
            full_context += f"\nRecent user actions: {json.dumps(user_input, indent=2)}"
        
        # Analyze with AI
        async with AIVisionAnalyzer(self.api_key, self.provider) as analyzer:
            analysis = await analyzer.analyze_screenshot(image, full_context)
            
            # Process feedback
            processor = GameUIFeedbackProcessor()
            feedback = processor.process_analysis(analysis, user_input)
            
            # Add raw recommendations
            feedback['recommendations'] = analysis.recommendations
            
            return feedback
    
    def run_api_server(self):
        """Run the FastAPI server"""
        if not API_AVAILABLE:
            logger.error("FastAPI not installed. Install with: pip install fastapi uvicorn")
            return
        
        host = self.config['api']['host']
        port = self.config['api']['port']
        
        logger.info(f"Starting UX Mirror API server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)
    
    def cli_analyze(self, screenshot_path: Optional[str] = None, 
                   context: Optional[str] = None) -> Dict:
        """CLI method to analyze a screenshot or capture current screen"""
        
        if screenshot_path:
            # Analyze provided screenshot
            from PIL import Image
            image = Image.open(screenshot_path)
            frame = VulkanFrame(
                timestamp=datetime.now().timestamp(),
                width=image.width,
                height=image.height,
                data=np.array(image)
            )
        else:
            # Capture current screen
            logger.info("Capturing current game screen...")
            frame = self._capture_screenshot_sync()
            if not frame:
                logger.error("Failed to capture screenshot")
                return {'error': 'Screenshot capture failed'}
        
        # Analyze
        logger.info("Analyzing with AI vision...")
        result = asyncio.run(self._analyze_frame_async(frame, context))
        
        return result

# CLI Interface
def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="UX Mirror - Visual feedback for AI game developers"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze game screenshot')
    analyze_parser.add_argument('--screenshot', '-s', help='Path to screenshot file')
    analyze_parser.add_argument('--context', '-c', help='Additional context')
    analyze_parser.add_argument('--output', '-o', help='Output file (JSON)')
    
    # API server command
    api_parser = subparsers.add_parser('api', help='Run API server')
    api_parser.add_argument('--port', '-p', type=int, default=8888, help='API port')
    api_parser.add_argument('--host', default='localhost', help='API host')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor game continuously')
    monitor_parser.add_argument('--fps', type=int, default=1, help='Analysis frequency')
    monitor_parser.add_argument('--duration', type=int, help='Duration in seconds')
    
    args = parser.parse_args()
    
    # Create API instance
    api = UXMirrorAPI()
    
    if args.command == 'analyze':
        # Analyze mode
        result = api.cli_analyze(args.screenshot, args.context)
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Results saved to {args.output}")
        else:
            print("\n=== UX Mirror Analysis ===")
            print(result.get('summary', 'No summary available'))
            print("\nTop Issues:")
            for issue in result.get('priority_fixes', []):
                print(f"- {issue.get('description', 'Unknown issue')}")
            print("\nRecommendations:")
            for rec in result.get('recommendations', []):
                print(f"- {rec}")
    
    elif args.command == 'api':
        # API server mode
        if API_AVAILABLE:
            api.config['api']['port'] = args.port
            api.config['api']['host'] = args.host
            api.run_api_server()
        else:
            logger.error("API mode requires FastAPI. Install with: pip install fastapi uvicorn")
    
    elif args.command == 'monitor':
        # Monitor mode
        logger.info("Monitor mode not yet implemented")
        # TODO: Implement continuous monitoring
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 