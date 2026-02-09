# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

# IDs to check
ids_to_check = [8416, 8417, 8415, 8426, 8413]


for cat_id in ids_to_check:
    try:
        response = requests.get(f"{BASE_URL}/categories/{cat_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            name = data.get("data", {}).get("name", "غير معروف")
            parent_id = data.get("data", {}).get("parent_id")
        else:
            pass
    except Exception as e:
        pass
