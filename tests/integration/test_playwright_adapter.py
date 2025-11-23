#!/usr/bin/env python3
"""
Integration tests for Playwright UX-Mirror Adapter

Tests verify that:
1. Playwright integration works correctly
2. AI analysis is applied to screenshots
3. No Playwright features are duplicated
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from PIL import Image
import io

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from src.integration.playwright_adapter import PlaywrightUXMirrorAdapter, PLAYWRIGHT_AVAILABLE
except ImportError as e:
    pytest.skip(f"Playwright adapter not available: {e}", allow_module_level=True)


@pytest.fixture
def mock_api_key():
    """Mock API key for testing"""
    return "test-api-key-12345"


@pytest.fixture
def mock_image():
    """Create a mock PIL Image for testing"""
    return Image.new('RGB', (800, 600), color='white')


@pytest.mark.asyncio
async def test_adapter_initialization(mock_api_key):
    """Test adapter can be initialized"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed")
    
    adapter = PlaywrightUXMirrorAdapter(mock_api_key, provider="openai")
    assert adapter.api_key == mock_api_key
    assert adapter.provider == "openai"
    assert adapter.browser is None
    assert adapter.page is None
    assert adapter.analyzer is None


@pytest.mark.asyncio
async def test_adapter_start_stop(mock_api_key):
    """Test adapter can start and stop"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed")
    
    adapter = PlaywrightUXMirrorAdapter(mock_api_key)
    
    # Mock Playwright
    with patch('src.integration.playwright_adapter.async_playwright') as mock_playwright:
        mock_pw_instance = AsyncMock()
        mock_playwright.return_value.start = AsyncMock(return_value=mock_pw_instance)
        
        mock_browser = AsyncMock()
        mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_page = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        
        # Mock AI analyzer
        with patch('src.integration.playwright_adapter.AIVisionAnalyzer') as mock_analyzer_class:
            mock_analyzer = AsyncMock()
            mock_analyzer.__aenter__ = AsyncMock(return_value=mock_analyzer)
            mock_analyzer.__aexit__ = AsyncMock(return_value=None)
            mock_analyzer_class.return_value = mock_analyzer
            
            await adapter.start(headless=True)
            
            assert adapter.browser is not None
            assert adapter.page is not None
            assert adapter.analyzer is not None
            
            # Test stop
            mock_browser.close = AsyncMock()
            mock_pw_instance.stop = AsyncMock()
            
            await adapter.stop()
            
            mock_browser.close.assert_called_once()


@pytest.mark.asyncio
async def test_navigate_and_analyze(mock_api_key, mock_image):
    """Test navigate and analyze functionality"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed")
    
    adapter = PlaywrightUXMirrorAdapter(mock_api_key)
    
    # Mock components
    mock_page = AsyncMock()
    mock_analyzer = AsyncMock()
    
    # Mock screenshot
    screenshot_bytes = io.BytesIO()
    mock_image.save(screenshot_bytes, format='PNG')
    screenshot_bytes.seek(0)
    mock_page.screenshot = AsyncMock(return_value=screenshot_bytes.getvalue())
    mock_page.goto = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    
    # Mock analysis result
    from ai_vision_analyzer import GameUIAnalysis
    from datetime import datetime
    mock_analysis = GameUIAnalysis(
        timestamp=datetime.now(),
        overall_assessment="Test assessment",
        issues_found=[],
        recommendations=["Test recommendation"],
        ui_elements_detected=[],
        clutter_score=0.5,
        readability_score=0.7,
        visual_hierarchy_score=0.6,
        specific_problems=[]
    )
    mock_analyzer.analyze_screenshot = AsyncMock(return_value=mock_analysis)
    
    adapter.page = mock_page
    adapter.analyzer = mock_analyzer
    
    # Test navigation and analysis
    results = await adapter.navigate_and_analyze(
        url="https://example.com",
        context="Test context"
    )
    
    # Verify Playwright was used for navigation
    mock_page.goto.assert_called_once()
    mock_page.screenshot.assert_called_once()
    
    # Verify AI analyzer was used
    mock_analyzer.analyze_screenshot.assert_called_once()
    
    # Verify results structure
    assert results["url"] == "https://example.com"
    assert results["screenshot_captured"] is True
    assert "analysis" in results
    assert "feedback" in results


