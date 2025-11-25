#!/usr/bin/env python3
"""
Comprehensive UX/UI Analysis Prompt Structure
Comparison of current vs. improved prompting for Anthropic API
"""

# CURRENT BASIC PROMPT (from ux_mirror_launcher.py)
CURRENT_BASIC_PROMPT = """Analyze this game/application screenshot for UX and UI issues (Iteration {iteration}). 

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

# IMPROVED COMPREHENSIVE PROMPT
COMPREHENSIVE_UX_PROMPT = """You are an expert UX/UI analyst and accessibility consultant analyzing a {app_type} application screenshot. 

**CONTEXT & METADATA:**
- Application Type: {app_type}
- Screen Resolution: {resolution}
- Target Platform: {platform}
- User Demographics: {user_demographics}
- Primary Use Case: {use_case}
- Analysis Iteration: {iteration}
- Previous Issues Tracked: {previous_issues}

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
- {platform} Human Interface Guidelines compliance
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
    "timestamp": "ISO datetime",
    "app_type": "{app_type}",
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
  "responsive_design": {{
    "layout_consistency": 0.0-1.0,
    "spacing_consistency": 0.0-1.0,
    "content_adaptation": "assessment",
    "breakpoint_handling": "assessment"
  }},
  "typography_analysis": {{
    "readability_score": 0.0-1.0,
    "font_size_hierarchy": "clear/unclear",
    "line_height_assessment": "adequate/inadequate",
    "content_density": "appropriate/too_dense/too_sparse"
  }},
  "user_journey_assessment": {{
    "primary_actions_clear": boolean,
    "navigation_clarity": 0.0-1.0,
    "error_handling_visible": boolean,
    "workflow_efficiency": 0.0-1.0
  }},
  "platform_compliance": {{
    "guideline_adherence": 0.0-1.0,
    "native_patterns_used": boolean,
    "platform_consistency": "assessment",
    "recommendations": ["platform-specific suggestions"]
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
  }},
  "next_steps": {{
    "immediate_actions": ["critical fixes needed now"],
    "short_term_goals": ["improvements for next iteration"],
    "long_term_strategy": ["strategic UX improvements"],
    "testing_recommendations": ["suggested user testing approaches"]
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

# Example of how to use the comprehensive prompt
def create_comprehensive_prompt(app_type="web application", resolution="1920x1080", 
                              platform="desktop", user_demographics="general", 
                              use_case="productivity", iteration=1, previous_issues="none"):
    """Create a comprehensive UX analysis prompt with context"""
    return COMPREHENSIVE_UX_PROMPT.format(
        app_type=app_type,
        resolution=resolution,
        platform=platform,
        user_demographics=user_demographics,
        use_case=use_case,
        iteration=iteration,
        previous_issues=previous_issues
    )

# Comparison analysis
PROMPT_COMPARISON = {
    "current_prompt": {
        "length": len(CURRENT_BASIC_PROMPT.split()),
        "focus_areas": 7,
        "specificity": "Low - generic analysis",
        "context_awareness": "None",
        "accessibility_depth": "Minimal mention",
        "actionability": "Basic recommendations",
        "structure": "Simple JSON response"
    },
    "comprehensive_prompt": {
        "length": len(COMPREHENSIVE_UX_PROMPT.split()),
        "focus_areas": 8,
        "specificity": "High - detailed framework",
        "context_awareness": "Full context integration",
        "accessibility_depth": "WCAG 2.1 AA compliance",
        "actionability": "Prioritized, effort-estimated actions",
        "structure": "Comprehensive structured analysis"
    }
}

if __name__ == "__main__":
    print("=== UX-MIRROR PROMPT ANALYSIS ===")
    print(f"Current prompt: {PROMPT_COMPARISON['current_prompt']['length']} words")
    print(f"Comprehensive prompt: {PROMPT_COMPARISON['comprehensive_prompt']['length']} words")
    print(f"Improvement factor: {PROMPT_COMPARISON['comprehensive_prompt']['length'] / PROMPT_COMPARISON['current_prompt']['length']:.1f}x more detailed")
    print("\nCURRENT PROMPT LIMITATIONS:")
    for key, value in PROMPT_COMPARISON['current_prompt'].items():
        if key != 'length':
            print(f"❌ {key}: {value}")
    
    print("\nCOMPREHENSIVE PROMPT IMPROVEMENTS:")
    for key, value in PROMPT_COMPARISON['comprehensive_prompt'].items():
        if key != 'length':
            print(f"✅ {key}: {value}")
    
    print("\n=== SUMMARY OF CRITICAL GAPS IN CURRENT APPROACH ===")
    print("🚨 Missing Context: No app type, platform, or user info")
    print("🚨 Weak Accessibility: Only mentions 'accessibility issues' generically")
    print("🚨 No Standards: No reference to WCAG, platform guidelines")
    print("🚨 Basic Output: Simple list vs. structured analysis")
    print("🚨 No Prioritization: All issues treated equally")
    print("🚨 No Progress Tracking: Can't compare iterations effectively")
    print("🚨 Limited Actionability: Generic recommendations")
    
    print("\n=== RECOMMENDED NEXT STEPS ===")
    print("1. Implement comprehensive prompt in ux_mirror_launcher.py")
    print("2. Add context detection for different app types")
    print("3. Integrate WCAG compliance checking")
    print("4. Add progress tracking between iterations")
    print("5. Implement recommendation prioritization")
    print("6. Add effort estimation for fixes") 