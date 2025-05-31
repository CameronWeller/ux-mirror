#!/usr/bin/env python3
"""
UX Mirror - AI Vision Analyzer
Sends game screenshots to AI models for UX/UI analysis and feedback
"""

import os
import base64
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from PIL import Image
import numpy as np
import aiohttp
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GameUIAnalysis:
    """Results from AI vision analysis"""
    timestamp: datetime
    overall_assessment: str
    issues_found: List[Dict[str, Any]]
    recommendations: List[str]
    ui_elements_detected: List[Dict[str, Any]]
    clutter_score: float  # 0-1, higher = more cluttered
    readability_score: float  # 0-1, higher = better
    visual_hierarchy_score: float  # 0-1, higher = better
    specific_problems: List[str]
    
    def to_json(self) -> str:
        """Convert to JSON for API responses"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return json.dumps(data, indent=2)

class AIVisionAnalyzer:
    """Analyzes game screenshots using AI vision models"""
    
    def __init__(self, api_key: str, provider: str = "openai"):
        self.api_key = api_key
        self.provider = provider
        self.session = None
        
        # API endpoints
        self.endpoints = {
            "openai": "https://api.openai.com/v1/chat/completions",
            "anthropic": "https://api.anthropic.com/v1/messages"
        }
        
        # Game-specific prompts
        self.game_ui_prompt = """You are a game UI/UX expert analyzing a screenshot from a 3D game. 
Please analyze this image and provide:

1. Overall UI assessment (is it cluttered, clean, intuitive?)
2. Specific UI issues found (list each with location and severity)
3. Visual hierarchy analysis (can player easily find important elements?)
4. Readability issues (text too small, poor contrast, etc.)
5. Button/control layout problems
6. Any glitches or rendering issues
7. Recommendations for improvement

Focus on practical, actionable feedback that an AI developer can use to improve the game.
Be specific about locations (e.g., "top-right corner", "center of screen").

