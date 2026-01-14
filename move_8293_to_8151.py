import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

CHILD_ID = 8293
PARENT_ID = 8151

print("=" * 80)
print(f"نقل الفئة 8293 إلى 8151 (Grandi elettrodomestici)")
print("=" * 80)

# Get current info
response = requests.get(f"{BASE_URL}/categories/{CHILD_ID}", headers=headers)
if response.status_code == 200:
    category = response.json()["data"]
    old_parent_id = category.get("parent_id")
    print(f"\n✅ الفئة الحالية: {category['name']} (ID: {CHILD_ID})")
    print(f"   Parent الحالي: {old_parent_id}")
else:
    print(f"❌ فشل جلب الفئة {CHILD_ID}")
    exit(1)

# Get parent info
response = requests.get(f"{BASE_URL}/categories/{PARENT_ID}", headers=headers)
if response.status_code == 200:
    parent = response.json()["data"]
    print(f"   Parent الجديد: {PARENT_ID} ({parent['name']})")
else:
    print(f"❌ فشل جلب الفئة الرئيسية {PARENT_ID}")
    exit(1)

# Check if already correct
if old_parent_id == PARENT_ID:
    print(f"\n✅ الفئة موجودة بالفعل تحت {PARENT_ID}! لا حاجة للتعديل.")
    exit(0)

# Update parent_id
print(f"\nتحديث parent_id من {old_parent_id} إلى {PARENT_ID}...")
update_data = {
    "name": category["name"],
    "parent_id": PARENT_ID,
    "is_active": True
}

response = requests.put(
    f"{BASE_URL}/categories/{CHILD_ID}",
    json=update_data,
    headers=headers
)

if response.status_code == 200:
    print(f"✅ تم نقل {category['name']} إلى {parent['name']}")
else:
    print(f"❌ فشل التحديث: {response.text}")
    exit(1)

# Update has_children for parent
print(f"\nتحديث has_children للفئة {PARENT_ID}...")
update_data = {
    "name": parent["name"],
    "has_children": True,
    "is_active": True
}
response = requests.put(
    f"{BASE_URL}/categories/{PARENT_ID}",
    json=update_data,
    headers=headers
)

if response.status_code == 200:
    print(f"✅ تم تحديث has_children = true")
else:
    print(f"❌ فشل تحديث has_children")

# Test
print(f"\n" + "=" * 80)
print(f"اختبار /categories/{PARENT_ID}/children...")
print("=" * 80)

response = requests.get(f"{BASE_URL}/categories/{PARENT_ID}/children")
if response.status_code == 200:
    children = response.json()["data"]
    print(f"\n✅ عدد الأطفال: {len(children)}\n")
    for child in children:
        marker = "⭐" if child['id'] == CHILD_ID else "  "
        print(f"{marker} • {child['name']} (ID: {child['id']})")
else:
    print(f"❌ فشل الاختبار")

print("\n" + "=" * 80)
print("✅ انتهى!")
print("=" * 80)
