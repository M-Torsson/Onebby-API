# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""Check single product with categories"""
import requests

BASE_URL = "https://onebby-api.onrender.com"

# Check the product you mentioned
response = requests.get(f"{BASE_URL}/api/v1/products/3622", timeout=30)

if response.status_code == 200:
    product = response.json()['data']
    
    
    if product.get('categories'):
        pass
        for cat in product['categories']:
            pass
    else:
        pass
else:
    pass
