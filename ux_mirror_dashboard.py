#!/usr/bin/env python3
"""
UX-Mirror Dashboard - Iterative Improvement Tracker
==================================================

Real-time dashboard showing the UX-Mirror feedback loop methodology:
1. Capture screenshots automatically
2. Send to Anthropic for visual analysis
3. Identify UX issues and problems
4. Implement fixes based on feedback
5. Validate improvements with new analysis

Author: UX-Mirror System
"""

import streamlit as st
import pandas as pd
import json
import os
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import sys

# Page config
st.set_page_config(
    page_title="UX-Mirror Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

class UXMirrorDashboard:
    def __init__(self):
        self.screenshot_dir = "game_screenshots"
        self.analysis_files = []
        self.update_analysis_files()
        
    def update_analysis_files(self):
        """Find all analysis result files"""
        self.analysis_files = []
        for file in os.listdir("."):
            if file.startswith("temporal_analysis_") and file.endswith(".json"):
                self.analysis_files.append(file)
        self.analysis_files.sort(reverse=True)  # Most recent first
    
    def load_analysis_results(self, filename: str) -> Dict:
        """Load analysis results from JSON file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading {filename}: {e}")
            return {}
    
    def count_screenshots(self) -> Dict[str, int]:
        """Count different types of screenshots"""
        if not os.path.exists(self.screenshot_dir):
            return {"total": 0, "original": 0, "fixed": 0, "optimized": 0}
        
        total = 0
        original = 0
        fixed = 0
        optimized = 0
        
        for file in os.listdir(self.screenshot_dir):
            if file.endswith('.png'):
                total += 1
                if file.startswith('game_of_life_gen_'):
                    original += 1
                elif file.startswith('fixed_'):
                    fixed += 1
                elif file.startswith('opt_'):
                    optimized += 1
        
        return {
            "total": total,
            "original": original, 
            "fixed": fixed,
            "optimized": optimized
        }
    
    def extract_issues_from_analysis(self, analysis_data: Dict) -> List[str]:
        """Extract identified issues from analysis"""
        issues = []
        
        for analysis_type in ['temporal_analysis', 'generation_focused_analysis', 'change_detection_analysis']:
            if analysis_type in analysis_data:
                analysis_text = analysis_data[analysis_type].get('analysis', '').lower()
                
                if 'solid navy blue' in analysis_text or 'solid blue' in analysis_text:
                    issues.append("❌ Only solid blue backgrounds visible")
                if 'no visible' in analysis_text and 'cellular' in analysis_text:
                    issues.append("👁️ No visible cellular structures")
                if 'rendering' in analysis_text and 'issue' in analysis_text:
                    issues.append("⚠️ Suspected rendering/display issues")
                if 'contrast' in analysis_text:
                    issues.append("🎨 Contrast/visibility problems")
                if 'extinction' in analysis_text:
                    issues.append("🦕 Possible complete cell extinction")
        
        return list(set(issues))  # Remove duplicates
    
    def get_iteration_summary(self) -> List[Dict]:
        """Get summary of iterations and improvements"""
        iterations = []
        
        # Original version analysis
        if "temporal_analysis_20250602_181132.json" in self.analysis_files:
            data = self.load_analysis_results("temporal_analysis_20250602_181132.json")
            if data:
                issues = self.extract_issues_from_analysis(data)
                iterations.append({
                    "iteration": 1,
                    "version": "Original 3D Game of Life",
                    "timestamp": "2025-06-02 18:11:32",
                    "issues_found": len(issues),
                    "issues": issues,
                    "status": "❌ Issues Identified",
                    "screenshots": data.get('metadata', {}).get('total_screenshots', 0),
                    "fixes_implemented": []
                })
        
        # Fixed version analysis
        if "temporal_analysis_20250602_202951.json" in self.analysis_files:
            data = self.load_analysis_results("temporal_analysis_20250602_202951.json")
            if data:
                issues = self.extract_issues_from_analysis(data)
                iterations.append({
                    "iteration": 2,
                    "version": "Fixed 3D Game of Life",
                    "timestamp": "2025-06-02 20:29:51",
                    "issues_found": len(issues),
                    "issues": issues,
                    "status": "🔄 Still Has Issues" if issues else "✅ Issues Resolved",
                    "screenshots": data.get('metadata', {}).get('total_screenshots', 0),
                    "fixes_implemented": [
                        "✅ Brighter, high-contrast cell colors",
                        "✅ Wireframe outlines for better visibility", 
                        "✅ Improved lighting and background contrast",
                        "✅ Closer camera for better detail"
                    ]
                })
        
        # Add current optimized version (if screenshots exist)
        screenshot_counts = self.count_screenshots()
        if screenshot_counts["optimized"] > 0:
            iterations.append({
                "iteration": 3,
                "version": "Optimized 3D Game of Life",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "issues_found": 0,  # Will be updated when analyzed
                "issues": [],
                "status": "🎯 Conservative Screenshot Capture",
                "screenshots": screenshot_counts["optimized"],
                "fixes_implemented": [
                    "✅ Reduced screenshot frequency (1/second)",
                    "✅ Limited to 10 screenshots per session",
                    "✅ Maintained visual enhancements",
                    "✅ Added session tracking"
                ]
            })
        
        return iterations

def main():
    # Initialize dashboard
    dashboard = UXMirrorDashboard()
    
    # Header
    st.title("🎯 UX-Mirror Dashboard")
    st.markdown("**Real-time Visual Analysis & Iterative Improvement Tracker**")
    
    # Sidebar
    st.sidebar.title("🔧 Controls")
    
    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=False)
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        dashboard.update_analysis_files()
        st.rerun()
    
    # Run optimized demo button
    if st.sidebar.button("🎮 Run Optimized Demo"):
        st.sidebar.info("Starting optimized 3D Game of Life...")
        try:
            subprocess.Popen([sys.executable, "optimized_3d_game_of_life.py"])
            st.sidebar.success("Demo started! Check terminal for output.")
        except Exception as e:
            st.sidebar.error(f"Failed to start demo: {e}")
    
    # Run analysis button
    if st.sidebar.button("🧠 Analyze Screenshots"):
        if os.path.exists(dashboard.screenshot_dir):
            st.sidebar.info("Running screenshot analysis...")
            try:
                result = subprocess.run([sys.executable, "agents/temporal_screenshot_analyzer.py"], 
                                     capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    st.sidebar.success("Analysis completed!")
                    dashboard.update_analysis_files()
                    st.rerun()
                else:
                    st.sidebar.error(f"Analysis failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                st.sidebar.warning("Analysis timed out (2 minutes)")
            except Exception as e:
                st.sidebar.error(f"Analysis error: {e}")
        else:
            st.sidebar.warning("No screenshots directory found")
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    # Screenshot counts
    screenshot_counts = dashboard.count_screenshots()
    
    with col1:
        st.metric("📸 Total Screenshots", screenshot_counts["total"])
    
    with col2:
        st.metric("🎯 Analysis Files", len(dashboard.analysis_files))
    
    with col3:
        st.metric("🔄 Iterations", len(dashboard.get_iteration_summary()))
    
    with col4:
        latest_file = dashboard.analysis_files[0] if dashboard.analysis_files else "None"
        st.metric("⏰ Latest Analysis", latest_file.split('_')[-1].split('.')[0] if latest_file != "None" else "None")
    
    # UX-Mirror Methodology Overview
    st.header("🎯 UX-Mirror Methodology")
    
    method_col1, method_col2 = st.columns(2)
    
    with method_col1:
        st.subheader("📋 Process Flow")
        st.markdown("""
        **1. 📸 Automatic Screenshot Capture**
        - Conservative capture (1/second, max 10)
        - Minimal performance impact
        - Timestamp and generation tracking
        
        **2. 🧠 AI Visual Analysis**
        - Send screenshots to Anthropic Claude
        - Temporal pattern detection
        - UX issue identification
        
        **3. 🔍 Issue Detection**
        - Visibility problems
        - Rendering issues
        - User experience gaps
        
        **4. 🛠️ Iterative Fixes**
        - Implement targeted improvements
        - Validate with new analysis
        - Continuous refinement
        """)
    
    with method_col2:
        st.subheader("📊 Screenshot Distribution")
        
        # Create pie chart of screenshot types
        if screenshot_counts["total"] > 0:
            fig = px.pie(
                values=[screenshot_counts["original"], screenshot_counts["fixed"], screenshot_counts["optimized"]],
                names=["Original", "Fixed", "Optimized"],
                title="Screenshot Types",
                color_discrete_sequence=["#ff6b6b", "#4ecdc4", "#45b7d1"]
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No screenshots available yet. Run the optimized demo to generate data.")
    
    # Iteration History
    st.header("🔄 Iteration History & Improvements")
    
    iterations = dashboard.get_iteration_summary()
    
    if iterations:
        # Create timeline visualization
        timeline_data = []
        for iteration in iterations:
            timeline_data.append({
                "Iteration": f"v{iteration['iteration']}",
                "Version": iteration['version'],
                "Issues Found": iteration['issues_found'],
                "Screenshots": iteration['screenshots'],
                "Status": iteration['status']
            })
        
        df = pd.DataFrame(timeline_data)
        
        # Display iteration table
        st.subheader("📈 Progress Timeline")
        st.dataframe(df, use_container_width=True)
        
        # Issues over time chart
        if len(iterations) > 1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[f"v{i['iteration']}" for i in iterations],
                y=[i['issues_found'] for i in iterations],
                mode='lines+markers',
                name='Issues Found',
                line=dict(color='red', width=3),
                marker=dict(size=10)
            ))
            fig.update_layout(
                title="Issues Found Over Iterations",
                xaxis_title="Version",
                yaxis_title="Number of Issues",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed iteration breakdown
        st.subheader("🔍 Detailed Iteration Analysis")
        
        for i, iteration in enumerate(iterations):
            with st.expander(f"**{iteration['version']}** - {iteration['status']}", expanded=(i == len(iterations)-1)):
                
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    st.markdown(f"**Timestamp:** {iteration['timestamp']}")
                    st.markdown(f"**Screenshots:** {iteration['screenshots']}")
                    st.markdown(f"**Issues Found:** {iteration['issues_found']}")
                    
                    if iteration['issues']:
                        st.markdown("**Issues Identified:**")
                        for issue in iteration['issues']:
                            st.markdown(f"- {issue}")
                
                with detail_col2:
                    if iteration['fixes_implemented']:
                        st.markdown("**Fixes Implemented:**")
                        for fix in iteration['fixes_implemented']:
                            st.markdown(f"- {fix}")
                    else:
                        st.info("No fixes implemented yet (baseline version)")
    
    else:
        st.info("No iteration data available. Run the analysis to see results.")
    
    # Latest Analysis Results
    if dashboard.analysis_files:
        st.header("🧠 Latest Analysis Results")
        
        latest_file = dashboard.analysis_files[0]
        latest_data = dashboard.load_analysis_results(latest_file)
        
        if latest_data:
            analysis_col1, analysis_col2 = st.columns(2)
            
            with analysis_col1:
                st.subheader("📊 Analysis Metrics")
                
                if 'temporal_analysis' in latest_data:
                    metrics = latest_data['temporal_analysis'].get('temporal_metrics', {})
                    
                    st.metric("Total Screenshots", metrics.get('total_screenshots', 0))
                    st.metric("Time Span (seconds)", f"{metrics.get('time_span_seconds', 0):.0f}")
                    st.metric("Generation Span", metrics.get('generation_span', 0))
                    st.metric("Avg Time/Generation", f"{metrics.get('avg_time_interval', 0):.1f}s")
            
            with analysis_col2:
                st.subheader("🔍 Analysis Types")
                
                for analysis_type in ['temporal_analysis', 'generation_focused_analysis', 'change_detection_analysis']:
                    if analysis_type in latest_data:
                        data = latest_data[analysis_type]
                        images_analyzed = data.get('images_analyzed', 0)
                        status = "❌ Issues Found" if "solid blue" in data.get('analysis', '').lower() else "✅ Looks Good"
                        st.markdown(f"**{analysis_type.replace('_', ' ').title()}**")
                        st.markdown(f"- Images: {images_analyzed}")
                        st.markdown(f"- Status: {status}")
            
            # Full analysis text
            st.subheader("📝 Full Analysis")
            
            for analysis_type in ['temporal_analysis', 'generation_focused_analysis', 'change_detection_analysis']:
                if analysis_type in latest_data:
                    with st.expander(f"{analysis_type.replace('_', ' ').title()}", expanded=False):
                        analysis_text = latest_data[analysis_type].get('analysis', 'No analysis available')
                        st.markdown(analysis_text)
    
    # Footer
    st.markdown("---")
    st.markdown("🎯 **UX-Mirror Dashboard** - Bridging the gap between AI assumptions and actual user experience")

if __name__ == "__main__":
    main() 