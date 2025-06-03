#!/usr/bin/env python3
"""
UX-MIRROR CLI Tool
==================

Simple command-line interface for UX analysis and fix generation.
Implements Phase 4 deliverables: User Interface

Usage:
    python ux_mirror_cli.py analyze <url_or_file>
    python ux_mirror_cli.py generate-fixes <analysis_report.json>
    python ux_mirror_cli.py full-pipeline <url_or_file>

Author: UX-MIRROR Team
"""

import click
import sys
from pathlib import Path
import json
import webbrowser
from datetime import datetime

# Import our modules
try:
    from start_simple_poc import SimpleUXAnalyzer
    from css_fix_generator import CSSFixGenerator
except ImportError:
    print("Error: Required modules not found. Make sure start_simple_poc.py and css_fix_generator.py are in the same directory.")
    sys.exit(1)


@click.group()
def cli():
    """UX-MIRROR: AI-Driven UX Analysis and Fix Generation"""
    pass


@cli.command()
@click.argument('source')
@click.option('--output-format', '-f', type=click.Choice(['json', 'html', 'both']), default='both',
              help='Output format for the analysis report')
@click.option('--open-report', '-o', is_flag=True, help='Open HTML report in browser after generation')
def analyze(source, output_format, open_report):
    """Analyze a screenshot or URL for UX issues"""
    click.echo(f"\n🔍 Analyzing: {source}")
    
    analyzer = SimpleUXAnalyzer()
    
    try:
        results = analyzer.analyze_screenshot(source)
        
        click.echo(f"\n✅ Analysis complete!")
        click.echo(f"   • Found {len(results['detected_elements'])} UI elements")
        click.echo(f"   • Detected {len(results['ux_issues'])} UX issues")
        
        # Show issue summary
        if results['ux_issues']:
            click.echo("\n📋 Issue Summary:")
            severity_counts = {}
            for issue in results['ux_issues']:
                severity = issue.get('severity', 'low')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
            for severity, count in severity_counts.items():
                emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
                click.echo(f"   {emoji} {severity.upper()}: {count} issues")
        
        # Report locations
        output_dir = Path("ux_analysis_results")
        json_files = list(output_dir.glob("ux_analysis_*.json"))
        html_files = list(output_dir.glob("ux_report_*.html"))
        
        if json_files:
            click.echo(f"\n📄 JSON report: {json_files[-1]}")
        if html_files:
            click.echo(f"📊 HTML report: {html_files[-1]}")
            if open_report:
                webbrowser.open(str(html_files[-1]))
                
        return str(json_files[-1]) if json_files else None
        
    except Exception as e:
        click.echo(f"\n❌ Error during analysis: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('report-path', type=click.Path(exists=True))
@click.option('--open-guide', '-g', is_flag=True, help='Open implementation guide in browser')
def generate_fixes(report_path, open_guide):
    """Generate CSS/JS fixes from an analysis report"""
    click.echo(f"\n🔧 Generating fixes from: {report_path}")
    
    generator = CSSFixGenerator()
    
    try:
        result = generator.generate_fixes_from_report(report_path)
        
        click.echo(f"\n✅ Fix generation complete!")
        click.echo(f"   • Generated {result['fixes_count']} total fixes")
        
        click.echo("\n📦 Generated files:")
        click.echo(f"   • CSS fixes: {Path(result['css_file']).name}")
        if result['js_file']:
            click.echo(f"   • JavaScript fixes: {Path(result['js_file']).name}")
        click.echo(f"   • Implementation guide: {Path(result['guide']).name}")
        
        if open_guide:
            webbrowser.open(result['guide'])
            
    except Exception as e:
        click.echo(f"\n❌ Error generating fixes: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('source')
@click.option('--open-all', '-a', is_flag=True, help='Open all generated reports in browser')
def full_pipeline(source, open_all):
    """Run complete analysis and fix generation pipeline"""
    click.echo("\n🚀 Running full UX-MIRROR pipeline")
    click.echo("=" * 50)
    
    # Step 1: Analysis
    click.echo("\n📊 Step 1/2: Analyzing UX...")
    analyzer = SimpleUXAnalyzer()
    
    try:
        results = analyzer.analyze_screenshot(source)
        
        # Get the JSON report path
        output_dir = Path("ux_analysis_results")
        json_files = list(output_dir.glob("ux_analysis_*.json"))
        if not json_files:
            click.echo("❌ No analysis report generated", err=True)
            sys.exit(1)
            
        report_path = json_files[-1]
        
        # Summary
        click.echo(f"   ✓ Found {len(results['detected_elements'])} elements")
        click.echo(f"   ✓ Detected {len(results['ux_issues'])} issues")
        
        # Step 2: Fix Generation
        click.echo("\n🔧 Step 2/2: Generating fixes...")
        generator = CSSFixGenerator()
        fix_result = generator.generate_fixes_from_report(report_path)
        
        click.echo(f"   ✓ Generated {fix_result['fixes_count']} fixes")
        
        # Final summary
        click.echo("\n" + "=" * 50)
        click.echo("✨ Pipeline complete! Generated files:")
        click.echo(f"\n📁 Analysis Results:")
        click.echo(f"   • JSON: {report_path.name}")
        
        html_files = list(output_dir.glob("ux_report_*.html"))
        if html_files:
            click.echo(f"   • HTML: {html_files[-1].name}")
            
        click.echo(f"\n📁 Generated Fixes:")
        click.echo(f"   • CSS: {Path(fix_result['css_file']).name}")
        if fix_result['js_file']:
            click.echo(f"   • JavaScript: {Path(fix_result['js_file']).name}")
        click.echo(f"   • Guide: {Path(fix_result['guide']).name}")
        
        # Open in browser if requested
        if open_all:
            if html_files:
                webbrowser.open(str(html_files[-1]))
            webbrowser.open(fix_result['guide'])
            
        # Provide next steps
        click.echo("\n📌 Next steps:")
        click.echo("   1. Review the implementation guide")
        click.echo("   2. Test the generated fixes in your development environment")
        click.echo("   3. Customize as needed for your specific design")
        click.echo("   4. Deploy after thorough testing")
        
    except Exception as e:
        click.echo(f"\n❌ Pipeline error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def demo():
    """Run a demo with a sample image"""
    click.echo("\n🎯 Running UX-MIRROR demo...")
    
    sample_url = "https://via.placeholder.com/800x600/007bff/ffffff?text=Demo+UI+Screenshot"
    
    # Run full pipeline on demo
    ctx = click.get_current_context()
    ctx.invoke(full_pipeline, source=sample_url, open_all=True)


@cli.command()
def version():
    """Show version information"""
    click.echo("\nUX-MIRROR CLI v1.0.0")
    click.echo("AI-Driven UX Analysis and Fix Generation")
    click.echo("Part of the UX-MIRROR Project")


@cli.command()
def stats():
    """Show statistics about generated reports and fixes"""
    click.echo("\n📊 UX-MIRROR Statistics")
    click.echo("=" * 40)
    
    # Count analysis reports
    analysis_dir = Path("ux_analysis_results")
    if analysis_dir.exists():
        json_count = len(list(analysis_dir.glob("*.json")))
        html_count = len(list(analysis_dir.glob("*.html")))
        click.echo(f"\n📄 Analysis Reports:")
        click.echo(f"   • JSON reports: {json_count}")
        click.echo(f"   • HTML reports: {html_count}")
    
    # Count generated fixes
    fixes_dir = Path("generated_fixes")
    if fixes_dir.exists():
        css_count = len(list(fixes_dir.glob("*.css")))
        js_count = len(list(fixes_dir.glob("*.js")))
        guide_count = len(list(fixes_dir.glob("implementation_guide_*.html")))
        click.echo(f"\n🔧 Generated Fixes:")
        click.echo(f"   • CSS files: {css_count}")
        click.echo(f"   • JavaScript files: {js_count}")
        click.echo(f"   • Implementation guides: {guide_count}")
    
    # Calculate total storage
    total_size = 0
    for dir_path in [analysis_dir, fixes_dir]:
        if dir_path.exists():
            for file in dir_path.iterdir():
                if file.is_file():
                    total_size += file.stat().st_size
                    
    click.echo(f"\n💾 Total storage used: {total_size / 1024:.1f} KB")


if __name__ == '__main__':
    # Add ASCII art banner
    banner = """
    ╔╦╗╔╦╗  ╔╦╗╦╔═╗╔═╗╔═╗╔═╗
    ║ ║╔╩╦╝  ║║║║╠╦╝╠╦╝║ ║╠╦╝
    ╚═╝╩ ╚═  ╩ ╩╩╩╚═╩╚═╚═╝╩╚═
    AI-Driven UX Analysis & Fix Generation
    """
    print(banner)
    cli() 