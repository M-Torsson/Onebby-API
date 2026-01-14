import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

CHILD_IDS = [8302, 8303]
PARENT_ID = 8152

print("=" * 80)
print(f"نقل الفئات {CHILD_IDS} إلى 8152 (Piccoli elettrodomestici da incasso)")
print("=" * 80)

# Get parent info
response = requests.get(f"{BASE_URL}/categories/{PARENT_ID}", headers=headers)
if response.status_code == 200:
    parent = response.json()["data"]
    print(f"\n✅ الفئة الرئيسية: {parent['name']} (ID: {PARENT_ID})")
else:
    print(f"❌ فشل جلب الفئة الرئيسية {PARENT_ID}")
    exit(1)

updated_count = 0

for child_id in CHILD_IDS:
    print(f"\n{'='*80}")
    print(f"معالجة الفئة {child_id}")
    print('='*80)
    
    # Get current info
    response = requests.get(f"{BASE_URL}/categories/{child_id}", headers=headers)
    if response.status_code == 200:
        category = response.json()["data"]
        old_parent_id = category.get("parent_id")
        print(f"✅ الفئة: {category['name']} (ID: {child_id})")
        print(f"   Parent الحالي: {old_parent_id}")
    else:
        print(f"❌ فشل جلب الفئة {child_id}")
        continue
    
    # Check if already correct
    if old_parent_id == PARENT_ID:
        print(f"✅ الفئة موجودة بالفعل تحت {PARENT_ID}! لا حاجة للتعديل.")
        continue
    
    # Update parent_id
    print(f"\nتحديث parent_id من {old_parent_id} إلى {PARENT_ID}...")
    update_data = {
        "name": category["name"],
        "parent_id": PARENT_ID,
        "is_active": True
    }
    
    response = requests.put(
        f"{BASE_URL}/categories/{child_id}",
        json=update_data,
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✅ تم نقل {category['name']} إلى {parent['name']}")
        updated_count += 1
    else:
        print(f"❌ فشل التحديث: {response.text}")

# Update has_children for parent if any updates made
if updated_count > 0:
    print(f"\n{'='*80}")
    print(f"تحديث has_children للفئة {PARENT_ID}...")
    print('='*80)
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
print(f"\n{'='*80}")
print(f"اختبار /categories/{PARENT_ID}/children...")
print('='*80)

response = requests.get(f"{BASE_URL}/categories/{PARENT_ID}/children")
if response.status_code == 200:
    children = response.json()["data"]
    print(f"\n✅ عدد الأطفال: {len(children)}\n")
    for child in children[:10]:
        marker = "⭐" if child['id'] in CHILD_IDS else "  "
        print(f"{marker} • {child['name']} (ID: {child['id']})")
    if len(children) > 10:
        print(f"   ... و {len(children)-10} أخرى")
else:
    print(f"❌ فشل الاختبار")

print("\n" + "=" * 80)
print(f"✅ انتهى! تم تحديث {updated_count} فئة")
print("=" * 80)
