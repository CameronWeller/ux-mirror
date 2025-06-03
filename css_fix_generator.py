#!/usr/bin/env python3
"""
UX-MIRROR CSS Fix Generator
===========================

Generates CSS fixes for common UX issues detected by the analysis system.
Part of Phase 3: Code Generation deliverables.

Author: UX-MIRROR Team
"""

import json
from pathlib import Path
from datetime import datetime
import colorsys

class CSSFixGenerator:
    """Generate CSS fixes for detected UX issues"""
    
    def __init__(self):
        self.fixes_generated = []
        self.output_dir = Path("generated_fixes")
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_fixes_from_report(self, analysis_report_path):
        """Generate CSS fixes from an analysis report"""
        with open(analysis_report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
            
        css_fixes = []
        js_fixes = []
        
        for issue in report.get('ux_issues', []):
            if issue['type'] == 'contrast':
                css_fixes.extend(self._generate_contrast_fix(issue))
            elif issue['type'] == 'usability':
                css_fixes.extend(self._generate_usability_fix(issue))
            elif issue['type'] == 'accessibility':
                css_fixes.extend(self._generate_accessibility_fix(issue))
                js_fixes.extend(self._generate_accessibility_js(issue))
                
        # Generate CSS file
        css_content = self._compile_css(css_fixes)
        css_path = self._save_css(css_content)
        
        # Generate JS file if needed
        js_content = self._compile_js(js_fixes)
        js_path = self._save_js(js_content) if js_content else None
        
        # Generate implementation guide
        guide_path = self._generate_implementation_guide(css_fixes, js_fixes)
        
        return {
            "css_file": str(css_path),
            "js_file": str(js_path) if js_path else None,
            "guide": str(guide_path),
            "fixes_count": len(css_fixes) + len(js_fixes)
        }
        
    def _generate_contrast_fix(self, issue):
        """Generate CSS to fix contrast issues"""
        fixes = []
        
        # Calculate improved colors
        bg_color = "#ffffff"  # Default white background
        text_color = "#212529"  # Dark gray for better contrast
        
        fixes.append({
            "selector": ".low-contrast-text",
            "properties": {
                "color": f"{text_color} !important",
                "background-color": f"{bg_color}",
                "text-shadow": "0 0 1px rgba(0,0,0,0.1)"
            },
            "comment": "Fix for low contrast text - WCAG AA compliant"
        })
        
        # Additional fixes for common elements
        fixes.append({
            "selector": "a.low-contrast",
            "properties": {
                "color": "#0066cc !important",
                "text-decoration": "underline"
            },
            "comment": "Ensure links are distinguishable"
        })
        
        return fixes
        
    def _generate_usability_fix(self, issue):
        """Generate CSS to fix usability issues"""
        fixes = []
        
        if "too small" in issue.get('description', ''):
            fixes.append({
                "selector": "button, .btn, input[type='button'], input[type='submit']",
                "properties": {
                    "min-width": "48px",
                    "min-height": "48px",
                    "padding": "12px 16px",
                    "font-size": "16px",
                    "cursor": "pointer"
                },
                "comment": "Ensure touch targets meet minimum size requirements"
            })
            
            # Mobile-specific improvements
            fixes.append({
                "selector": "@media (max-width: 768px)",
                "nested": {
                    "button, .btn": {
                        "min-width": "44px",
                        "min-height": "44px",
                        "margin": "4px"
                    }
                },
                "comment": "Mobile-optimized touch targets"
            })
            
        return fixes
        
    def _generate_accessibility_fix(self, issue):
        """Generate CSS accessibility fixes"""
        fixes = []
        
        # Focus indicators
        fixes.append({
            "selector": ":focus",
            "properties": {
                "outline": "3px solid #4A90E2",
                "outline-offset": "2px"
            },
            "comment": "Visible focus indicators for keyboard navigation"
        })
        
        # Skip links
        fixes.append({
            "selector": ".skip-link",
            "properties": {
                "position": "absolute",
                "left": "-9999px",
                "top": "0",
                "z-index": "999"
            },
            "comment": "Skip navigation link styling"
        })
        
        fixes.append({
            "selector": ".skip-link:focus",
            "properties": {
                "left": "0",
                "background": "#000",
                "color": "#fff",
                "padding": "8px",
                "text-decoration": "none"
            },
            "comment": "Skip link visible on focus"
        })
        
        return fixes
        
    def _generate_accessibility_js(self, issue):
        """Generate JavaScript for accessibility improvements"""
        fixes = []
        
        if issue.get('element', {}).get('type') == 'image':
            fixes.append({
                "name": "addMissingAltText",
                "code": """
// Auto-add descriptive alt text for images missing it
function addMissingAltText() {
    const images = document.querySelectorAll('img:not([alt])');
    images.forEach((img, index) => {
        // Try to infer alt text from nearby content
        const parent = img.closest('article, section, div');
        const heading = parent?.querySelector('h1, h2, h3, h4, h5, h6');
        const figcaption = img.closest('figure')?.querySelector('figcaption');
        
        let altText = 'Decorative image';
        if (figcaption) {
            altText = figcaption.textContent.trim();
        } else if (heading) {
            altText = `Image related to: ${heading.textContent.trim()}`;
        } else if (img.src.includes('logo')) {
            altText = 'Company logo';
        }
        
        img.setAttribute('alt', altText);
        console.log(`Added alt text to image ${index + 1}: "${altText}"`);
    });
}

// Run on page load
document.addEventListener('DOMContentLoaded', addMissingAltText);
""",
                "description": "Automatically adds alt text to images"
            })
            
        return fixes
        
    def _compile_css(self, fixes):
        """Compile CSS fixes into a single stylesheet"""
        css_lines = [
            "/* UX-MIRROR Auto-Generated CSS Fixes */",
            f"/* Generated: {datetime.now().isoformat()} */",
            "/* Apply these fixes to resolve detected UX issues */",
            "",
        ]
        
        for fix in fixes:
            if 'comment' in fix:
                css_lines.append(f"\n/* {fix['comment']} */")
                
            if 'nested' in fix:
                # Handle media queries and nested rules
                css_lines.append(f"{fix['selector']} {{")
                for nested_selector, props in fix['nested'].items():
                    css_lines.append(f"  {nested_selector} {{")
                    for prop, value in props.items():
                        css_lines.append(f"    {prop}: {value};")
                    css_lines.append("  }")
                css_lines.append("}")
            else:
                css_lines.append(f"{fix['selector']} {{")
                for prop, value in fix['properties'].items():
                    css_lines.append(f"  {prop}: {value};")
                css_lines.append("}")
                
        return "\n".join(css_lines)
        
    def _compile_js(self, fixes):
        """Compile JavaScript fixes"""
        if not fixes:
            return ""
            
        js_lines = [
            "// UX-MIRROR Auto-Generated JavaScript Fixes",
            f"// Generated: {datetime.now().isoformat()}",
            "// Accessibility and UX improvements",
            "",
            "(function() {",
            "  'use strict';",
            "",
        ]
        
        for fix in fixes:
            js_lines.append(f"  // {fix['description']}")
            js_lines.append(fix['code'])
            js_lines.append("")
            
        js_lines.extend([
            "  // Initialize all fixes",
            "  console.log('UX-MIRROR fixes applied');",
            "})();"
        ])
        
        return "\n".join(js_lines)
        
    def _save_css(self, content):
        """Save CSS content to file"""
        filename = f"ux_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.css"
        path = self.output_dir / filename
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return path
        
    def _save_js(self, content):
        """Save JavaScript content to file"""
        filename = f"ux_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.js"
        path = self.output_dir / filename
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return path
        
    def _generate_implementation_guide(self, css_fixes, js_fixes):
        """Generate implementation guide HTML"""
        guide_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>UX-MIRROR Fix Implementation Guide</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .code-block {{ background: #f4f4f4; padding: 15px; border-radius: 5px; 
                      overflow-x: auto; margin: 15px 0; }}
        .fix-item {{ background: #e8f4f8; padding: 15px; margin: 15px 0; 
                    border-left: 4px solid #3498db; }}
        .warning {{ background: #fff3cd; padding: 10px; border-radius: 5px; 
                   margin: 15px 0; border-left: 4px solid #ffc107; }}
        code {{ background: #e9ecef; padding: 2px 5px; border-radius: 3px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                 gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; 
                     text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
    </style>
</head>
<body>
    <h1>UX-MIRROR Fix Implementation Guide</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{len(css_fixes)}</div>
            <div>CSS Fixes</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(js_fixes)}</div>
            <div>JavaScript Fixes</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(css_fixes) + len(js_fixes)}</div>
            <div>Total Fixes</div>
        </div>
    </div>
    
    <h2>Implementation Steps</h2>
    
    <div class="fix-item">
        <h3>Step 1: Add CSS Fixes</h3>
        <p>Add the following line to your HTML <code>&lt;head&gt;</code> section:</p>
        <div class="code-block">
            &lt;link rel="stylesheet" href="ux_fixes_[timestamp].css"&gt;
        </div>
        <p>Or include the CSS directly in your existing stylesheet.</p>
    </div>
    
    {f'''<div class="fix-item">
        <h3>Step 2: Add JavaScript Fixes</h3>
        <p>Add the following line before your closing <code>&lt;/body&gt;</code> tag:</p>
        <div class="code-block">
            &lt;script src="ux_fixes_[timestamp].js"&gt;&lt;/script&gt;
        </div>
    </div>''' if js_fixes else ''}
    
    <div class="warning">
        <strong>⚠️ Important:</strong> Test these fixes in a development environment first. 
        Some fixes use <code>!important</code> which may override existing styles.
    </div>
    
    <h2>Applied Fixes</h2>
    
    <h3>CSS Fixes ({len(css_fixes)})</h3>
    {self._format_fix_list(css_fixes)}
    
    {f'<h3>JavaScript Fixes ({len(js_fixes)})</h3>{self._format_js_fix_list(js_fixes)}' if js_fixes else ''}
    
    <h2>Testing Checklist</h2>
    <ul>
        <li>✓ Test on multiple screen sizes (mobile, tablet, desktop)</li>
        <li>✓ Verify keyboard navigation works properly</li>
        <li>✓ Check color contrast with browser tools</li>
        <li>✓ Test with screen readers if accessibility fixes were applied</li>
        <li>✓ Ensure no existing functionality is broken</li>
    </ul>
    
    <h2>Next Steps</h2>
    <ol>
        <li>Review the generated fixes</li>
        <li>Test in your development environment</li>
        <li>Customize as needed for your specific design</li>
        <li>Deploy to production after thorough testing</li>
    </ol>
</body>
</html>
"""
        
        guide_path = self.output_dir / f"implementation_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
            
        return guide_path
        
    def _format_fix_list(self, fixes):
        """Format CSS fixes for the guide"""
        items = []
        for fix in fixes:
            comment = fix.get('comment', 'Style improvement')
            selector = fix['selector']
            items.append(f'<li><code>{selector}</code> - {comment}</li>')
        return '<ul>' + '\n'.join(items) + '</ul>' if items else '<p>No CSS fixes generated.</p>'
        
    def _format_js_fix_list(self, fixes):
        """Format JS fixes for the guide"""
        items = []
        for fix in fixes:
            items.append(f'<li><strong>{fix["name"]}</strong> - {fix["description"]}</li>')
        return '<ul>' + '\n'.join(items) + '</ul>' if items else ''


def demo():
    """Demo the CSS fix generator"""
    print("=== UX-MIRROR CSS Fix Generator Demo ===")
    
    # First, create a sample analysis report
    sample_report = {
        "timestamp": datetime.now().isoformat(),
        "source": "demo",
        "ux_issues": [
            {
                "type": "contrast",
                "severity": "high",
                "description": "Low contrast between text and background"
            },
            {
                "type": "usability",
                "severity": "medium",
                "description": "Button too small for touch targets"
            },
            {
                "type": "accessibility",
                "severity": "high",
                "element": {"type": "image"},
                "description": "Image missing alt text"
            }
        ]
    }
    
    # Save sample report
    report_path = Path("sample_analysis.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(sample_report, f)
    
    # Generate fixes
    generator = CSSFixGenerator()
    result = generator.generate_fixes_from_report(report_path)
    
    print("\nGenerated files:")
    print(f"- CSS: {result['css_file']}")
    if result['js_file']:
        print(f"- JavaScript: {result['js_file']}")
    print(f"- Implementation Guide: {result['guide']}")
    print(f"\nTotal fixes generated: {result['fixes_count']}")
    
    # Clean up
    report_path.unlink()


if __name__ == "__main__":
    demo() 