#!/usr/bin/env python3
"""
Practical example showing exactly what gets sent to Anthropic API
Current vs. Improved approach for UX-MIRROR
"""

import json
import base64
from datetime import datetime

# Simulate what currently gets sent to Anthropic API
def current_api_call_example():
    """Shows the current basic API call structure"""
    
    # This is what your current ux_mirror_launcher.py sends
    current_prompt = """Analyze this game/application screenshot for UX and UI issues (Iteration 3). 

Provide a JSON response with:
1. "quality_score": Overall UI quality (0.0-1.0)
2. "ui_elements_detected": Number of UI elements you can identify
3. "issues_found": List of specific UI/UX problems
4. "recommendations": List of actionable improvement suggestions
5. "accessibility_issues": List of accessibility concerns
6. "response_time": How responsive the interface appears (0.0-1.0)
7. "change_score": How much has changed since last iteration (0.0-1.0)

Focus on: button spacing, text readability, color contrast, layout clarity, navigation ease, visual hierarchy.
Be specific and actionable in your recommendations."""

    # Current API payload structure
    current_payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": current_prompt
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": "[BASE64_IMAGE_DATA_HERE]"
                        }
                    }
                ]
            }
        ]
    }
    
    return current_payload, current_prompt

def improved_api_call_example():
    """Shows the improved comprehensive API call structure"""
    
    # Detected context (this would be auto-detected in real implementation)
    context = {
        "app_type": "desktop application",
        "resolution": "1920x1080",
        "platform": "Windows 11",
        "user_demographics": "productivity users",
        "use_case": "document editing",
        "iteration": 3,
        "previous_issues": "color contrast, button sizing"
    }
    
    # Comprehensive prompt with context
    improved_prompt = f"""You are an expert UX/UI analyst and accessibility consultant analyzing a {context['app_type']} screenshot. 

**CONTEXT & METADATA:**
- Application Type: {context['app_type']}
- Screen Resolution: {context['resolution']}
- Target Platform: {context['platform']}
- User Demographics: {context['user_demographics']}
- Primary Use Case: {context['use_case']}
- Analysis Iteration: {context['iteration']}
- Previous Issues Tracked: {context['previous_issues']}

**COMPREHENSIVE ANALYSIS FRAMEWORK:**

**1. VISUAL HIERARCHY & INFORMATION ARCHITECTURE**
- Analyze the visual flow and information prioritization
- Assess whether the most important elements are prominent
- Evaluate grouping and categorization of related elements
- Check for proper use of whitespace and visual separation

**2. USABILITY & INTERACTION DESIGN**
- Identify all interactive elements (buttons, links, forms, controls)
- Assess button/touch target sizes (minimum 44px recommended)
- Evaluate feedback mechanisms and system status indicators
- Check for consistent interaction patterns and affordances

**3. ACCESSIBILITY COMPLIANCE (WCAG 2.1 AA Standards)**
- Color contrast ratios (minimum 4.5:1 for normal text, 3:1 for large text)
- Text scaling and readability at 200% zoom
- Focus indicators and keyboard navigation support
- Alternative text and semantic structure
- Color-blind and motion sensitivity considerations

**4. RESPONSIVE DESIGN & LAYOUT**
- Element positioning and alignment consistency
- Spacing consistency (margins, padding, gutters)
- Grid system adherence and breakpoint handling
- Content overflow and truncation handling

**5. TYPOGRAPHY & CONTENT PRESENTATION**
- Font size hierarchy (minimum 16px for body text recommended)
- Line height, letter spacing, and readability metrics
- Content density and cognitive load assessment
- Multilingual and RTL support considerations

**6. USER JOURNEY & WORKFLOW ANALYSIS**
- Primary action paths and conversion funnels
- Error states and recovery mechanisms
- Navigation breadcrumbs and user orientation
- Progressive disclosure and information scoping

**7. PLATFORM-SPECIFIC GUIDELINES**
- {context['platform']} Human Interface Guidelines compliance
- Native UI patterns vs. custom components
- Platform-appropriate gestures and interactions
- System integration and consistency

**8. PERFORMANCE & TECHNICAL UX**
- Loading states and progressive enhancement
- Image optimization and visual quality
- Animation smoothness and purposefulness
- Error handling and offline states

**STRUCTURED OUTPUT FORMAT:**
Provide your analysis in the following JSON structure:

{{
  "analysis_metadata": {{
    "timestamp": "{datetime.now().isoformat()}",
    "app_type": "{context['app_type']}",
    "analysis_version": "v2.0_comprehensive"
  }},
  "overall_assessment": {{
    "quality_score": 0.0-1.0,
    "confidence_level": 0.0-1.0,
    "executive_summary": "2-3 sentence overview",
    "critical_issues_count": 0
  }},
  "visual_hierarchy": {{
    "score": 0.0-1.0,
    "primary_focus_clear": boolean,
    "information_grouping": "excellent/good/needs_work/poor",
    "whitespace_usage": "assessment",
    "issues": ["specific issues found"]
  }},
  "usability_analysis": {{
    "interaction_score": 0.0-1.0,
    "target_sizes_adequate": boolean,
    "feedback_mechanisms": ["list of feedback types observed"],
    "consistency_score": 0.0-1.0,
    "critical_usability_issues": ["high-priority issues"]
  }},
  "accessibility_audit": {{
    "wcag_compliance_estimate": "AA/A/Non-compliant",
    "contrast_issues": [
      {{
        "location": "specific location",
        "foreground_color": "#hex",
        "background_color": "#hex",
        "contrast_ratio": 0.0,
        "severity": "high/medium/low"
      }}
    ],
    "text_scaling_issues": ["issues when scaled"],
    "focus_visibility": "assessment",
    "accessibility_score": 0.0-1.0
  }},
  "detailed_findings": [
    {{
      "category": "visual_hierarchy/usability/accessibility/etc",
      "severity": "critical/high/medium/low",
      "location": "specific screen location",
      "issue_description": "detailed description",
      "impact_on_users": "how this affects user experience",
      "recommended_solution": "specific actionable fix",
      "effort_estimate": "low/medium/high",
      "wcag_violation": "if applicable, which guideline"
    }}
  ],
  "prioritized_recommendations": [
    {{
      "priority": 1,
      "category": "category name",
      "action": "specific action to take",
      "expected_impact": "high/medium/low",
      "implementation_complexity": "low/medium/high",
      "success_metrics": ["how to measure improvement"]
    }}
  ],
  "comparison_with_previous": {{
    "improvements_noted": ["improvements since last analysis"],
    "new_issues_identified": ["new problems found"],
    "regression_analysis": ["things that got worse"],
    "progress_score": 0.0-1.0
  }}
}}

**ANALYSIS GUIDELINES:**
- Be extremely specific about locations (use coordinates, element descriptions)
- Provide quantitative measurements where possible
- Consider the target user context and use cases
- Balance technical feasibility with user impact
- Flag any potential legal/compliance issues (ADA, GDPR, etc.)
- Suggest A/B testing opportunities for uncertain recommendations
- Consider mobile-first and inclusive design principles
- Assess cognitive load and mental model alignment

**CRITICAL EVALUATION CRITERIA:**
- Does this interface serve its primary purpose effectively?
- Can users with disabilities successfully use this interface?
- Are there any dark patterns or manipulative design elements?
- Does the design respect user privacy and autonomy?
- Is the interface future-proof and maintainable?

Please provide comprehensive, actionable, and user-centered analysis that goes beyond surface-level observations to deliver strategic UX insights."""

    # Improved API payload structure
    improved_payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 2000,  # Increased for comprehensive response
        "temperature": 0.1,  # Lower temperature for consistent analysis
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": improved_prompt
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": "[BASE64_IMAGE_DATA_HERE]"
                        }
                    }
                ]
            }
        ]
    }
    
    return improved_payload, improved_prompt, context

