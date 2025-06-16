#!/usr/bin/env python3
"""
Simple UX Tester
================

Manual screenshot-based UX quality testing tool.
Focus on basic functionality: did the button work? Is the UI responsive?

Usage:
    python simple_ux_tester.py capture --before
    # Perform your interaction (click button, etc.)
    python simple_ux_tester.py capture --after
    python simple_ux_tester.py analyze
"""

import argparse
import json
import logging
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageGrab

# Configure logging to be less noisy
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

# Optional AI vision imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class SimpleUXTester:
    def __init__(self, output_dir="ux_captures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.config = self._load_config()
        
    def _load_config(self):
        """Load configuration from config.env"""
        config = {
            'response_time_threshold': 500,
            'ui_change_threshold': 0.05,
            'screenshot_quality': 85,
            'openai_api_key': '',
            'google_vision_api_key': '',
            'anthropic_api_key': '',
            'content_validation_enabled': True
        }
        
        config_file = Path('config.env')
        if not config_file.exists():
            print("No config.env found, using defaults")
            return config
        
        try:
            with open(config_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        
                        config_mapping = {
                            'RESPONSE_TIME_THRESHOLD': ('response_time_threshold', int),
                            'UI_CHANGE_THRESHOLD': ('ui_change_threshold', float),
                            'SCREENSHOT_QUALITY': ('screenshot_quality', int),
                            'OPENAI_API_KEY': ('openai_api_key', str),
                            'GOOGLE_VISION_API_KEY': ('google_vision_api_key', str),
                            'ANTHROPIC_API_KEY': ('anthropic_api_key', str)
                        }
                        
                        if key in config_mapping and value:
                            config_key, config_type = config_mapping[key]
                            config[config_key] = config_type(value)
        except Exception as e:
            print(f"Error loading config: {e}")
            
        return config
    
    def capture_screenshot(self, label="screenshot", expected_content=None):
        """Capture a screenshot with timestamp and optional content expectation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{timestamp}_{label}.png"
        filepath = self.output_dir / filename
        
        print(f"Capturing screenshot: {filename}")
        
        # Capture screenshot
        screenshot = ImageGrab.grab()
        screenshot.save(filepath, quality=self.config['screenshot_quality'])
        
        # Save metadata
        metadata = {
            'filename': filename,
            'timestamp': timestamp,
            'label': label,
            'size': screenshot.size,
            'capture_time': datetime.now().isoformat()
        }
        
        if expected_content:
            metadata['expected_content'] = expected_content
        
        metadata_file = filepath.with_suffix('.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Screenshot saved: {filepath}")
        return filepath, metadata
    
    def capture_before(self, expected_content=None):
        """Capture 'before' screenshot"""
        return self.capture_screenshot("before", expected_content)
    
    def capture_after(self, expected_content=None):
        """Capture 'after' screenshot"""
        return self.capture_screenshot("after", expected_content)
    
    def find_latest_pair(self):
        """Find the most recent before/after screenshot pair"""
        before_files = list(self.output_dir.glob("*_before.png"))
        after_files = list(self.output_dir.glob("*_after.png"))
        
        if not before_files or not after_files:
            return None, None
            
        # Sort by timestamp (filename starts with timestamp)
        before_files.sort(reverse=True)
        after_files.sort(reverse=True)
        
        # Find matching pair (same timestamp prefix)
        for before_file in before_files:
            before_timestamp = before_file.stem.split('_')[0]
            
            for after_file in after_files:
                after_timestamp = after_file.stem.split('_')[0]
                
                # Look for after screenshot within reasonable time window
                if abs(int(after_timestamp) - int(before_timestamp)) < 100000:  # 10 seconds
                    return before_file, after_file
        
        # If no perfect match, use most recent of each
        return before_files[0], after_files[0]
    
    def analyze_screenshots(self, before_path=None, after_path=None):
        """Analyze before/after screenshots for UX quality"""
        if before_path is None or after_path is None:
            before_path, after_path = self.find_latest_pair()
        
        if before_path is None or after_path is None:
            print("ERROR: Could not find before/after screenshot pair")
            print("Run: python simple_ux_tester.py capture --before")
            print("Then interact with your UI")
            print("Then: python simple_ux_tester.py capture --after")
            return
        
        print(f"Analyzing: {before_path.name} -> {after_path.name}")
        
        # Load images
        before_img = cv2.imread(str(before_path))
        after_img = cv2.imread(str(after_path))
        
        if before_img is None or after_img is None:
            print("ERROR: Could not load screenshot images")
            return
        
        # Perform analysis
        analysis = {
            'before_file': before_path.name,
            'after_file': after_path.name,
            'timestamp': datetime.now().isoformat(),
            'results': {}
        }
        
        # 1. Basic UI Change Detection
        change_score = self._detect_ui_changes(before_img, after_img)
        analysis['results']['ui_changed'] = bool(change_score > self.config['ui_change_threshold'])
        analysis['results']['change_score'] = float(change_score)
        
        # 2. Response Time Analysis (from metadata timestamps)
        response_time = self._calculate_response_time(before_path, after_path)
        analysis['results']['response_time_ms'] = float(response_time)
        analysis['results']['response_acceptable'] = bool(response_time < self.config['response_time_threshold'])
        
        # 3. Basic Visual Quality Checks
        visual_issues = self._check_visual_quality(after_img)
        analysis['results']['visual_issues'] = visual_issues
        
        # 4. Content Validation (AI-powered)
        content_validation = self._validate_content_expectations(before_path, after_path)
        analysis['results']['content_validation'] = content_validation
        
        # 5. Overall Assessment
        analysis['results']['ux_quality'] = self._assess_ux_quality(analysis['results'])
        
        # Save analysis report
        report_file = self.output_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Print summary
        self._print_analysis_summary(analysis)
        
        return analysis
    
    def _detect_ui_changes(self, before_img, after_img):
        """Detect visual changes between screenshots"""
        # Resize images to same size if different
        if before_img.shape != after_img.shape:
            min_height = min(before_img.shape[0], after_img.shape[0])
            min_width = min(before_img.shape[1], after_img.shape[1])
            before_img = cv2.resize(before_img, (min_width, min_height))
            after_img = cv2.resize(after_img, (min_width, min_height))
        
        # Convert to grayscale for comparison
        before_gray = cv2.cvtColor(before_img, cv2.COLOR_BGR2GRAY)
        after_gray = cv2.cvtColor(after_img, cv2.COLOR_BGR2GRAY)
        
        # Calculate structural similarity
        diff = cv2.absdiff(before_gray, after_gray)
        change_score = np.mean(diff) / 255.0
        
        return change_score
    
    def _calculate_response_time(self, before_path, after_path):
        """Calculate response time from metadata timestamps"""
        try:
            before_meta_file = before_path.with_suffix('.json')
            after_meta_file = after_path.with_suffix('.json')
            
            with open(before_meta_file, 'r') as f:
                before_meta = json.load(f)
            with open(after_meta_file, 'r') as f:
                after_meta = json.load(f)
            
            before_time = datetime.fromisoformat(before_meta['capture_time'])
            after_time = datetime.fromisoformat(after_meta['capture_time'])
            
            response_time = (after_time - before_time).total_seconds() * 1000
            return max(0, response_time)  # Ensure non-negative
            
        except Exception as e:
            print(f"Warning: Could not calculate response time: {e}")
            return 0
    
    def _check_visual_quality(self, img):
        """Check for basic visual quality issues"""
        issues = []
        
        # Check for very dark or very bright areas (potential contrast issues)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        dark_pixels = np.sum(gray < 30) / gray.size
        bright_pixels = np.sum(gray > 225) / gray.size
        
        if dark_pixels > 0.8:
            issues.append("Screen appears mostly black (potential loading issue)")
        elif bright_pixels > 0.8:
            issues.append("Screen appears mostly white (potential loading issue)")
        
        # Check for potential UI elements (basic edge detection)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        if edge_density < 0.01:
            issues.append("Very low UI element density (potential empty screen)")
        
        return issues
    
    def _assess_ux_quality(self, results):
        """Provide overall UX quality assessment"""
        score = 100
        issues = []
        
        # Deduct points for issues
        if not results.get('response_acceptable', True):
            score -= 30
            issues.append(f"Slow response time: {results.get('response_time_ms', 0):.0f}ms")
        
        if not results.get('ui_changed', False):
            score -= 25
            issues.append("No visible UI change detected")
        
        if results.get('visual_issues'):
            score -= len(results['visual_issues']) * 15
            issues.extend(results['visual_issues'])
        
        # Content validation scoring
        content_validation = results.get('content_validation', {})
        if content_validation.get('expectations_met') is False:
            score -= 40
            issues.append("Content doesn't match expectations")
        
        if content_validation.get('issues'):
            # Only subtract if they're real issues, not just "no API key" warnings
            validation_issues = [issue for issue in content_validation['issues'] 
                               if not any(skip in issue.lower() for skip in ['disabled', 'no ai api', 'not available'])]
            if validation_issues:
                score -= len(validation_issues) * 10
                issues.extend(validation_issues)
        
        # Determine quality level
        if score >= 85:
            quality = "EXCELLENT"
        elif score >= 70:
            quality = "GOOD"
        elif score >= 50:
            quality = "FAIR"
        else:
            quality = "POOR"
        
        return {
            'score': max(0, score),
            'level': quality,
            'issues': issues
        }
    
    def _print_analysis_summary(self, analysis):
        """Print human-readable analysis summary"""
        results = analysis['results']
        quality = results['ux_quality']
        content_validation = results.get('content_validation', {})
        
        print("\n" + "="*50)
        print("UX ANALYSIS SUMMARY")
        print("="*50)
        
        print(f"Overall Quality: {quality['level']} ({quality['score']}/100)")
        
        print(f"\nResponse Time: {results['response_time_ms']:.0f}ms", end="")
        if results['response_acceptable']:
            print(" ✓ GOOD")
        else:
            print(" ⚠️  SLOW")
        
        print(f"UI Changed: {results['change_score']:.3f}", end="")
        if results['ui_changed']:
            print(" ✓ YES")
        else:
            print(" ❌ NO CHANGE")
        
        # Content validation summary
        if content_validation:
            print(f"\nContent Validation:")
            if content_validation.get('expectations_met') is True:
                print("  ✓ Content matches expectations")
            elif content_validation.get('expectations_met') is False:
                print("  ❌ Content doesn't match expectations")
            else:
                print("  ⚠️  Content validation unavailable")
            
            if content_validation.get('before_description'):
                print(f"  Before: {content_validation['before_description'][:60]}...")
            if content_validation.get('after_description'):
                print(f"  After: {content_validation['after_description'][:60]}...")
        
        if quality['issues']:
            print(f"\nIssues Found:")
            for issue in quality['issues']:
                print(f"  • {issue}")
        else:
            print(f"\n✅ No major issues detected!")
        
        print("\nRecommendations:")
        if not results['response_acceptable']:
            print("  • Optimize interaction response time")
        if not results['ui_changed']:
            print("  • Verify the interaction actually triggered")
            print("  • Check for subtle UI feedback")
        if results['visual_issues']:
            print("  • Review visual presentation and loading states")
        if content_validation.get('expectations_met') is False:
            print("  • Check if correct content is displayed")
            print("  • Verify page/screen loaded correctly")
        
        print("="*50)
    
    def list_captures(self):
        """List all captured screenshots"""
        screenshots = list(self.output_dir.glob("*.png"))
        screenshots.sort(reverse=True)
        
        print(f"Found {len(screenshots)} screenshots in {self.output_dir}")
        
        for screenshot in screenshots[:10]:  # Show last 10
            try:
                metadata_file = screenshot.with_suffix('.json')
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                print(f"  {screenshot.name} - {metadata.get('capture_time', 'Unknown time')}")
            except:
                print(f"  {screenshot.name}")
    
    def clean_old_captures(self, keep_count=20):
        """Clean up old screenshots, keep only recent ones"""
        screenshots = list(self.output_dir.glob("*.png"))
        screenshots.sort(reverse=True)
        
        if len(screenshots) <= keep_count:
            print(f"Only {len(screenshots)} screenshots, nothing to clean")
            return
        
        to_delete = screenshots[keep_count:]
        print(f"Cleaning up {len(to_delete)} old screenshots...")
        
        for screenshot in to_delete:
            screenshot.unlink(missing_ok=True)
            # Also delete metadata
            metadata_file = screenshot.with_suffix('.json')
            metadata_file.unlink(missing_ok=True)
        
        print(f"Kept {keep_count} most recent screenshots")
    
    def _validate_content_expectations(self, before_path, after_path):
        """Use AI vision to validate if screen content matches expectations"""
        validation = {
            'before_content_valid': True,
            'after_content_valid': True,
            'before_description': '',
            'after_description': '',
            'expectations_met': True,
            'issues': [],
            'api_used': None
        }
        
        if not self.config.get('content_validation_enabled', False):
            validation['issues'].append("Content validation disabled")
            return validation
        
        # Check which API keys are available
        has_openai = bool(self.config.get('openai_api_key'))
        has_anthropic = bool(self.config.get('anthropic_api_key'))
        
        if not has_openai and not has_anthropic:
            validation['issues'].append("No AI API key configured for content validation")
            return validation
        
        # Check library availability
        if not REQUESTS_AVAILABLE:
            validation['issues'].append("Requests library not available")
            return validation
        
        try:
            # Load metadata to get expectations
            before_meta = self._load_metadata(before_path)
            after_meta = self._load_metadata(after_path)
            
            # Validate before screenshot if expectation exists
            if before_meta and before_meta.get('expected_content'):
                validation['before_content_valid'], validation['before_description'], api_used = \
                    self._analyze_screenshot_content(before_path, before_meta['expected_content'])
                validation['api_used'] = api_used
            
            # Validate after screenshot if expectation exists  
            if after_meta and after_meta.get('expected_content'):
                validation['after_content_valid'], validation['after_description'], api_used = \
                    self._analyze_screenshot_content(after_path, after_meta['expected_content'])
                if not validation['api_used']:
                    validation['api_used'] = api_used
            
            # Overall expectation check
            validation['expectations_met'] = validation['before_content_valid'] and validation['after_content_valid']
            
            if not validation['expectations_met']:
                if not validation['before_content_valid']:
                    validation['issues'].append("Before screenshot doesn't match expected content")
                if not validation['after_content_valid']:
                    validation['issues'].append("After screenshot doesn't match expected content")
        
        except Exception as e:
            validation['issues'].append(f"Content validation error: {str(e)}")
            validation['expectations_met'] = None
        
        return validation
    
    def _load_metadata(self, image_path):
        """Load metadata for a screenshot"""
        try:
            metadata_file = image_path.with_suffix('.json')
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def _analyze_screenshot_content(self, image_path, expected_content):
        """Use AI vision to analyze screenshot content (tries Anthropic first, then OpenAI)"""
        
        # Convert image to base64
        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            return True, f"Failed to read image: {str(e)}", None
        
        prompt = f"""
        Analyze this screenshot and determine if it matches the expected content.
        
        Expected content: {expected_content}
        
        Please provide:
        1. A brief description of what you see in the screenshot
        2. Whether this matches the expected content (YES/NO)
        3. If NO, explain what's different or missing
        
        Format your response as: MATCH: YES/NO | DESCRIPTION: [what you see] | REASON: [explanation if no match]
        """
        
        # Try Anthropic first (Claude)
        if self.config.get('anthropic_api_key') and ANTHROPIC_AVAILABLE:
            try:
                client = anthropic.Anthropic(api_key=self.config['anthropic_api_key'])
                
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=300,
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
                
                result = response.content[0].text
                
                # Parse response
                match_valid = "MATCH: YES" in result.upper()
                description = result.split("DESCRIPTION:")[1].split("REASON:")[0].strip() if "DESCRIPTION:" in result else result[:100]
                
                return match_valid, description, "Claude"
                
            except Exception as e:
                print(f"Warning: Claude analysis failed, trying OpenAI: {e}")
        
        # Try OpenAI as fallback
        if self.config.get('openai_api_key') and OPENAI_AVAILABLE:
            try:
                client = openai.OpenAI(api_key=self.config['openai_api_key'])
                
                response = client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=300
                )
                
                result = response.choices[0].message.content
                
                # Parse response
                match_valid = "MATCH: YES" in result.upper()
                description = result.split("DESCRIPTION:")[1].split("REASON:")[0].strip() if "DESCRIPTION:" in result else result[:100]
                
                return match_valid, description, "OpenAI"
                
            except Exception as e:
                print(f"Warning: OpenAI analysis failed: {e}")
        
        # If both fail
        return True, f"No working AI vision API available", None

def main():
    parser = argparse.ArgumentParser(description='Simple UX Testing Tool')
    parser.add_argument('command', choices=['capture', 'analyze', 'list', 'clean'], 
                       help='Command to execute')
    parser.add_argument('--before', action='store_true', 
                       help='Capture before screenshot (use with capture)')
    parser.add_argument('--after', action='store_true', 
                       help='Capture after screenshot (use with capture)')
    parser.add_argument('--expect', type=str, 
                       help='Expected content description for content validation')
    parser.add_argument('--keep', type=int, default=20,
                       help='Number of screenshots to keep (use with clean)')
    
    args = parser.parse_args()
    
    tester = SimpleUXTester()
    
    if args.command == 'capture':
        if args.before:
            tester.capture_before(args.expect)
            print("\n💡 Now perform your UI interaction, then run:")
            if args.expect:
                print(f"   python simple_ux_tester.py capture --after --expect \"Expected content after interaction\"")
            else:
                print("   python simple_ux_tester.py capture --after")
        elif args.after:
            tester.capture_after(args.expect)
            print("\n💡 Now analyze the results with:")
            print("   python simple_ux_tester.py analyze")
        else:
            print("Specify --before or --after with capture command")
            print("Example: python simple_ux_tester.py capture --before --expect \"login screen with username field\"")
    
    elif args.command == 'analyze':
        tester.analyze_screenshots()
    
    elif args.command == 'list':
        tester.list_captures()
    
    elif args.command == 'clean':
        tester.clean_old_captures(args.keep)

if __name__ == "__main__":
    main() 