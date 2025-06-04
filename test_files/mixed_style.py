
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
