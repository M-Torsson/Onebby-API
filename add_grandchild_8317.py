import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

PARENT_ID = 8317
GRANDCHILD_ID = 8426

print("=" * 80)
print(f"إضافة الحفيد 8426 للفئة 8317")
print("=" * 80)

# Get parent info
response = requests.get(f"{BASE_URL}/categories/{PARENT_ID}", headers=headers)
if response.status_code == 200:
    parent = response.json()["data"]
    print(f"\n✅ الفئة: {parent['name']} (ID: {PARENT_ID})")
    print(f"   Parent الحالي: {parent.get('parent_id')}")
else:
    print(f"❌ فشل جلب الفئة {PARENT_ID}")
    exit(1)

# Get grandchild info
print(f"\n{'='*80}")
print(f"معالجة الحفيد {GRANDCHILD_ID}")
print('='*80)

response = requests.get(f"{BASE_URL}/categories/{GRANDCHILD_ID}", headers=headers)
if response.status_code == 200:
    category = response.json()["data"]
    old_parent_id = category.get("parent_id")
    print(f"✅ الفئة: {category['name']} (ID: {GRANDCHILD_ID})")
    print(f"   Parent الحالي: {old_parent_id}")
else:
    print(f"❌ فشل جلب الفئة {GRANDCHILD_ID}")
    exit(1)

# Check if already correct
if old_parent_id == PARENT_ID:
    print(f"✅ الفئة موجودة بالفعل تحت {PARENT_ID}! لا حاجة للتعديل.")
else:
    # Update parent_id
    print(f"\nتحديث parent_id من {old_parent_id} إلى {PARENT_ID}...")
    update_data = {
        "name": category["name"],
        "parent_id": PARENT_ID,
        "is_active": True
    }
    
    response = requests.put(
        f"{BASE_URL}/categories/{GRANDCHILD_ID}",
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
        "parent_id": parent.get("parent_id"),
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
print(f"\n{'='*80}")
print(f"اختبار /categories/{PARENT_ID}/children...")
print('='*80)

response = requests.get(f"{BASE_URL}/categories/{PARENT_ID}/children")
if response.status_code == 200:
    children = response.json()["data"]
    print(f"\n✅ عدد الأحفاد: {len(children)}\n")
    for child in children:
        marker = "⭐" if child['id'] == GRANDCHILD_ID else "  "
        print(f"{marker} • {child['name']} (ID: {child['id']})")
else:
    print(f"❌ فشل الاختبار")

print("\n" + "=" * 80)
print("✅ انتهى!")
print("=" * 80)
