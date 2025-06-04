
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
