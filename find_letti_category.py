"""
Find Letti category and work with it
"""
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = os.getenv("API_KEY")

headers = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

print("=" * 80)
print("🔍 FINDING LETTI CATEGORY")
print("=" * 80)

# Get all categories
response = requests.get(f"{BASE_URL}/categories", headers=headers, params={"limit": 500, "active_only": False})

if response.status_code == 200:
    data = response.json()
    categories = data.get('data', [])
    
    # Find Letti category
    letti_cat = next((c for c in categories if 'letti' in c.get('slug', '').lower() and c.get('parent_id') is None), None)
    
    if letti_cat:
        print(f"\n✅ Found Letti category:")
        print(f"   ID: {letti_cat['id']}")
        print(f"   Name: {letti_cat['name']}")
        print(f"   Slug: {letti_cat.get('slug')}")
        print(f"   Active: {letti_cat.get('is_active')}")
        print(f"   Parent ID: {letti_cat.get('parent_id')}")
        
        letti_id = letti_cat['id']
        
        # Check ID 500
        cat_500 = next((c for c in categories if c['id'] == 500), None)
        if cat_500:
            print(f"\n⚠️  ID 500 is used by: {cat_500['name']}")
            print(f"   We will use ID {letti_id} for Letti structure instead")
        else:
            print(f"\n✅ ID 500 is available")
            print(f"\nOption 1: Delete current Letti (ID: {letti_id}) and create new one with ID 500")
            print(f"Option 2: Keep current Letti (ID: {letti_id}) and update children to use this ID")
        
        # Show which option user wants
        print("\n" + "=" * 80)
        print("RECOMMENDATION: Use existing Letti category")
        print("=" * 80)
        
        print(f"\n📋 Action Plan:")
        print(f"1. Activate Letti (ID: {letti_id}) if not active")
        print(f"2. Create child categories with parent_id = {letti_id}:")
        print(f"   - 501: Letti in Ferro Battuto")
        print(f"   - 502: Letti in Legno")
        print(f"3. Update existing categories to parent_id = {letti_id}:")
        print(f"   - 746: Letti imbottiti")
        print(f"   - 743: Letti a castello")
        print(f"   - 808: Letti a scomparsa")
        print(f"   - 827: Testiera per letti")
        
        # Save letti_id to file for next script
        with open('letti_id.txt', 'w') as f:
            f.write(str(letti_id))
        
        print(f"\n💾 Saved Letti ID ({letti_id}) to letti_id.txt")
        
    else:
        print("\n❌ No Letti category found!")
        print("Checking for categories with 'lett' in name...")
        letti_cats = [c for c in categories if 'lett' in c['name'].lower()]
        for cat in letti_cats[:10]:
            print(f"  - ID {cat['id']}: {cat['name']} (parent: {cat.get('parent_id')})")

else:
    print(f"❌ Failed to get categories: {response.status_code}")
