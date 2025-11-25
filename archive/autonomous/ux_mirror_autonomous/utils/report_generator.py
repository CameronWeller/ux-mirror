#!/usr/bin/env python3
"""
Report Generator for UX-MIRROR Autonomous Testing
Phase 2: Input Automation System

Generates comprehensive test reports in multiple formats.
"""

import json
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates comprehensive test reports in multiple formats"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.base_path = Path(__file__).parent.parent
        self.reports_dir = self.base_path / "test_results" / "reports"
        self.templates_dir = self.base_path / "templates" / "reports"
        
        # Create directories
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("ReportGenerator initialized")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default report configuration"""
        return {
            "generate_html_report": True,
            "generate_json_report": True,
            "generate_csv_metrics": True,
            "include_screenshots": True,
            "include_performance_graphs": False,  # Would require matplotlib
            "include_error_details": True
        }
    
    def generate_full_report(self, results: Dict[str, Any], session_id: str) -> str:
        """Generate a comprehensive report in all configured formats"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = f"autonomous_test_report_{session_id}_{timestamp}"
            
            report_paths = []
            
            # Generate JSON report (always)
            json_path = self._generate_json_report(results, f"{base_name}.json")
            if json_path:
                report_paths.append(json_path)
            
            # Generate HTML report
            if self.config.get("generate_html_report", True):
                html_path = self._generate_html_report(results, f"{base_name}.html")
                if html_path:
                    report_paths.append(html_path)
            
            # Generate CSV metrics
            if self.config.get("generate_csv_metrics", True):
                csv_path = self._generate_csv_report(results, f"{base_name}_metrics.csv")
                if csv_path:
                    report_paths.append(csv_path)
            
            # Return primary report path (HTML if available, otherwise JSON)
            primary_path = next((p for p in report_paths if p.endswith('.html')), 
                              report_paths[0] if report_paths else "")
            
            logger.info(f"Generated {len(report_paths)} report files")
            return primary_path
            
        except Exception as e:
            logger.error(f"Failed to generate full report: {e}")
            return ""
    
    def _generate_json_report(self, results: Dict[str, Any], filename: str) -> str:
        """Generate detailed JSON report"""
        try:
            report_path = self.reports_dir / filename
            
            # Enhanced results with metadata
            enhanced_results = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "generator": "UX-MIRROR Autonomous Testing Phase 2",
                    "target_application": "3D Game of Life",
                    "framework_version": "2.0",
                    "report_format": "json"
                },
                "summary": {
                    "session_id": results.get("session_id", "unknown"),
                    "suite_type": results.get("suite_type", "unknown"),
                    "total_tests": results.get("total_count", 0),
                    "passed_tests": results.get("pass_count", 0),
                    "failed_tests": results.get("fail_count", 0),
                    "error_tests": results.get("error_count", 0),
                    "pass_rate": results.get("pass_rate", 0.0),
                    "total_duration_seconds": results.get("total_duration", 0.0),
                    "average_fps": results.get("average_fps"),
                    "total_screenshots": results.get("total_screenshots", 0)
                },
                "configuration": results.get("config", {}),
                "detailed_results": results.get("test_results", []),
                "performance_metrics": self._extract_performance_metrics(results),
                "error_analysis": self._analyze_errors(results),
                "recommendations": self._generate_recommendations(results)
            }
            
            with open(report_path, 'w') as f:
                json.dump(enhanced_results, f, indent=2, default=str)
            
            logger.info(f"JSON report saved: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Failed to generate JSON report: {e}")
            return ""
    
    def _generate_html_report(self, results: Dict[str, Any], filename: str) -> str:
        """Generate comprehensive HTML report"""
        try:
            report_path = self.reports_dir / filename
            
            # Generate HTML content
            html_content = self._create_html_content(results)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report saved: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            return ""
    
    def _generate_csv_report(self, results: Dict[str, Any], filename: str) -> str:
        """Generate CSV metrics report"""
        try:
            report_path = self.reports_dir / filename
            
            # Extract test results for CSV
            test_results = results.get("test_results", [])
            
            if not test_results:
                logger.warning("No test results to export to CSV")
                return ""
            
            with open(report_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'Test Name',
                    'Category', 
                    'Result',
                    'Duration (s)',
                    'FPS Average',
                    'FPS Min',
                    'FPS Max',
                    'Generation Reached',
                    'Max Living Cells',
                    'UI Response Time',
                    'Screenshots Taken',
                    'Errors Encountered'
                ])
                
                # Data rows
                for test_result in test_results:
                    metrics = test_result.get("metrics", {})
                    
                    writer.writerow([
                        test_result.get("scenario_name", ""),
                        test_result.get("category", ""),
                        test_result.get("result", ""),
                        metrics.get("duration", 0),
                        metrics.get("fps_average", ""),
                        metrics.get("fps_min", ""),
                        metrics.get("fps_max", ""),
                        metrics.get("generation_reached", ""),
                        metrics.get("max_living_cells", ""),
                        metrics.get("ui_response_time", 0),
                        metrics.get("screenshots_taken", 0),
                        metrics.get("errors_encountered", 0)
                    ])
            
            logger.info(f"CSV report saved: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Failed to generate CSV report: {e}")
            return ""
    
    def _create_html_content(self, results: Dict[str, Any]) -> str:
        """Create comprehensive HTML report content"""
        # Basic HTML template with embedded CSS
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UX-MIRROR Autonomous Test Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #2E86AB;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #2E86AB;
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1.1em;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .summary-card.success {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        }}
        .summary-card.warning {{
            background: linear-gradient(135deg, #ff9800 0%, #e68900 100%);
        }}
        .summary-card.error {{
            background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 2em;
        }}
        .summary-card p {{
            margin: 0;
            opacity: 0.9;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #2E86AB;
            border-bottom: 2px solid #2E86AB;
            padding-bottom: 10px;
        }}
        .test-results {{
            overflow-x: auto;
        }}
        .test-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .test-table th, .test-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .test-table th {{
            background-color: #2E86AB;
            color: white;
            font-weight: bold;
        }}
        .test-table tr:hover {{
            background-color: #f5f5f5;
        }}
        .result-pass {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .result-fail {{
            color: #f44336;
            font-weight: bold;
        }}
        .result-error {{
            color: #ff9800;
            font-weight: bold;
        }}
        .performance-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .recommendations {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2196F3;
        }}
        .recommendations h3 {{
            color: #1976D2;
            margin-top: 0;
        }}
        .recommendations ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .recommendations li {{
            margin: 5px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>
        """
        
        # Generate content sections
        content_sections = []
        
        # Header
        content_sections.append(self._create_header_section(results))
        
        # Summary cards
        content_sections.append(self._create_summary_section(results))
        
        # Performance metrics
        content_sections.append(self._create_performance_section(results))
        
        # Detailed test results
        content_sections.append(self._create_results_section(results))
        
        # Error analysis
        content_sections.append(self._create_error_section(results))
        
        # Recommendations
        content_sections.append(self._create_recommendations_section(results))
        
        # Footer
        content_sections.append(self._create_footer_section(results))
        
        # Combine all sections
        content = "\n".join(content_sections)
        
        return html_template.format(content=content)
    
    def _create_header_section(self, results: Dict[str, Any]) -> str:
        """Create HTML header section"""
        session_id = results.get("session_id", "Unknown")
        suite_type = results.get("suite_type", "Unknown")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return f"""
        <div class="header">
            <h1>🤖 UX-MIRROR Autonomous Test Report</h1>
            <p>Session: {session_id} | Suite: {suite_type} | Generated: {timestamp}</p>
            <p>Phase 2: Input Automation System | Target: 3D Game of Life</p>
        </div>
        """
    
    def _create_summary_section(self, results: Dict[str, Any]) -> str:
        """Create HTML summary section"""
        total_count = results.get("total_count", 0)
        pass_count = results.get("pass_count", 0)
        fail_count = results.get("fail_count", 0)
        error_count = results.get("error_count", 0)
        pass_rate = results.get("pass_rate", 0.0) * 100
        duration = results.get("total_duration", 0.0)
        
        # Determine overall status
        if pass_rate >= 90:
            status_class = "success"
            status_text = "Excellent"
        elif pass_rate >= 70:
            status_class = "warning"
            status_text = "Good"
        else:
            status_class = "error" 
            status_text = "Needs Attention"
        
        return f"""
        <div class="summary">
            <div class="summary-card {status_class}">
                <h3>{pass_rate:.1f}%</h3>
                <p>Pass Rate ({status_text})</p>
            </div>
            <div class="summary-card">
                <h3>{pass_count}/{total_count}</h3>
                <p>Tests Passed</p>
            </div>
            <div class="summary-card">
                <h3>{duration:.1f}s</h3>
                <p>Total Duration</p>
            </div>
            <div class="summary-card">
                <h3>{results.get('total_screenshots', 0)}</h3>
                <p>Screenshots</p>
            </div>
        </div>
        """
    
    def _create_performance_section(self, results: Dict[str, Any]) -> str:
        """Create HTML performance section"""
        perf_metrics = self._extract_performance_metrics(results)
        
        fps_info = ""
        if perf_metrics.get("average_fps"):
            fps_info = f"<p><strong>Average FPS:</strong> {perf_metrics['average_fps']:.1f}</p>"
            if perf_metrics.get("fps_range"):
                fps_info += f"<p><strong>FPS Range:</strong> {perf_metrics['fps_range'][0]:.1f} - {perf_metrics['fps_range'][1]:.1f}</p>"
        
        return f"""
        <div class="section">
            <h2>📊 Performance Metrics</h2>
            <div class="performance-section">
                {fps_info}
                <p><strong>Total Test Duration:</strong> {results.get('total_duration', 0):.1f} seconds</p>
                <p><strong>Average Test Duration:</strong> {perf_metrics.get('avg_test_duration', 0):.1f} seconds</p>
                <p><strong>Screenshots Captured:</strong> {results.get('total_screenshots', 0)}</p>
                <p><strong>Errors Encountered:</strong> {results.get('total_errors', 0)}</p>
            </div>
        </div>
        """
    
    def _create_results_section(self, results: Dict[str, Any]) -> str:
        """Create HTML detailed results section"""
        test_results = results.get("test_results", [])
        
        if not test_results:
            return """
            <div class="section">
                <h2>📋 Test Results</h2>
                <p>No test results available.</p>
            </div>
            """
        
        # Create table rows
        table_rows = []
        for test_result in test_results:
            result_status = test_result.get("result", "unknown")
            result_class = f"result-{result_status}"
            
            metrics = test_result.get("metrics", {})
            
            # Format result icon
            result_icon = {
                "pass": "✅",
                "fail": "❌", 
                "error": "⚠️",
                "skip": "⏭️"
            }.get(result_status, "❓")
            
            table_rows.append(f"""
                <tr>
                    <td>{result_icon} {test_result.get('scenario_name', 'Unknown')}</td>
                    <td><span class="{result_class}">{result_status.upper()}</span></td>
                    <td>{metrics.get('duration', 0):.2f}s</td>
                    <td>{metrics.get('fps_average', 'N/A')}</td>
                    <td>{metrics.get('screenshots_taken', 0)}</td>
                    <td>{metrics.get('errors_encountered', 0)}</td>
                </tr>
            """)
        
        return f"""
        <div class="section">
            <h2>📋 Detailed Test Results</h2>
            <div class="test-results">
                <table class="test-table">
                    <thead>
                        <tr>
                            <th>Test Name</th>
                            <th>Result</th>
                            <th>Duration</th>
                            <th>Avg FPS</th>
                            <th>Screenshots</th>
                            <th>Errors</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(table_rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """
    
    def _create_error_section(self, results: Dict[str, Any]) -> str:
        """Create HTML error analysis section"""
        error_analysis = self._analyze_errors(results)
        
        if not error_analysis.get("has_errors", False):
            return """
            <div class="section">
                <h2>🔍 Error Analysis</h2>
                <div class="performance-section">
                    <p>✅ No errors detected during testing!</p>
                </div>
            </div>
            """
        
        error_list = ""
        for error in error_analysis.get("error_details", []):
            error_list += f"<li><strong>{error['test']}:</strong> {error['description']}</li>"
        
        return f"""
        <div class="section">
            <h2>🔍 Error Analysis</h2>
            <div class="performance-section">
                <p><strong>Total Errors:</strong> {error_analysis.get('total_errors', 0)}</p>
                <p><strong>Failed Tests:</strong> {error_analysis.get('failed_tests', 0)}</p>
                <h4>Error Details:</h4>
                <ul>
                    {error_list}
                </ul>
            </div>
        </div>
        """
    
    def _create_recommendations_section(self, results: Dict[str, Any]) -> str:
        """Create HTML recommendations section"""
        recommendations = self._generate_recommendations(results)
        
        rec_list = ""
        for rec in recommendations:
            rec_list += f"<li>{rec}</li>"
        
        return f"""
        <div class="section">
            <div class="recommendations">
                <h3>💡 Recommendations</h3>
                <ul>
                    {rec_list}
                </ul>
            </div>
        </div>
        """
    
    def _create_footer_section(self, results: Dict[str, Any]) -> str:
        """Create HTML footer section"""
        return f"""
        <div class="footer">
            <p>Generated by UX-MIRROR Autonomous Testing System | Phase 2: Input Automation</p>
            <p>Framework Version 2.0 | Target Application: 3D Game of Life (Vulkan Edition)</p>
        </div>
        """
    
    def _extract_performance_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance metrics from results"""
        test_results = results.get("test_results", [])
        
        fps_values = []
        durations = []
        
        for test_result in test_results:
            metrics = test_result.get("metrics", {})
            
            if metrics.get("fps_average"):
                fps_values.append(metrics["fps_average"])
            
            if metrics.get("duration"):
                durations.append(metrics["duration"])
        
        performance_metrics = {
            "avg_test_duration": sum(durations) / len(durations) if durations else 0,
            "total_tests": len(test_results)
        }
        
        if fps_values:
            performance_metrics.update({
                "average_fps": sum(fps_values) / len(fps_values),
                "fps_range": [min(fps_values), max(fps_values)],
                "fps_samples": len(fps_values)
            })
        
        return performance_metrics
    
    def _analyze_errors(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze errors from test results"""
        test_results = results.get("test_results", [])
        
        failed_tests = []
        error_tests = []
        total_errors = 0
        
        for test_result in test_results:
            result_status = test_result.get("result", "")
            test_name = test_result.get("scenario_name", "Unknown")
            
            if result_status == "fail":
                failed_tests.append({
                    "test": test_name,
                    "description": "Test assertions failed"
                })
            elif result_status == "error":
                error_tests.append({
                    "test": test_name,
                    "description": "Test execution error"
                })
            
            # Count individual errors within tests
            metrics = test_result.get("metrics", {})
            total_errors += metrics.get("errors_encountered", 0)
        
        error_details = failed_tests + error_tests
        
        return {
            "has_errors": len(error_details) > 0 or total_errors > 0,
            "failed_tests": len(failed_tests),
            "error_tests": len(error_tests),
            "total_errors": total_errors,
            "error_details": error_details
        }
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        pass_rate = results.get("pass_rate", 0.0)
        total_duration = results.get("total_duration", 0.0)
        
        # Pass rate recommendations
        if pass_rate < 0.7:
            recommendations.append("🔴 Pass rate is below 70%. Review failed tests and consider application stability.")
        elif pass_rate < 0.9:
            recommendations.append("🟡 Pass rate is good but could be improved. Check specific test failures.")
        else:
            recommendations.append("✅ Excellent pass rate! Consider adding more comprehensive tests.")
        
        # Performance recommendations
        perf_metrics = self._extract_performance_metrics(results)
        if perf_metrics.get("average_fps"):
            avg_fps = perf_metrics["average_fps"]
            if avg_fps < 30:
                recommendations.append("🎮 Low FPS detected. Consider performance optimization.")
            elif avg_fps < 60:
                recommendations.append("🎮 FPS is acceptable but could be improved for better user experience.")
            else:
                recommendations.append("🎮 Excellent FPS performance!")
        
        # Duration recommendations
        if total_duration > 1800:  # 30 minutes
            recommendations.append("⏱️ Test suite duration is quite long. Consider optimizing test execution.")
        
        # Error recommendations
        error_analysis = self._analyze_errors(results)
        if error_analysis.get("has_errors"):
            recommendations.append("🔧 Address detected errors to improve test reliability.")
        
        # Coverage recommendations
        total_tests = results.get("total_count", 0)
        if total_tests < 10:
            recommendations.append("📋 Consider adding more test scenarios for better coverage.")
        
        # Default recommendation if no specific issues
        if not recommendations:
            recommendations.append("✨ All metrics look good! Consider adding stress tests or edge cases.")
        
        return recommendations

def main():
    """Test the report generator"""
    print("📄 Testing Report Generator...")
    
    # Create sample test results
    sample_results = {
        "session_id": "test_session_123",
        "suite_type": "basic",
        "total_count": 5,
        "pass_count": 4,
        "fail_count": 1,
        "error_count": 0,
        "pass_rate": 0.8,
        "total_duration": 125.5,
        "average_fps": 58.3,
        "total_screenshots": 15,
        "test_results": [
            {
                "scenario_name": "application_startup",
                "result": "pass",
                "metrics": {
                    "duration": 25.2,
                    "fps_average": 60.0,
                    "screenshots_taken": 3,
                    "errors_encountered": 0
                }
            },
            {
                "scenario_name": "basic_play_pause",
                "result": "pass", 
                "metrics": {
                    "duration": 30.1,
                    "fps_average": 58.5,
                    "screenshots_taken": 5,
                    "errors_encountered": 0
                }
            },
            {
                "scenario_name": "performance_test",
                "result": "fail",
                "metrics": {
                    "duration": 45.8,
                    "fps_average": 25.2,
                    "screenshots_taken": 7,
                    "errors_encountered": 1
                }
            }
        ]
    }
    
    generator = ReportGenerator()
    
    print("Generating sample report...")
    report_path = generator.generate_full_report(sample_results, "test_session")
    
    print(f"✅ Report generated: {report_path}")

if __name__ == "__main__":
    main() 