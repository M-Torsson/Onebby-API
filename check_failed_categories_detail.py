# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
Check specific failed categories with their children
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"

failed_ids = [8159, 8167, 8179, 8180, 8192, 8193, 8195, 8197, 8198]


all_children = []

for cat_id in failed_ids:
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/categories/{cat_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()['data']
            
            children = data.get('children', [])
            if children:
                pass
                for child in children:
                    all_children.append(child['id'])
            else:
                pass
                
        elif response.status_code == 404:
            pass
        else:
            pass
            
    except Exception as e:
        pass

if all_children:
    pass

# Save children IDs
if all_children:
    with open('children_to_delete.txt', 'w') as f:
        pass
        for child_id in all_children:
            f.write(f"{child_id}\n")
