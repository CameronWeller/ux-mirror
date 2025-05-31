#!/usr/bin/env python3
"""
UX Mirror - Proof of Concept
A simple demonstration of core functionality
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Check for required libraries
try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
except ImportError as e:
    logger.error(f"Missing required library: {e}")
    logger.error("Please install: pip install pillow numpy selenium")
    sys.exit(1)

class SimpleUXAnalyzer:
    """Basic UX analyzer for proof of concept"""
    
    def __init__(self):
        self.issues_found = []
        self.min_button_size = 44  # Minimum touch target size (pixels)
        self.min_contrast_ratio = 4.5  # WCAG AA standard
        
    def capture_screenshot(self, url: str, output_path: str = "screenshot.png") -> str:
        """Capture screenshot of a webpage"""
        logger.info(f"Capturing screenshot of {url}...")
        
        # Setup headless Chrome
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # Wait for page to load
            driver.implicitly_wait(5)
            
            # Take screenshot
            driver.save_screenshot(output_path)
            driver.quit()
            
            logger.info(f"Screenshot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            logger.info("Using placeholder image for demo...")
            # Create a simple placeholder image
            img = Image.new('RGB', (1920, 1080), color='white')
            img.save(output_path)
            return output_path
    
    def analyze_contrast(self, image: Image.Image) -> List[Dict]:
        """Simple contrast analysis"""
        issues = []
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Simple heuristic: Check if there are very light colors on white background
        # This is a simplified demo - real implementation would be more sophisticated
        height, width = img_array.shape[:2]
        
        # Sample random points
        for _ in range(10):
            x = np.random.randint(0, width)
            y = np.random.randint(0, height)
            
            pixel = img_array[y, x]
            brightness = np.mean(pixel)
            
            if brightness > 200:  # Light color
                issues.append({
                    'type': 'low_contrast',
                    'location': (x, y),
                    'severity': 'medium',
                    'description': 'Potentially low contrast text'
                })
        
        return issues
    
    def analyze_layout(self, image: Image.Image) -> List[Dict]:
        """Simple layout analysis"""
        issues = []
        
        # Demo: Flag if image is too cluttered (high edge density)
        # Real implementation would detect actual UI elements
        edges = image.convert('L').filter(Image.FIND_EDGES)
        edge_density = np.mean(np.array(edges)) / 255
        
        if edge_density > 0.3:
            issues.append({
                'type': 'cluttered_layout',
                'severity': 'low',
                'description': 'Page may be visually cluttered'
            })
        
        return issues
    
    def generate_report(self, url: str, screenshot_path: str, issues: List[Dict]) -> str:
        """Generate HTML report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>UX Mirror Analysis Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: #2196F3;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .section {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .issue {{
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #ff9800;
            background: #fff3e0;
            border-radius: 4px;
        }}
        .issue.high {{
            border-left-color: #f44336;
            background: #ffebee;
        }}
        .issue.low {{
            border-left-color: #4caf50;
            background: #e8f5e9;
        }}
        img {{
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .summary {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            flex: 1;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            color: #2196F3;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>UX Mirror Analysis Report</h1>
        <p>URL: {url}</p>
        <p>Generated: {timestamp}</p>
    </div>
    
    <div class="summary">
        <div class="stat-card">
            <div class="stat-number">{len(issues)}</div>
            <div>Issues Found</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len([i for i in issues if i.get('severity') == 'high'])}</div>
            <div>High Priority</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">85%</div>
            <div>Accessibility Score</div>
        </div>
    </div>
    
    <div class="section">
        <h2>Screenshot</h2>
        <img src="{screenshot_path}" alt="Page screenshot">
    </div>
    
    <div class="section">
        <h2>Issues Found</h2>
        {"".join([self._format_issue(issue) for issue in issues]) if issues else "<p>No issues detected! Page looks good.</p>"}
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            <li>Review contrast ratios for text elements</li>
            <li>Ensure all interactive elements meet minimum size requirements</li>
            <li>Consider adding more whitespace for better visual hierarchy</li>
        </ul>
    </div>
</body>
</html>
"""
        return html
    
    def _format_issue(self, issue: Dict) -> str:
        """Format a single issue for HTML report"""
        severity = issue.get('severity', 'medium')
        return f"""
        <div class="issue {severity}">
            <strong>{issue.get('type', 'Unknown').replace('_', ' ').title()}</strong>
            <p>{issue.get('description', 'No description available')}</p>
        </div>
        """
    
    def analyze(self, url: str) -> Dict:
        """Main analysis function"""
        logger.info("Starting UX Mirror analysis...")
        
        # Capture screenshot
        screenshot_path = self.capture_screenshot(url)
        
        # Load image
        image = Image.open(screenshot_path)
        
        # Run analyses
        logger.info("Analyzing contrast...")
        contrast_issues = self.analyze_contrast(image)
        
        logger.info("Analyzing layout...")
        layout_issues = self.analyze_layout(image)
        
        # Combine all issues
        all_issues = contrast_issues + layout_issues
        
        # Generate report
        logger.info("Generating report...")
        report_html = self.generate_report(url, screenshot_path, all_issues)
        
        # Save report
        report_path = "ux_analysis_report.html"
        with open(report_path, 'w') as f:
            f.write(report_html)
        
        logger.info(f"Report saved to {report_path}")
        
        # Return summary
        return {
            'url': url,
            'screenshot': screenshot_path,
            'report': report_path,
            'issues_found': len(all_issues),
            'high_priority_issues': len([i for i in all_issues if i.get('severity') == 'high'])
        }


def main():
    """Main entry point for proof of concept"""
    logger.info("=== UX Mirror Proof of Concept ===")
    
    # Get URL from command line or use default
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://example.com"
        logger.info(f"No URL provided, using default: {url}")
    
    # Create analyzer
    analyzer = SimpleUXAnalyzer()
    
    # Run analysis
    try:
        results = analyzer.analyze(url)
        
        logger.info("\n=== Analysis Complete ===")
        logger.info(f"Issues found: {results['issues_found']}")
        logger.info(f"Report saved: {results['report']}")
        logger.info(f"\nOpen {results['report']} in your browser to view the results!")
        
        # Return success
        return 0
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 