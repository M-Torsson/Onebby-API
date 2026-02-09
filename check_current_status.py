# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
Check current product and category status
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"


# 1. Check categories
response = requests.get(f"{BASE_URL}/api/v1/categories", params={"limit": 500}, timeout=30)
if response.status_code == 200:
    cats = response.json()['data']
    
    parents = [c for c in cats if not c.get('parent_id')]
    children = [c for c in cats if c.get('parent_id') and c['id'] not in [gc.get('parent_id') for gc in cats if gc.get('parent_id')]]
    grandchildren = [c for c in cats if c.get('parent_id') and any(gc.get('parent_id') == c['id'] for gc in cats)]
    

# 2. Check products
response = requests.get(f"{BASE_URL}/api/v1/products", params={"limit": 10, "active_only": False}, timeout=30)
if response.status_code == 200:
    data = response.json()
    products = data['data']
    total = data['meta']['total']
    
    
    # Check first few products for category info
    with_category = 0
    without_category = 0
    
    for p in products:
        if p.get('categories'):
            with_category += 1
        else:
            without_category += 1
    
    
    # Show sample
    if products:
        first = products[0]