Respond in JSON format with these fields:
{
    "overall_assessment": "brief overall assessment",
    "clutter_score": 0.0-1.0,
    "readability_score": 0.0-1.0,
    "visual_hierarchy_score": 0.0-1.0,
    "issues_found": [
        {
            "type": "issue type",
            "location": "screen location",
            "severity": "high/medium/low",
            "description": "detailed description"
        }
    ],
    "ui_elements_detected": [
        {
            "type": "button/text/panel/etc",
            "location": "screen location",
            "assessment": "good/needs_work/broken"
        }
    ],
    "specific_problems": ["problem 1", "problem 2"],
    "recommendations": ["recommendation 1", "recommendation 2"]
}"""
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _encode_image(self, image: Image.Image) -> str:
        """Encode PIL image to base64"""
        import io
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')
    
    async def analyze_screenshot(self, image: Image.Image, 
                               context: Optional[str] = None) -> GameUIAnalysis:
        """Analyze a game screenshot using AI vision"""
        
        # Encode image
        base64_image = self._encode_image(image)
        
        # Build prompt with optional context
        prompt = self.game_ui_prompt
        if context:
            prompt += f"\n\nAdditional context: {context}"
        
        try:
            if self.provider == "openai":
                response = await self._call_openai(base64_image, prompt)
            elif self.provider == "anthropic":
                response = await self._call_anthropic(base64_image, prompt)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            # Parse response
            return self._parse_response(response)
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # Return a basic analysis on error
            return GameUIAnalysis(
                timestamp=datetime.now(),
                overall_assessment="Analysis failed",
                issues_found=[],
                recommendations=["Unable to analyze image"],
                ui_elements_detected=[],
                clutter_score=0.5,
                readability_score=0.5,
                visual_hierarchy_score=0.5,
                specific_problems=["Analysis error"]
            )
    
    async def _call_openai(self, base64_image: str, prompt: str) -> Dict:
        """Call OpenAI Vision API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1  # Low temperature for consistent analysis
        }
        
        async with self.session.post(
            self.endpoints["openai"], 
            headers=headers, 
            json=data
        ) as response:
            result = await response.json()
            
            if response.status != 200:
                raise Exception(f"OpenAI API error: {result}")
            
            return result
    
    async def _call_anthropic(self, base64_image: str, prompt: str) -> Dict:
        """Call Anthropic Claude Vision API"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": "claude-3-opus-20240229",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        async with self.session.post(
            self.endpoints["anthropic"],
            headers=headers,
            json=data
        ) as response:
            result = await response.json()
            
            if response.status != 200:
                raise Exception(f"Anthropic API error: {result}")
            
            return result
    
    def _parse_response(self, api_response: Dict) -> GameUIAnalysis:
        """Parse API response into GameUIAnalysis object"""
        try:
            # Extract content based on provider
            if self.provider == "openai":
                content = api_response['choices'][0]['message']['content']
            else:  # anthropic
                content = api_response['content'][0]['text']
            
            # Parse JSON from content
            # Handle case where model includes markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content)
            
            return GameUIAnalysis(
                timestamp=datetime.now(),
                overall_assessment=data.get('overall_assessment', ''),
                issues_found=data.get('issues_found', []),
                recommendations=data.get('recommendations', []),
                ui_elements_detected=data.get('ui_elements_detected', []),
                clutter_score=float(data.get('clutter_score', 0.5)),
                readability_score=float(data.get('readability_score', 0.5)),
                visual_hierarchy_score=float(data.get('visual_hierarchy_score', 0.5)),
                specific_problems=data.get('specific_problems', [])
            )
            
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            logger.debug(f"Raw response: {api_response}")
            
            # Return basic analysis on parse error
            return GameUIAnalysis(
                timestamp=datetime.now(),
                overall_assessment="Failed to parse AI response",
                issues_found=[],
                recommendations=["Check API response format"],
                ui_elements_detected=[],
                clutter_score=0.5,
                readability_score=0.5,
                visual_hierarchy_score=0.5,
                specific_problems=["Response parsing error"]
            )

class GameUIFeedbackProcessor:
    """Processes AI feedback for game developers"""
    
    def __init__(self):
        self.feedback_history = []
        
    def process_analysis(self, analysis: GameUIAnalysis, 
                        user_input: Optional[Dict] = None) -> Dict[str, Any]:
        """Process analysis results for developer consumption"""
        
        # Store in history
        self.feedback_history.append({
            'timestamp': analysis.timestamp,
            'analysis': analysis,
            'user_input': user_input
        })
        
        # Create developer-friendly feedback
        feedback = {
            'summary': self._create_summary(analysis),
            'priority_fixes': self._prioritize_issues(analysis),
            'code_suggestions': self._generate_code_suggestions(analysis),
            'metrics': {
                'clutter_score': analysis.clutter_score,
                'readability_score': analysis.readability_score,
                'visual_hierarchy_score': analysis.visual_hierarchy_score
            }
        }
        
        # Add user context if provided
        if user_input:
            feedback['user_context'] = user_input
        
        return feedback
    
    def _create_summary(self, analysis: GameUIAnalysis) -> str:
        """Create a concise summary for developers"""
        high_priority = [i for i in analysis.issues_found 
                        if i.get('severity') == 'high']
        
        summary = f"UI Analysis: {analysis.overall_assessment}\n"
        summary += f"Found {len(analysis.issues_found)} issues "
        summary += f"({len(high_priority)} high priority)\n"
        
        if analysis.clutter_score > 0.7:
            summary += "⚠️ UI is cluttered - consider simplifying\n"
        if analysis.readability_score < 0.5:
            summary += "⚠️ Text readability issues detected\n"
        
        return summary
    
    def _prioritize_issues(self, analysis: GameUIAnalysis) -> List[Dict]:
        """Prioritize issues for fixing"""
        # Sort by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_issues = sorted(
            analysis.issues_found,
            key=lambda x: severity_order.get(x.get('severity', 'low'), 3)
        )
        
        return sorted_issues[:5]  # Top 5 issues
    
    def _generate_code_suggestions(self, analysis: GameUIAnalysis) -> List[str]:
        """Generate code suggestions based on issues"""
        suggestions = []
        
        for issue in analysis.issues_found:
            issue_type = issue.get('type', '').lower()
            
            if 'contrast' in issue_type:
                suggestions.append(
                    "// Increase text contrast\n"
                    "textColor = vec4(0.1, 0.1, 0.1, 1.0);  // Darker text"
                )
            elif 'size' in issue_type or 'small' in issue_type:
                suggestions.append(
                    "// Increase UI element size\n"
                    "uiScale *= 1.2f;  // 20% larger"
                )
            elif 'clutter' in issue_type:
                suggestions.append(
                    "// Add spacing between elements\n"
                    "elementPadding = 20.0f;  // Increase padding"
                )
        
        return suggestions

# Example usage
async def analyze_game_screenshot(image_path: str, api_key: str):
    """Example function to analyze a game screenshot"""
    
    # Load image
    image = Image.open(image_path)
    
    # Create analyzer
    async with AIVisionAnalyzer(api_key, provider="openai") as analyzer:
        # Analyze screenshot
        analysis = await analyzer.analyze_screenshot(
            image,
            context="3D Game of Life - main gameplay view"
        )
        
        # Process feedback
        processor = GameUIFeedbackProcessor()
        feedback = processor.process_analysis(analysis)
        
        # Print results
        print(feedback['summary'])
        print("\nTop Issues:")
        for issue in feedback['priority_fixes']:
            print(f"- {issue['description']} ({issue['severity']})")
        
        return feedback

if __name__ == "__main__":
    # Test with dummy image
    import sys
    
    if len(sys.argv) > 1:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            logger.error("Please set OPENAI_API_KEY environment variable")
            sys.exit(1)
        
        asyncio.run(analyze_game_screenshot(sys.argv[1], api_key)) 