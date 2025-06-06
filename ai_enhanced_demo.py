#!/usr/bin/env python3
"""
AI-Enhanced Screenshot Analysis Demo

Shows the difference between local analysis and AI-powered analysis
"""

import asyncio
import sys
import os
import base64
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def load_config():
    """Load configuration from config.env"""
    config = {}
    try:
        with open('config.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        print("⚠️ config.env not found")
    return config

async def ai_analyze_screenshot(image_path: str, config: dict) -> dict:
    """Analyze screenshot using AI APIs"""
    try:
        # Try OpenAI first
        openai_key = config.get('OPENAI_API_KEY', '')
        if openai_key and openai_key != 'your_openai_api_key_here':
            print("🤖 Using OpenAI GPT-4 Vision for analysis...")
            return await openai_vision_analysis(image_path, openai_key)
        
        # Try Anthropic
        anthropic_key = config.get('ANTHROPIC_API_KEY', '')
        if anthropic_key and anthropic_key != 'your_anthropic_api_key_here':
            print("🤖 Using Anthropic Claude for analysis...")
            return await anthropic_vision_analysis(image_path, anthropic_key)
        
        return {"error": "No valid API keys configured"}
        
    except Exception as e:
        return {"error": f"AI analysis failed: {e}"}

async def openai_vision_analysis(image_path: str, api_key: str) -> dict:
    """Analyze image using OpenAI GPT-4 Vision"""
    try:
        import openai
        
        # Encode image to base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this screenshot for game UX elements. Describe:
1. What UI elements you see (buttons, menus, text, etc.)
2. Visual quality and readability
3. Accessibility concerns
4. Overall game UX assessment
5. Specific recommendations for improvement

Be specific and detailed about what you observe."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        ai_description = response.choices[0].message.content
        
        return {
            "ai_provider": "OpenAI GPT-4 Vision",
            "description": ai_description,
            "analysis_type": "AI-powered visual analysis"
        }
        
    except Exception as e:
        return {"error": f"OpenAI analysis failed: {e}"}

async def anthropic_vision_analysis(image_path: str, api_key: str) -> dict:
    """Analyze image using Anthropic Claude"""
    try:
        import anthropic
        
        # Encode image to base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        client = anthropic.Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this screenshot for game UX elements. Describe:
1. What UI elements you see (buttons, menus, text, etc.)
2. Visual quality and readability
3. Accessibility concerns
4. Overall game UX assessment
5. Specific recommendations for improvement

Be specific and detailed about what you observe."""
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": base64_image
                            }
                        }
                    ]
                }
            ]
        )
        
        ai_description = response.content[0].text
        
        return {
            "ai_provider": "Anthropic Claude 3 Sonnet",
            "description": ai_description,
            "analysis_type": "AI-powered visual analysis"
        }
        
    except Exception as e:
        return {"error": f"Anthropic analysis failed: {e}"}

async def enhanced_demo():
    """Demo both local and AI-enhanced analysis"""
    try:
        from core.screenshot_analyzer import ScreenshotAnalyzer
        
        print("🎯 UX-MIRROR Enhanced Analysis Demo")
        print("=" * 50)
        
        # Load configuration
        config = load_config()
        
        # Create analyzer
        analyzer = ScreenshotAnalyzer()
        
        print("📸 Capturing screenshot...")
        screenshot_path = await analyzer.capture_screenshot()
        
        if not screenshot_path or not os.path.exists(screenshot_path):
            print("❌ Failed to capture screenshot")
            return
        
        print(f"✅ Screenshot saved: {screenshot_path}")
        print()
        
        # 1. Local Analysis
        print("🔍 LOCAL ANALYSIS")
        print("-" * 20)
        local_analysis = await analyzer.analyze_image(screenshot_path)
        
        if local_analysis and 'error' not in local_analysis:
            print(f"📊 Dimensions: {local_analysis['dimensions']['width']}x{local_analysis['dimensions']['height']}")
            print(f"📊 Quality: {local_analysis['quality_score']:.1%}")
            print(f"📊 UI Elements: {len(local_analysis['ui_elements'])}")
            print(f"📊 Performance: {local_analysis['performance_assessment']}")
            
            if local_analysis['ui_elements']:
                print(f"🎮 UI Elements:")
                for i, element in enumerate(local_analysis['ui_elements'], 1):
                    print(f"   {i}. {element['type']} at ({element['x']}, {element['y']})")
        
        print()
        
        # 2. AI-Enhanced Analysis
        print("🤖 AI-ENHANCED ANALYSIS")
        print("-" * 25)
        
        ai_analysis = await ai_analyze_screenshot(screenshot_path, config)
        
        if 'error' in ai_analysis:
            print(f"❌ {ai_analysis['error']}")
            print("💡 To enable AI analysis:")
            print("   1. Get API keys from OpenAI or Anthropic")
            print("   2. Update config.env with your keys")
            print("   3. Install: pip install openai anthropic")
        else:
            print(f"🤖 Provider: {ai_analysis['ai_provider']}")
            print(f"📝 AI Analysis:")
            print()
            # Format the AI description nicely
            lines = ai_analysis['description'].split('\n')
            for line in lines:
                if line.strip():
                    print(f"   {line.strip()}")
        
        print("\n" + "=" * 50)
        print("🎯 COMPARISON SUMMARY")
        print("=" * 50)
        print("📊 Local Analysis:")
        print("   ✅ Fast (instant)")
        print("   ✅ Works offline")
        print("   ✅ Basic metrics (quality, dimensions, performance)")
        print("   ✅ Simple UI element detection")
        print("   ❌ Limited context understanding")
        print()
        print("🤖 AI-Enhanced Analysis:")
        print("   ✅ Deep contextual understanding")
        print("   ✅ Natural language descriptions")
        print("   ✅ Game-specific UX insights")
        print("   ✅ Detailed accessibility analysis")
        print("   ❌ Requires API keys")
        print("   ❌ Slower (API calls)")
        
    except Exception as e:
        print(f"❌ Enhanced demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting enhanced analysis demo...")
    asyncio.run(enhanced_demo())
    print("\nDemo completed!") 