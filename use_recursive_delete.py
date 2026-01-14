"""
Use the new recursive delete endpoint to delete categories with children
"""
import requests
import json

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

failed_ids = [8159, 8167, 8179, 8180, 8192, 8193, 8195, 8197, 8198]

print("=" * 100)
print("🗑️ حذف الفئات بشكل تلقائي (مع الأطفال والأحفاد)")
print("=" * 100)
print(f"\nانتظر... جاري رفع الكود الجديد على Render")
print("بعد الانتظار 2-3 دقائق، سيبدأ الحذف\n")

input("اضغط Enter عندما ينتهي الـ deployment...")

print(f"\n🚀 بدء الحذف للـ {len(failed_ids)} فئة\n")

response = requests.post(
    f"{BASE_URL}/api/v1/admin/categories/recursive-delete",
    headers=headers,
    json={"category_ids": failed_ids},
    timeout=120
)

if response.status_code in [200, 204]:
    result = response.json()
    print(f"✅ نجح الحذف!")
    print(f"   • عدد الفئات المحذوفة: {result.get('deleted_count', 0)}")
    print(f"   • IDs: {result.get('deleted_ids', [])}")
    
    if result.get('errors'):
        print(f"\n⚠️ أخطاء:")
        for error in result['errors']:
            print(f"   • {error}")
else:
    print(f"❌ فشل: {response.status_code}")
    print(f"Response: {response.text}")

print("\n" + "=" * 100)
print("📊 الآن تحقق من الفئات المتبقية:")
print("   python identify_categories_to_remove.py")
print("=" * 100)
