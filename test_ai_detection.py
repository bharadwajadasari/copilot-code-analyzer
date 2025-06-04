"""
AI Detection Calibration Test
Tests the balanced detector with known AI-generated code patterns
"""

from analyzer.balanced_detector import BalancedCopilotDetector

def test_ai_patterns():
    """Test detector with various code patterns"""
    
    # Initialize detector
    config = {
        'comment_patterns': ['copilot', 'generated', 'ai'],
        'high_velocity_threshold': 0.8,
        'perfect_syntax_weight': 0.3,
        'common_patterns_weight': 0.4,
    }
    
    detector = BalancedCopilotDetector(config)
    
    # Test 1: Typical AI-generated code (should detect ~30-50%)
    ai_code = '''
def calculate_user_metrics(user_data: List[Dict[str, Any]]) -> Optional[Dict[str, float]]:
    """
    Calculate comprehensive user metrics from provided data.
    
    Args:
        user_data: List of user dictionaries containing user information
        
    Returns:
        Dictionary containing calculated metrics or None if error occurs
        
    Example:
        >>> users = [{'name': 'John', 'active': True}]
        >>> calculate_user_metrics(users)
        {'total_users': 1.0, 'active_users': 1.0, 'activity_rate': 1.0}
    """
    try:
        if not user_data or not isinstance(user_data, list):
            logger.warning("Invalid user data provided")
            return None
            
        total_users = len(user_data)
        active_users = len([user for user in user_data if user.get('active', False)])
        
        metrics = {
            'total_users': float(total_users),
            'active_users': float(active_users),
            'activity_rate': active_users / total_users if total_users > 0 else 0.0
        }
        
        logger.info(f"Calculated metrics for {total_users} users")
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating user metrics: {e}")
        return None
    finally:
        logger.debug("User metrics calculation completed")

def process_data_batch(data_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process a batch of data with validation and transformation.
    
    Args:
        data_batch: List of data dictionaries to process
        
    Returns:
        List of processed and validated data dictionaries
    """
    processed_data = []
    
    for item in data_batch:
        if validate_data_item(item):
            processed_item = {
                'id': item.get('id'),
                'name': item.get('name', '').strip(),
                'email': item.get('email', '').lower(),
                'created_at': item.get('created_at'),
                'status': item.get('status', 'pending')
            }
            processed_data.append(processed_item)
    
    return processed_data

def validate_data_item(item: Dict[str, Any]) -> bool:
    """
    Validate individual data item.
    
    Args:
        item: Data dictionary to validate
        
    Returns:
        True if item is valid, False otherwise
    """
    required_fields = ['id', 'name', 'email']
    return all(field in item and item[field] for field in required_fields)

if __name__ == "__main__":
    main()
'''
    
    # Test 2: Human-style code (should detect ~5-15%)
    human_code = '''
# quick fix for user stats
def get_stats(users):
    cnt = 0
    active = 0
    for u in users:
        cnt += 1
        if u['status'] == 'active':
            active += 1
    
    return {'total': cnt, 'active': active, 'rate': active/cnt if cnt > 0 else 0}

# helper func
def clean_data(data):
    result = []
    for item in data:
        # basic check
        if 'id' in item and 'name' in item:
            clean_item = {
                'id': item['id'],
                'name': item['name'].strip() if item['name'] else '',
                'email': item.get('email', '').lower()
            }
            result.append(clean_item)
    return result

def check_user(user):
    # TODO: add more validation
    return user.get('id') and user.get('name') and '@' in user.get('email', '')
'''
    
    # Test 3: Mixed style code (should detect ~20-35%)
    mixed_code = '''
from typing import Dict, List, Optional

def process_user_metrics(data):
    """Process user metrics with mixed coding styles"""
    total = len(data)
    active_count = 0
    
    # Quick loop through users
    for user in data:
        if user.get('active'):
            active_count += 1
    
    def calculate_advanced_metrics(users: List[Dict]) -> Optional[Dict[str, float]]:
        """
        Calculate advanced user engagement metrics.
        
        Args:
            users: List of user dictionaries
            
        Returns:
            Dictionary containing advanced metrics or None if error
        """
        try:
            engagement_scores = [
                user.get('engagement_score', 0.0) 
                for user in users 
                if 'engagement_score' in user
            ]
            
            if not engagement_scores:
                return None
                
            return {
                'avg_engagement': sum(engagement_scores) / len(engagement_scores),
                'max_engagement': max(engagement_scores),
                'min_engagement': min(engagement_scores)
            }
        except Exception as e:
            print(f"Error calculating advanced metrics: {e}")
            return None
    
    advanced = calculate_advanced_metrics(data)
    
    return {
        'basic_stats': {'total': total, 'active': active_count},
        'advanced_metrics': advanced
    }
'''
    
    test_cases = [
        ("AI-style code", ai_code),
        ("Human-style code", human_code),
        ("Mixed-style code", mixed_code)
    ]
    
    print("AI Detection Calibration Test")
    print("=" * 50)
    
    for description, code in test_cases:
        analysis = detector.analyze_content(code, '.py')
        
        print(f"\n{description}:")
        print(f"  Confidence Score: {analysis['confidence_score']:.3f} ({analysis['confidence_score']:.1%})")
        print(f"  Risk Level: {analysis['risk_level']}")
        print(f"  Estimated AI Lines: {analysis['estimated_lines']}/{analysis['total_analyzed_lines']}")
        
        print(f"  Strong Indicators: {analysis['detailed_scores']['strong_indicators']:.3f}")
        print(f"  Moderate Indicators: {analysis['detailed_scores']['moderate_indicators']:.3f}")
        print(f"  Weak Indicators: {analysis['detailed_scores']['weak_indicators']:.3f}")
        print(f"  Human Patterns: {analysis['detailed_scores']['human_patterns']:.3f}")
        
        print(f"  Explanation: {analysis['analysis_explanation'][0]}")

if __name__ == "__main__":
    test_ai_patterns()