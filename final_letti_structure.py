"""
Create Letti structure with ID 500 - Final Solution
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

def create_or_update_category(cat_id, name, slug, parent_id, sort_order):
    """Create or update category"""
    # Try to create first
    create_url = f"{BASE_URL}/categories/"
    create_data = {
        "id": cat_id,
        "name": name,
        "slug": slug,
        "parent_id": parent_id,
        "sort_order": sort_order,
        "is_active": True
    }
    
    response = requests.post(create_url, json=create_data, headers=headers, timeout=30)
    if response.status_code in [200, 201]:
        print(f"✅ Created: {name} (ID: {cat_id})")
        return True
    elif "already exists" in response.text.lower() or "slug" in response.text.lower():
        # Try to update instead
        print(f"ℹ️  Category with this slug exists, trying to update ID {cat_id}...")
        update_url = f"{BASE_URL}/categories/{cat_id}"
        update_data = {
            "name": name,
            "parent_id": parent_id,
            "sort_order": sort_order,
            "is_active": True
        }
        update_response = requests.put(update_url, json=update_data, headers=headers, timeout=30)
        if update_response.status_code == 200:
            print(f"✅ Updated: {name} (ID: {cat_id})")
            return True
        else:
            print(f"❌ Update failed: {update_response.status_code} - {update_response.text}")
            return False
    else:
        print(f"❌ Failed: {response.status_code} - {response.text[:200]}")
        return False

print("=" * 80)
print("🏗️  CREATING LETTI STRUCTURE - FINAL SOLUTION")
print("=" * 80)

# Step 1: Create main Letti category with ID 500 and unique slug
print("\n📌 Step 1: Creating main Letti category (ID: 500)")
print("-" * 80)
success = create_or_update_category(500, "Letti", "letti-main", None, 1)
if not success:
    print("❌ Cannot proceed without parent category")
    exit(1)

time.sleep(3)  # Wait for parent to be saved

# Step 2: Create children
print("\n📌 Step 2: Creating child categories")
print("-" * 80)

children = [
    (501, "Letti in Ferro Battuto", "letti-in-ferro-battuto", 1),
    (502, "Letti in Legno", "letti-in-legno", 2),
]

for cat_id, name, slug, sort_order in children:
    create_or_update_category(cat_id, name, slug, 500, sort_order)
    time.sleep(2)

# Step 3: Update existing categories
print("\n📌 Step 3: Updating existing Letti categories to be children")
print("-" * 80)

updates = [
    (746, 3),  # Letti imbottiti
    (743, 4),  # Letti a castello  
    (808, 5),  # Letti a scomparsa
    (827, 6),  # Testiera per letti
]

for cat_id, sort_order in updates:
    update_url = f"{BASE_URL}/categories/{cat_id}"
    update_data = {
        "parent_id": 500,
        "sort_order": sort_order,
        "is_active": True
    }
    
    response = requests.put(update_url, json=update_data, headers=headers, timeout=30)
    if response.status_code == 200:
        result = response.json()
        cat_data = result.get('data', {})
        print(f"✅ Updated: {cat_data.get('name', f'Category {cat_id}')} -> Parent: 500")
    else:
        print(f"❌ Failed to update {cat_id}: {response.status_code} - {response.text[:100]}")
    time.sleep(1.5)

# Verification
print("\n📌 Verification")
print("-" * 80)

response = requests.get(f"{BASE_URL}/categories", headers=headers, params={"limit": 500, "active_only": False})
if response.status_code == 200:
    all_cats = response.json().get('data', [])
    
    parent = next((c for c in all_cats if c['id'] == 500), None)
    if parent:
        print(f"\n✅ Parent: {parent['name']} (ID: 500, Active: {parent.get('is_active')})")
        
        children_cats = [c for c in all_cats if c.get('parent_id') == 500]
        children_cats.sort(key=lambda x: x.get('sort_order', 999))
        
        print(f"\n   Children ({len(children_cats)}):")
        for child in children_cats:
            print(f"   ├─ {child.get('sort_order')}. {child['name']} (ID: {child['id']})")
    else:
        print("❌ Parent category 500 not found!")

print("\n" + "=" * 80)
print("✅ COMPLETE!")
print("=" * 80)