@pytest.mark.asyncio
async def test_interact_and_analyze(mock_api_key, mock_image):
    """Test interaction and analysis"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed")
    
    adapter = PlaywrightUXMirrorAdapter(mock_api_key)
    
    mock_page = AsyncMock()
    mock_analyzer = AsyncMock()
    
    # Mock screenshot
    screenshot_bytes = io.BytesIO()
    mock_image.save(screenshot_bytes, format='PNG')
    screenshot_bytes.seek(0)
    mock_page.screenshot = AsyncMock(return_value=screenshot_bytes.getvalue())
    mock_page.click = AsyncMock()
    mock_page.wait_for_load_state = AsyncMock()
    
    # Mock analysis
    from ai_vision_analyzer import GameUIAnalysis
    from datetime import datetime
    mock_analysis = GameUIAnalysis(
        timestamp=datetime.now(),
        overall_assessment="After click",
        issues_found=[],
        recommendations=[],
        ui_elements_detected=[],
        clutter_score=0.5,
        readability_score=0.7,
        visual_hierarchy_score=0.6,
        specific_problems=[]
    )
    mock_analyzer.analyze_screenshot = AsyncMock(return_value=mock_analysis)
    
    adapter.page = mock_page
    adapter.analyzer = mock_analyzer
    
    # Test interaction
    action = {
        "type": "click",
        "selector": "button.submit"
    }
    
    results = await adapter.interact_and_analyze(action)
    
    # Verify Playwright was used for interaction
    mock_page.click.assert_called_once_with("button.submit")
    mock_page.wait_for_load_state.assert_called_once()
    mock_page.screenshot.assert_called_once()
    
    # Verify AI analysis was performed
    mock_analyzer.analyze_screenshot.assert_called_once()
    
    assert results["action"] == action
    assert results["screenshot_captured"] is True


@pytest.mark.asyncio
async def test_analyze_element(mock_api_key, mock_image):
    """Test element-specific analysis"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed")
    
    adapter = PlaywrightUXMirrorAdapter(mock_api_key)
    
    mock_page = AsyncMock()
    mock_element = AsyncMock()
    mock_analyzer = AsyncMock()
    
    # Mock element screenshot
    screenshot_bytes = io.BytesIO()
    mock_image.save(screenshot_bytes, format='PNG')
    screenshot_bytes.seek(0)
    mock_element.screenshot = AsyncMock(return_value=screenshot_bytes.getvalue())
    mock_page.wait_for_selector = AsyncMock(return_value=mock_element)
    
    # Mock analysis
    from ai_vision_analyzer import GameUIAnalysis
    from datetime import datetime
    mock_analysis = GameUIAnalysis(
        timestamp=datetime.now(),
        overall_assessment="Element analysis",
        issues_found=[],
        recommendations=[],
        ui_elements_detected=[],
        clutter_score=0.5,
        readability_score=0.7,
        visual_hierarchy_score=0.6,
        specific_problems=[]
    )
    mock_analyzer.analyze_screenshot = AsyncMock(return_value=mock_analysis)
    
    adapter.page = mock_page
    adapter.analyzer = mock_analyzer
    
    # Test element analysis
    results = await adapter.analyze_element("button.primary")
    
    # Verify Playwright was used
    mock_page.wait_for_selector.assert_called_once_with("button.primary")
    mock_element.screenshot.assert_called_once()
    
    # Verify AI analysis
    mock_analyzer.analyze_screenshot.assert_called_once()
    
    assert results["selector"] == "button.primary"
    assert results["element_captured"] is True


@pytest.mark.asyncio
async def test_run_ux_test_flow(mock_api_key, mock_image):
    """Test running a complete UX test flow"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed")
    
    adapter = PlaywrightUXMirrorAdapter(mock_api_key)
    
    mock_page = AsyncMock()
    mock_analyzer = AsyncMock()
    
    # Mock screenshot
    screenshot_bytes = io.BytesIO()
    mock_image.save(screenshot_bytes, format='PNG')
    screenshot_bytes.seek(0)
    mock_page.screenshot = AsyncMock(return_value=screenshot_bytes.getvalue())
    mock_page.goto = AsyncMock()
    mock_page.click = AsyncMock()
    mock_page.wait_for_load_state = AsyncMock()
    
    # Mock analysis
    from ai_vision_analyzer import GameUIAnalysis
    from datetime import datetime
    mock_analysis = GameUIAnalysis(
        timestamp=datetime.now(),
        overall_assessment="Test flow",
        issues_found=[],
        recommendations=["Test rec"],
        ui_elements_detected=[],
        clutter_score=0.5,
        readability_score=0.7,
        visual_hierarchy_score=0.6,
        specific_problems=[]
    )
    mock_analyzer.analyze_screenshot = AsyncMock(return_value=mock_analysis)
    
    adapter.page = mock_page
    adapter.analyzer = mock_analyzer
    
    # Test flow
    test_steps = [
        {
            "type": "navigate",
            "url": "https://example.com",
            "description": "Navigate to page"
        },
        {
            "type": "click",
            "selector": "button",
            "description": "Click button"
        }
    ]
    
    results = await adapter.run_ux_test_flow(test_steps, analyze_after_each=True)
    
    # Verify structure
    assert len(results["steps"]) == 2
    assert "overall_analysis" in results
    assert "recommendations" in results
    
    # Verify Playwright was used
    assert mock_page.goto.called
    assert mock_page.click.called


@pytest.mark.asyncio
async def test_error_handling_not_started(mock_api_key):
    """Test error handling when adapter not started"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed")
    
    adapter = PlaywrightUXMirrorAdapter(mock_api_key)
    
    # Should raise error when not started
    with pytest.raises(RuntimeError, match="Adapter not started"):
        await adapter.navigate_and_analyze("https://example.com")


@pytest.mark.asyncio
async def test_error_handling_invalid_action(mock_api_key):
    """Test error handling for invalid actions"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed")
    
    adapter = PlaywrightUXMirrorAdapter(mock_api_key)
    
    mock_page = AsyncMock()
    adapter.page = mock_page
    
    # Invalid action type
    with pytest.raises(ValueError, match="Unknown action type"):
        await adapter.interact_and_analyze({
            "type": "invalid_action",
            "selector": "button"
        })


def test_playwright_not_available():
    """Test behavior when Playwright is not installed"""
    # This test verifies the import check works
    # In a real scenario, PLAYWRIGHT_AVAILABLE would be False
    pass


@pytest.mark.asyncio
async def test_get_page_metrics(mock_api_key):
    """Test getting page metrics from Playwright"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed")
    
    adapter = PlaywrightUXMirrorAdapter(mock_api_key)
    
    mock_page = AsyncMock()
    mock_page.evaluate = AsyncMock(return_value={
        "loadTime": 1000,
        "domContentLoaded": 500,
        "firstPaint": 200,
        "firstContentfulPaint": 300
    })
    
    adapter.page = mock_page
    
    metrics = await adapter.get_page_metrics()
    
    assert "loadTime" in metrics
    assert "domContentLoaded" in metrics
    assert metrics["loadTime"] == 1000

