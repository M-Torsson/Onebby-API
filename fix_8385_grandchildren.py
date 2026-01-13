import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

# Categories to move under parent 8385 (Preparazione cibi - GRANDCHILDREN)
CHILDREN_IDS = [8431, 8438, 8434, 8432, 8436, 8437, 8433, 8439, 8435]
PARENT_ID = 8385

headers = {"X-API-Key": API_KEY}

print("=" * 80)
print(f"تحديث الأحفاد للفئة 8385 (Preparazione cibi) - المستوى الثالث!")
print("=" * 80)

# Get parent info
response = requests.get(f"{BASE_URL}/categories/{PARENT_ID}", headers=headers)
if response.status_code == 200:
    result = response.json()
    parent = result if "data" not in result else result["data"]
    parent_name = parent.get("name", "Preparazione cibi")
    print(f"\n✅ الفئة الفرعية: {parent_name} (ID: {PARENT_ID})")
    print(f"   تحت: Elettrodomestici cucina (8155)")
else:
    print(f"❌ خطأ في جلب الفئة: {response.status_code}")
    print(response.text)
    exit(1)

print(f"\nسيتم نقل {len(CHILDREN_IDS)} أحفاد تحت هذه الفئة:\n")

# Update each child
success_count = 0
for child_id in CHILDREN_IDS:
    # Get category details
    response = requests.get(f"{BASE_URL}/categories/{child_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ [{child_id}] فشل جلب المعلومات")
        continue
    
    category = response.json()["data"]
    old_parent_id = category.get("parent_id")
    
    # Update parent_id
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
        print(f"✅ [{child_id}] {category['name']}: نُقل من {old_parent_id} إلى {PARENT_ID}")
        success_count += 1
    else:
        print(f"❌ [{child_id}] {category['name']}: فشل التحديث - {response.text}")

print("\n" + "=" * 80)
print(f"تم بنجاح: {success_count}/{len(CHILDREN_IDS)}")
print("=" * 80)

# Update has_children for parent 8385
print(f"\nتحديث has_children للفئة {PARENT_ID}...")
update_data = {
    "name": parent_name,
    "has_children": True,
    "is_active": True
}
response = requests.put(
    f"{BASE_URL}/categories/{PARENT_ID}",
    json=update_data,
    headers=headers
)

if response.status_code == 200:
    print(f"✅ تم تحديث has_children = true للفئة {PARENT_ID}")
else:
    print(f"❌ فشل تحديث has_children")

# Test the children endpoint
print(f"\n" + "=" * 80)
print(f"اختبار /categories/{PARENT_ID}/children...")
print("=" * 80)

response = requests.get(f"{BASE_URL}/categories/{PARENT_ID}/children")
if response.status_code == 200:
    children = response.json()["data"]
    print(f"\n✅ عدد الأحفاد (المستوى الثالث): {len(children)}\n")
    for child in children:
        print(f"   • {child['name']} (ID: {child['id']})")
else:
    print(f"❌ فشل الاختبار")

print("\n" + "=" * 80)
print("✅ انتهى! شجرة 3 مستويات تعمل بنجاح!")
print("=" * 80)
