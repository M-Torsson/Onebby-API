"""
Fix Home Cinema structure
"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

print("=" * 80)
print("Fixing Home Cinema structure")
print("=" * 80)

# Get all categories
response = requests.get(f"{BASE_URL}/api/v1/categories", params={"limit": 200}, timeout=30)
all_cats = response.json()['data']
cat_map = {cat['name']: cat for cat in all_cats}

# Step 1: Delete wrongly placed items under Televisori
wrong_items = ["Staffe TV", "Decoder Digitale Terrestre", "Decoder Satellitare", 
               "Lettori Blu Ray e DVD", "Film DVD e Blu Ray", "Antenne TV"]

print("\n1. Deleting items wrongly placed under Televisori...")
for name in wrong_items:
    if name in cat_map:
        try:
            response = requests.delete(
                f"{BASE_URL}/api/v1/categories/{cat_map[name]['id']}",
                headers=headers,
                timeout=30
            )
            if response.status_code in [200, 204]:
                print(f"  Deleted: {name}")
        except:
            pass

# Step 2: Create "Home Cinema" under Audio video
print("\n2. Creating 'Home Cinema' category...")
audio_video_id = cat_map.get("Audio video", {}).get("id")

if audio_video_id:
    try:
        payload = {
            "name": "Home Cinema",
            "parent_id": audio_video_id,
            "is_active": True,
            "translations": {
                "it": {"name": "Home Cinema"},
                "en": {"name": "Home Cinema"}
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/categories",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            home_cinema_id = response.json()['data']['id']
            print(f"  Created: Home Cinema (ID: {home_cinema_id})")
            
            # Step 3: Create all grandchildren under Home Cinema
            print("\n3. Creating grandchildren under Home Cinema...")
            
            grandchildren = [
                "Home Theatre e Soundbar",
                "Decoder Digitale Terrestre",
                "Decoder Satellitare",
                "Lettori Blu Ray e DVD",
                "Videoproiettori",
                "Staffe TV",
                "Film DVD e Blu Ray",
                "Antenne TV"
            ]
            
            for gc_name in grandchildren:
                try:
                    payload = {
                        "name": gc_name,
                        "parent_id": home_cinema_id,
                        "is_active": True,
                        "translations": {
                            "it": {"name": gc_name},
                            "en": {"name": gc_name}
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
                        print(f"  Created: {gc_name} (ID: {result['id']})")
                    elif response.status_code == 409:
                        print(f"  Exists: {gc_name}")
                    else:
                        print(f"  Failed: {gc_name} - {response.status_code}")
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"  Error: {gc_name} - {e}")
        elif response.status_code == 409:
            print("  Home Cinema already exists")
    except Exception as e:
        print(f"  Error creating Home Cinema: {e}")

# Final count
print("\n" + "=" * 80)
response = requests.get(f"{BASE_URL}/api/v1/categories", timeout=30)
final_total = response.json()['meta']['total']
print(f"Total categories: {final_total}")
print(f"Expected: 134")
print("=" * 80)
