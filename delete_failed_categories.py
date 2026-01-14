"""
Check failed categories structure and delete children first
"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

failed_ids = [8159, 8167, 8179, 8180, 8192, 8193, 8195, 8197, 8198]

print("=" * 100)
print("🔍 فحص الفئات التي فشل حذفها")
print("=" * 100)

# Get all categories again
response = requests.get(f"{BASE_URL}/api/v1/categories", timeout=60)
categories = response.json()['data']

print(f"\n📦 إجمالي الفئات المتبقية: {len(categories)}\n")

# Find children of failed categories
children_to_delete = []

for cat in categories:
    parent_id = cat.get('parent', {}).get('id') if cat.get('parent') else None
    if parent_id in failed_ids:
        children_to_delete.append(cat)
        print(f"   • [{cat['id']}] {cat.get('name')} ← [{parent_id}]")

print(f"\n{'='*100}")
print(f"🗑️ حذف {len(children_to_delete)} فئة فرعية أولاً")
print(f"{'='*100}\n")

deleted = 0
for cat in children_to_delete:
    try:
        response = requests.delete(
            f"{BASE_URL}/api/v1/categories/{cat['id']}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            deleted += 1
            print(f"✅ حُذفت {cat['id']} - {cat.get('name')}")
        else:
            print(f"❌ فشل {cat['id']}: {response.status_code}")
        
        time.sleep(0.1)
    except Exception as e:
        print(f"❌ خطأ {cat['id']}: {e}")

print(f"\n{'='*100}")
print(f"🗑️ الآن حذف الفئات الأصلية ({len(failed_ids)})")
print(f"{'='*100}\n")

deleted_parents = 0
for cat_id in failed_ids:
    try:
        response = requests.delete(
            f"{BASE_URL}/api/v1/categories/{cat_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            deleted_parents += 1
            print(f"✅ حُذفت فئة {cat_id}")
        else:
            print(f"❌ فشل {cat_id}: {response.status_code} - {response.text[:100]}")
        
        time.sleep(0.1)
    except Exception as e:
        print(f"❌ خطأ {cat_id}: {e}")

print(f"\n{'='*100}")
print(f"📊 النتيجة:")
print(f"   • فئات فرعية محذوفة: {deleted}")
print(f"   • فئات رئيسية محذوفة: {deleted_parents}")
print("=" * 100)
