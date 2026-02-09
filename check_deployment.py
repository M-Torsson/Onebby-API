# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""Check if new endpoint is deployed"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"


# Check health
try:
    response = requests.get(f"{BASE_URL}/api/health", timeout=10)
except Exception as e:
    pass


# Try the new endpoint
try:
    response = requests.post(
        f"{BASE_URL}/api/v1/categories/deactivate-all",
        headers={"X-API-Key": API_KEY},
        timeout=30
    )
    
    if response.status_code == 200:
        pass
    elif response.status_code == 404:
        pass
    else:
        pass
        
except Exception as e:
    pass
