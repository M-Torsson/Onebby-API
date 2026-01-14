"""
Add remaining Telefonia children
"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Telefonia children (parent_id: 8158)
telefonia_children = [
    {"name": "Smartphone", "name_en": "Smartphones"},
    {"name": "Telefoni fissi", "name_en": "Landline phones"},
    {"name": "Accessori telefonia", "name_en": "Phone accessories"},
    {"name": "Smartwatch", "name_en": "Smartwatches"},
]

print("=" * 100)
print("📱 إضافة فئات Telefonia المتبقية")
print("=" * 100)

created = 0
skipped = 0

for child in telefonia_children:
    try:
        payload = {
            "name": child["name"],
            "parent_id": 8158,
            "is_active": True,
            "translations": {
                "it": {"name": child["name"]},
                "en": {"name": child["name_en"]}
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/categories",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            created += 1
            result = response.json()['data']
            print(f"✅ {child['name']} (ID: {result['id']})")
        elif response.status_code == 409:
            skipped += 1
            print(f"⚠️  {child['name']} موجودة مسبقاً")
        else:
            print(f"❌ {child['name']}: {response.status_code} - {response.text[:100]}")
        
        time.sleep(0.1)
        
    except Exception as e:
        print(f"❌ خطأ في {child['name']}: {e}")

print(f"\n{'='*100}")
print(f"📊 النتيجة: {created} جديدة، {skipped} موجودة")

# Final count
response = requests.get(f"{BASE_URL}/api/v1/categories", timeout=30)
if response.status_code == 200:
    data = response.json()
    total = data['meta']['total']
    print(f"✅ إجمالي الفئات الآن: {total}")
    
    # Show tree structure
    print(f"\n📊 هيكل الشجرة:")
    parents = [c for c in data['data'] if c['parent_id'] is None]
    for parent in parents:
        children_count = sum(1 for c in data['data'] if c.get('parent_id') == parent['id'])
        print(f"  • {parent['name']}: {children_count} فئة فرعية")

print("=" * 100)
