import requests

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

for cat_id in [8219, 8220]:
    response = requests.delete(
        f"{BASE_URL}/api/v1/categories/{cat_id}?force=true",
        headers=headers,
        timeout=30
    )
    
    if response.status_code in [200, 204]:
        print(f"✅ حُذفت فئة {cat_id}")
    else:
        print(f"❌ فشل {cat_id}: {response.status_code} - {response.text}")

print("\nالآن أفحص الفئات النهائية...")
response = requests.get(f"{BASE_URL}/api/v1/categories", timeout=30)
categories = response.json()['data']
print(f"إجمالي الفئات المتبقية: {len(categories)}")

# Show remaining categories
new_cats = [c for c in categories if c.get('id') >= 8151]
print(f"\nالفئات الجديدة ({len(new_cats)}):")
for cat in new_cats:
    parent_info = f" ← {cat.get('parent', {}).get('name', '')}" if cat.get('parent') else " (رئيسية)"
    print(f"  • [{cat['id']}] {cat.get('name')}{parent_info}")
