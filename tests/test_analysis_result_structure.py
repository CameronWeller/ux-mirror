#!/usr/bin/env python3
"""
Test Claude Analysis Result Structure
Tests for Phase 1, Step 12 of v0.1.0 release
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    # Try importing from project root
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ai_vision_analyzer", 
        project_root / "ai_vision_analyzer.py"
    )
    if spec and spec.loader:
        ai_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ai_module)
        GameUIAnalysis = ai_module.GameUIAnalysis
    else:
        raise ImportError("Could not load module")
except Exception as e:
    try:
        # Fallback: direct import
        from ai_vision_analyzer import GameUIAnalysis
    except ImportError:
        GameUIAnalysis = None
        print(f"[WARNING] GameUIAnalysis not available: {e}")


def test_dataclass_structure():
    """Test 12.1: Review GameUIAnalysis dataclass"""
    if not GameUIAnalysis:
        print("[SKIP] GameUIAnalysis not available")
        return False
    
    # Check required fields exist
    required_fields = [
        'timestamp', 'overall_assessment', 'issues_found', 
        'recommendations', 'ui_elements_detected', 'clutter_score',
        'readability_score', 'visual_hierarchy_score', 'specific_problems'
    ]
    
    # Get field names from dataclass
    import dataclasses
    if dataclasses.is_dataclass(GameUIAnalysis):
        field_names = [f.name for f in dataclasses.fields(GameUIAnalysis)]
        
        for field in required_fields:
            assert field in field_names, f"Required field '{field}' missing"
        
        print("[OK] All required fields are present in GameUIAnalysis")
        return True
    else:
        print("[ERROR] GameUIAnalysis is not a dataclass")
        return False


def test_to_json_method():
    """Test 12.3: Test to_json() method"""
    if not GameUIAnalysis:
        print("[SKIP] GameUIAnalysis not available")
        return False
    
    # Create test analysis
    analysis = GameUIAnalysis(
        timestamp=datetime.now(),
        overall_assessment="Test assessment",
        issues_found=[{"type": "test", "severity": "low"}],
        recommendations=["Test recommendation"],
        ui_elements_detected=[{"type": "button", "location": "top"}],
        clutter_score=0.5,
        readability_score=0.7,
        visual_hierarchy_score=0.6,
        specific_problems=["Test problem"]
    )
    
    # Test to_json
    json_str = analysis.to_json()
    assert json_str is not None, "to_json() should return a string"
    
    # Verify it's valid JSON
    data = json.loads(json_str)
    assert 'timestamp' in data, "JSON should contain timestamp"
    assert 'overall_assessment' in data, "JSON should contain overall_assessment"
    
    print("[OK] to_json() method works correctly")
    return True


def test_timestamp_format():
    """Test 12.4: Verify timestamp format (ISO 8601)"""
    if not GameUIAnalysis:
        print("[SKIP] GameUIAnalysis not available")
        return False
    
    analysis = GameUIAnalysis(
        timestamp=datetime.now(),
        overall_assessment="Test",
        issues_found=[],
        recommendations=[],
        ui_elements_detected=[],
        clutter_score=0.5,
        readability_score=0.5,
        visual_hierarchy_score=0.5,
        specific_problems=[]
    )
    
    json_str = analysis.to_json()
    data = json.loads(json_str)
    
    # Check timestamp is ISO format
    timestamp_str = data['timestamp']
    try:
        # Try to parse as ISO format
        datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        print("[OK] Timestamp is in ISO 8601 format")
        return True
    except ValueError:
        print(f"[ERROR] Timestamp format invalid: {timestamp_str}")
        return False


def test_scores_are_floats():
    """Test 12.5: Verify scores are floats 0.0-1.0"""
    if not GameUIAnalysis:
        print("[SKIP] GameUIAnalysis not available")
        return False
    
    analysis = GameUIAnalysis(
        timestamp=datetime.now(),
        overall_assessment="Test",
        issues_found=[],
        recommendations=[],
        ui_elements_detected=[],
        clutter_score=0.5,
        readability_score=0.7,
        visual_hierarchy_score=0.6,
        specific_problems=[]
    )
    
    # Check types
    assert isinstance(analysis.clutter_score, float), \
        "clutter_score should be float"
    assert isinstance(analysis.readability_score, float), \
        "readability_score should be float"
    assert isinstance(analysis.visual_hierarchy_score, float), \
        "visual_hierarchy_score should be float"
    
    # Check ranges
    assert 0.0 <= analysis.clutter_score <= 1.0, \
        "clutter_score should be 0.0-1.0"
    assert 0.0 <= analysis.readability_score <= 1.0, \
        "readability_score should be 0.0-1.0"
    assert 0.0 <= analysis.visual_hierarchy_score <= 1.0, \
        "visual_hierarchy_score should be 0.0-1.0"
    
    print("[OK] All scores are floats in range 0.0-1.0")
    return True


def test_issues_found_structure():
    """Test 12.6: Verify issues_found is list of dicts"""
    if not GameUIAnalysis:
        print("[SKIP] GameUIAnalysis not available")
        return False
    
    analysis = GameUIAnalysis(
        timestamp=datetime.now(),
        overall_assessment="Test",
        issues_found=[
            {"type": "contrast", "severity": "high", "location": "button"},
            {"type": "spacing", "severity": "medium", "location": "menu"}
        ],
        recommendations=[],
        ui_elements_detected=[],
        clutter_score=0.5,
        readability_score=0.5,
        visual_hierarchy_score=0.5,
        specific_problems=[]
    )
    
    assert isinstance(analysis.issues_found, list), \
        "issues_found should be a list"
    assert all(isinstance(issue, dict) for issue in analysis.issues_found), \
        "All issues should be dictionaries"
    
    print("[OK] issues_found is list of dicts")
    return True


def test_recommendations_structure():
    """Test 12.7: Verify recommendations is list of strings"""
    if not GameUIAnalysis:
        print("[SKIP] GameUIAnalysis not available")
        return False
    
    analysis = GameUIAnalysis(
        timestamp=datetime.now(),
        overall_assessment="Test",
        issues_found=[],
        recommendations=["Fix contrast", "Add spacing", "Improve hierarchy"],
        ui_elements_detected=[],
        clutter_score=0.5,
        readability_score=0.5,
        visual_hierarchy_score=0.5,
        specific_problems=[]
    )
    
    assert isinstance(analysis.recommendations, list), \
        "recommendations should be a list"
    assert all(isinstance(rec, str) for rec in analysis.recommendations), \
        "All recommendations should be strings"
    
    print("[OK] recommendations is list of strings")
    return True


def validate_result_structure(analysis: GameUIAnalysis) -> bool:
    """Test 12.8: Add validation function for result structure"""
    if not GameUIAnalysis:
        return False
    
    try:
        # Check all required fields
        assert hasattr(analysis, 'timestamp'), "Missing timestamp"
        assert hasattr(analysis, 'overall_assessment'), "Missing overall_assessment"
        assert hasattr(analysis, 'issues_found'), "Missing issues_found"
        assert hasattr(analysis, 'recommendations'), "Missing recommendations"
        assert hasattr(analysis, 'clutter_score'), "Missing clutter_score"
        assert hasattr(analysis, 'readability_score'), "Missing readability_score"
        assert hasattr(analysis, 'visual_hierarchy_score'), "Missing visual_hierarchy_score"
        
        # Check types
        assert isinstance(analysis.timestamp, datetime), "timestamp should be datetime"
        assert isinstance(analysis.overall_assessment, str), "overall_assessment should be str"
        assert isinstance(analysis.issues_found, list), "issues_found should be list"
        assert isinstance(analysis.recommendations, list), "recommendations should be list"
        assert isinstance(analysis.clutter_score, float), "clutter_score should be float"
        
        return True
    except AssertionError as e:
        print(f"[ERROR] Validation failed: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Claude Analysis Result Structure Tests")
    print("=" * 60)
    print()
    print("Phase 1, Step 12: Verify Claude analysis result structure")
    print()
    
    results = []
    
    print("Testing dataclass structure...")
    results.append(("Dataclass structure", test_dataclass_structure()))
    print()
    
    print("Testing to_json() method...")
    results.append(("to_json() method", test_to_json_method()))
    print()
    
    print("Testing timestamp format...")
    results.append(("Timestamp format", test_timestamp_format()))
    print()
    
    print("Testing scores are floats...")
    results.append(("Scores are floats", test_scores_are_floats()))
    print()
    
    print("Testing issues_found structure...")
    results.append(("issues_found structure", test_issues_found_structure()))
    print()
    
    print("Testing recommendations structure...")
    results.append(("recommendations structure", test_recommendations_structure()))
    print()
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All structure tests passed!")
    else:
        print("\n[WARNING] Some structure tests failed")

