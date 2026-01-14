"""Check categories count"""
import requests

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

print("🔍 التحقق من عدد الفئات...")
print("=" * 80)

# Get all categories
response = requests.get(
    f"{BASE_URL}/api/v1/categories",
    headers={"X-API-Key": API_KEY},
    params={"limit": 500},
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    categories = data.get('data', [])
    
    total = len(categories)
    active = sum(1 for c in categories if c.get('is_active', True))
    inactive = total - active
    
    print(f"📊 إجمالي الفئات: {total}")
    print(f"✅ نشطة: {active}")
    print(f"❌ غير نشطة: {inactive}")
    
    # Show first few
    print(f"\n📋 أول 10 فئات:")
    for i, cat in enumerate(categories[:10], 1):
        status = "✅" if cat.get('is_active', True) else "❌"
        parent = f" (Parent: {cat.get('parent_id')})" if cat.get('parent_id') else " (ROOT)"
        print(f"   {status} {i}. {cat['name']}{parent}")
else:
    print(f"❌ فشل: {response.status_code}")
    print(response.text)

print("=" * 80)
