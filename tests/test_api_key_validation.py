#!/usr/bin/env python3
"""
API Key Validation Test Script
Tests for Phase 1, Step 5 of v0.1.0 release
"""

import os
import sys
import re
from pathlib import Path
from typing import Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def validate_anthropic_key_format(api_key: str) -> Tuple[bool, str]:
    """
    Test 5.2: Validate Anthropic API key format
    
    Anthropic keys should:
    - Start with 'sk-ant-'
    - Be at least 20 characters long
    - Contain only alphanumeric characters and hyphens
    
    Returns:
        (is_valid, error_message)
    """
    if not api_key:
        return False, "API key is empty"
    
    if not api_key.startswith('sk-ant-'):
        return False, "Anthropic API key must start with 'sk-ant-'"
    
    if len(api_key) < 20:
        return False, "API key appears to be too short"
    
    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
        return False, "API key contains invalid characters"
    
    return True, "Valid Anthropic API key format"


def validate_openai_key_format(api_key: str) -> Tuple[bool, str]:
    """
    Test 5.3: Validate OpenAI API key format
    
    OpenAI keys should:
    - Start with 'sk-'
    - Be at least 20 characters long
    - Contain only alphanumeric characters
    
    Returns:
        (is_valid, error_message)
    """
    if not api_key:
        return False, "API key is empty"
    
    if not api_key.startswith('sk-'):
        return False, "OpenAI API key must start with 'sk-'"
    
    if len(api_key) < 20:
        return False, "API key appears to be too short"
    
    # OpenAI keys are typically alphanumeric
    if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
        return False, "API key contains invalid characters"
    
    return True, "Valid OpenAI API key format"


def check_key_presence(key_name: str) -> Tuple[bool, Optional[str]]:
    """
    Test 5.4: Check if API key is present in environment
    
    Args:
        key_name: Environment variable name (e.g., 'ANTHROPIC_API_KEY')
    
    Returns:
        (is_present, key_value_or_none)
    """
    key_value = os.getenv(key_name)
    is_present = key_value is not None and key_value.strip() != ""
    
    return is_present, key_value


def validate_all_keys() -> dict:
    """
    Test 5.5: Validate all API keys
    
    Returns:
        Dictionary with validation results
    """
    results = {
        'anthropic': {
            'present': False,
            'valid_format': False,
            'value': None,
            'error': None
        },
        'openai': {
            'present': False,
            'valid_format': False,
            'value': None,
            'error': None
        }
    }
    
    # Check Anthropic key
    is_present, key_value = check_key_presence('ANTHROPIC_API_KEY')
    results['anthropic']['present'] = is_present
    results['anthropic']['value'] = key_value if is_present else None
    
    if is_present:
        is_valid, error_msg = validate_anthropic_key_format(key_value)
        results['anthropic']['valid_format'] = is_valid
        results['anthropic']['error'] = None if is_valid else error_msg
    else:
        results['anthropic']['error'] = "ANTHROPIC_API_KEY not set in environment"
    
    # Check OpenAI key
    is_present, key_value = check_key_presence('OPENAI_API_KEY')
    results['openai']['present'] = is_present
    results['openai']['value'] = key_value if is_present else None
    
    if is_present:
        is_valid, error_msg = validate_openai_key_format(key_value)
        results['openai']['valid_format'] = is_valid
        results['openai']['error'] = None if is_valid else error_msg
    else:
        results['openai']['error'] = "OPENAI_API_KEY not set (optional)"
    
    return results


def print_validation_results(results: dict):
    """Print validation results in a readable format"""
    print("=" * 60)
    print("API Key Validation Results")
    print("=" * 60)
    print()
    
    # Anthropic key
    print("Anthropic API Key (ANTHROPIC_API_KEY):")
    anth = results['anthropic']
    if anth['present']:
        if anth['valid_format']:
            print("  [OK] Key is present and format is valid")
            print(f"  Key preview: {anth['value'][:15]}...")
        else:
            print("  [ERROR] Key is present but format is invalid")
            print(f"  Error: {anth['error']}")
    else:
        print("  [MISSING] Key is not set in environment")
        print(f"  Error: {anth['error']}")
    print()
    
    # OpenAI key
    print("OpenAI API Key (OPENAI_API_KEY):")
    openai = results['openai']
    if openai['present']:
        if openai['valid_format']:
            print("  [OK] Key is present and format is valid")
            print(f"  Key preview: {openai['value'][:15]}...")
        else:
            print("  [ERROR] Key is present but format is invalid")
            print(f"  Error: {openai['error']}")
    else:
        print("  [OPTIONAL] Key is not set (OpenAI is optional)")
        print(f"  Note: {openai['error']}")
    print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    anthropic_ok = anth['present'] and anth['valid_format']
    openai_ok = not openai['present'] or openai['valid_format']  # Optional
    
    if anthropic_ok:
        print("[SUCCESS] Anthropic API key is configured correctly")
        print("  You can use Claude for AI vision analysis")
    else:
        print("[WARNING] Anthropic API key needs attention")
        print("  Set it with: $env:ANTHROPIC_API_KEY = 'your-key' (PowerShell)")
        print("  Or: export ANTHROPIC_API_KEY='your-key' (Linux/Mac)")
    
    if openai['present']:
        if openai_ok:
            print("[SUCCESS] OpenAI API key is configured correctly")
        else:
            print("[WARNING] OpenAI API key format is invalid")
    else:
        print("[INFO] OpenAI API key is optional (not required)")
    
    print()
    
    return anthropic_ok and (not openai['present'] or openai_ok)


if __name__ == '__main__':
    print()
    print("API Key Validation Script")
    print("Phase 1, Step 5: Create test script for API key validation")
    print()
    
    results = validate_all_keys()
    success = print_validation_results(results)
    
    sys.exit(0 if success else 1)


