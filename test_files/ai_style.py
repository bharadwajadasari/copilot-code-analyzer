
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
