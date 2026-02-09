# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
Check electronics products and their categories
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"

electronics_keywords = [
    'lavatrice', 'frigorifero', 'forno', 'microonde', 'lavastoviglie',
    'tv', 'televisore', 'computer', 'notebook', 'laptop', 'tablet', 
    'smartphone', 'cellulare', 'telefono', 'condizionatore', 'climatizzatore',
    'aspirapolvere', 'robot', 'frullatore', 'mixer', 'tostapane',
    'macchina caffè', 'bollitore', 'ferro da stiro', 'asciugacapelli',
    'monitor', 'stampante', 'scanner', 'cuffie', 'speaker', 'soundbar'
]


# Get products
response = requests.get(
    f"{BASE_URL}/api/v1/products",
    timeout=60
)

if response.status_code != 200:
    exit(1)

products = response.json()['data']

electronics_found = []

for product in products:
    title = product.get('title', '').lower()
    reference = product.get('reference', '').lower()
    
    # Check if it's electronics
    is_electronics = any(kw in title or kw in reference for kw in electronics_keywords)
    
    if is_electronics and len(electronics_found) < 15:  # Get 15 electronics samples
        # Get full details
        detail_response = requests.get(
            f"{BASE_URL}/api/v1/products/{product['id']}",
            timeout=10
        )
        
        if detail_response.status_code == 200:
            detailed = detail_response.json()['data']
            electronics_found.append(detailed)
            
            if len(electronics_found) >= 15:
                break

if not electronics_found:
    exit(1)


for idx, product in enumerate(electronics_found, 1):
    pass
    
    categories = product.get('categories', [])
    if categories:
        pass
        for cat in categories:
            parent_info = ""
            if cat.get('parent'):
                parent = cat['parent']
                if parent.get('parent'):
                    grandparent = parent['parent']
                    parent_info = f" ← {parent.get('name', 'N/A')} ← {grandparent.get('name', 'N/A')}"
                else:
                    parent_info = f" ← {parent.get('name', 'N/A')}"
            
    else:
        pass


# Collect all unique categories
all_categories = set()
for product in electronics_found:
    pass
    for cat in product.get('categories', []):
        cat_name = cat.get('name', '')
        if cat_name:
            all_categories.add(cat_name)
        if cat.get('parent'):
            parent_name = cat['parent'].get('name', '')
            if parent_name:
                all_categories.add(parent_name)
            if cat['parent'].get('parent'):
                grandparent_name = cat['parent']['parent'].get('name', '')
                if grandparent_name:
                    all_categories.add(grandparent_name)

for cat_name in sorted(all_categories):
    pass
