# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""Check for duplicate Rete networking"""
import requests

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

response = requests.get(
    f"{BASE_URL}/api/v1/categories",
    headers={"X-API-Key": API_KEY},
    params={"limit": 500},
    timeout=30
)

categories = response.json()['data']

rete_cats = [c for c in categories if 'Rete' in c['name'] or 'networking' in c['name']]

for cat in rete_cats:
    pass
