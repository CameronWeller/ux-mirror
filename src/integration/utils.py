#!/usr/bin/env python3
"""
Utility functions for Playwright integration

Helper functions to make working with Playwright adapter easier
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path


def load_test_steps(file_path: str) -> List[Dict[str, Any]]:
    """
    Load test steps from a JSON file.
    
    Args:
        file_path: Path to JSON file with test steps
        
    Returns:
        List of test step dictionaries
        
    Example JSON format:
    [
        {
            "type": "navigate",
            "url": "https://example.com",
            "description": "Navigate to homepage"
        },
        {
            "type": "click",
            "selector": "button.submit",
            "description": "Click submit button"
        },
        {
            "type": "type",
            "selector": "input[name='email']",
            "text": "test@example.com",
            "description": "Enter email"
        }
    ]
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Test steps file not found: {file_path}")
    
    with open(path, 'r') as f:
        steps = json.load(f)
    
    if not isinstance(steps, list):
        raise ValueError("Test steps file must contain a JSON array")
    
    return steps


def save_test_steps(steps: List[Dict[str, Any]], file_path: str):
    """
    Save test steps to a JSON file.
    
    Args:
        steps: List of test step dictionaries
        file_path: Path to save JSON file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(steps, f, indent=2)


def create_navigation_step(url: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Create a navigation test step."""
    return {
        "type": "navigate",
        "url": url,
        "description": description or f"Navigate to {url}"
    }


def create_click_step(selector: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Create a click test step."""
    return {
        "type": "click",
        "selector": selector,
        "description": description or f"Click {selector}"
    }


def create_type_step(selector: str, text: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Create a type/fill test step."""
    return {
        "type": "type",
        "selector": selector,
        "text": text,
        "description": description or f"Type '{text}' into {selector}"
    }


def create_wait_step(timeout: int = 1000, description: Optional[str] = None) -> Dict[str, Any]:
    """Create a wait test step."""
    return {
        "type": "wait",
        "timeout": timeout,
        "description": description or f"Wait {timeout}ms"
    }


def format_analysis_results(results: Dict[str, Any]) -> str:
    """
    Format analysis results for display.
    
    Args:
        results: Results dictionary from adapter
        
    Returns:
        Formatted string
    """
    output = []
    output.append("=" * 60)
    output.append("UX Analysis Results")
    output.append("=" * 60)
    
    if "url" in results:
        output.append(f"\nURL: {results['url']}")
    
    if results.get("screenshot_captured"):
        output.append(f"Screenshot: ✅ Captured")
        if "screenshot_size" in results:
            output.append(f"Size: {results['screenshot_size']}")
    
    if "feedback" in results:
        feedback = results["feedback"]
        
        if "summary" in feedback:
            output.append(f"\n📝 Summary:")
            output.append(feedback["summary"])
        
        if "priority_fixes" in feedback and feedback["priority_fixes"]:
            output.append(f"\n🎯 Top Issues:")
            for issue in feedback["priority_fixes"][:5]:
                desc = issue.get('description', 'Unknown')
                severity = issue.get('severity', 'unknown')
                output.append(f"  • {desc} ({severity})")
        
        if "recommendations" in feedback and feedback["recommendations"]:
            output.append(f"\n💡 Recommendations:")
            for rec in feedback["recommendations"][:5]:
                output.append(f"  • {rec}")
        
        if "code_suggestions" in feedback and feedback["code_suggestions"]:
            output.append(f"\n💻 Code Suggestions:")
            for suggestion in feedback["code_suggestions"][:3]:
                output.append(f"  {suggestion}")
    
    output.append("\n" + "=" * 60)
    return "\n".join(output)


def validate_test_step(step: Dict[str, Any]) -> bool:
    """
    Validate a test step dictionary.
    
    Args:
        step: Test step dictionary
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    if not isinstance(step, dict):
        raise ValueError("Test step must be a dictionary")
    
    if "type" not in step:
        raise ValueError("Test step must have a 'type' field")
    
    step_type = step["type"]
    valid_types = ["navigate", "click", "type", "fill", "select", "hover", "wait"]
    
    if step_type not in valid_types:
        raise ValueError(f"Invalid step type: {step_type}. Must be one of {valid_types}")
    
    # Type-specific validation
    if step_type == "navigate":
        if "url" not in step:
            raise ValueError("Navigation step must have 'url' field")
    elif step_type in ["click", "type", "fill", "select", "hover"]:
        if "selector" not in step:
            raise ValueError(f"{step_type} step must have 'selector' field")
    elif step_type == "type":
        if "text" not in step:
            raise ValueError("Type step must have 'text' field")
    elif step_type == "wait":
        if "timeout" not in step:
            raise ValueError("Wait step must have 'timeout' field")
    
    return True

