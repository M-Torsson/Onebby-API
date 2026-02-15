# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
Complete analysis before starting product categorization
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"


# 1. Categories Analysis
categories_response = requests.get(
    f"{BASE_URL}/api/v1/categories",
    params={"limit": 500},
    timeout=30
)

if categories_response.status_code == 200:
    cats_data = categories_response.json()
    all_cats = cats_data['data']
    
    # Analyze structure
    parents = {}
    children = {}
    grandchildren = {}
    
    for cat in all_cats:
        cat_id = cat['id']
        cat_name = cat['name']
        parent_id = cat.get('parent_id')
        
        if not parent_id:
            parents[cat_id] = cat_name
        else:
            # Check if it's a child or grandchild
            is_grandchild = False
            for c in all_cats:
                pass
                if c['id'] == parent_id and c.get('parent_id'):
                    is_grandchild = True
                    grandchildren[cat_id] = cat_name
                    break
            
            if not is_grandchild:
                children[cat_id] = cat_name
    
    
    # Show main categories
    for cat_id, cat_name in list(parents.items())[:8]:
        pass

# 2. Products Analysis
products_response = requests.get(
    f"{BASE_URL}/api/v1/products",
    params={"limit": 500, "active_only": False},
    timeout=60
)

if products_response.status_code == 200:
    prod_data = products_response.json()
    total_products = prod_data['meta']['total']
    products = prod_data['data']
    
    
    # Check current categorization
    with_cat = [p for p in products if p.get('categories')]
    without_cat = [p for p in products if not p.get('categories')]
    
    
    # Check product structure
    if products:
        sample = products[0]

# 3. Assessment
