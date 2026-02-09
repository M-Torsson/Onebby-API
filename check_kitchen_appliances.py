# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"

# Kitchen appliances = Elettrodomestici cucina = ID 8155
CATEGORY_ID = 8155


# Get category info
response = requests.get(f"{BASE_URL}/categories/{CATEGORY_ID}")
if response.status_code == 200:
    data = response.json()["data"]
else:
    exit(1)

# Get children

response = requests.get(f"{BASE_URL}/categories/{CATEGORY_ID}/children")
if response.status_code == 200:
    data = response.json()
    children = data.get("data", [])
    
    if len(children) == 0:
        pass
    else:
        pass
        
        for child in children:
            pass
            
            # Check for grandchildren
            if child['has_children']:
                gc_response = requests.get(f"{BASE_URL}/categories/{child['id']}/children")
                if gc_response.status_code == 200:
                    gc_data = gc_response.json()
                    grandchildren = gc_data.get("data", [])
                    if grandchildren:
                        pass
                        for gc in grandchildren:
                            pass
else:
    pass

# Try subcategories endpoint

response = requests.get(f"{BASE_URL}/categories/{CATEGORY_ID}/subcategories")
if response.status_code == 200:
    data = response.json()
    subs = data.get("data", [])
    
    if len(subs) == 0:
        pass
    else:
        pass
        for sub in subs:
            pass
else:
    pass
