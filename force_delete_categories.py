"""
Delete old categories using force=true
"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

failed_ids = [8159, 8167, 8179, 8180, 8192, 8193, 8195, 8197, 8198]

print("=" * 100)
print("🗑️ حذف الفئات القديمة باستخدام force=true")
print("=" * 100)
print(f"\n📋 سيتم حذف {len(failed_ids)} فئة\n")

deleted = 0
failed = []

for idx, cat_id in enumerate(failed_ids, 1):
    try:
        response = requests.delete(
            f"{BASE_URL}/api/v1/categories/{cat_id}?force=true",
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 204]:
            deleted += 1
            print(f"✅ [{idx}/{len(failed_ids)}] حُذفت فئة {cat_id}")
        elif response.status_code == 404:
            print(f"⚠️ [{idx}/{len(failed_ids)}] فئة {cat_id} غير موجودة")
        else:
            failed.append((cat_id, response.status_code, response.text[:100]))
            print(f"❌ [{idx}/{len(failed_ids)}] فشل {cat_id}: {response.status_code}")
        
        time.sleep(0.2)
        
    except Exception as e:
        failed.append((cat_id, 'Exception', str(e)[:100]))
        print(f"❌ [{idx}/{len(failed_ids)}] خطأ {cat_id}: {e}")

print(f"\n{'='*100}")
print(f"📊 النتيجة:")
print(f"   • نجح: {deleted}")
print(f"   • فشل: {len(failed)}")

if failed:
    print(f"\n❌ الفئات التي فشل حذفها:")
    for cat_id, status, msg in failed:
        print(f"   • {cat_id}: {status} - {msg}")

print("\n" + "=" * 100)
print("📊 الآن تحقق من الفئات المتبقية:")
print("   python identify_categories_to_remove.py")
print("=" * 100)
