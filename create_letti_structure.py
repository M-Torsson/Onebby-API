"""
Delete old Letti category (8588) and create new structure with ID 500
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

def delete_category(category_id):
    """Delete a category"""
    url = f"{BASE_URL}/categories/{category_id}"
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print(f"✅ Deleted category {category_id}")
            return True
        else:
            print(f"❌ Failed to delete {category_id}: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def create_category(name, category_id, parent_id=None, sort_order=0, slug=None):
    """Create a new category"""
    url = f"{BASE_URL}/categories/"
    
    if not slug:
        slug = name.lower().replace(" ", "-")
    
    data = {
        "id": category_id,
        "name": name,
        "slug": slug,
        "parent_id": parent_id,
        "sort_order": sort_order
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code in [200, 201]:
            print(f"✅ Created: {name} (ID: {category_id})")
            return True
        else:
            print(f"❌ Failed to create {name}: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def update_category_parent(category_id, parent_id, sort_order):
    """Update category's parent_id"""
    url = f"{BASE_URL}/categories/{category_id}"
    
    data = {
        "parent_id": parent_id,
        "sort_order": sort_order
    }
    
    try:
        response = requests.put(url, json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            cat_data = result.get('data', {})
            print(f"✅ Updated: {cat_data.get('name', 'Category')} (ID: {category_id}) -> Parent: {parent_id}, Order: {sort_order}")
            return True
        else:
            print(f"❌ Failed to update {category_id}: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

print("=" * 80)
print("🏗️  CREATING LETTI CATEGORY STRUCTURE")
print("=" * 80)

# Step 1: Delete old Letti category (8588)
print("\n📌 Step 1: Deleting old Letti category (ID: 8588)")
print("-" * 80)
delete_category(8588)
time.sleep(1)

# Step 2: Create new parent category with ID 500
print("\n📌 Step 2: Creating new parent category (ID: 500)")
print("-" * 80)
create_category("Letti", 500, parent_id=None, sort_order=1, slug="letti")
time.sleep(1)

# Step 3: Create new child categories
print("\n📌 Step 3: Creating child categories")
print("-" * 80)
create_category("Letti in Ferro Battuto", 501, parent_id=500, sort_order=1)
time.sleep(0.5)
create_category("Letti in Legno", 502, parent_id=500, sort_order=2)
time.sleep(0.5)

# Step 4: Update existing categories
print("\n📌 Step 4: Updating existing categories to be children of Letti")
print("-" * 80)

updates = [
    (746, 3),  # Letti imbottiti
    (743, 4),  # Letti a castello
    (808, 5),  # Letti a scomparsa
    (827, 6),  # Testiera per letti
]

for cat_id, sort_order in updates:
    update_category_parent(cat_id, parent_id=500, sort_order=sort_order)
    time.sleep(0.5)

print("\n" + "=" * 80)
print("✅ LETTI STRUCTURE COMPLETE!")
print("=" * 80)
print("\nFinal Structure:")
print("└─ Letti (500)")
print("   ├─ 1. Letti in Ferro Battuto (501)")
print("   ├─ 2. Letti in Legno (502)")
print("   ├─ 3. Letti imbottiti (746)")
print("   ├─ 4. Letti a castello (743)")
print("   ├─ 5. Letti a scomparsa (808)")
print("   └─ 6. Testiera per letti (827)")
