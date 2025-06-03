#!/usr/bin/env python3
"""
UX-MIRROR Simple POC: Lightweight UX Analysis Demo
==================================================

This script demonstrates core UX analysis capabilities with minimal dependencies.
Implements Phase 1 deliverables from the roadmap:
- Screenshot analysis
- Basic element detection
- Simple JSON report generation
- HTML report with annotations

Author: UX-MIRROR Team
"""

import os
import json
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import logging
import base64
from pathlib import Path
from advanced_ux_heuristics import AdvancedUXAnalyzer, analyze_image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleUXAnalyzer:
    """Simple UX analyzer with minimal dependencies"""
    
    def __init__(self):
        self.output_dir = Path("ux_analysis_results")
        self.output_dir.mkdir(exist_ok=True)
        self.advanced_analyzer = AdvancedUXAnalyzer()
        
    def analyze_screenshot(self, image_path_or_url):
        """Analyze a screenshot and generate reports"""
        logger.info(f"Starting analysis of: {image_path_or_url}")
        
        # Load image
        if image_path_or_url.startswith(('http://', 'https://')):
            response = requests.get(image_path_or_url)
            img = Image.open(BytesIO(response.content))
        else:
            img = Image.open(image_path_or_url)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Basic analysis
        analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "source": str(image_path_or_url),
            "dimensions": {"width": img.width, "height": img.height},
            "detected_elements": [],
            "ux_issues": []
        }
        
        # Use advanced heuristics for analysis
        issues = analyze_image(img)
        
        # Convert issues to analysis format
        analysis_results["ux_issues"] = [
            {
                "type": issue.type,
                "severity": issue.severity,
                "description": issue.description,
                "location": issue.location,
                "fix": issue.fix,
                "confidence": issue.confidence,
                "metrics": issue.metrics
            }
            for issue in issues
        ]
        
        # Generate reports
        json_path = self._generate_json_report(analysis_results)
        html_path = self._generate_html_report(img, analysis_results)
        
        logger.info(f"Analysis complete! Results saved to:")
        logger.info(f"  - JSON: {json_path}")
        logger.info(f"  - HTML: {html_path}")
        
        return analysis_results
        
    def _generate_json_report(self, results):
        """Generate JSON report"""
        filename = f"ux_analysis_{int(time.time())}.json"
        path = self.output_dir / filename
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
            
        return path
        
    def _generate_html_report(self, img, results):
        """Generate HTML report with annotated screenshot"""
        # Create annotated image
        annotated = img.copy()
        draw = ImageDraw.Draw(annotated)
        
        # Draw issue markers
        for issue in results["ux_issues"]:
            location = issue["location"]
            x, y = location["x"], location["y"]
            
            # Choose color based on severity
            colors = {
                "high": "red",
                "medium": "orange",
                "low": "yellow"
            }
            color = colors.get(issue["severity"], "gray")
            
            # Draw marker
            draw.ellipse([x-5, y-5, x+5, y+5], fill=color)
            
            # Add label
            draw.text((x+10, y-10), issue["type"], fill=color)
        
        # Save annotated image
        img_filename = f"annotated_{int(time.time())}.png"
        img_path = self.output_dir / img_filename
        annotated.save(img_path)
        
        # Convert to base64 for embedding
        buffered = BytesIO()
        annotated.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Generate HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>UX Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; }}
        .section {{ margin: 20px 0; }}
        .issue {{ background: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .high {{ border-left: 5px solid #dc3545; }}
        .medium {{ border-left: 5px solid #ffc107; }}
        .low {{ border-left: 5px solid #28a745; }}
        .stats {{ display: flex; gap: 20px; }}
        .stat-box {{ background: #e9ecef; padding: 15px; border-radius: 5px; }}
        img {{ max-width: 100%; height: auto; }}
        .metrics {{ font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>UX Analysis Report</h1>
        <p>Generated: {results['timestamp']}</p>
        <p>Source: {results['source']}</p>
    </div>
    
    <div class="section">
        <h2>Summary Statistics</h2>
        <div class="stats">
            <div class="stat-box">
                <h3>{len(results['ux_issues'])}</h3>
                <p>UX Issues Found</p>
            </div>
            <div class="stat-box">
                <h3>{results['dimensions']['width']}x{results['dimensions']['height']}</h3>
                <p>Resolution</p>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>Annotated Screenshot</h2>
        <img src="data:image/png;base64,{img_base64}" alt="Annotated screenshot">
    </div>
    
    <div class="section">
        <h2>UX Issues</h2>
        {"".join([f'''
        <div class="issue {issue['severity']}">
            <h3>{issue['type'].title()} Issue</h3>
            <p><strong>Description:</strong> {issue['description']}</p>
            <p><strong>Severity:</strong> {issue['severity'].upper()}</p>
            <p><strong>Recommended Fix:</strong> {issue['fix']}</p>
            {f"<p class='metrics'><strong>Metrics:</strong> {json.dumps(issue['metrics'], indent=2)}</p>" if issue.get('metrics') else ""}
        </div>
        ''' for issue in results['ux_issues']])}
    </div>
</body>
</html>
"""
        
        # Save HTML report
        html_filename = f"ux_report_{int(time.time())}.html"
        html_path = self.output_dir / html_filename
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return html_path

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="UX-MIRROR Simple POC")
    parser.add_argument("image", help="Path or URL to screenshot")
    args = parser.parse_args()
    
    analyzer = SimpleUXAnalyzer()
    analyzer.analyze_screenshot(args.image)

if __name__ == "__main__":
    main() 