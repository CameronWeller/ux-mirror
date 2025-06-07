#!/usr/bin/env python3
"""
UX-MIRROR Report Generator
Generates comprehensive UX analysis reports in multiple formats
"""

import json
import os
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class UXReportGenerator:
    """Generates comprehensive UX analysis reports"""
    
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different report types
        (self.reports_dir / "html").mkdir(exist_ok=True)
        (self.reports_dir / "json").mkdir(exist_ok=True)
        (self.reports_dir / "screenshots").mkdir(exist_ok=True)
    
    def generate_comprehensive_report(self, 
                                    analysis_data: Dict[str, Any],
                                    screenshot_path: Optional[str] = None,
                                    app_context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Generate a comprehensive UX report in multiple formats
        
        Args:
            analysis_data: AI analysis results
            screenshot_path: Path to the screenshot analyzed
            app_context: Application context information
            
        Returns:
            Dictionary with paths to generated reports
        """
        timestamp = datetime.now()
        report_id = f"ux_analysis_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Prepare report data
        report_data = self._prepare_report_data(analysis_data, app_context, timestamp)
        
        # Copy screenshot to reports folder if provided
        screenshot_report_path = None
        if screenshot_path and os.path.exists(screenshot_path):
            screenshot_report_path = self._copy_screenshot(screenshot_path, report_id)
            report_data['screenshot_path'] = str(screenshot_report_path)
        
        # Generate reports
        report_paths = {}
        
        # JSON Report (detailed data)
        json_path = self._generate_json_report(report_data, report_id)
        report_paths['json'] = str(json_path)
        
        # HTML Report (visual presentation)
        html_path = self._generate_html_report(report_data, report_id)
        report_paths['html'] = str(html_path)
        
        logger.info(f"Generated UX analysis report: {report_id}")
        return report_paths
    
    def _prepare_report_data(self, analysis_data: Dict[str, Any], 
                           app_context: Optional[Dict[str, Any]], 
                           timestamp: datetime) -> Dict[str, Any]:
        """Prepare structured report data"""
        return {
            "report_metadata": {
                "generated_at": timestamp.isoformat(),
                "report_version": "2.0",
                "tool": "UX-MIRROR",
                "analysis_type": "comprehensive_ux_audit"
            },
            "application_context": app_context or {},
            "analysis_results": analysis_data,
            "summary": self._generate_executive_summary(analysis_data),
            "recommendations": self._extract_prioritized_recommendations(analysis_data),
            "accessibility_audit": self._extract_accessibility_findings(analysis_data),
            "technical_metrics": self._extract_technical_metrics(analysis_data)
        }
    
    def _copy_screenshot(self, screenshot_path: str, report_id: str) -> Path:
        """Copy screenshot to reports folder"""
        import shutil
        
        screenshot_ext = Path(screenshot_path).suffix
        target_path = self.reports_dir / "screenshots" / f"{report_id}{screenshot_ext}"
        shutil.copy2(screenshot_path, target_path)
        return target_path
    
    def _generate_json_report(self, report_data: Dict[str, Any], report_id: str) -> Path:
        """Generate detailed JSON report"""
        json_path = self.reports_dir / "json" / f"{report_id}.json"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        return json_path
    
    def _generate_html_report(self, report_data: Dict[str, Any], report_id: str) -> Path:
        """Generate visual HTML report"""
        html_path = self.reports_dir / "html" / f"{report_id}.html"
        
        html_content = self._build_html_content(report_data, report_id)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path
    
    def _build_html_content(self, report_data: Dict[str, Any], report_id: str) -> str:
        """Build comprehensive HTML report content"""
        
        # Extract data
        metadata = report_data.get('report_metadata', {})
        context = report_data.get('application_context', {})
        analysis = report_data.get('analysis_results', {})
        summary = report_data.get('summary', {})
        recommendations = report_data.get('recommendations', [])
        accessibility = report_data.get('accessibility_audit', {})
        
        # Build screenshot section
        screenshot_section = ""
        if 'screenshot_path' in report_data:
            screenshot_rel_path = f"../screenshots/{Path(report_data['screenshot_path']).name}"
            screenshot_section = f"""
            <div class="screenshot-section">
                <h2>📸 Analyzed Screenshot</h2>
                <img src="{screenshot_rel_path}" alt="Analyzed Screenshot" class="screenshot">
            </div>
            """
        
        # Build recommendations HTML
        recommendations_html = ""
        for i, rec in enumerate(recommendations[:10], 1):  # Top 10 recommendations
            priority_class = {1: "high", 2: "medium", 3: "medium"}.get(rec.get('priority', 3), "low")
            recommendations_html += f"""
            <div class="recommendation {priority_class}">
                <div class="rec-header">
                    <span class="priority">Priority {rec.get('priority', '?')}</span>
                    <span class="category">{rec.get('category', 'General')}</span>
                </div>
                <h4>{rec.get('action', 'No action specified')}</h4>
                <p><strong>Impact:</strong> {rec.get('expected_impact', 'Unknown')}</p>
                <p><strong>Complexity:</strong> {rec.get('implementation_complexity', 'Unknown')}</p>
                <div class="metrics">
                    <strong>Success Metrics:</strong> {', '.join(rec.get('success_metrics', ['Not specified']))}
                </div>
            </div>
            """
        
        # Build accessibility issues HTML
        accessibility_html = ""
        if isinstance(accessibility, dict):
            contrast_issues = accessibility.get('contrast_issues', [])
            for issue in contrast_issues[:5]:  # Top 5 contrast issues
                severity_class = issue.get('severity', 'medium')
                accessibility_html += f"""
                <div class="accessibility-issue {severity_class}">
                    <strong>Location:</strong> {issue.get('location', 'Unknown')}<br>
                    <strong>Contrast Ratio:</strong> {issue.get('contrast_ratio', 'Unknown')}<br>
                    <strong>Severity:</strong> {issue.get('severity', 'Unknown')}<br>
                    <span class="color-sample" style="background: {issue.get('foreground_color', '#000')}; color: {issue.get('background_color', '#fff')}">Sample</span>
                </div>
                """
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UX Analysis Report - {report_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; 
            color: #333; 
            background: #f8f9fa;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{ color: #2c3e50; border-bottom: 3px solid #667eea; padding-bottom: 10px; margin-bottom: 20px; }}
        .metadata {{ background: #f8f9fa; padding: 20px; border-radius: 6px; margin-bottom: 30px; }}
        .metadata-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .metadata-item {{ background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #667eea; }}
        .metadata-item strong {{ color: #2c3e50; display: block; margin-bottom: 5px; }}
        .score-card {{ display: inline-block; background: #667eea; color: white; padding: 15px 25px; border-radius: 50px; margin: 10px; text-align: center; min-width: 120px; }}
        .score-card .score {{ font-size: 2em; font-weight: bold; display: block; }}
        .score-card .label {{ font-size: 0.9em; opacity: 0.9; }}
        .recommendation {{ border: 1px solid #e9ecef; border-radius: 6px; padding: 20px; margin-bottom: 15px; }}
        .recommendation.high {{ border-left: 5px solid #dc3545; background: #fff5f5; }}
        .recommendation.medium {{ border-left: 5px solid #ffc107; background: #fffbf0; }}
        .recommendation.low {{ border-left: 5px solid #28a745; background: #f8fff9; }}
        .rec-header {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
        .priority {{ background: #667eea; color: white; padding: 4px 12px; border-radius: 4px; font-size: 0.9em; }}
        .category {{ background: #e9ecef; padding: 4px 12px; border-radius: 4px; font-size: 0.9em; }}
        .metrics {{ background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; }}
        .accessibility-issue {{ border: 1px solid #e9ecef; padding: 15px; margin-bottom: 10px; border-radius: 6px; }}
        .accessibility-issue.high {{ border-left: 5px solid #dc3545; }}
        .accessibility-issue.medium {{ border-left: 5px solid #ffc107; }}
        .accessibility-issue.low {{ border-left: 5px solid #28a745; }}
        .color-sample {{ display: inline-block; padding: 5px 10px; margin-left: 10px; border-radius: 4px; font-size: 0.8em; }}
        .screenshot {{ max-width: 100%; height: auto; border: 1px solid #e9ecef; border-radius: 6px; }}
        .screenshot-section {{ text-align: center; margin: 30px 0; }}
        .footer {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        @media (max-width: 768px) {{
            .container {{ margin: 10px; }}
            .content {{ padding: 20px; }}
            .header {{ padding: 20px; }}
            .header h1 {{ font-size: 2em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>UX Analysis Report</h1>
            <p>Comprehensive User Experience Audit</p>
            <p><em>Generated on {metadata.get('generated_at', 'Unknown')}</em></p>
        </div>
        
        <div class="content">
            <!-- Application Context -->
            <div class="section">
                <h2>Application Context</h2>
                <div class="metadata">
                    <div class="metadata-grid">
                        <div class="metadata-item">
                            <strong>Application Type</strong>
                            {context.get('app_type', 'Not specified')}
                        </div>
                        <div class="metadata-item">
                            <strong>Platform</strong>
                            {context.get('platform', 'Not specified')}
                        </div>
                        <div class="metadata-item">
                            <strong>Resolution</strong>
                            {context.get('resolution', 'Not specified')}
                        </div>
                        <div class="metadata-item">
                            <strong>Use Case</strong>
                            {context.get('use_case', 'Not specified')}
                        </div>
                        <div class="metadata-item">
                            <strong>Analysis Iteration</strong>
                            {context.get('iteration', 'Not specified')}
                        </div>
                        <div class="metadata-item">
                            <strong>User Demographics</strong>
                            {context.get('user_demographics', 'Not specified')}
                        </div>
                    </div>
                </div>
            </div>
            
            {screenshot_section}
            
            <!-- Executive Summary -->
            <div class="section">
                <h2>Executive Summary</h2>
                <div class="grid">
                    <div class="score-card">
                        <span class="score">{analysis.get('overall_assessment', {}).get('quality_score', 0.0):.1f}</span>
                        <span class="label">Overall Quality</span>
                    </div>
                    <div class="score-card">
                        <span class="score">{analysis.get('accessibility_audit', {}).get('accessibility_score', 0.0):.1f}</span>
                        <span class="label">Accessibility</span>
                    </div>
                    <div class="score-card">
                        <span class="score">{analysis.get('usability_analysis', {}).get('interaction_score', 0.0):.1f}</span>
                        <span class="label">Usability</span>
                    </div>
                    <div class="score-card">
                        <span class="score">{analysis.get('visual_hierarchy', {}).get('score', 0.0):.1f}</span>
                        <span class="label">Visual Hierarchy</span>
                    </div>
                </div>
                <p style="margin-top: 20px; font-size: 1.1em; line-height: 1.8;">
                    {analysis.get('overall_assessment', {}).get('executive_summary', 'No executive summary available.')}
                </p>
            </div>
            
            <!-- Priority Recommendations -->
            <div class="section">
                <h2>Priority Recommendations</h2>
                {recommendations_html or '<p>No specific recommendations available.</p>'}
            </div>
            
            <!-- Accessibility Audit -->
            <div class="section">
                <h2>Accessibility Audit</h2>
                <div class="metadata">
                    <p><strong>WCAG Compliance Estimate:</strong> {analysis.get('accessibility_audit', {}).get('wcag_compliance_estimate', 'Unknown')}</p>
                    <p><strong>Overall Accessibility Score:</strong> {analysis.get('accessibility_audit', {}).get('accessibility_score', 0.0):.1f}/1.0</p>
                </div>
                <h3>Color Contrast Issues</h3>
                {accessibility_html or '<p>No specific accessibility issues identified.</p>'}
            </div>
            
            <!-- Detailed Analysis -->
            <div class="section">
                <h2>Detailed Findings</h2>
                <div class="metadata">
                    <h3>Analysis Breakdown</h3>
                    <p><strong>Visual Hierarchy Score:</strong> {analysis.get('visual_hierarchy', {}).get('score', 0.0):.1f}/1.0</p>
                    <p><strong>Usability Score:</strong> {analysis.get('usability_analysis', {}).get('interaction_score', 0.0):.1f}/1.0</p>
                    <p><strong>Typography Assessment:</strong> {analysis.get('typography_analysis', {}).get('readability_score', 0.0):.1f}/1.0</p>
                    <p><strong>Responsive Design:</strong> {analysis.get('responsive_design', {}).get('layout_consistency', 0.0):.1f}/1.0</p>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by UX-MIRROR v2.0 | Report ID: {report_id}</p>
            <p>For technical details, see the accompanying JSON report</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
    
    def _generate_executive_summary(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary from analysis data"""
        return {
            "overall_quality": analysis_data.get('overall_assessment', {}).get('quality_score', 0.0),
            "critical_issues": analysis_data.get('overall_assessment', {}).get('critical_issues_count', 0),
            "summary": analysis_data.get('overall_assessment', {}).get('executive_summary', '')
        }
    
    def _extract_prioritized_recommendations(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and prioritize recommendations"""
        recommendations = analysis_data.get('prioritized_recommendations', [])
        if isinstance(recommendations, list):
            return sorted(recommendations, key=lambda x: x.get('priority', 999))[:10]
        return []
    
    def _extract_accessibility_findings(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract accessibility audit findings"""
        return analysis_data.get('accessibility_audit', {})
    
    def _extract_technical_metrics(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical UX metrics"""
        return {
            "visual_hierarchy": analysis_data.get('visual_hierarchy', {}),
            "usability": analysis_data.get('usability_analysis', {}),
            "typography": analysis_data.get('typography_analysis', {}),
            "responsive_design": analysis_data.get('responsive_design', {})
        }

def create_sample_report():
    """Create a sample report for testing"""
    
    # Sample analysis data (what would come from improved AI analysis)
    sample_analysis = {
        "analysis_metadata": {
            "timestamp": datetime.now().isoformat(),
            "app_type": "desktop application",
            "analysis_version": "v2.0_comprehensive"
        },
        "overall_assessment": {
            "quality_score": 0.7,
            "confidence_level": 0.9,
            "executive_summary": "The application shows good visual hierarchy but has several accessibility issues that need immediate attention. The interface is generally usable but could benefit from improved contrast ratios and better button sizing.",
            "critical_issues_count": 3
        },
        "visual_hierarchy": {
            "score": 0.8,
            "primary_focus_clear": True,
            "information_grouping": "good",
            "whitespace_usage": "adequate",
            "issues": ["Some elements compete for attention", "Call-to-action could be more prominent"]
        },
        "usability_analysis": {
            "interaction_score": 0.75,
            "target_sizes_adequate": False,
            "feedback_mechanisms": ["Loading indicators", "Button hover states"],
            "consistency_score": 0.8,
            "critical_usability_issues": ["Small touch targets", "Inconsistent navigation patterns"]
        },
        "accessibility_audit": {
            "wcag_compliance_estimate": "A",
            "contrast_issues": [
                {
                    "location": "Main navigation text",
                    "foreground_color": "#666666",
                    "background_color": "#ffffff",
                    "contrast_ratio": 3.2,
                    "severity": "high"
                },
                {
                    "location": "Secondary buttons",
                    "foreground_color": "#999999",
                    "background_color": "#f0f0f0",
                    "contrast_ratio": 2.1,
                    "severity": "medium"
                }
            ],
            "text_scaling_issues": ["Text becomes unreadable at 200% zoom"],
            "focus_visibility": "Poor - no visible focus indicators",
            "accessibility_score": 0.4
        },
        "prioritized_recommendations": [
            {
                "priority": 1,
                "category": "Accessibility",
                "action": "Increase color contrast for navigation text to meet WCAG AA standards",
                "expected_impact": "high",
                "implementation_complexity": "low",
                "success_metrics": ["Contrast ratio > 4.5:1", "Improved accessibility score"]
            },
            {
                "priority": 2,
                "category": "Usability",
                "action": "Increase button sizes to minimum 44px touch targets",
                "expected_impact": "medium",
                "implementation_complexity": "medium",
                "success_metrics": ["Reduced misclick rate", "Improved mobile usability"]
            },
            {
                "priority": 3,
                "category": "Visual Design",
                "action": "Add visible focus indicators for keyboard navigation",
                "expected_impact": "high",
                "implementation_complexity": "low",
                "success_metrics": ["WCAG compliance", "Better keyboard accessibility"]
            }
        ]
    }
    
    sample_context = {
        "app_type": "desktop application",
        "platform": "Windows 11",
        "resolution": "1920x1080",
        "user_demographics": "productivity users",
        "use_case": "document editing",
        "iteration": 1
    }
    
    # Generate sample report
    generator = UXReportGenerator()
    report_paths = generator.generate_comprehensive_report(
        analysis_data=sample_analysis,
        app_context=sample_context
    )
    
    print("Sample UX report generated:")
    for format_type, path in report_paths.items():
        print(f"  {format_type.upper()}: {path}")
    
    return report_paths

if __name__ == "__main__":
    create_sample_report() 