"""
Test script to demonstrate enhanced AI detection accuracy
Creates sample code files to test detection capabilities
"""

import os
import json
from analyzer.enhanced_detector import EnhancedCopilotDetector

def create_test_files():
    """Create test files with known AI vs human characteristics"""
    
    # AI-generated style code (high confidence expected)
    ai_style_code = '''
def calculate_user_metrics(user_data: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate comprehensive user metrics from provided data.
    
    Args:
        user_data: List of user dictionaries containing user information
        
    Returns:
        Dictionary containing calculated metrics
    """
    try:
        total_users = len(user_data)
        active_users = len([user for user in user_data if user.get('active', False)])
        
        metrics = {
            'total_users': float(total_users),
            'active_users': float(active_users),
            'activity_rate': active_users / total_users if total_users > 0 else 0.0
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return {}
    finally:
        logger.info("Metrics calculation completed")

def process_user_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process and validate user data"""
    processed_data = []
    
    for user in data:
        if validate_user_data(user):
            processed_user = {
                'id': user.get('id'),
                'name': user.get('name', '').strip(),
                'email': user.get('email', '').lower(),
                'active': user.get('active', False)
            }
            processed_data.append(processed_user)
    
    return processed_data

def validate_user_data(user: Dict[str, Any]) -> bool:
    """Validate individual user data"""
    required_fields = ['id', 'name', 'email']
    return all(field in user for field in required_fields)
'''

    # Human-written style code (low confidence expected)
    human_style_code = '''
# Quick fix for user stats
def get_stats(users):
    cnt = 0
    active = 0
    for u in users:
        cnt += 1
        if u['status'] == 'active':
            active += 1
    
    return {
        'total': cnt,
        'active': active,
        'rate': active/cnt if cnt > 0 else 0
    }

# Helper function
def clean_data(data):
    result = []
    for item in data:
        # Basic validation
        if 'id' in item and 'name' in item:
            clean_item = {
                'id': item['id'],
                'name': item['name'].strip() if item['name'] else '',
                'email': item.get('email', '').lower()
            }
            result.append(clean_item)
    return result

# Another utility
def check_user(user):
    return user.get('id') and user.get('name') and '@' in user.get('email', '')
'''

    # Mixed style code (medium confidence expected)
    mixed_style_code = '''
import json
from typing import Dict, List

def process_metrics(data):
    """Process user metrics with mixed approaches"""
    total = len(data)
    active_count = 0
    
    # Quick loop
    for user in data:
        if user.get('active'):
            active_count += 1
    
    def calculate_advanced_metrics(users: List[Dict]) -> Dict[str, float]:
        """Calculate advanced user engagement metrics"""
        try:
            engagement_scores = [
                user.get('engagement_score', 0.0) 
                for user in users 
                if 'engagement_score' in user
            ]
            
            return {
                'avg_engagement': sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.0,
                'max_engagement': max(engagement_scores) if engagement_scores else 0.0
            }
        except Exception as e:
            print(f"Error: {e}")
            return {}
    
    advanced = calculate_advanced_metrics(data)
    
    return {
        'basic_stats': {'total': total, 'active': active_count},
        'advanced_metrics': advanced
    }
'''

    # Write test files
    os.makedirs('test_files', exist_ok=True)
    
    with open('test_files/ai_style.py', 'w') as f:
        f.write(ai_style_code)
    
    with open('test_files/human_style.py', 'w') as f:
        f.write(human_style_code)
    
    with open('test_files/mixed_style.py', 'w') as f:
        f.write(mixed_style_code)

def test_detection_accuracy():
    """Test the enhanced detector on sample files"""
    
    # Initialize detector with config
    config = {
        'comment_patterns': ['copilot', 'generated', 'ai'],
        'high_velocity_threshold': 0.8,
        'perfect_syntax_weight': 0.3,
        'common_patterns_weight': 0.4,
        'complexity_threshold': 10
    }
    
    detector = EnhancedCopilotDetector(config)
    
    test_files = [
        ('test_files/ai_style.py', 'AI-Style Code'),
        ('test_files/human_style.py', 'Human-Style Code'),
        ('test_files/mixed_style.py', 'Mixed-Style Code')
    ]
    
    results = {}
    
    print("Enhanced AI Detection Accuracy Test")
    print("=" * 50)
    
    for file_path, description in test_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            analysis = detector.analyze_content(content, '.py')
            results[description] = analysis
            
            print(f"\n{description}:")
            print(f"  Confidence Score: {analysis['confidence_score']:.3f}")
            print(f"  Risk Level: {analysis['risk_level']}")
            print(f"  Language: {analysis['language']}")
            
            print(f"  Indicators:")
            for indicator, value in analysis['indicators'].items():
                print(f"    {indicator}: {value}")
            
            print(f"  Detailed Scores:")
            for score_type, score in analysis['detailed_scores'].items():
                print(f"    {score_type}: {score:.3f}")
    
    # Save detailed results
    with open('detection_accuracy_test.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: detection_accuracy_test.json")
    
    return results

if __name__ == "__main__":
    create_test_files()
    test_detection_accuracy()