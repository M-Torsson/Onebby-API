"""
Final solution - Create Letti structure with proper delays and verification
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

def wait_for_category(cat_id, max_wait=15):
    """Wait for category to be available in API"""
    print(f"   ⏳ Waiting for category {cat_id} to be available...", end="", flush=True)
    for i in range(max_wait):
        try:
            response = requests.get(f"{BASE_URL}/categories/{cat_id}", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json().get('data', {})
                if data.get('is_active'):
                    print(f" ✅ Ready! (Active: {data.get('is_active')})")
                    return True
                else:
                    print(f" ⚠️  Exists but not active", flush=True)
                    return False
        except:
            pass
        time.sleep(1)
        if i < max_wait - 1:
            print(".", end="", flush=True)
    print(" ❌ Timeout")
    return False

print("=" * 80)
print("🏗️  CREATING LETTI STRUCTURE - FINAL ATTEMPT")
print("=" * 80)

# Step 1: Create parent with explicit is_active=True
print("\n📌 Step 1: Creating main Letti category (ID: 500)")
print("-" * 80)

create_data = {
    "id": 500,
    "name": "Letti",
    "slug": "letti-category-main",
    "parent_id": None,
    "sort_order": 1,
    "is_active": True
}

response = requests.post(f"{BASE_URL}/categories/", json=create_data, headers=headers, timeout=30)
if response.status_code in [200, 201]:
    print("✅ Created: Letti (ID: 500)")
    # Wait for it to be available
    if wait_for_category(500, max_wait=20):
        print("   Category 500 is ready!")
    else:
        print("   ⚠️  Category may not be fully active yet, proceeding anyway...")
else:
    print(f"❌ Failed: {response.status_code}")
    print(f"   Response: {response.text}")
    if "slug" in response.text.lower():
        print("\n   Slug conflict detected. Trying alternate slug...")
        create_data["slug"] = f"letti-cat-{int(time.time())}"
        response = requests.post(f"{BASE_URL}/categories/", json=create_data, headers=headers, timeout=30)
        if response.status_code in [200, 201]:
            print(f"✅ Created with slug: {create_data['slug']}")
            wait_for_category(500, max_wait=20)
        else:
            print(f"❌ Still failed: {response.text[:200]}")
            print("\n⚠️  Cannot proceed without parent category!")
            exit(1)

# Extra wait for database replication
print("\n⏳ Waiting 5 seconds for database sync...")
time.sleep(5)

# Step 2: Create children
print("\n📌 Step 2: Creating child categories")
print("-" * 80)

children = [
    (501, "Letti in Ferro Battuto", 1),
    (502, "Letti in Legno", 2),
]

for cat_id, name, sort_order in children:
    slug = name.lower().replace(" ", "-")
    child_data = {
        "id": cat_id,
        "name": name,
        "slug": slug,
        "parent_id": 500,
        "sort_order": sort_order,
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/categories/", json=child_data, headers=headers, timeout=30)
    if response.status_code in [200, 201]:
        print(f"✅ Created: {name} (ID: {cat_id})")
    else:
        print(f"❌ Failed {name}: {response.status_code} - {response.text[:100]}")
    time.sleep(3)

# Step 3: Update existing categories
print("\n📌 Step 3: Updating existing Letti subcategories")
print("-" * 80)

updates = [
    (746, 3, "Letti imbottiti"),
    (743, 4, "Letti a castello"),
    (808, 5, "Letti a scomparsa"),
    (827, 6, "Testiera per letti"),
]

for cat_id, sort_order, name in updates:
    update_data = {
        "parent_id": 500,
        "sort_order": sort_order,
        "is_active": True
    }
    
    response = requests.put(f"{BASE_URL}/categories/{cat_id}", json=update_data, headers=headers, timeout=30)
    if response.status_code == 200:
        print(f"✅ Updated: {name} (ID: {cat_id}) -> Parent: 500")
    else:
        print(f"❌ Failed {name}: {response.status_code} - {response.text[:100]}")
    time.sleep(2)

# Final verification
print("\n📌 Final Verification")
print("-" * 80)

time.sleep(2)
response = requests.get(f"{BASE_URL}/categories", headers=headers, params={"limit": 500, "active_only": False})
if response.status_code == 200:
    all_cats = response.json().get('data', [])
    
    parent = next((c for c in all_cats if c['id'] == 500), None)
    if parent:
        print(f"\n✅ Parent Found: {parent['name']} (ID: 500)")
        print(f"   Active: {parent.get('is_active')}")
        print(f"   Slug: {parent.get('slug')}")
        
        children_cats = [c for c in all_cats if c.get('parent_id') == 500]
        children_cats.sort(key=lambda x: x.get('sort_order', 999))
        
        print(f"\n   Children ({len(children_cats)}):")
        if children_cats:
            for child in children_cats:
                active_icon = "✅" if child.get('is_active') else "❌"
                print(f"   ├─ {child.get('sort_order')}. {child['name']} (ID: {child['id']}) {active_icon}")
        else:
            print("   ⚠️  No children found yet")
    else:
        print("❌ Parent category 500 still not found in list!")
        # Check if it exists individually
        direct_check = requests.get(f"{BASE_URL}/categories/500", headers=headers)
        if direct_check.status_code == 200:
            print("   But it exists when queried directly!")
            print(f"   Data: {direct_check.json()}")

print("\n" + "=" * 80)
print("✅ PROCESS COMPLETE!")
print("=" * 80)
