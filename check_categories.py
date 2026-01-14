import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

# IDs to check
ids_to_check = [8416, 8417, 8415, 8426, 8413]

print("=" * 60)
print("التحقق من وجود الفئات:")
print("=" * 60)

for cat_id in ids_to_check:
    try:
        response = requests.get(f"{BASE_URL}/categories/{cat_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            name = data.get("data", {}).get("name", "غير معروف")
            parent_id = data.get("data", {}).get("parent_id")
            print(f"✅ [{cat_id}] {name} (parent_id: {parent_id})")
        else:
            print(f"❌ [{cat_id}] لا يوجد (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ [{cat_id}] خطأ: {e}")

print("=" * 60)
