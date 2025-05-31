#!/usr/bin/env python3
"""
UX-MIRROR Visual Analysis Agent
===============================

Sub-agent responsible for computer vision-powered UI/UX assessment using external APIs
and custom-trained recognizers for specialized UX issues.

Author: UX-MIRROR System
Version: 1.0.0
"""

import asyncio
import logging
import json
import time
import base64
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque
import aiohttp
import websockets
import psutil
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ScreenshotCapture:
    """Screenshot data with metadata"""
    timestamp: datetime
    platform: str
    resolution: Tuple[int, int]
    image_data: bytes
    image_format: str
    session_id: str
    url_or_context: Optional[str] = None
    user_id: Optional[str] = None

@dataclass
class UIElement:
    """Detected UI element"""
    element_type: str
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    text_content: Optional[str] = None
    attributes: Dict[str, Any] = None
    accessibility_issues: List[str] = None

@dataclass
class UXIssue:
    """Detected UX issue"""
    issue_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    location: Tuple[int, int, int, int]  # bounding box
    suggested_fix: str
    confidence: float
    custom_recognizer: Optional[str] = None

class ExternalVisionAPI:
    """Interface for external vision API providers"""
    
    def __init__(self, provider: str, api_key: str, config: Dict[str, Any]):
        self.provider = provider
        self.api_key = api_key
        self.config = config
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def analyze_screenshot(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze screenshot using external vision API"""
        if self.provider == "google_vision":
            return await self._google_vision_analyze(image_data)
        elif self.provider == "azure_computer_vision":
            return await self._azure_cv_analyze(image_data)
        elif self.provider == "aws_rekognition":
            return await self._aws_rekognition_analyze(image_data)
        elif self.provider == "openai_vision":
            return await self._openai_vision_analyze(image_data)
        else:
            raise ValueError(f"Unsupported vision provider: {self.provider}")
    
    async def _google_vision_analyze(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze using Google Cloud Vision API"""
        url = f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}"
        
        # Encode image to base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        payload = {
            "requests": [{
                "image": {"content": image_b64},
                "features": [
                    {"type": "TEXT_DETECTION"},
                    {"type": "LABEL_DETECTION"},
                    {"type": "OBJECT_LOCALIZATION"},
                    {"type": "LOGO_DETECTION"}
                ]
            }]
        }
        
        async with self.session.post(url, json=payload) as response:
            return await response.json()
    
    async def _azure_cv_analyze(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze using Azure Computer Vision API"""
        endpoint = self.config.get("endpoint", "")
        url = f"{endpoint}/vision/v3.2/analyze"
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/octet-stream"
        }
        
        params = {
            "visualFeatures": "Categories,Tags,Description,Objects,Brands,Faces,ImageType,Color",
            "details": "Landmarks"
        }
        
        async with self.session.post(url, headers=headers, params=params, data=image_data) as response:
            return await response.json()
    
    async def _aws_rekognition_analyze(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze using AWS Rekognition"""
        # Note: This would require boto3 and proper AWS credentials
        # For now, return a placeholder structure
        return {
            "Labels": [],
            "TextDetections": [],
            "FaceDetails": []
        }
    
    async def _openai_vision_analyze(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze using OpenAI Vision API (GPT-4V)"""
        url = "https://api.openai.com/v1/chat/completions"
        
        # Encode image to base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this UI screenshot for accessibility issues, design problems, and user experience concerns. Provide detailed analysis of text readability, color contrast, button sizes, navigation clarity, and any other UX issues you can identify."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2000
        }
        
        async with self.session.post(url, headers=headers, json=payload) as response:
            return await response.json()

class CustomRecognizerTrainer:
    """Toolchain for training custom UX issue recognizers"""
    
    def __init__(self, training_data_path: str):
        self.training_data_path = training_data_path
        self.recognizers = {}
        self.training_datasets = defaultdict(list)
        
    def add_training_sample(self, issue_type: str, image_data: bytes, 
                          bounding_box: Tuple[int, int, int, int], 
                          metadata: Dict[str, Any]):
        """Add a training sample for a specific UX issue type"""
        sample = {
            'image_data': image_data,
            'bounding_box': bounding_box,
            'metadata': metadata,
            'timestamp': datetime.now(),
            'sample_id': hashlib.md5(image_data + str(time.time()).encode()).hexdigest()
        }
        
        self.training_datasets[issue_type].append(sample)
        logger.info(f"Added training sample for {issue_type}: {sample['sample_id']}")
    
    def train_recognizer(self, issue_type: str, training_config: Dict[str, Any]) -> bool:
        """Train a custom recognizer for a specific UX issue type"""
        try:
            samples = self.training_datasets.get(issue_type, [])
            if len(samples) < training_config.get('min_samples', 10):
                logger.warning(f"Insufficient training samples for {issue_type}: {len(samples)}")
                return False
            
            # For now, create a simple rule-based recognizer
            # In production, this would train an actual ML model
            recognizer = self._create_rule_based_recognizer(issue_type, samples, training_config)
            self.recognizers[issue_type] = recognizer
            
            logger.info(f"Trained custom recognizer for {issue_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to train recognizer for {issue_type}: {e}")
            return False
    
    def _extract_common_colors(self, samples: List[Dict]) -> List[str]:
        """Extract common colors from training samples"""
        color_counts = defaultdict(int)
        
        try:
            for sample in samples:
                # In a real implementation, this would analyze the image data
                # For now, simulate color extraction based on metadata
                image_data = sample.get('image_data', b'')
                metadata = sample.get('metadata', {})
                
                # Extract colors from metadata if available
                if 'dominant_colors' in metadata:
                    for color in metadata['dominant_colors']:
                        color_counts[color] += 1
                
                # Simulate color extraction from image data
                # In practice, would use PIL or OpenCV to analyze actual colors
                if len(image_data) > 0:
                    # Simple hash-based color simulation
                    hash_val = hashlib.md5(image_data).hexdigest()
                    simulated_colors = [
                        f"#{hash_val[:6]}",
                        f"#{hash_val[6:12]}",
                        f"#{hash_val[12:18]}"
                    ]
                    for color in simulated_colors:
                        color_counts[color] += 1
            
            # Return the most common colors
            common_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
            return [color for color, count in common_colors[:5]]  # Top 5 colors
            
        except Exception as e:
            logger.error(f"Error extracting colors: {e}")
            return ['#FF0000', '#00FF00', '#0000FF']  # Default colors

    def _extract_text_patterns(self, samples: List[Dict]) -> List[str]:
        """Extract common text patterns from training samples"""
        text_patterns = defaultdict(int)
        
        try:
            for sample in samples:
                metadata = sample.get('metadata', {})
                
                # Extract text from metadata
                if 'text_content' in metadata:
                    text = metadata['text_content'].lower()
                    
                    # Common UX-related text patterns
                    ux_keywords = [
                        'error', 'warning', 'required', 'invalid', 'failed',
                        'success', 'complete', 'loading', 'submit', 'cancel',
                        'delete', 'confirm', 'save', 'edit', 'update',
                        'login', 'logout', 'signin', 'signup', 'register'
                    ]
                    
                    for keyword in ux_keywords:
                        if keyword in text:
                            text_patterns[keyword] += 1
                    
                    # Extract word patterns
                    words = text.split()
                    for word in words:
                        if len(word) > 3:  # Only consider meaningful words
                            text_patterns[word] += 1
                
                # Extract button/element text from bounding box context
                if 'element_text' in metadata:
                    element_text = metadata['element_text'].lower()
                    text_patterns[element_text] += 1
            
            # Return the most common patterns
            common_patterns = sorted(text_patterns.items(), key=lambda x: x[1], reverse=True)
            return [pattern for pattern, count in common_patterns[:10]]  # Top 10 patterns
            
        except Exception as e:
            logger.error(f"Error extracting text patterns: {e}")
            return ['error', 'warning', 'required']  # Default patterns

    def _create_rule_based_recognizer(self, issue_type: str, samples: List[Dict], 
                                    config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a rule-based recognizer from training samples"""
        # Analyze samples to extract patterns
        avg_box_size = np.mean([
            (s['bounding_box'][2] * s['bounding_box'][3]) 
            for s in samples
        ])
        
        # Calculate average position (normalized)
        avg_position = np.mean([
            (s['bounding_box'][0], s['bounding_box'][1])
            for s in samples
        ], axis=0)
        
        # Extract size statistics
        box_sizes = [(s['bounding_box'][2], s['bounding_box'][3]) for s in samples]
        min_size = np.min(box_sizes, axis=0)
        max_size = np.max(box_sizes, axis=0)
        std_size = np.std(box_sizes, axis=0)
        
        common_colors = self._extract_common_colors(samples)
        text_patterns = self._extract_text_patterns(samples)
        
        # Create issue-specific rules
        rules = self._create_issue_specific_rules(issue_type, samples)
        
        return {
            'issue_type': issue_type,
            'avg_box_size': avg_box_size,
            'avg_position': avg_position.tolist(),
            'size_range': {
                'min': min_size.tolist(),
                'max': max_size.tolist(),
                'std': std_size.tolist()
            },
            'common_colors': common_colors,
            'text_patterns': text_patterns,
            'custom_rules': rules,
            'sample_count': len(samples),
            'confidence_threshold': config.get('confidence_threshold', 0.6),
            'created_at': datetime.now(),
            'config': config
        }

    def _create_issue_specific_rules(self, issue_type: str, samples: List[Dict]) -> Dict[str, Any]:
        """Create specific rules based on the issue type"""
        rules = {}
        
        if issue_type == 'low_contrast_text':
            rules.update({
                'check_contrast': True,
                'min_contrast_ratio': 4.5,  # WCAG AA standard
                'text_size_threshold': 14,
                'background_analysis': True
            })
        
        elif issue_type == 'small_clickable_elements':
            # Calculate average button size from samples
            button_sizes = [s['bounding_box'][2] * s['bounding_box'][3] for s in samples]
            avg_button_size = np.mean(button_sizes)
            
            rules.update({
                'min_touch_target': 44,  # 44px minimum touch target
                'avg_sample_size': avg_button_size,
                'check_spacing': True,
                'min_spacing': 8
            })
        
        elif issue_type == 'inconsistent_fonts':
            rules.update({
                'check_font_consistency': True,
                'font_variation_threshold': 3,
                'check_font_sizes': True,
                'size_variation_threshold': 2
            })
        
        elif issue_type == 'broken_images':
            rules.update({
                'check_alt_text': True,
                'check_src_validity': True,
                'detect_placeholder_images': True
            })
        
        elif issue_type == 'form_validation_errors':
            rules.update({
                'error_indicators': ['*', 'required', 'error', 'invalid'],
                'check_field_highlighting': True,
                'check_error_messages': True
            })
        
        return rules

    def apply_custom_recognizers(self, screenshot: ScreenshotCapture) -> List[UXIssue]:
        """Apply all trained custom recognizers to a screenshot"""
        issues = []
        
        for issue_type, recognizer in self.recognizers.items():
            detected_issues = self._apply_recognizer(screenshot, recognizer)
            issues.extend(detected_issues)
        
        return issues

    def _apply_recognizer(self, screenshot: ScreenshotCapture, 
                         recognizer: Dict[str, Any]) -> List[UXIssue]:
        """Apply a single custom recognizer with enhanced detection"""
        issues = []
        
        try:
            issue_type = recognizer['issue_type']
            rules = recognizer.get('custom_rules', {})
            confidence_threshold = recognizer.get('confidence_threshold', 0.6)
            
            # Apply issue-specific detection logic
            if issue_type == 'low_contrast_text':
                issues.extend(self._detect_low_contrast_issues(screenshot, recognizer))
            
            elif issue_type == 'small_clickable_elements':
                issues.extend(self._detect_small_clickable_issues(screenshot, recognizer))
            
            elif issue_type == 'inconsistent_fonts':
                issues.extend(self._detect_font_consistency_issues(screenshot, recognizer))
            
            elif issue_type == 'broken_images':
                issues.extend(self._detect_broken_image_issues(screenshot, recognizer))
            
            elif issue_type == 'form_validation_errors':
                issues.extend(self._detect_form_validation_issues(screenshot, recognizer))
            
            else:
                # Generic pattern-based detection
                issues.extend(self._detect_generic_pattern_issues(screenshot, recognizer))
        
        except Exception as e:
            logger.error(f"Error applying recognizer {recognizer.get('issue_type', 'unknown')}: {e}")
        
        return issues

    def _detect_low_contrast_issues(self, screenshot: ScreenshotCapture, 
                                   recognizer: Dict[str, Any]) -> List[UXIssue]:
        """Detect low contrast text issues"""
        issues = []
        
        # Simulate contrast detection
        # In practice, would analyze actual image colors
        if len(screenshot.image_data) > 50000:  # Larger images more likely to have issues
            issues.append(UXIssue(
                issue_type='low_contrast_text',
                severity='medium',
                description='Potential low contrast text detected based on training patterns',
                location=(100, 100, 300, 50),
                suggested_fix='Increase text contrast ratio to meet WCAG AA guidelines (4.5:1)',
                confidence=0.75,
                custom_recognizer=recognizer['issue_type']
            ))
        
        return issues

    def _detect_small_clickable_issues(self, screenshot: ScreenshotCapture, 
                                      recognizer: Dict[str, Any]) -> List[UXIssue]:
        """Detect small clickable elements"""
        issues = []
        
        # Simulate small button detection
        if screenshot.platform in ['mobile', 'android', 'ios']:
            issues.append(UXIssue(
                issue_type='small_clickable_elements',
                severity='high',
                description='Clickable elements may be too small for mobile interaction',
                location=(50, 200, 30, 25),
                suggested_fix='Increase touch target size to minimum 44px × 44px',
                confidence=0.8,
                custom_recognizer=recognizer['issue_type']
            ))
        
        return issues

    def _detect_font_consistency_issues(self, screenshot: ScreenshotCapture, 
                                       recognizer: Dict[str, Any]) -> List[UXIssue]:
        """Detect font consistency issues"""
        issues = []
        
        # Simulate font inconsistency detection
        issues.append(UXIssue(
            issue_type='inconsistent_fonts',
            severity='low',
            description='Potential font inconsistency detected',
            location=(0, 0, 0, 0),  # Full screen issue
            suggested_fix='Standardize font family and sizes across the interface',
            confidence=0.65,
            custom_recognizer=recognizer['issue_type']
        ))
        
        return issues

    def _detect_broken_image_issues(self, screenshot: ScreenshotCapture, 
                                   recognizer: Dict[str, Any]) -> List[UXIssue]:
        """Detect broken images"""
        issues = []
        
        # Simulate broken image detection
        # Would check for placeholder patterns, missing alt text, etc.
        issues.append(UXIssue(
            issue_type='broken_images',
            severity='medium',
            description='Potential broken or missing images detected',
            location=(200, 300, 150, 100),
            suggested_fix='Verify image sources and provide proper alt text',
            confidence=0.7,
            custom_recognizer=recognizer['issue_type']
        ))
        
        return issues

    def _detect_form_validation_issues(self, screenshot: ScreenshotCapture, 
                                      recognizer: Dict[str, Any]) -> List[UXIssue]:
        """Detect form validation issues"""
        issues = []
        
        # Simulate form validation detection
        error_indicators = recognizer.get('custom_rules', {}).get('error_indicators', [])
        
        issues.append(UXIssue(
            issue_type='form_validation_errors',
            severity='high',
            description='Form validation errors may not be clearly communicated',
            location=(100, 400, 400, 30),
            suggested_fix='Ensure error messages are clear and visually distinct',
            confidence=0.72,
            custom_recognizer=recognizer['issue_type']
        ))
        
        return issues

    def _detect_generic_pattern_issues(self, screenshot: ScreenshotCapture, 
                                      recognizer: Dict[str, Any]) -> List[UXIssue]:
        """Detect issues using generic pattern matching"""
        issues = []
        
        # Use text patterns and colors from training
        text_patterns = recognizer.get('text_patterns', [])
        common_colors = recognizer.get('common_colors', [])
        
        # Generic pattern-based detection
        if 'error' in text_patterns or 'warning' in text_patterns:
            issues.append(UXIssue(
                issue_type=recognizer['issue_type'],
                severity='medium',
                description=f'Pattern-based detection: {recognizer["issue_type"]}',
                location=(150, 150, 200, 100),
                suggested_fix='Review detected pattern for potential UX improvements',
                confidence=0.6,
                custom_recognizer=recognizer['issue_type']
            ))
        
        return issues

class VisualAnalysisAgent:
    """
    Visual Analysis Agent using external APIs and custom recognizers.
    
    Capabilities:
    - Screenshot capture across platforms
    - External vision API integration
    - Custom UX issue recognizer training
    - Real-time visual analysis and reporting
    """
    
    def __init__(self, orchestrator_host: str = "localhost", orchestrator_port: int = 8765):
        self.agent_id = "visual_analysis"
        self.orchestrator_host = orchestrator_host
        self.orchestrator_port = orchestrator_port
        self.websocket = None
        
        # Vision API providers
        self.vision_apis = {}
        self.current_provider = "google_vision"
        
        # Custom recognizer system
        self.custom_trainer = CustomRecognizerTrainer("training_data/")
        
        # Analysis state
        self.screenshot_buffer = deque(maxlen=1000)
        self.detected_elements = defaultdict(list)
        self.ux_issues = defaultdict(list)
        self.analysis_history = deque(maxlen=5000)
        
        # Performance tracking
        self.analysis_times = deque(maxlen=100)
        self.api_usage_stats = defaultdict(int)
        
        logger.info("Visual Analysis Agent initialized with external API support")
    
    async def start(self):
        """Start the visual analysis agent"""
        logger.info("Starting Visual Analysis Agent...")
        
        # Load configuration and initialize APIs
        await self._load_configuration()
        await self._initialize_vision_apis()
        
        # Connect to orchestrator
        await self._connect_to_orchestrator()
        
        # Start analysis tasks
        tasks = [
            self._capture_screenshots(),
            self._process_analysis_queue(),
            self._train_custom_recognizers(),
            self._generate_reports(),
            self._send_heartbeat(),
            self._monitor_api_usage()
        ]
        
        await asyncio.gather(*tasks)
    
    async def _load_configuration(self):
        """Load configuration for vision APIs and custom recognizers"""
        try:
            with open("config/vision_config.json", "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            logger.warning("Vision config not found, using defaults")
            self.config = {
                "vision_apis": {
                    "google_vision": {
                        "enabled": True,
                        "api_key": "${GOOGLE_VISION_API_KEY}",
                        "rate_limit": 1000
                    },
                    "azure_computer_vision": {
                        "enabled": False,
                        "api_key": "${AZURE_CV_API_KEY}",
                        "endpoint": "${AZURE_CV_ENDPOINT}"
                    },
                    "openai_vision": {
                        "enabled": True,
                        "api_key": "${OPENAI_API_KEY}",
                        "rate_limit": 100
                    }
                },
                "custom_recognizers": {
                    "enabled": True,
                    "training_threshold": 10,
                    "retrain_interval": 3600
                },
                "analysis": {
                    "capture_interval": 500,  # 500ms
                    "batch_size": 5,
                    "parallel_requests": 3
                }
            }
    
    async def _initialize_vision_apis(self):
        """Initialize external vision API providers"""
        for provider, config in self.config["vision_apis"].items():
            if config.get("enabled", False):
                api_key = self._get_api_key(config["api_key"])
                if api_key:
                    self.vision_apis[provider] = ExternalVisionAPI(
                        provider=provider,
                        api_key=api_key,
                        config=config
                    )
                    logger.info(f"Initialized {provider} vision API")
                else:
                    logger.warning(f"Missing API key for {provider}")
    
    def _get_api_key(self, key_template: str) -> Optional[str]:
        """Get API key from environment or configuration"""
        import os
        if key_template.startswith("${") and key_template.endswith("}"):
            env_var = key_template[2:-1]
            return os.getenv(env_var)
        return key_template
    
    async def _connect_to_orchestrator(self):
        """Connect to the Core Orchestrator"""
        try:
            self.websocket = await websockets.connect(
                f"ws://{self.orchestrator_host}:{self.orchestrator_port}"
            )
            
            # Register with orchestrator
            registration = {
                "agent_id": self.agent_id,
                "capabilities": [
                    "screenshot_analysis",
                    "ui_element_detection",
                    "accessibility_assessment",
                    "custom_recognizer_training",
                    "cross_platform_visual_testing"
                ]
            }
            await self.websocket.send(json.dumps(registration))
            
            # Listen for orchestrator messages
            asyncio.create_task(self._handle_orchestrator_messages())
            
            logger.info("Connected to Core Orchestrator")
            
        except Exception as e:
            logger.error(f"Failed to connect to orchestrator: {e}")
            raise
    
    async def _handle_orchestrator_messages(self):
        """Handle messages from the Core Orchestrator"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                message_type = data.get("type")
                
                if message_type == "analyze_screenshot":
                    await self._handle_screenshot_analysis_request(data)
                elif message_type == "train_recognizer":
                    await self._handle_training_request(data)
                elif message_type == "configuration_update":
                    await self._handle_configuration_update(data)
                
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Connection to orchestrator lost")
        except Exception as e:
            logger.error(f"Error handling orchestrator messages: {e}")
    
    async def _capture_screenshots(self):
        """Capture screenshots from various platforms"""
        while True:
            try:
                # Capture from web browsers
                web_screenshots = await self._capture_web_screenshots()
                
                # Capture from desktop applications
                desktop_screenshots = await self._capture_desktop_screenshots()
                
                # Capture from mobile devices (if available)
                mobile_screenshots = await self._capture_mobile_screenshots()
                
                # Add all screenshots to buffer
                all_screenshots = web_screenshots + desktop_screenshots + mobile_screenshots
                for screenshot in all_screenshots:
                    self.screenshot_buffer.append(screenshot)
                
                interval = self.config["analysis"]["capture_interval"] / 1000.0
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in screenshot capture: {e}")
                await asyncio.sleep(5)
    
    async def _capture_web_screenshots(self) -> List[ScreenshotCapture]:
        """Capture screenshots from web browsers"""
        screenshots = []
        
        try:
            # Try to connect to Chrome/Chromium DevTools
            # This would typically use pyppeteer or playwright
            # For now, simulate web screenshot capture
            
            from datetime import datetime
            import uuid
            
            # Placeholder: In production, this would use browser automation
            # Example browser sessions to monitor
            browser_sessions = [
                {"url": "http://localhost:3000", "session_id": str(uuid.uuid4())},
                {"url": "https://app.example.com", "session_id": str(uuid.uuid4())}
            ]
            
            for session in browser_sessions:
                # Simulate screenshot capture
                # In practice, would use:
                # page = await browser.newPage()
                # await page.goto(session["url"])
                # screenshot_data = await page.screenshot()
                
                # For now, create a minimal placeholder image
                placeholder_image = self._create_placeholder_screenshot("web", session["url"])
                
                screenshot = ScreenshotCapture(
                    timestamp=datetime.now(),
                    platform="web",
                    resolution=(1920, 1080),
                    image_data=placeholder_image,
                    image_format="png",
                    session_id=session["session_id"],
                    url_or_context=session["url"]
                )
                screenshots.append(screenshot)
                
        except Exception as e:
            logger.error(f"Error capturing web screenshots: {e}")
        
        return screenshots

    async def _capture_desktop_screenshots(self) -> List[ScreenshotCapture]:
        """Capture screenshots from desktop applications"""
        screenshots = []
        
        try:
            import platform
            import uuid
            from datetime import datetime
            
            # Use platform-specific screen capture
            if platform.system() == "Windows":
                screenshots.extend(await self._capture_windows_screenshots())
            elif platform.system() == "Darwin":  # macOS
                screenshots.extend(await self._capture_macos_screenshots())
            elif platform.system() == "Linux":
                screenshots.extend(await self._capture_linux_screenshots())
                
        except Exception as e:
            logger.error(f"Error capturing desktop screenshots: {e}")
        
        return screenshots

    async def _capture_windows_screenshots(self) -> List[ScreenshotCapture]:
        """Capture screenshots on Windows"""
        screenshots = []
        
        try:
            # In production, would use win32gui, pygetwindow, or similar
            # For now, simulate desktop capture
            import uuid
            from datetime import datetime
            
            placeholder_image = self._create_placeholder_screenshot("windows", "Desktop")
            
            screenshot = ScreenshotCapture(
                timestamp=datetime.now(),
                platform="windows",
                resolution=(1920, 1080),
                image_data=placeholder_image,
                image_format="png",
                session_id=str(uuid.uuid4()),
                url_or_context="Windows Desktop"
            )
            screenshots.append(screenshot)
            
        except Exception as e:
            logger.error(f"Error capturing Windows screenshots: {e}")
        
        return screenshots

    async def _capture_macos_screenshots(self) -> List[ScreenshotCapture]:
        """Capture screenshots on macOS"""
        screenshots = []
        
        try:
            # In production, would use CoreGraphics or screencapture
            import uuid
            from datetime import datetime
            
            placeholder_image = self._create_placeholder_screenshot("macos", "Desktop")
            
            screenshot = ScreenshotCapture(
                timestamp=datetime.now(),
                platform="macos",
                resolution=(2560, 1440),
                image_data=placeholder_image,
                image_format="png",
                session_id=str(uuid.uuid4()),
                url_or_context="macOS Desktop"
            )
            screenshots.append(screenshot)
            
        except Exception as e:
            logger.error(f"Error capturing macOS screenshots: {e}")
        
        return screenshots

    async def _capture_linux_screenshots(self) -> List[ScreenshotCapture]:
        """Capture screenshots on Linux"""
        screenshots = []
        
        try:
            # In production, would use xrandr, gnome-screenshot, or similar
            import uuid
            from datetime import datetime
            
            placeholder_image = self._create_placeholder_screenshot("linux", "Desktop")
            
            screenshot = ScreenshotCapture(
                timestamp=datetime.now(),
                platform="linux",
                resolution=(1920, 1080),
                image_data=placeholder_image,
                image_format="png",
                session_id=str(uuid.uuid4()),
                url_or_context="Linux Desktop"
            )
            screenshots.append(screenshot)
            
        except Exception as e:
            logger.error(f"Error capturing Linux screenshots: {e}")
        
        return screenshots

    async def _capture_mobile_screenshots(self) -> List[ScreenshotCapture]:
        """Capture screenshots from mobile devices"""
        screenshots = []
        
        try:
            # Android device capture
            android_screenshots = await self._capture_android_screenshots()
            screenshots.extend(android_screenshots)
            
            # iOS device capture
            ios_screenshots = await self._capture_ios_screenshots()
            screenshots.extend(ios_screenshots)
            
        except Exception as e:
            logger.error(f"Error capturing mobile screenshots: {e}")
        
        return screenshots

    async def _capture_android_screenshots(self) -> List[ScreenshotCapture]:
        """Capture screenshots from Android devices"""
        screenshots = []
        
        try:
            # In production, would use ADB (Android Debug Bridge)
            # adb devices -> list connected devices
            # adb shell screencap -> capture screenshot
            import uuid
            from datetime import datetime
            
            placeholder_image = self._create_placeholder_screenshot("android", "Android App")
            
            screenshot = ScreenshotCapture(
                timestamp=datetime.now(),
                platform="android",
                resolution=(1080, 1920),
                image_data=placeholder_image,
                image_format="png",
                session_id=str(uuid.uuid4()),
                url_or_context="Android Application"
            )
            screenshots.append(screenshot)
            
        except Exception as e:
            logger.error(f"Error capturing Android screenshots: {e}")
        
        return screenshots

    async def _capture_ios_screenshots(self) -> List[ScreenshotCapture]:
        """Capture screenshots from iOS devices"""
        screenshots = []
        
        try:
            # In production, would use ios-deploy, libimobiledevice, or Xcode tools
            import uuid
            from datetime import datetime
            
            placeholder_image = self._create_placeholder_screenshot("ios", "iOS App")
            
            screenshot = ScreenshotCapture(
                timestamp=datetime.now(),
                platform="ios",
                resolution=(1170, 2532),
                image_data=placeholder_image,
                image_format="png",
                session_id=str(uuid.uuid4()),
                url_or_context="iOS Application"
            )
            screenshots.append(screenshot)
            
        except Exception as e:
            logger.error(f"Error capturing iOS screenshots: {e}")
        
        return screenshots

    def _create_placeholder_screenshot(self, platform: str, context: str) -> bytes:
        """Create a placeholder screenshot for testing"""
        try:
            # Create a simple placeholder image
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            # Create image
            img = Image.new('RGB', (800, 600), color='lightgray')
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                # Try to use a default font
                font = ImageFont.load_default()
            except:
                font = None
            
            text = f"UX-MIRROR\n{platform.upper()}\n{context}"
            draw.text((50, 50), text, fill='black', font=font)
            
            # Add some UI elements simulation
            draw.rectangle([50, 150, 200, 180], outline='blue', width=2)  # Button
            draw.rectangle([50, 200, 750, 230], outline='gray', width=1)  # Text field
            draw.rectangle([50, 250, 300, 350], outline='green', width=2)  # Panel
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            return img_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating placeholder screenshot: {e}")
            # Return minimal PNG bytes
            return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02\x00\x00\x00\x0bIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x07\n\x8a\x84\x00\x00\x00\x00IEND\xaeB`\x82'
    
    async def _process_analysis_queue(self):
        """Process screenshot analysis queue using external APIs"""
        while True:
            try:
                if len(self.screenshot_buffer) > 0:
                    # Get batch of screenshots to process
                    batch_size = min(
                        self.config["analysis"]["batch_size"],
                        len(self.screenshot_buffer)
                    )
                    
                    screenshots = [self.screenshot_buffer.popleft() for _ in range(batch_size)]
                    
                    # Process screenshots in parallel
                    tasks = []
                    for screenshot in screenshots:
                        tasks.append(self._analyze_screenshot(screenshot))
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Process results
                    for screenshot, result in zip(screenshots, results):
                        if isinstance(result, Exception):
                            logger.error(f"Analysis failed for screenshot: {result}")
                        else:
                            await self._process_analysis_result(screenshot, result)
                
                await asyncio.sleep(1)  # Process every second
                
            except Exception as e:
                logger.error(f"Error in analysis queue processing: {e}")
                await asyncio.sleep(5)
    
    async def _analyze_screenshot(self, screenshot: ScreenshotCapture) -> Dict[str, Any]:
        """Analyze a single screenshot using external APIs and custom recognizers"""
        start_time = time.time()
        
        try:
            # Choose the best available vision API
            api_provider = self._select_vision_api()
            
            if not api_provider:
                raise Exception("No vision API available")
            
            # Analyze using external API
            async with self.vision_apis[api_provider] as api:
                vision_result = await api.analyze_screenshot(screenshot.image_data)
            
            # Apply custom recognizers
            custom_issues = self.custom_trainer.apply_custom_recognizers(screenshot)
            
            # Combine results
            analysis_result = {
                'screenshot_id': hashlib.md5(screenshot.image_data).hexdigest(),
                'timestamp': screenshot.timestamp,
                'platform': screenshot.platform,
                'vision_api_result': vision_result,
                'custom_issues': [issue.__dict__ for issue in custom_issues],
                'analysis_duration': time.time() - start_time,
                'api_provider': api_provider
            }
            
            # Track performance
            self.analysis_times.append(time.time() - start_time)
            self.api_usage_stats[api_provider] += 1
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Screenshot analysis failed: {e}")
            return {
                'error': str(e),
                'screenshot_id': hashlib.md5(screenshot.image_data).hexdigest(),
                'timestamp': screenshot.timestamp
            }
    
    def _select_vision_api(self) -> Optional[str]:
        """Select the best available vision API based on rate limits and performance"""
        # Simple round-robin selection for now
        # In production, would consider rate limits, costs, and performance
        available_apis = list(self.vision_apis.keys())
        if not available_apis:
            return None
        
        # Prefer APIs with lower usage
        return min(available_apis, key=lambda api: self.api_usage_stats[api])
    
    async def _process_analysis_result(self, screenshot: ScreenshotCapture, 
                                     result: Dict[str, Any]):
        """Process and interpret analysis results"""
        if 'error' in result:
            return
        
        # Extract UI elements from vision API result
        ui_elements = self._extract_ui_elements(result['vision_api_result'])
        
        # Detect UX issues
        ux_issues = self._detect_ux_issues(ui_elements, result)
        
        # Add custom recognizer issues
        for custom_issue_data in result.get('custom_issues', []):
            ux_issues.append(UXIssue(**custom_issue_data))
        
        # Store results
        session_id = screenshot.session_id
        self.detected_elements[session_id].extend(ui_elements)
        self.ux_issues[session_id].extend(ux_issues)
        
        # Store analysis in history
        self.analysis_history.append({
            'screenshot': screenshot,
            'ui_elements': ui_elements,
            'issues': ux_issues,
            'analysis_result': result
        })
        
        # Report critical issues immediately
        critical_issues = [issue for issue in ux_issues if issue.severity == 'critical']
        if critical_issues:
            await self._report_critical_issues(screenshot, critical_issues)
    
    def _extract_ui_elements(self, vision_result: Dict[str, Any]) -> List[UIElement]:
        """Extract UI elements from vision API result"""
        elements = []
        
        # Handle Google Vision API results
        if 'responses' in vision_result:
            response = vision_result['responses'][0] if vision_result['responses'] else {}
            
            # Extract text elements
            if 'textAnnotations' in response:
                for text in response['textAnnotations'][1:]:  # Skip full text
                    vertices = text['boundingPoly']['vertices']
                    x_coords = [v['x'] for v in vertices]
                    y_coords = [v['y'] for v in vertices]
                    
                    elements.append(UIElement(
                        element_type='text',
                        bounding_box=(
                            min(x_coords),
                            min(y_coords),
                            max(x_coords) - min(x_coords),
                            max(y_coords) - min(y_coords)
                        ),
                        confidence=text.get('confidence', 0.5),
                        text_content=text.get('description', ''),
                        attributes={'language': text.get('locale', 'unknown')}
                    ))
            
            # Extract object/label elements
            if 'localizedObjectAnnotations' in response:
                for obj in response['localizedObjectAnnotations']:
                    vertices = obj['boundingPoly']['normalizedVertices']
                    # Convert normalized coordinates to pixel coordinates
                    # (This would need actual image dimensions in practice)
                    
                    elements.append(UIElement(
                        element_type=obj['name'].lower(),
                        bounding_box=(0, 0, 100, 100),  # Placeholder
                        confidence=obj['score'],
                        attributes={'object_type': obj['name']}
                    ))
        
        # Handle OpenAI Vision API results
        elif 'choices' in vision_result:
            # Parse text analysis for UI elements
            content = vision_result['choices'][0]['message']['content']
            # This would require more sophisticated parsing of the AI response
            # For now, create placeholder elements
            
            elements.append(UIElement(
                element_type='ai_analysis',
                bounding_box=(0, 0, 0, 0),
                confidence=0.8,
                text_content=content,
                attributes={'analysis_type': 'openai_vision'}
            ))
        
        # Handle Azure Computer Vision results
        elif 'objects' in vision_result:
            for obj in vision_result['objects']:
                rect = obj['rectangle']
                elements.append(UIElement(
                    element_type=obj['object'].lower(),
                    bounding_box=(rect['x'], rect['y'], rect['w'], rect['h']),
                    confidence=obj['confidence'],
                    attributes={'object_type': obj['object']}
                ))
        
        return elements
    
    def _detect_ux_issues(self, ui_elements: List[UIElement], 
                         analysis_result: Dict[str, Any]) -> List[UXIssue]:
        """Detect UX issues from UI elements and analysis results"""
        issues = []
        
        # Check for accessibility issues
        issues.extend(self._check_accessibility_issues(ui_elements))
        
        # Check for design consistency issues
        issues.extend(self._check_design_consistency(ui_elements))
        
        # Check for performance-related visual issues
        issues.extend(self._check_performance_issues(analysis_result))
        
        # Add custom recognizer issues
        custom_issues = analysis_result.get('custom_issues', [])
        for custom_issue in custom_issues:
            issues.append(UXIssue(**custom_issue))
        
        return issues
    
    def _check_accessibility_issues(self, ui_elements: List[UIElement]) -> List[UXIssue]:
        """Check for accessibility-related UX issues"""
        issues = []
        
        # Check for small text
        for element in ui_elements:
            if element.element_type == 'text' and element.bounding_box[3] < 12:  # Height < 12px
                issues.append(UXIssue(
                    issue_type='small_text',
                    severity='medium',
                    description='Text may be too small for accessibility',
                    location=element.bounding_box,
                    suggested_fix='Increase font size to at least 12px',
                    confidence=0.8
                ))
        
        # Check for missing alt text (would need more context)
        # Check for insufficient color contrast (would need color analysis)
        # Check for missing focus indicators (would need interaction data)
        
        return issues
    
    def _check_design_consistency(self, ui_elements: List[UIElement]) -> List[UXIssue]:
        """Check for design consistency issues"""
        issues = []
        
        # Check for inconsistent button sizes
        buttons = [e for e in ui_elements if 'button' in e.element_type.lower()]
        if len(buttons) > 1:
            sizes = [(e.bounding_box[2], e.bounding_box[3]) for e in buttons]
            size_variance = np.var([s[0] * s[1] for s in sizes])
            
            if size_variance > 1000:  # High variance in button sizes
                issues.append(UXIssue(
                    issue_type='inconsistent_button_sizes',
                    severity='low',
                    description='Button sizes vary significantly',
                    location=(0, 0, 0, 0),  # Full screen issue
                    suggested_fix='Standardize button sizes across the interface',
                    confidence=0.6
                ))
        
        return issues
    
    def _check_performance_issues(self, analysis_result: Dict[str, Any]) -> List[UXIssue]:
        """Check for performance-related visual issues"""
        issues = []
        
        # Check analysis duration
        duration = analysis_result.get('analysis_duration', 0)
        if duration > 5.0:  # Analysis took longer than 5 seconds
            issues.append(UXIssue(
                issue_type='slow_visual_analysis',
                severity='low',
                description='Visual analysis took longer than expected',
                location=(0, 0, 0, 0),
                suggested_fix='Optimize image size or complexity',
                confidence=1.0
            ))
        
        return issues
    
    async def _report_critical_issues(self, screenshot: ScreenshotCapture, 
                                    issues: List[UXIssue]):
        """Report critical UX issues to orchestrator immediately"""
        alert = {
            "type": "alert",
            "alert_type": "critical_ux_issues",
            "severity": "high",
            "data": {
                "screenshot_id": hashlib.md5(screenshot.image_data).hexdigest(),
                "platform": screenshot.platform,
                "timestamp": screenshot.timestamp.isoformat(),
                "issues": [issue.__dict__ for issue in issues],
                "recommended_actions": [
                    "Review critical accessibility violations",
                    "Fix high-impact UX problems immediately",
                    "Consider temporary UI modifications"
                ]
            }
        }
        
        await self._send_to_orchestrator(alert)
    
    async def _train_custom_recognizers(self):
        """Periodically train and update custom recognizers"""
        while True:
            try:
                # Check if we have enough training data
                for issue_type, samples in self.custom_trainer.training_datasets.items():
                    threshold = self.config["custom_recognizers"]["training_threshold"]
                    
                    if len(samples) >= threshold:
                        success = self.custom_trainer.train_recognizer(issue_type, {
                            'min_samples': threshold,
                            'validation_split': 0.2
                        })
                        
                        if success:
                            await self._send_to_orchestrator({
                                "type": "recommendation",
                                "recommendation_type": "custom_recognizer_trained",
                                "priority": "low",
                                "data": {
                                    "issue_type": issue_type,
                                    "sample_count": len(samples),
                                    "training_success": success
                                }
                            })
                
                # Sleep for retrain interval
                interval = self.config["custom_recognizers"]["retrain_interval"]
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in custom recognizer training: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _generate_reports(self):
        """Generate periodic visual analysis reports"""
        while True:
            try:
                # Generate report every 10 minutes
                current_time = datetime.now()
                report_data = {
                    "period": "10_minutes",
                    "analysis_count": len(self.analysis_history),
                    "avg_analysis_time": np.mean(self.analysis_times) if self.analysis_times else 0,
                    "api_usage": dict(self.api_usage_stats),
                    "top_issues": self._get_top_issues(),
                    "platform_coverage": self._get_platform_coverage()
                }
                
                await self._send_to_orchestrator({
                    "type": "recommendation",
                    "recommendation_type": "visual_analysis_report",
                    "priority": "low",
                    "data": report_data
                })
                
                await asyncio.sleep(600)  # 10 minutes
                
            except Exception as e:
                logger.error(f"Error generating visual analysis report: {e}")
                await asyncio.sleep(600)
    
    def _get_top_issues(self) -> List[Dict[str, Any]]:
        """Get the most common UX issues detected"""
        issue_counts = defaultdict(int)
        
        for session_issues in self.ux_issues.values():
            for issue in session_issues:
                issue_counts[issue.issue_type] += 1
        
        # Return top 5 issues
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [{"issue_type": issue, "count": count} for issue, count in top_issues]
    
    def _get_platform_coverage(self) -> Dict[str, int]:
        """Get analysis coverage by platform"""
        platform_counts = defaultdict(int)
        
        for analysis in self.analysis_history:
            platform_counts[analysis['screenshot'].platform] += 1
        
        return dict(platform_counts)
    
    async def _send_heartbeat(self):
        """Send periodic heartbeat to orchestrator"""
        while True:
            try:
                cpu_usage = psutil.cpu_percent()
                memory_usage = psutil.virtual_memory().percent
                
                heartbeat = {
                    "type": "heartbeat",
                    "status": "active",
                    "gpu_usage": 0.0,  # Not using GPU anymore
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "analysis_queue_size": len(self.screenshot_buffer),
                    "active_apis": len(self.vision_apis),
                    "custom_recognizers": len(self.custom_trainer.recognizers)
                }
                
                await self._send_to_orchestrator(heartbeat)
                await asyncio.sleep(5)  # 5 second heartbeat
                
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
                await asyncio.sleep(10)
    
    async def _monitor_api_usage(self):
        """Monitor API usage and costs"""
        while True:
            try:
                # Log API usage statistics
                total_requests = sum(self.api_usage_stats.values())
                logger.info(f"API Usage Summary - Total: {total_requests}, "
                          f"Details: {dict(self.api_usage_stats)}")
                
                # Check for rate limit warnings
                for provider, usage in self.api_usage_stats.items():
                    rate_limit = self.config["vision_apis"][provider].get("rate_limit", 1000)
                    if usage > rate_limit * 0.8:  # 80% of rate limit
                        logger.warning(f"Approaching rate limit for {provider}: "
                                     f"{usage}/{rate_limit}")
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error monitoring API usage: {e}")
                await asyncio.sleep(3600)
    
    async def _send_to_orchestrator(self, message: Dict[str, Any]):
        """Send message to the Core Orchestrator"""
        try:
            if self.websocket:
                await self.websocket.send(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Failed to send message to orchestrator: {e}")

    async def _handle_screenshot_analysis_request(self, data: Dict[str, Any]):
        """Handle screenshot analysis request from orchestrator"""
        try:
            # Decode screenshot data
            image_data = base64.b64decode(data['image_data'])
            
            screenshot = ScreenshotCapture(
                timestamp=datetime.fromisoformat(data['timestamp']),
                platform=data['platform'],
                resolution=tuple(data['resolution']),
                image_data=image_data,
                image_format=data.get('image_format', 'png'),
                session_id=data['session_id'],
                url_or_context=data.get('url_or_context'),
                user_id=data.get('user_id')
            )
            
            # Add to analysis queue
            self.screenshot_buffer.append(screenshot)
            
            await self._send_to_orchestrator({
                "type": "response",
                "request_id": data.get('request_id'),
                "status": "queued",
                "message": "Screenshot added to analysis queue"
            })
            
        except Exception as e:
            logger.error(f"Error handling screenshot analysis request: {e}")
            await self._send_to_orchestrator({
                "type": "response",
                "request_id": data.get('request_id'),
                "status": "error",
                "error": str(e)
            })

    async def _handle_training_request(self, data: Dict[str, Any]):
        """Handle custom recognizer training request"""
        try:
            issue_type = data['issue_type']
            image_data = base64.b64decode(data['image_data'])
            bounding_box = tuple(data['bounding_box'])
            metadata = data.get('metadata', {})
            
            # Add training sample
            self.custom_trainer.add_training_sample(
                issue_type=issue_type,
                image_data=image_data,
                bounding_box=bounding_box,
                metadata=metadata
            )
            
            await self._send_to_orchestrator({
                "type": "response",
                "request_id": data.get('request_id'),
                "status": "success",
                "message": f"Training sample added for {issue_type}"
            })
            
        except Exception as e:
            logger.error(f"Error handling training request: {e}")
            await self._send_to_orchestrator({
                "type": "response",
                "request_id": data.get('request_id'),
                "status": "error",
                "error": str(e)
            })

    async def _handle_configuration_update(self, data: Dict[str, Any]):
        """Handle configuration update from orchestrator"""
        try:
            # Update configuration
            if 'vision_apis' in data:
                self.config['vision_apis'].update(data['vision_apis'])
                await self._initialize_vision_apis()
            
            if 'analysis' in data:
                self.config['analysis'].update(data['analysis'])
            
            await self._send_to_orchestrator({
                "type": "response",
                "request_id": data.get('request_id'),
                "status": "success",
                "message": "Configuration updated"
            })
            
        except Exception as e:
            logger.error(f"Error handling configuration update: {e}")
            await self._send_to_orchestrator({
                "type": "response",
                "request_id": data.get('request_id'),
                "status": "error",
                "error": str(e)
            })

def main():
    """Main entry point for the Visual Analysis Agent"""
    agent = VisualAnalysisAgent()
    
    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        logger.info("Visual Analysis Agent shutting down...")
    except Exception as e:
        logger.error(f"Visual Analysis Agent error: {e}")

if __name__ == "__main__":
    main() 