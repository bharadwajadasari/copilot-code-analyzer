#!/usr/bin/env python3
"""
Test Evasion-Resistant AI Detection
Demonstrates how the enhanced detector handles code that's been processed through formatters
"""

import json
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer.evasion_resistant_detector import EvasionResistantDetector

def create_test_samples():
    """Create test samples showing original AI code vs formatted versions"""
    
    # Original AI-generated code
    original_ai_code = '''
def process_data(data, options=None, validate=True):
    """
    Process the provided data with optional validation and configuration.
    
    Args:
        data: The input data to process
        options: Optional configuration dictionary
        validate: Whether to validate input data
        
    Returns:
        Processed data result
        
    Raises:
        ValueError: If data validation fails
    """
    if data is None:
        return None
    
    result = {}
    
    if validate and data:
        if not isinstance(data, (dict, list)):
            raise ValueError("Data must be dict or list")
    
    try:
        if options is not None and options.get('transform'):
            for item in data:
                if item is not None:
                    result[item] = process_item(item)
        else:
            result = data
    except Exception as e:
        print(f"Error processing data: {e}")
        return None
    
    return result

def process_item(item):
    """Process individual item with validation"""
    if item is None:
        return None
    
    return str(item).upper()
'''

    # Same code after running through Black formatter + manual obfuscation
    formatted_ai_code = '''
def process_data(d, opts=None, val=True):
    # Process input with config
    if d is None:
        return None

    res = {}

    if val and d:
        if not isinstance(d, (dict, list)):
            raise ValueError("Invalid input type")

    try:
        if opts is not None and opts.get("transform"):
            for i in d:
                if i is not None:
                    res[i] = process_item(i)
        else:
            res = d
    except Exception as ex:
        print(f"Processing failed: {ex}")
        return None

    return res


def process_item(i):
    # Individual item processing
    if i is None:
        return None

    return str(i).upper()
'''

    # Human-written equivalent
    human_code = '''
def process_user_data(user_input, config=None, should_validate=True):
    # Quick and dirty data processor I wrote for the user management system
    if not user_input:
        return None
    
    output = {}
    
    # Validate if needed (sometimes we skip this for performance)
    if should_validate:
        if type(user_input) not in [dict, list]:
            raise ValueError("Wrong data type")
    
    # Main processing loop - could probably optimize this later
    try:
        if config and 'transform' in config and config['transform']:
            # Transform each item
            for item in user_input:
                if item:  # Skip empty items
                    output[item] = transform_single_item(item)
        else:
            # Just pass through
            output = user_input
    except:
        # TODO: Better error handling
        print("Something went wrong")
        return None
    
    return output

def transform_single_item(item):
    # Convert to uppercase - simple but effective
    return str(item).upper() if item else None
'''

    return {
        'original_ai': original_ai_code,
        'formatted_ai': formatted_ai_code,
        'human_written': human_code
    }

def test_evasion_resistance():
    """Test the evasion-resistant detector"""
    
    print("Testing Evasion-Resistant AI Detection")
    print("=" * 50)
    
    # Initialize detector
    config = {
        'ai_indicators': {
            'strong_indicators': [],
            'moderate_indicators': [],
            'weak_indicators': []
        }
    }
    
    detector = EvasionResistantDetector(config)
    
    # Get test samples
    samples = create_test_samples()
    
    # Test each sample
    results = {}
    
    for sample_name, code in samples.items():
        print(f"\nAnalyzing {sample_name.replace('_', ' ').title()}:")
        print("-" * 30)
        
        analysis = detector.analyze_content(code, '.py')
        results[sample_name] = analysis
        
        print(f"AI Confidence: {analysis['copilot_confidence']:.2%}")
        print(f"Risk Level: {analysis['risk_level']}")
        
        # Show evasion resistance details
        evasion_data = analysis['evasion_resistance']
        print(f"Semantic Score: {evasion_data['semantic_score']:.2f}")
        print(f"AST Structure Score: {evasion_data['ast_score']:.2f}")
        print(f"Complexity Score: {evasion_data['complexity_score']:.2f}")
        
        if evasion_data['evasion_detected']:
            print(f"⚠️  Evasion Attempts: {', '.join(evasion_data['evasion_indicators'])}")
        
        print("Explanation:")
        for explanation in analysis['explanation']:
            print(f"  • {explanation}")
    
    # Summary comparison
    print("\n" + "=" * 50)
    print("DETECTION SUMMARY")
    print("=" * 50)
    
    for sample_name, result in results.items():
        confidence = result['copilot_confidence']
        evasion_detected = result['evasion_resistance']['evasion_detected']
        
        print(f"{sample_name.replace('_', ' ').title():<20}: {confidence:.1%} AI confidence", end="")
        if evasion_detected:
            print(" [EVASION DETECTED]")
        else:
            print()
    
    # Analysis insights
    print("\n" + "=" * 50)
    print("KEY INSIGHTS")
    print("=" * 50)
    
    original_conf = results['original_ai']['copilot_confidence']
    formatted_conf = results['formatted_ai']['copilot_confidence']
    human_conf = results['human_written']['copilot_confidence']
    
    detection_resilience = (formatted_conf / original_conf) if original_conf > 0 else 0
    
    print(f"Detection Resilience: {detection_resilience:.1%}")
    print(f"  Original AI Code: {original_conf:.1%}")
    print(f"  Formatted AI Code: {formatted_conf:.1%}")
    print(f"  Human Code: {human_conf:.1%}")
    
    if detection_resilience > 0.7:
        print("✅ Strong evasion resistance - formatting didn't fool the detector")
    elif detection_resilience > 0.4:
        print("⚠️ Moderate evasion resistance - some detection lost to formatting")
    else:
        print("❌ Weak evasion resistance - formatting significantly reduced detection")
    
    print("\nTechniques that help detect formatted AI code:")
    print("• Semantic pattern analysis (logic structures survive formatting)")
    print("• Abstract Syntax Tree analysis (code structure independent of style)")
    print("• Complexity pattern recognition (AI complexity signatures persist)")
    print("• Algorithmic choice analysis (AI preferences remain detectable)")
    print("• Deep linguistic analysis (AI documentation patterns)")

if __name__ == "__main__":
    test_evasion_resistance()