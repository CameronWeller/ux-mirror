"""
Unit tests for AI-powered content validation functionality.
"""
import json
import base64
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pytest

from src.analysis.content_validation import ContentValidator


class TestContentValidator:
    """Test cases for ContentValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ContentValidator(
            openai_api_key="test_openai_key",
            anthropic_api_key="test_anthropic_key"
        )
    
    def test_init_without_keys(self):
        """Test initialization without API keys."""
        validator = ContentValidator()
        assert validator.openai_api_key == ""
        assert validator.anthropic_api_key == ""
        assert validator.openai_client is None
        assert validator.anthropic_client is None
    
    @patch('src.analysis.content_validation.openai')
    @patch('src.analysis.content_validation.OPENAI_AVAILABLE', True)
    def test_init_with_openai_key(self, mock_openai):
        """Test initialization with OpenAI key."""
        mock_client = Mock()
        mock_openai.OpenAI.return_value = mock_client
        
        validator = ContentValidator(openai_api_key="test_key")
        
        mock_openai.OpenAI.assert_called_once_with(api_key="test_key")
        assert validator.openai_client == mock_client
    
    @patch('src.analysis.content_validation.anthropic')
    @patch('src.analysis.content_validation.ANTHROPIC_AVAILABLE', True)
    def test_init_with_anthropic_key(self, mock_anthropic):
        """Test initialization with Anthropic key."""
        mock_client = Mock()
        mock_anthropic.Anthropic.return_value = mock_client
        
        validator = ContentValidator(anthropic_api_key="test_key")
        
        mock_anthropic.Anthropic.assert_called_once_with(api_key="test_key")
        assert validator.anthropic_client == mock_client
    
    @patch('src.analysis.content_validation.openai')
    @patch('src.analysis.content_validation.OPENAI_AVAILABLE', True)
    def test_init_openai_client_error(self, mock_openai):
        """Test initialization with OpenAI client error."""
        mock_openai.OpenAI.side_effect = Exception("API error")
        
        validator = ContentValidator(openai_api_key="test_key")
        
        assert validator.openai_client is None
    
    def test_encode_image_base64_success(self):
        """Test successful image encoding to base64."""
        test_image_data = b"fake_image_data"
        expected_base64 = base64.b64encode(test_image_data).decode('utf-8')
        
        with patch('builtins.open', mock_open(read_data=test_image_data)):
            result = self.validator._encode_image_base64(Path("test.png"))
            assert result == expected_base64
    
    def test_encode_image_base64_error(self):
        """Test image encoding error handling."""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            result = self.validator._encode_image_base64(Path("nonexistent.png"))
            assert result is None
    
    @patch('src.analysis.content_validation.Image')
    def test_resize_image_for_api_no_resize_needed(self, mock_image):
        """Test image resize when no resize is needed."""
        mock_img = Mock()
        mock_img.size = (800, 600)
        mock_image.open.return_value.__enter__.return_value = mock_img
        
        result = self.validator._resize_image_for_api(Path("test.png"), max_size=1024)
        
        assert result == Path("test.png")
        mock_img.resize.assert_not_called()
    
    @patch('src.analysis.content_validation.Image')
    def test_resize_image_for_api_resize_needed(self, mock_image):
        """Test image resize when resize is needed."""
        mock_img = Mock()
        mock_img.size = (2048, 1536)
        mock_resized_img = Mock()
        mock_img.resize.return_value = mock_resized_img
        
        mock_image.open.return_value.__enter__.return_value = mock_img
        mock_image.Resampling.LANCZOS = "LANCZOS"
        
        result = self.validator._resize_image_for_api(Path("test.png"), max_size=1024)
        
        # Should resize to maintain aspect ratio
        mock_img.resize.assert_called_once()
        mock_resized_img.save.assert_called_once()
        assert "resized_" in str(result)
    
    @patch('src.analysis.content_validation.Image')
    def test_resize_image_for_api_error(self, mock_image):
        """Test image resize error handling."""
        mock_image.open.side_effect = Exception("Image error")
        
        result = self.validator._resize_image_for_api(Path("test.png"))
        
        assert result == Path("test.png")
    
    def test_validate_with_openai_no_client(self):
        """Test OpenAI validation without client."""
        validator = ContentValidator()  # No API key
        
        result = validator.validate_with_openai(Path("test.png"), "expected content")
        
        assert result['provider'] == 'openai'
        assert result['success'] is False
        assert result['error'] == "OpenAI client not available"
    
    @patch.object(ContentValidator, '_resize_image_for_api')
    @patch.object(ContentValidator, '_encode_image_base64')
    def test_validate_with_openai_encoding_failure(self, mock_encode, mock_resize):
        """Test OpenAI validation with encoding failure."""
        mock_resize.return_value = Path("test.png")
        mock_encode.return_value = None
        
        # Mock client
        self.validator.openai_client = Mock()
        
        result = self.validator.validate_with_openai(Path("test.png"), "expected content")
        
        assert result['success'] is False
        assert result['error'] == "Failed to encode image"
    
    @patch.object(ContentValidator, '_resize_image_for_api')
    @patch.object(ContentValidator, '_encode_image_base64')
    def test_validate_with_openai_success_json_response(self, mock_encode, mock_resize):
        """Test successful OpenAI validation with JSON response."""
        mock_resize.return_value = Path("test.png")
        mock_encode.return_value = "encoded_image_data"
        
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = json.dumps({
            'content_matches': True,
            'confidence': 0.9,
            'description': 'Test description',
            'issues': ['Test issue']
        })
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        self.validator.openai_client = mock_client
        
        result = self.validator.validate_with_openai(Path("test.png"), "expected content")
        
        assert result['success'] is True
        assert result['content_matches'] is True
        assert result['confidence'] == 0.9
        assert result['description'] == 'Test description'
        assert result['issues'] == ['Test issue']
    
    @patch.object(ContentValidator, '_resize_image_for_api')
    @patch.object(ContentValidator, '_encode_image_base64')
    def test_validate_with_openai_success_text_response(self, mock_encode, mock_resize):
        """Test successful OpenAI validation with text response."""
        mock_resize.return_value = Path("test.png")
        mock_encode.return_value = "encoded_image_data"
        
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "The image contains expected content clearly visible"
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        self.validator.openai_client = mock_client
        
        result = self.validator.validate_with_openai(Path("test.png"), "expected content")
        
        assert result['success'] is True
        assert result['content_matches'] is True
        assert result['confidence'] == 0.7
        assert "expected content" in result['description']
    
    @patch.object(ContentValidator, '_resize_image_for_api')
    @patch.object(ContentValidator, '_encode_image_base64')
    def test_validate_with_openai_api_error(self, mock_encode, mock_resize):
        """Test OpenAI validation API error."""
        mock_resize.return_value = Path("test.png")
        mock_encode.return_value = "encoded_image_data"
        
        # Mock OpenAI client with error
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        self.validator.openai_client = mock_client
        
        result = self.validator.validate_with_openai(Path("test.png"), "expected content")
        
        assert result['success'] is False
        assert result['error'] == "API error"
    
    def test_validate_with_claude_no_client(self):
        """Test Claude validation without client."""
        validator = ContentValidator()  # No API key
        
        result = validator.validate_with_claude(Path("test.png"), "expected content")
        
        assert result['provider'] == 'anthropic'
        assert result['success'] is False
        assert result['error'] == "Anthropic client not available"
    
    @patch.object(ContentValidator, '_resize_image_for_api')
    @patch.object(ContentValidator, '_encode_image_base64')
    def test_validate_with_claude_success_positive(self, mock_encode, mock_resize):
        """Test successful Claude validation with positive response."""
        mock_resize.return_value = Path("test.png")
        mock_encode.return_value = "encoded_image_data"
        
        # Mock Anthropic client
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock()]
        mock_message.content[0].text = "Yes, the screenshot contains the expected content with 90% confidence"
        mock_client.messages.create.return_value = mock_message
        self.validator.anthropic_client = mock_client
        
        result = self.validator.validate_with_claude(Path("test.png"), "expected content")
        
        assert result['success'] is True
        assert result['content_matches'] is True
        assert result['confidence'] == 0.9  # Extracted from "90% confidence"
        assert "expected content" in result['description']
    
    @patch.object(ContentValidator, '_resize_image_for_api')
    @patch.object(ContentValidator, '_encode_image_base64')
    def test_validate_with_claude_success_negative(self, mock_encode, mock_resize):
        """Test successful Claude validation with negative response."""
        mock_resize.return_value = Path("test.png")
        mock_encode.return_value = "encoded_image_data"
        
        # Mock Anthropic client
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock()]
        mock_message.content[0].text = "No, the screenshot does not contain the expected content. There are issues with the layout."
        mock_client.messages.create.return_value = mock_message
        self.validator.anthropic_client = mock_client
        
        result = self.validator.validate_with_claude(Path("test.png"), "expected content")
        
        assert result['success'] is True
        assert result['content_matches'] is False
        assert len(result['issues']) > 0  # Should extract issues
    
    @patch.object(ContentValidator, '_resize_image_for_api')
    @patch.object(ContentValidator, '_encode_image_base64')
    def test_validate_with_claude_api_error(self, mock_encode, mock_resize):
        """Test Claude validation API error."""
        mock_resize.return_value = Path("test.png")
        mock_encode.return_value = "encoded_image_data"
        
        # Mock Anthropic client with error
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API error")
        self.validator.anthropic_client = mock_client
        
        result = self.validator.validate_with_claude(Path("test.png"), "expected content")
        
        assert result['success'] is False
        assert result['error'] == "API error"
    
    @patch.object(ContentValidator, 'validate_with_openai')
    @patch.object(ContentValidator, 'validate_with_claude')
    def test_validate_content_both_providers(self, mock_claude, mock_openai):
        """Test content validation with both providers."""
        # Mock both clients exist
        self.validator.openai_client = Mock()
        self.validator.anthropic_client = Mock()
        
        # Mock provider results
        openai_result = {
            'success': True,
            'content_matches': True,
            'confidence': 0.8,
            'description': 'OpenAI description',
            'issues': ['OpenAI issue']
        }
        claude_result = {
            'success': True,
            'content_matches': True,
            'confidence': 0.9,
            'description': 'Claude description',
            'issues': ['Claude issue']
        }
        
        mock_openai.return_value = openai_result
        mock_claude.return_value = claude_result
        
        result = self.validator.validate_content(Path("test.png"), "expected content")
        
        assert len(result['providers']) == 2
        assert result['consensus']['content_matches'] is True
        assert abs(result['consensus']['confidence'] - 0.85) < 0.001  # Use tolerance for floating point
        assert 'OpenAI description | Claude description' in result['consensus']['description']
        assert len(result['consensus']['issues']) == 2
    
    @patch.object(ContentValidator, 'validate_with_openai')
    def test_validate_content_openai_only(self, mock_openai):
        """Test content validation with OpenAI only."""
        # Only OpenAI client exists
        self.validator.openai_client = Mock()
        self.validator.anthropic_client = None
        
        openai_result = {
            'success': True,
            'content_matches': False,
            'confidence': 0.7,
            'description': 'OpenAI description',
            'issues': []
        }
        mock_openai.return_value = openai_result
        
        result = self.validator.validate_content(Path("test.png"), "expected content")
        
        assert len(result['providers']) == 1
        assert result['consensus']['content_matches'] is False
        assert result['consensus']['confidence'] == 0.7
    
    def test_validate_content_no_providers(self):
        """Test content validation with no providers."""
        validator = ContentValidator()  # No API keys
        
        result = validator.validate_content(Path("test.png"), "expected content")
        
        assert len(result['providers']) == 0
        assert 'No AI providers available' in result['consensus']['description']
    
    def test_analyze_screenshot_content_with_expected_content(self):
        """Test screenshot content analysis with expected content."""
        with patch.object(self.validator, 'validate_content') as mock_validate:
            mock_validate.return_value = {'validation': 'result'}
            
            result = self.validator.analyze_screenshot_content(Path("test.png"), "expected content")
            
            mock_validate.assert_called_once_with(Path("test.png"), "expected content")
            assert result == {'validation': 'result'}
    
    def test_analyze_screenshot_content_without_expected_content(self):
        """Test screenshot content analysis without expected content."""
        result = self.validator.analyze_screenshot_content(Path("test.png"))
        
        assert result['image_file'] == "test.png"
        assert 'General content analysis' in result['analysis']
        assert len(result['suggestions']) > 0 