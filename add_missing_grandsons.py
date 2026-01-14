"""
Add missing grandchildren categories
"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Missing grandchildren with their parent IDs
# Need to find parent IDs first
missing_grandsons = [
    ("Home Cinema", "Home Cinema"),  # Under Audio video -> Home Cinema
    ("Home Theatre e Soundbar", "Home Cinema"),
    ("Videoproiettori", "Home Cinema"),
    ("Staffe TV", "Televisori"),
    ("Decoder Digitale Terrestre", "Televisori"),
    ("Decoder Satellitare", "Televisori"),
    ("Lettori Blu Ray e DVD", "Televisori"),
    ("Film DVD e Blu Ray", "Televisori"),
    ("Antenne TV", "Televisori"),
    ("Condizionatori Fissi", "Condizionatori"),
    ("Condizionatori Portatili", "Condizionatori"),
]

print("=" * 80)
print("Adding missing grandchildren categories")
print("=" * 80)

# Get all categories
response = requests.get(f"{BASE_URL}/api/v1/categories", params={"limit": 200}, timeout=30)
all_cats = response.json()['data']

# Build name -> ID mapping
cat_map = {cat['name']: cat for cat in all_cats}

created = 0
failed = []

for grandson_name, parent_name in missing_grandsons:
    if parent_name not in cat_map:
        failed.append(f"{grandson_name}: Parent '{parent_name}' not found")
        continue
    
    parent_id = cat_map[parent_name]['id']
    
    try:
        payload = {
            "name": grandson_name,
            "parent_id": parent_id,
            "is_active": True,
            "translations": {
                "it": {"name": grandson_name},
                "en": {"name": grandson_name}
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/categories",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()['data']
            created += 1
            print(f"Created: {grandson_name} (ID: {result['id']}) under {parent_name}")
            time.sleep(0.1)
        elif response.status_code == 409:
            print(f"Exists: {grandson_name}")
        else:
            failed.append(f"{grandson_name}: {response.status_code}")
            print(f"Failed: {grandson_name} - {response.status_code}")
    
    except Exception as e:
        failed.append(f"{grandson_name}: {str(e)}")
        print(f"Error: {grandson_name} - {e}")

print(f"\n{'-'*80}")
print(f"Created: {created}")
print(f"Failed: {len(failed)}")

if failed:
    print("\nFailed items:")
    for item in failed:
        print(f"  - {item}")

# Final count
response = requests.get(f"{BASE_URL}/api/v1/categories", timeout=30)
final_total = response.json()['meta']['total']
print(f"\nTotal categories now: {final_total}")
print(f"Expected: 134")
print("=" * 80)
