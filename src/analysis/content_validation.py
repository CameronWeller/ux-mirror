"""
AI-powered content validation for UX testing.

This module handles AI vision analysis using OpenAI and Anthropic Claude APIs.
"""
import base64
import json
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from PIL import Image

logger = logging.getLogger(__name__)

# Optional AI imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    anthropic = None
    ANTHROPIC_AVAILABLE = False


class ContentValidator:
    """Handles AI-powered content validation for screenshots."""
    
    def __init__(self, openai_api_key: str = "", anthropic_api_key: str = ""):
        """
        Initialize content validator.
        
        Args:
            openai_api_key: OpenAI API key
            anthropic_api_key: Anthropic API key
        """
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
        
        # Initialize clients if keys are provided
        self.openai_client = None
        self.anthropic_client = None
        
        if OPENAI_AVAILABLE and openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        
        if ANTHROPIC_AVAILABLE and anthropic_api_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
                logger.info("Anthropic client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")
    
    def _encode_image_base64(self, image_path: Path) -> Optional[str]:
        """
        Encode image to base64 for API transmission.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded image string or None if failed
        """
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            return None
    
    def _resize_image_for_api(self, image_path: Path, max_size: int = 1024) -> Optional[Path]:
        """
        Resize image if too large for API limits.
        
        Args:
            image_path: Path to original image
            max_size: Maximum dimension in pixels
            
        Returns:
            Path to resized image or original if no resize needed
        """
        try:
            with Image.open(image_path) as img:
                # Check if resize is needed
                if max(img.size) <= max_size:
                    return image_path
                
                # Calculate new size maintaining aspect ratio
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                
                # Resize and save
                resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                resized_path = image_path.parent / f"resized_{image_path.name}"
                resized_img.save(resized_path)
                
                logger.debug(f"Resized image from {img.size} to {new_size}")
                return resized_path
                
        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            return image_path
    
    def validate_with_openai(self, image_path: Path, expected_content: str) -> Dict[str, Any]:
        """
        Validate screenshot content using OpenAI Vision API.
        
        Args:
            image_path: Path to screenshot
            expected_content: Description of expected content
            
        Returns:
            Validation results
        """
        result = {
            'provider': 'openai',
            'success': False,
            'content_matches': False,
            'confidence': 0.0,
            'description': '',
            'issues': [],
            'error': None
        }
        
        if not self.openai_client:
            result['error'] = "OpenAI client not available"
            return result
        
        try:
            # Resize image if needed
            processed_image_path = self._resize_image_for_api(image_path)
            
            # Encode image
            base64_image = self._encode_image_base64(processed_image_path)
            if not base64_image:
                result['error'] = "Failed to encode image"
                return result
            
            # Create prompt
            prompt = f"""
            Analyze this screenshot and determine if it contains the expected content.
            
            Expected content: {expected_content}
            
            Please respond with a JSON object containing:
            1. "content_matches": boolean - does the screenshot contain the expected content?
            2. "confidence": number 0-1 - how confident are you in this assessment?
            3. "description": string - what do you see in the screenshot?
            4. "issues": array of strings - any UX issues you notice
            
            Focus on:
            - Visual elements mentioned in the expected content
            - Overall UI layout and design quality
            - Any obvious usability issues
            - Text readability and contrast
            """
            
            # Make API call
            response = self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            # Parse response
            response_text = response.choices[0].message.content
            
            try:
                # Try to parse as JSON
                response_data = json.loads(response_text)
                result.update(response_data)
                result['success'] = True
            except json.JSONDecodeError:
                # Fallback to text analysis
                result['description'] = response_text
                result['content_matches'] = expected_content.lower() in response_text.lower()
                result['confidence'] = 0.7 if result['content_matches'] else 0.3
                result['success'] = True
            
            # Clean up resized image if created
            if processed_image_path != image_path:
                processed_image_path.unlink(missing_ok=True)
            
            logger.info(f"OpenAI validation completed: {result['content_matches']} ({result['confidence']:.2f})")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"OpenAI validation failed: {e}")
        
        return result
    
    def validate_with_claude(self, image_path: Path, expected_content: str) -> Dict[str, Any]:
        """
        Validate screenshot content using Anthropic Claude.
        
        Args:
            image_path: Path to screenshot
            expected_content: Description of expected content
            
        Returns:
            Validation results
        """
        result = {
            'provider': 'anthropic',
            'success': False,
            'content_matches': False,
            'confidence': 0.0,
            'description': '',
            'issues': [],
            'error': None
        }
        
        if not self.anthropic_client:
            result['error'] = "Anthropic client not available"
            return result
        
        try:
            # Resize image if needed
            processed_image_path = self._resize_image_for_api(image_path)
            
            # Encode image
            base64_image = self._encode_image_base64(processed_image_path)
            if not base64_image:
                result['error'] = "Failed to encode image"
                return result
            
            # Create prompt
            prompt = f"""
            Analyze this screenshot and determine if it contains the expected content.
            
            Expected content: {expected_content}
            
            Please provide:
            1. Does the screenshot contain the expected content? (Yes/No)
            2. Your confidence level (0-100%)
            3. A description of what you see
            4. Any UX issues or recommendations
            
            Focus on visual elements, layout quality, and usability.
            """
            
            # Make API call
            message = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[
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
                ]
            )
            
            response_text = message.content[0].text
            
            # Parse response (Claude typically responds in natural language)
            result['description'] = response_text
            result['success'] = True
            
            # Extract confidence and content match from response
            response_lower = response_text.lower()
            
            # Check for positive indicators
            positive_indicators = ['yes', 'contains', 'matches', 'correct', 'expected']
            negative_indicators = ['no', 'does not', 'missing', 'incorrect', 'different']
            
            positive_count = sum(1 for indicator in positive_indicators if indicator in response_lower)
            negative_count = sum(1 for indicator in negative_indicators if indicator in response_lower)
            
            if positive_count > negative_count:
                result['content_matches'] = True
                result['confidence'] = min(0.9, 0.6 + (positive_count * 0.1))
            else:
                result['content_matches'] = False
                result['confidence'] = min(0.9, 0.6 + (negative_count * 0.1))
            
            # Extract confidence percentage if mentioned
            import re
            confidence_match = re.search(r'(\d+)%', response_text)
            if confidence_match:
                result['confidence'] = int(confidence_match.group(1)) / 100
            
            # Extract issues from response
            if 'issue' in response_lower or 'problem' in response_lower or 'recommend' in response_lower:
                result['issues'] = [response_text]  # Full response as issue for now
            
            # Clean up resized image if created
            if processed_image_path != image_path:
                processed_image_path.unlink(missing_ok=True)
            
            logger.info(f"Claude validation completed: {result['content_matches']} ({result['confidence']:.2f})")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Claude validation failed: {e}")
        
        return result
    
    def validate_content(self, image_path: Path, expected_content: str) -> Dict[str, Any]:
        """
        Validate screenshot content using available AI providers.
        
        Args:
            image_path: Path to screenshot
            expected_content: Description of expected content
            
        Returns:
            Combined validation results
        """
        validation_results = {
            'expected_content': expected_content,
            'image_file': image_path.name,
            'timestamp': json.dumps(None, default=str),  # Current timestamp
            'providers': [],
            'consensus': {
                'content_matches': False,
                'confidence': 0.0,
                'description': '',
                'issues': []
            }
        }
        
        # Try OpenAI first
        if self.openai_client:
            openai_result = self.validate_with_openai(image_path, expected_content)
            validation_results['providers'].append(openai_result)
        
        # Try Claude as backup/confirmation
        if self.anthropic_client:
            claude_result = self.validate_with_claude(image_path, expected_content)
            validation_results['providers'].append(claude_result)
        
        # Calculate consensus
        if validation_results['providers']:
            successful_results = [r for r in validation_results['providers'] if r['success']]
            
            if successful_results:
                # Average confidence and match status
                matches = [r['content_matches'] for r in successful_results]
                confidences = [r['confidence'] for r in successful_results]
                
                validation_results['consensus']['content_matches'] = sum(matches) / len(matches) > 0.5
                validation_results['consensus']['confidence'] = sum(confidences) / len(confidences)
                
                # Combine descriptions
                descriptions = [r['description'] for r in successful_results if r['description']]
                validation_results['consensus']['description'] = ' | '.join(descriptions)
                
                # Combine issues
                all_issues = []
                for r in successful_results:
                    all_issues.extend(r.get('issues', []))
                validation_results['consensus']['issues'] = all_issues
        
        if not validation_results['providers']:
            validation_results['consensus']['description'] = "No AI providers available for content validation"
        
        logger.info(f"Content validation completed: {validation_results['consensus']['content_matches']}")
        return validation_results
    
    def analyze_screenshot_content(self, image_path: Path, expected_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze screenshot content with or without specific expectations.
        
        Args:
            image_path: Path to screenshot
            expected_content: Optional description of expected content
            
        Returns:
            Content analysis results
        """
        if expected_content:
            return self.validate_content(image_path, expected_content)
        
        # General content analysis without specific expectations
        general_analysis = {
            'image_file': image_path.name,
            'timestamp': json.dumps(None, default=str),
            'analysis': 'General content analysis requested but not implemented',
            'suggestions': ['Consider providing expected content for validation']
        }
        
        return general_analysis 