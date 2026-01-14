"""
Add Letti category structure via API
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = os.getenv("API_KEY")

headers = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

def create_category(name, category_id, parent_id=None, sort_order=0, slug=None):
    """Create a new category"""
    url = f"{BASE_URL}/categories/"
    
    # Auto-generate slug if not provided
    if not slug:
        slug = name.lower().replace(" ", "-").replace("à", "a").replace("è", "e").replace("ì", "i").replace("ò", "o").replace("ù", "u")
    
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
        print(f"❌ Exception creating {name}: {e}")
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
            print(f"✅ Updated: {cat_data.get('name', 'Category')} (ID: {category_id}) -> Parent: {parent_id}")
            return True
        else:
            print(f"❌ Failed to update {category_id}: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception updating {category_id}: {e}")
        return False

def main():
    print("=" * 80)
    print("🏗️  CREATING LETTI CATEGORY STRUCTURE")
    print("=" * 80)
    
    # Step 1: Check if parent category exists
    print("\n📌 Step 1: Checking parent category")
    print("-" * 80)
    try:
        url = f"{BASE_URL}/categories/500"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ Parent category 'Letti' (ID: 500) already exists")
        else:
            print("Creating parent category...")
            success = create_category(
                name="Letti",
                category_id=500,
                parent_id=None,
                sort_order=1,
                slug="letti"
            )
            if not success:
                print("\n❌ Failed to create parent category. Stopping.")
                return
    except Exception as e:
        print(f"Error checking parent: {e}")
    
    # Step 2: Create new child categories
    print("\n📌 Step 2: Creating new child categories")
    print("-" * 80)
    
    create_category(
        name="Letti in Ferro Battuto",
        category_id=501,
        parent_id=500,
        sort_order=1,
        slug="letti-in-ferro-battuto"
    )
    
    create_category(
        name="Letti in Legno",
        category_id=502,
        parent_id=500,
        sort_order=2,
        slug="letti-in-legno"
    )
    
    # Step 3: Update existing categories to be children of Letti
    print("\n📌 Step 3: Updating existing categories")
    print("-" * 80)
    
    updates = [
        (746, 3),  # Letti imbottiti
        (743, 4),  # Letti a castello
        (808, 5),  # Letti a scomparsa
        (827, 6),  # Testiera per letti
    ]
    
    for cat_id, sort_order in updates:
        update_category_parent(cat_id, parent_id=500, sort_order=sort_order)
    
    print("\n" + "=" * 80)
    print("✅ LETTI STRUCTURE COMPLETE!")
    print("=" * 80)
    print("\nStructure:")
    print("└─ Letti (500)")
    print("   ├─ Letti in Ferro Battuto (501) - sort: 1")
    print("   ├─ Letti in Legno (502) - sort: 2")
    print("   ├─ Letti imbottiti (746) - sort: 3")
    print("   ├─ Letti a castello (743) - sort: 4")
    print("   ├─ Letti a scomparsa (808) - sort: 5")
    print("   └─ Testiera per letti (827) - sort: 6")

if __name__ == "__main__":
    main()
