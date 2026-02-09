# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

import requests

API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

# Check products stats
response = requests.get(
    "https://onebby-api.onrender.com/api/admin/stats/products",
    headers={"X-API-KEY": API_KEY}
)

if response.status_code == 200:
    data = response.json()
    for ptype, count in data['products_by_type'].items():
        pass
else:
    pass
