"""
Complete Letti structure with better error handling and retry logic
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

def check_category_exists(category_id):
    """Check if category exists and return its status"""
    try:
        response = requests.get(f"{BASE_URL}/categories", headers=headers, params={"limit": 500, "active_only": False})
        if response.status_code == 200:
            data = response.json()
            categories = data.get('data', [])
            cat = next((c for c in categories if c['id'] == category_id), None)
            return cat
        return None
    except Exception as e:
        print(f"Error checking category: {e}")
        return None

def create_category_with_retry(name, category_id, parent_id=None, sort_order=0, slug=None, max_retries=3):
    """Create category with retry logic"""
    if not slug:
        slug = name.lower().replace(" ", "-").replace("à", "a").replace("è", "e").replace("ì", "i").replace("ò", "o").replace("ù", "u")
    
    url = f"{BASE_URL}/categories/"
    data = {
        "id": category_id,
        "name": name,
        "slug": slug,
        "parent_id": parent_id,
        "sort_order": sort_order,
        "is_active": True
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            if response.status_code in [200, 201]:
                print(f"✅ Created: {name} (ID: {category_id})")
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                print(f"ℹ️  Category {name} already exists, updating instead...")
                return update_category(category_id, {"is_active": True, "parent_id": parent_id, "sort_order": sort_order})
            else:
                print(f"⚠️  Attempt {attempt+1}/{max_retries} failed: {response.status_code}")
                print(f"   Response: {response.text}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        except Exception as e:
            print(f"⚠️  Attempt {attempt+1}/{max_retries} exception: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    return False

def update_category(category_id, data, max_retries=3):
    """Update category with retry logic"""
    url = f"{BASE_URL}/categories/{category_id}"
    
    for attempt in range(max_retries):
        try:
            response = requests.put(url, json=data, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                cat_data = result.get('data', {})
                print(f"✅ Updated: {cat_data.get('name', f'Category {category_id}')}")
                return True
            else:
                print(f"⚠️  Attempt {attempt+1}/{max_retries} failed: {response.status_code}")
                print(f"   Response: {response.text}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        except Exception as e:
            print(f"⚠️  Attempt {attempt+1}/{max_retries} exception: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    return False

print("=" * 80)
print("🏗️  CREATING LETTI CATEGORY STRUCTURE (IMPROVED)")
print("=" * 80)

# Step 1: Check/Create parent category
print("\n📌 Step 1: Checking/Creating parent category Letti (ID: 500)")
print("-" * 80)

cat_500 = check_category_exists(500)
if cat_500:
    print(f"ℹ️  Category 500 exists: {cat_500['name']}")
    print(f"   Active: {cat_500.get('is_active')}")
    if not cat_500.get('is_active'):
        print("   Activating...")
        update_category(500, {"is_active": True})
else:
    print("Creating new parent category...")
    create_category_with_retry("Letti", 500, parent_id=None, sort_order=1, slug="letti")

time.sleep(3)  # Wait for parent to be fully created

# Step 2: Create child categories
print("\n📌 Step 2: Creating child categories")
print("-" * 80)

children = [
    (501, "Letti in Ferro Battuto", 1),
    (502, "Letti in Legno", 2),
]

for cat_id, name, sort_order in children:
    cat = check_category_exists(cat_id)
    if cat:
        print(f"ℹ️  {name} already exists, ensuring it's under Letti...")
        update_category(cat_id, {"parent_id": 500, "sort_order": sort_order, "is_active": True})
    else:
        create_category_with_retry(name, cat_id, parent_id=500, sort_order=sort_order)
    time.sleep(2)

# Step 3: Update existing categories
print("\n📌 Step 3: Updating existing categories to be children of Letti")
print("-" * 80)

updates = [
    (746, 3, "Letti imbottiti"),
    (743, 4, "Letti a castello"),
    (808, 5, "Letti a scomparsa"),
    (827, 6, "Testiera per letti"),
]

for cat_id, sort_order, expected_name in updates:
    cat = check_category_exists(cat_id)
    if cat:
        print(f"Updating {cat['name']} (ID: {cat_id})...")
        update_category(cat_id, {"parent_id": 500, "sort_order": sort_order})
    else:
        print(f"⚠️  Category {cat_id} ({expected_name}) not found!")
    time.sleep(1.5)

# Step 4: Verify final structure
print("\n📌 Step 4: Verifying final structure")
print("-" * 80)

parent = check_category_exists(500)
if parent:
    print(f"\n✅ Parent: {parent['name']} (ID: 500)")
    print(f"   Active: {parent.get('is_active')}")
    
    # Get all children
    all_cats_response = requests.get(f"{BASE_URL}/categories", headers=headers, params={"limit": 500, "active_only": False})
    if all_cats_response.status_code == 200:
        all_cats = all_cats_response.json().get('data', [])
        children_cats = [c for c in all_cats if c.get('parent_id') == 500]
        children_cats.sort(key=lambda x: x.get('sort_order', 999))
        
        print(f"\n   Children ({len(children_cats)}):")
        for child in children_cats:
            print(f"   ├─ {child.get('sort_order', '?')}. {child['name']} (ID: {child['id']}) - Active: {child.get('is_active')}")

print("\n" + "=" * 80)
print("✅ PROCESS COMPLETE!")
print("=" * 80)