def compare_api_calls():
    """Compare the two approaches side by side"""
    
    current_payload, current_prompt = current_api_call_example()
    improved_payload, improved_prompt, context = improved_api_call_example()
    
    print("=" * 80)
    print("CURRENT API CALL TO ANTHROPIC")
    print("=" * 80)
    print(f"Model: {current_payload['model']}")
    print(f"Max Tokens: {current_payload['max_tokens']}")
    print(f"Temperature: {current_payload.get('temperature', 'default')}")
    print(f"Prompt Length: {len(current_prompt)} characters")
    print(f"Prompt Word Count: {len(current_prompt.split())} words")
    print("\nPrompt Preview (first 200 chars):")
    print(f'"{current_prompt[:200]}..."')
    
    print("\n" + "=" * 80)
    print("IMPROVED API CALL TO ANTHROPIC")
    print("=" * 80)
    print(f"Model: {improved_payload['model']}")
    print(f"Max Tokens: {improved_payload['max_tokens']}")
    print(f"Temperature: {improved_payload['temperature']}")
    print(f"Prompt Length: {len(improved_prompt)} characters")
    print(f"Prompt Word Count: {len(improved_prompt.split())} words")
    print("\nContext Added:")
    for key, value in context.items():
        print(f"  • {key}: {value}")
    print("\nPrompt Preview (first 200 chars):")
    print(f'"{improved_prompt[:200]}..."')
    
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    
    improvement_factor = len(improved_prompt) / len(current_prompt)
    token_increase = (improved_payload['max_tokens'] - current_payload['max_tokens']) / current_payload['max_tokens'] * 100
    
    print(f"Prompt size increase: {improvement_factor:.1f}x larger")
    print(f"Token limit increase: +{token_increase:.0f}%")
    print(f"Context awareness: None -> Full context integration")
    print(f"Analysis depth: Basic -> 8 comprehensive frameworks")
    print(f"Accessibility: Generic mention -> WCAG 2.1 AA compliance")
    print(f"Output structure: Simple JSON -> Rich structured analysis")
    print(f"Actionability: Basic recommendations -> Prioritized with effort estimates")
    
    print("\nEXPECTED IMPROVEMENT IN AI RESPONSES:")
    print("+ More specific and actionable recommendations")
    print("+ WCAG-compliant accessibility analysis")
    print("+ Platform-specific guidance")
    print("+ Prioritized issues with effort estimates")
    print("+ Progress tracking between iterations")
    print("+ Quantitative scoring and metrics")
    print("+ Strategic UX insights, not just surface observations")

if __name__ == "__main__":
    compare_api_calls() 