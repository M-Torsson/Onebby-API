import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

# Categories to move under parent 8154 (Clima)
CHILDREN_IDS = [8380, 8317, 8381, 8382, 8383]
PARENT_ID = 8154

headers = {"X-API-Key": API_KEY}

print("=" * 80)
print(f"تحديث الأطفال للفئة 8154 (Clima)")
print("=" * 80)

# Get parent info
response = requests.get(f"{BASE_URL}/categories/{PARENT_ID}", headers=headers)
if response.status_code == 200:
    result = response.json()
    parent = result if "data" not in result else result["data"]
    parent_name = parent.get("name", "Clima")
    print(f"\n✅ الفئة الرئيسية: {parent_name} (ID: {PARENT_ID})")
else:
    print(f"❌ خطأ في جلب الفئة الرئيسية: {response.status_code}")
    print(response.text)
    exit(1)

print(f"\nسيتم نقل {len(CHILDREN_IDS)} فئات تحت هذه الفئة الرئيسية:\n")

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

# Update has_children for parent 8154
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
    print(f"\n✅ عدد الأطفال: {len(children)}\n")
    for child in children:
        print(f"   • {child['name']} (ID: {child['id']})")
else:
    print(f"❌ فشل الاختبار")

print("\n" + "=" * 80)
print("✅ انتهى!")
print("=" * 80)
