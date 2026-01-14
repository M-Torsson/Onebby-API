"""
Test the recursive delete endpoint after deployment
"""
import requests
import json
import time

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

failed_ids = [8159, 8167, 8179, 8180, 8192, 8193, 8195, 8197, 8198]

print("=" * 100)
print("⏳ الانتظار 2 دقيقة حتى يكتمل الـ deployment...")
print("=" * 100)

time.sleep(120)

print(f"\n🚀 بدء الحذف للـ {len(failed_ids)} فئة\n")

response = requests.post(
    f"{BASE_URL}/api/v1/admin/categories/recursive-delete",
    headers=headers,
    json={"category_ids": failed_ids},
    timeout=120
)

print(f"Status: {response.status_code}")

if response.status_code in [200, 204]:
    result = response.json()
    print(f"\n✅ نجح الحذف!")
    print(f"   • عدد الفئات المحذوفة: {result.get('deleted_count', 0)}")
    print(f"   • IDs المحذوفة: {result.get('deleted_ids', [])}")
    
    if result.get('errors'):
        print(f"\n⚠️ أخطاء:")
        for error in result['errors']:
            print(f"   • {error}")
else:
    print(f"\n❌ فشل: {response.status_code}")
    print(f"Response: {response.text}")

print("\n" + "=" * 100)
print("📊 الآن تحقق من الفئات المتبقية:")
print("   python identify_categories_to_remove.py")
print("=" * 100)
