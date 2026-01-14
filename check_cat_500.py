"""
Check if Letti category exists and add children
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = os.getenv("API_KEY")

headers = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

# Check if category 500 exists
print("🔍 Checking if category 500 exists...")
try:
    response = requests.get(f"{BASE_URL}/categories", headers=headers, params={"limit": 500})
    if response.status_code == 200:
        data = response.json()
        categories = data.get('data', [])
        cat_500 = next((c for c in categories if c['id'] == 500), None)
        
        if cat_500:
            print(f"✅ Found category 500: {cat_500['name']}")
            print(f"   Slug: {cat_500.get('slug')}")
            print(f"   Parent: {cat_500.get('parent_id')}")
        else:
            print("❌ Category 500 NOT found")
            
        # Check for "letti" slug
        letti_cat = next((c for c in categories if c.get('slug') == 'letti'), None)
        if letti_cat:
            print(f"\n⚠️  Category with slug 'letti' exists:")
            print(f"   ID: {letti_cat['id']}")
            print(f"   Name: {letti_cat['name']}")
except Exception as e:
    print(f"Error: {e}")
