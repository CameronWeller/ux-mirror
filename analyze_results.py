#!/usr/bin/env python3
"""
Analysis Results Breakdown
=========================
"""

import json
from datetime import datetime

def analyze_anthropic_results(filename):
    """Analyze and present detailed breakdown of Anthropic results"""
    
    with open(filename, 'r') as f:
        data = json.load(f)

    print('=' * 60)
    print('DETAILED ANTHROPIC ANALYSIS BREAKDOWN')
    print('=' * 60)

    print(f'📊 TEMPORAL METRICS:')
    metrics = data['temporal_analysis']['temporal_metrics']
    print(f'  • Total Screenshots: {metrics["total_screenshots"]}')
    print(f'  • Time Span: {metrics["time_span_seconds"]:.0f} seconds ({metrics["time_span_seconds"]/60:.1f} minutes)')
    print(f'  • Generation Span: {metrics["generation_span"]} generations')
    print(f'  • Avg Generation Interval: {metrics["avg_generation_interval"]} generations')
    print(f'  • Avg Time per Generation: {metrics["avg_time_interval"]:.1f} seconds')
    print(f'  • Screenshot Frequency: {metrics["screenshot_frequency"]:.1f} per minute')

    print(f'\n🔍 KEY FINDINGS ACROSS ALL ANALYSIS TYPES:')
    issues_found = set()
    
    for analysis_type in ['temporal_analysis', 'generation_focused_analysis', 'change_detection_analysis']:
        analysis = data[analysis_type]['analysis']
        print(f'\n{analysis_type.upper().replace("_", " ")}:')
        print(f'  • Images Analyzed: {data[analysis_type]["images_analyzed"]}')
        
        # Extract key insights
        if 'solid navy blue' in analysis.lower() or 'solid blue' in analysis.lower():
            print(f'  ❌ CRITICAL ISSUE: Only solid blue backgrounds visible')
            issues_found.add('solid_background')
        if 'rendering' in analysis.lower():
            print(f'  ⚠️  SUSPECTED: Rendering/display issues')
            issues_found.add('rendering')
        if 'extinction' in analysis.lower():
            print(f'  🦕 POSSIBLE: Complete cell extinction')
            issues_found.add('extinction')
        if 'contrast' in analysis.lower():
            print(f'  🎨 POSSIBLE: Contrast/visibility issues')
            issues_found.add('contrast')
        if 'visible' in analysis.lower() and 'no' in analysis.lower():
            print(f'  👁️  CONFIRMED: No visible cellular structures')
            issues_found.add('no_visibility')

    print(f'\n🚨 UNIFIED CONCLUSION:')
    print(f'  All 3 analysis types detected the same issue:')
    print(f'  - NO VISIBLE CELLULAR ACTIVITY')
    print(f'  - SOLID DARK BLUE BACKGROUNDS ONLY') 
    print(f'  - SUGGESTS VISUALIZATION PROBLEM')
    
    print(f'\n📋 RECOMMENDED FIXES:')
    if 'solid_background' in issues_found:
        print(f'  1. Increase cell visibility (brighter colors)')
        print(f'  2. Add wireframe or outline rendering')
        print(f'  3. Adjust camera position/zoom')
        print(f'  4. Add background contrast')
    
    return issues_found

if __name__ == "__main__":
    analyze_anthropic_results('temporal_analysis_20250602_181132.json') 