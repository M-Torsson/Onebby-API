import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

# IDs to keep
KEEP_IDS = {8151, 8152, 8153, 8154, 8155, 8156, 8157, 8158, 8385}

print("=" * 80)
print("حذف جميع الفئات ما عدا الـ9 المحددة")
print("=" * 80)

# Get all categories
print("\nجلب جميع الفئات...")
response = requests.get(f"{BASE_URL}/categories?limit=500")
if response.status_code != 200:
    print(f"❌ فشل جلب الفئات: {response.status_code}")
    exit(1)

data = response.json()
all_categories = data.get("data", [])
print(f"✅ تم جلب {len(all_categories)} فئة")

# Filter categories to delete
to_delete = [cat for cat in all_categories if cat["id"] not in KEEP_IDS]
to_keep = [cat for cat in all_categories if cat["id"] in KEEP_IDS]

print(f"\n{'='*80}")
print(f"الفئات التي سيتم الاحتفاظ بها: {len(to_keep)}")
print(f"الفئات التي سيتم حذفها: {len(to_delete)}")
print('='*80)

for cat in to_keep:
    print(f"✅ سيبقى: {cat['name']} (ID: {cat['id']})")

print(f"\n{'='*80}")
print("بدء عملية الحذف...")
print('='*80)

deleted_count = 0
failed_count = 0

for cat in to_delete:
    cat_id = cat["id"]
    cat_name = cat["name"]
    
    print(f"\nحذف: {cat_name} (ID: {cat_id})...", end=" ")
    
    response = requests.delete(
        f"{BASE_URL}/categories/{cat_id}",
        headers=headers
    )
    
    if response.status_code in [200, 204]:
        print("✅")
        deleted_count += 1
    else:
        print(f"❌ ({response.status_code})")
        failed_count += 1

print(f"\n{'='*80}")
print("النتيجة النهائية:")
print('='*80)
print(f"✅ تم حذف: {deleted_count} فئة")
print(f"❌ فشل حذف: {failed_count} فئة")
print(f"✅ تم الاحتفاظ بـ: {len(to_keep)} فئة")
print('='*80)

# Verify remaining categories
print(f"\n{'='*80}")
print("التحقق من الفئات المتبقية...")
print('='*80)

response = requests.get(f"{BASE_URL}/categories?limit=500")
if response.status_code == 200:
    data = response.json()
    remaining = data.get("data", [])
    print(f"\n✅ العدد الإجمالي للفئات المتبقية: {len(remaining)}\n")
    for cat in remaining:
        print(f"  • {cat['name']} (ID: {cat['id']})")
else:
    print(f"❌ فشل التحقق")

print("\n" + "=" * 80)
print("انتهى!")
print("=" * 80)
