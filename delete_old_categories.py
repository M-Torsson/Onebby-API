"""
Delete old categories and re-categorize products properly
"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

print("=" * 100)
print("🗑️ حذف الفئات القديمة")
print("=" * 100)

# Read old category IDs
with open('old_category_ids.txt', 'r') as f:
    old_ids = [int(line.strip()) for line in f if line.strip()]

print(f"\n📋 سيتم حذف {len(old_ids)} فئة قديمة\n")

deleted = 0
failed = []

for idx, cat_id in enumerate(old_ids, 1):
    try:
        response = requests.delete(
            f"{BASE_URL}/api/v1/categories/{cat_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            deleted += 1
            print(f"✅ [{idx}/{len(old_ids)}] حُذفت فئة {cat_id}")
        elif response.status_code == 404:
            print(f"⚠️ [{idx}/{len(old_ids)}] فئة {cat_id} غير موجودة")
        else:
            failed.append((cat_id, response.status_code, response.text[:100]))
            print(f"❌ [{idx}/{len(old_ids)}] فشل حذف {cat_id}: {response.status_code}")
        
        time.sleep(0.1)  # Avoid rate limiting
        
    except Exception as e:
        failed.append((cat_id, 'Exception', str(e)[:100]))
        print(f"❌ [{idx}/{len(old_ids)}] خطأ في {cat_id}: {e}")

print(f"\n{'='*100}")
print(f"📊 النتيجة:")
print(f"   • نجح: {deleted}")
print(f"   • فشل: {len(failed)}")

if failed:
    print(f"\n❌ الفئات التي فشل حذفها:")
    for cat_id, status, msg in failed[:10]:
        print(f"   • {cat_id}: {status} - {msg}")

print("=" * 100)
