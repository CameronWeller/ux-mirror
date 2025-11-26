#!/usr/bin/env python3
"""
Test Full Workflow: Capture → Analyze → Report
Tests for Phase 3, Step 27 of v0.1.0 release

This test verifies the complete workflow from screenshot capture
through analysis to report generation.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.screenshot_analyzer import ScreenshotAnalyzer
    SCREENSHOT_ANALYZER_AVAILABLE = True
except ImportError:
    SCREENSHOT_ANALYZER_AVAILABLE = False
    print("[INFO] ScreenshotAnalyzer not available - some tests will be skipped")

try:
    from ai_vision_analyzer import AIVisionAnalyzer, GameUIAnalysis
    AI_VISION_AVAILABLE = True
except ImportError:
    AI_VISION_AVAILABLE = False
    print("[INFO] AIVisionAnalyzer not available - some tests will be skipped")

try:
    import asyncio
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    print("[INFO] asyncio not available - some tests will be skipped")


class TestFullWorkflow:
    """Test 27: Test full workflow (capture → analyze → report)"""
    
    def __init__(self):
        self.screenshot_analyzer = None
        self.ai_analyzer = None
        self.test_results_dir = project_root / "test_outputs"
        self.test_results_dir.mkdir(exist_ok=True)
        
    def setup(self):
        """27.1: Create test script and setup"""
        if not SCREENSHOT_ANALYZER_AVAILABLE:
            print("[SKIP] ScreenshotAnalyzer not available")
            return False
        
        try:
            self.screenshot_analyzer = ScreenshotAnalyzer()
            print("[OK] ScreenshotAnalyzer initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize ScreenshotAnalyzer: {e}")
            return False
        
        if AI_VISION_AVAILABLE:
            try:
                self.ai_analyzer = AIVisionAnalyzer()
                print("[OK] AIVisionAnalyzer initialized")
            except Exception as e:
                print(f"[WARN] AIVisionAnalyzer not available: {e}")
        
        return True
    
    async def test_capture_screenshot(self) -> Optional[str]:
        """27.2: Step 1: Capture screenshot"""
        if not self.screenshot_analyzer:
            print("[SKIP] ScreenshotAnalyzer not available")
            return None
        
        try:
            print("Step 27.2: Capturing screenshot...")
            start_time = time.time()
            
            screenshot_path = await self.screenshot_analyzer.capture_screenshot()
            
            capture_time = time.time() - start_time
            
            if screenshot_path:
                print(f"[OK] Screenshot captured: {screenshot_path}")
                print(f"[OK] Capture time: {capture_time:.2f}s")
                
                # Verify file exists
                if Path(screenshot_path).exists():
                    file_size = Path(screenshot_path).stat().st_size
                    print(f"[OK] File size: {file_size} bytes")
                    return screenshot_path
                else:
                    print(f"[ERROR] Screenshot file not found: {screenshot_path}")
                    return None
            else:
                print("[ERROR] Screenshot capture returned None")
                return None
                
        except Exception as e:
            print(f"[ERROR] Failed to capture screenshot: {e}")
            return None
    
    async def test_analyze_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """27.3: Step 2: Analyze screenshot"""
        if not self.screenshot_analyzer:
            print("[SKIP] ScreenshotAnalyzer not available")
            return None
        
        if not image_path or not Path(image_path).exists():
            print("[ERROR] Invalid image path for analysis")
            return None
        
        try:
            print("Step 27.3: Analyzing screenshot...")
            start_time = time.time()
            
            analysis_result = await self.screenshot_analyzer.analyze_image(image_path)
            
            analysis_time = time.time() - start_time
            
            if analysis_result:
                print(f"[OK] Analysis completed in {analysis_time:.2f}s")
                print(f"[OK] Analysis keys: {list(analysis_result.keys())}")
                return analysis_result
            else:
                print("[ERROR] Analysis returned None")
                return None
                
        except Exception as e:
            print(f"[ERROR] Failed to analyze image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def test_ai_analysis(self, image_path: str) -> Optional[GameUIAnalysis]:
        """27.3b: Step 2b: AI analysis (if available)"""
        if not self.ai_analyzer:
            print("[SKIP] AIVisionAnalyzer not available")
            return None
        
        if not image_path or not Path(image_path).exists():
            print("[ERROR] Invalid image path for AI analysis")
            return None
        
        try:
            print("Step 27.3b: Running AI analysis...")
            start_time = time.time()
            
            ai_result = await self.ai_analyzer.analyze_screenshot(image_path)
            
            ai_time = time.time() - start_time
            
            if ai_result:
                print(f"[OK] AI analysis completed in {ai_time:.2f}s")
                print(f"[OK] AI result type: {type(ai_result)}")
                return ai_result
            else:
                print("[WARN] AI analysis returned None (may need API key)")
                return None
                
        except Exception as e:
            print(f"[WARN] AI analysis failed (may need API key): {e}")
            return None
    
    def test_generate_report_json(self, analysis_result: Dict[str, Any], 
                                  ai_result: Optional[GameUIAnalysis] = None) -> Optional[str]:
        """27.4: Step 3: Generate report (JSON format)"""
        if not analysis_result:
            print("[ERROR] No analysis result to generate report from")
            return None
        
        try:
            print("Step 27.4: Generating JSON report...")
            
            # Combine results
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis_result,
            }
            
            if ai_result:
                if hasattr(ai_result, 'to_json'):
                    report_data["ai_analysis"] = json.loads(ai_result.to_json())
                elif hasattr(ai_result, '__dict__'):
                    report_data["ai_analysis"] = ai_result.__dict__
            
            # Generate report file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = self.test_results_dir / f"workflow_report_{timestamp}.json"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"[OK] Report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            print(f"[ERROR] Failed to generate report: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_verify_all_steps_complete(self, screenshot_path: Optional[str],
                                      analysis_result: Optional[Dict[str, Any]],
                                      report_path: Optional[str]) -> bool:
        """27.5: Verify all steps complete without errors"""
        print("Step 27.5: Verifying all steps completed...")
        
        all_complete = True
        
        if not screenshot_path:
            print("[ERROR] Screenshot capture step failed")
            all_complete = False
        else:
            print("[OK] Screenshot capture step completed")
        
        if not analysis_result:
            print("[ERROR] Analysis step failed")
            all_complete = False
        else:
            print("[OK] Analysis step completed")
        
        if not report_path:
            print("[ERROR] Report generation step failed")
            all_complete = False
        else:
            print("[OK] Report generation step completed")
        
        return all_complete
    
    def test_verify_data_flow(self, screenshot_path: str,
                              analysis_result: Dict[str, Any],
                              report_path: str) -> bool:
        """27.6: Verify data flows correctly between steps"""
        print("Step 27.6: Verifying data flow...")
        
        try:
            # Check screenshot path in analysis
            if "image_path" in analysis_result:
                if analysis_result["image_path"] == screenshot_path:
                    print("[OK] Screenshot path flows correctly to analysis")
                else:
                    print(f"[WARN] Path mismatch: {analysis_result['image_path']} != {screenshot_path}")
            
            # Check report contains analysis
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            if "analysis" in report_data:
                print("[OK] Report contains analysis data")
            else:
                print("[ERROR] Report missing analysis data")
                return False
            
            # Check report contains image path
            if "image_path" in report_data.get("analysis", {}):
                print("[OK] Report contains image path")
            else:
                print("[WARN] Report missing image path")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to verify data flow: {e}")
            return False
    
    def test_check_execution_time(self, total_time: float) -> bool:
        """27.7: Check execution time (should be reasonable)"""
        print(f"Step 27.7: Checking execution time: {total_time:.2f}s")
        
        # Reasonable time: under 30 seconds for full workflow
        if total_time < 30.0:
            print(f"[OK] Execution time is reasonable: {total_time:.2f}s")
            return True
        elif total_time < 60.0:
            print(f"[WARN] Execution time is acceptable but slow: {total_time:.2f}s")
            return True
        else:
            print(f"[WARN] Execution time is high: {total_time:.2f}s")
            return False
    
    def test_verify_output_files(self, screenshot_path: Optional[str],
                                report_path: Optional[str]) -> bool:
        """27.8: Verify output files are created"""
        print("Step 27.8: Verifying output files...")
        
        all_exist = True
        
        if screenshot_path:
            if Path(screenshot_path).exists():
                print(f"[OK] Screenshot file exists: {screenshot_path}")
            else:
                print(f"[ERROR] Screenshot file missing: {screenshot_path}")
                all_exist = False
        else:
            print("[ERROR] No screenshot path provided")
            all_exist = False
        
        if report_path:
            if Path(report_path).exists():
                print(f"[OK] Report file exists: {report_path}")
                
                # Verify report is valid JSON
                try:
                    with open(report_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    print("[OK] Report file is valid JSON")
                except json.JSONDecodeError:
                    print("[ERROR] Report file is not valid JSON")
                    all_exist = False
            else:
                print(f"[ERROR] Report file missing: {report_path}")
                all_exist = False
        else:
            print("[ERROR] No report path provided")
            all_exist = False
        
        return all_exist


async def run_full_workflow_test():
    """Run all workflow tests"""
    print("=" * 60)
    print("Test 27: Full Workflow Test")
    print("=" * 60)
    print()
    
    test = TestFullWorkflow()
    
    # Setup
    if not test.setup():
        print("[ERROR] Setup failed")
        return False
    
    # Track total time
    workflow_start = time.time()
    
    # Step 1: Capture screenshot
    screenshot_path = await test.test_capture_screenshot()
    
    if not screenshot_path:
        print("[ERROR] Workflow failed at screenshot capture")
        return False
    
    # Step 2: Analyze
    analysis_result = await test.test_analyze_image(screenshot_path)
    
    # Step 2b: AI analysis (optional)
    ai_result = None
    if test.ai_analyzer:
        ai_result = await test.test_ai_analysis(screenshot_path)
    
    if not analysis_result:
        print("[ERROR] Workflow failed at analysis")
        return False
    
    # Step 3: Generate report
    report_path = test.test_generate_report_json(analysis_result, ai_result)
    
    if not report_path:
        print("[ERROR] Workflow failed at report generation")
        return False
    
    # Verify steps
    total_time = time.time() - workflow_start
    
    all_complete = test.test_verify_all_steps_complete(
        screenshot_path, analysis_result, report_path
    )
    
    data_flow_ok = test.test_verify_data_flow(
        screenshot_path, analysis_result, report_path
    )
    
    time_ok = test.test_check_execution_time(total_time)
    
    files_ok = test.test_verify_output_files(screenshot_path, report_path)
    
    # Summary
    print()
    print("=" * 60)
    print("Workflow Test Summary")
    print("=" * 60)
    print(f"All steps complete: {'✅' if all_complete else '❌'}")
    print(f"Data flow correct: {'✅' if data_flow_ok else '❌'}")
    print(f"Execution time OK: {'✅' if time_ok else '⚠️'}")
    print(f"Output files exist: {'✅' if files_ok else '❌'}")
    print(f"Total time: {total_time:.2f}s")
    print()
    
    success = all_complete and data_flow_ok and files_ok
    
    if success:
        print("[SUCCESS] Full workflow test passed!")
    else:
        print("[WARN] Full workflow test completed with some issues")
    
    return success


if __name__ == '__main__':
    if ASYNC_AVAILABLE:
        result = asyncio.run(run_full_workflow_test())
        sys.exit(0 if result else 1)
    else:
        print("[ERROR] asyncio not available")
        sys.exit(1)


