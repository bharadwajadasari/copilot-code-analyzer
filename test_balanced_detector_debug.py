#!/usr/bin/env python3
"""
Debug Balanced Detector Issues
Test why AI-generated code is being classified as human-written
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer.balanced_detector import BalancedCopilotDetector

def test_ai_generated_file():
    """Test the balanced detector on a known AI-generated file"""
    
    # Initialize detector
    detector = BalancedCopilotDetector({})
    
    # Test with this file (AI-generated)
    with open('analyzer/balanced_detector.py', 'r') as f:
        content = f.read()
    
    print("Testing Balanced Detector on analyzer/balanced_detector.py")
    print("=" * 60)
    print(f"File size: {len(content):,} characters")
    lines_count = len(content.split('\n'))
    print(f"Lines: {lines_count} lines")
    print()
    
    # Analyze the content
    result = detector.analyze_content(content, '.py')
    
    # Print detailed results
    print("ANALYSIS RESULTS:")
    print("-" * 40)
    print(f"Final Confidence: {result['confidence_score']:.1%}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Estimated AI Lines: {result['estimated_lines']}/{result['total_analyzed_lines']}")
    print()
    
    print("DETAILED SCORES:")
    print("-" * 40)
    scores = result['detailed_scores']
    for key, value in scores.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f} ({value:.1%})")
        else:
            print(f"{key}: {value}")
    print()
    
    print("INDICATORS DETECTED:")
    print("-" * 40)
    indicators = result['indicators']
    for key, value in indicators.items():
        status = "✓ YES" if value else "✗ NO"
        print(f"{key}: {status}")
    print()
    
    print("ANALYSIS EXPLANATION:")
    print("-" * 40)
    for explanation in result['analysis_explanation']:
        print(f"• {explanation}")
    print()
    
    # Test specific patterns
    print("PATTERN MATCHING DEBUG:")
    print("-" * 40)
    
    # Check for explicit AI markers
    import re
    ai_markers = [
        r'#\s*AI-generated',
        r'Balanced Copilot Detection Engine',
        r'Uses contextual analysis',
        r'def __init__',
        r'"""[\s\S]*?"""',  # Docstrings
        r'from typing import'
    ]
    
    for pattern_text in ai_markers:
        pattern = re.compile(pattern_text, re.MULTILINE | re.IGNORECASE)
        matches = pattern.findall(content)
        print(f"Pattern '{pattern_text}': {len(matches)} matches")
        if matches and len(matches) <= 3:  # Show first few matches
            for match in matches[:3]:
                print(f"  → '{match[:50]}...'")
    
    print()
    print("THRESHOLD ANALYSIS:")
    print("-" * 40)
    
    # Show how thresholds are affecting the score
    base_confidence = scores['base_confidence']
    print(f"Base confidence before thresholds: {base_confidence:.3f} ({base_confidence:.1%})")
    
    # Simulate threshold application
    total_lines = result['total_analyzed_lines']
    simulated_confidence = base_confidence
    
    if total_lines < 20:
        simulated_confidence *= 0.5
        print(f"Small file penalty (lines < 20): NOT APPLIED (lines = {total_lines})")
    elif total_lines < 50:
        simulated_confidence *= 0.7
        print(f"Medium file penalty (lines < 50): NOT APPLIED (lines = {total_lines})")
    
    if simulated_confidence > 0.2 and total_lines > 30:
        old_confidence = simulated_confidence
        simulated_confidence = min(simulated_confidence * 0.6, 0.15)
        print(f"Conservative cap applied: {old_confidence:.3f} → {simulated_confidence:.3f}")
    
    if simulated_confidence < 0.08:
        print(f"Minimum threshold applied: {simulated_confidence:.3f} → 0.0 (ZEROED OUT)")
        simulated_confidence = 0.0
    
    print(f"Final confidence after thresholds: {simulated_confidence:.3f} ({simulated_confidence:.1%})")
    
    # Analysis
    print()
    print("ISSUE ANALYSIS:")
    print("-" * 40)
    
    if result['confidence_score'] == 0.0:
        print("❌ PROBLEM: Confidence zeroed out by minimum threshold")
        print("   The 8% minimum threshold is too aggressive")
    elif result['confidence_score'] < 0.1:
        print("❌ PROBLEM: Confidence heavily reduced by conservative cap")
        print("   The 15% maximum cap is too restrictive for AI-generated code")
    
    if base_confidence > 0.2:
        print("✓ DETECTION: Base algorithm detected AI patterns")
        print("   Issue is in the threshold application, not pattern matching")
    else:
        print("❌ DETECTION: Base algorithm failed to detect AI patterns")
        print("   Issue is in the pattern matching logic")

def test_simple_ai_sample():
    """Test with a simple AI-generated code sample"""
    
    print()
    print("TESTING SIMPLE AI-GENERATED SAMPLE:")
    print("=" * 60)
    
    ai_sample = '''
def process_user_data(user_data, validate_input=True):
    """
    Process user data with validation and error handling.
    
    Args:
        user_data (list): List of user data items to process
        validate_input (bool): Whether to validate input data
        
    Returns:
        dict: Processed data with count and items
        
    Example:
        >>> process_user_data(['item1', 'item2'])
        {'data': ['item1', 'item2'], 'count': 2}
    """
    if user_data is None or len(user_data) == 0:
        return {}
    
    result = {}
    try:
        if validate_input:
            user_data = validate_user_data(user_data)
        
        processed_data = []
        for item in user_data:
            if item is not None:
                processed_item = transform_user_item(item)
                processed_data.append(processed_item)
        
        result["data"] = processed_data
        result["count"] = len(processed_data)
        
    except Exception as e:
        logger.error(f"Error processing user data: {e}")
        return {}
    
    return result

def validate_user_data(user_data):
    """Validate user data items."""
    return [item for item in user_data if item]

def transform_user_item(item):
    """Transform individual user item."""
    return str(item).lower()
'''
    
    detector = BalancedCopilotDetector({})
    result = detector.analyze_content(ai_sample, '.py')
    
    print(f"Confidence: {result['confidence_score']:.1%}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"AI Lines: {result['estimated_lines']}/{result['total_analyzed_lines']}")
    
    print("Explanations:")
    for explanation in result['analysis_explanation']:
        print(f"• {explanation}")

if __name__ == "__main__":
    test_ai_generated_file()
    test_simple_ai_sample()