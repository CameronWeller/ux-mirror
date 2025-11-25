#!/usr/bin/env python3
"""
Test script to verify real AI analysis integration with Anthropic API
"""

import os
import sys
import asyncio
import tempfile
from datetime import datetime
from PIL import ImageGrab

async def test_anthropic_analysis():
    """Test the real Anthropic API analysis"""
    print("🧪 Testing Real AI Analysis Integration")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("Please set it with: set ANTHROPIC_API_KEY=your_key_here")
        return False
    
    print(f"✅ API key found (length: {len(api_key)} chars)")
    
    # Test screenshot capture
    print("\n📸 Capturing screenshot...")
    try:
        screenshot = ImageGrab.grab()
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        screenshot_path = os.path.join(temp_dir, f"test_screenshot_{timestamp}.png")
        screenshot.save(screenshot_path)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
    except Exception as e:
        print(f"❌ Screenshot failed: {e}")
        return False
    
    # Test AI analysis
    print("\n🤖 Testing Anthropic Claude analysis...")
    try:
        import base64
        import anthropic
        
        # Load and encode image
        with open(screenshot_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Create client
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = """Analyze this screenshot for UI/UX elements. Describe:
1. What UI elements you can see
2. Overall visual quality
3. Any potential improvements
4. Color scheme and layout

Be specific about what you observe."""

        print("   Sending request to Claude...")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_data
                            }
                        }
                    ]
                }
            ]
        )
        
        ai_response = response.content[0].text
        
        print("✅ AI analysis successful!")
        print("\n🎯 Claude's Analysis:")
        print("-" * 30)
        print(ai_response[:300] + "..." if len(ai_response) > 300 else ai_response)
        
        # Clean up
        try:
            os.remove(screenshot_path)
            print(f"\n🧹 Cleaned up: {screenshot_path}")
        except:
            pass
        
        return True
        
    except ImportError:
        print("❌ Anthropic library not installed")
        print("Install with: pip install anthropic")
        return False
    except Exception as e:
        print(f"❌ AI analysis failed: {e}")
        return False

async def test_launcher_integration():
    """Test if the launcher can use real analysis"""
    print("\n🚀 Testing UX-MIRROR Launcher Integration")
    print("=" * 50)
    
    try:
        # Import our updated launcher
        sys.path.insert(0, '.')
        from ux_mirror_launcher import UXMirrorLauncher
        
        print("✅ UX-MIRROR launcher imported successfully")
        
        # Create launcher instance (don't show GUI)
        launcher = UXMirrorLauncher()
        
        # Test screenshot capture
        screenshot_path = await launcher._capture_screenshot()
        if screenshot_path:
            print("✅ Screenshot capture works")
            
            # Test AI analysis
            analysis_result = await launcher._perform_ai_analysis(screenshot_path, 1)
            
            if analysis_result:
                print("✅ AI analysis integration works")
                print(f"   Quality Score: {analysis_result.get('quality_score', 0):.2f}")
                print(f"   UI Elements: {analysis_result.get('ui_elements_detected', 0)}")
                if 'issues_found' in analysis_result:
                    print(f"   Issues Found: {len(analysis_result['issues_found'])}")
                if 'recommendations' in analysis_result:
                    print(f"   Recommendations: {len(analysis_result['recommendations'])}")
                return True
            else:
                print("❌ AI analysis failed")
                return False
        else:
            print("❌ Screenshot capture failed")
            return False
            
    except Exception as e:
        print(f"❌ Launcher integration failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🎯 UX-MIRROR Real Analysis Test Suite")
    print("🤖 Testing Anthropic API Integration")
    print("=" * 60)
    
    # Test 1: Direct API test
    api_success = await test_anthropic_analysis()
    
    # Test 2: Launcher integration test
    launcher_success = await test_launcher_integration()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Direct API Test: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"   Launcher Integration: {'✅ PASS' if launcher_success else '❌ FAIL'}")
    
    if api_success and launcher_success:
        print("\n🎉 All tests passed! Real AI analysis is working!")
        print("\n🚀 You can now run:")
        print("   python ux_mirror_launcher.py")
        print("   And get real AI-powered UX analysis!")
        return True
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 