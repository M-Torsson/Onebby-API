import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

# Define all grandchildren mappings
grandchildren_mappings = [
    {
        "parent_id": 8287,
        "parent_name": "Lavatrici",
        "grandchildren": [8412, 8414]
    },
    {
        "parent_id": 8454,
        "parent_name": "Home Cinema",
        "grandchildren": [8455, 8456, 8457, 8458, 8459, 8460, 8461, 8462]
    },
    {
        "parent_id": 8380,
        "parent_name": "Condizionatori",
        "grandchildren": [8452, 8453]
    },
    {
        "parent_id": 8382,
        "parent_name": "Riscaldamento",
        "grandchildren": [8427, 8318]
    }
]

print("=" * 80)
print("إضافة الأحفاد (المستوى الثالث) لعدة فئات")
print("=" * 80)

total_success = 0
total_items = sum(len(mapping["grandchildren"]) for mapping in grandchildren_mappings)

for mapping in grandchildren_mappings:
    parent_id = mapping["parent_id"]
    parent_name = mapping["parent_name"]
    grandchildren_ids = mapping["grandchildren"]
    
    print(f"\n{'='*80}")
    print(f"الفئة الفرعية: {parent_name} (ID: {parent_id})")
    print(f"عدد الأحفاد: {len(grandchildren_ids)}")
    print(f"{'='*80}\n")
    
    success_count = 0
    for child_id in grandchildren_ids:
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
            "parent_id": parent_id,
            "is_active": True
        }
        
        response = requests.put(
            f"{BASE_URL}/categories/{child_id}",
            json=update_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ [{child_id}] {category['name']}: نُقل من {old_parent_id} إلى {parent_id}")
            success_count += 1
            total_success += 1
        else:
            print(f"❌ [{child_id}] {category['name']}: فشل التحديث - {response.text}")
    
    print(f"\nتم بنجاح: {success_count}/{len(grandchildren_ids)} لهذه الفئة")
    
    # Update has_children for parent
    print(f"تحديث has_children للفئة {parent_id}...")
    parent_response = requests.get(f"{BASE_URL}/categories/{parent_id}", headers=headers)
    if parent_response.status_code == 200:
        parent_data = parent_response.json()["data"]
        update_data = {
            "name": parent_data["name"],
            "has_children": True,
            "is_active": True
        }
        response = requests.put(
            f"{BASE_URL}/categories/{parent_id}",
            json=update_data,
            headers=headers
        )
        if response.status_code == 200:
            print(f"✅ تم تحديث has_children = true")
        else:
            print(f"❌ فشل تحديث has_children")

print("\n" + "=" * 80)
print(f"✅ الإجمالي: {total_success}/{total_items} تم بنجاح")
print("=" * 80)

# Test endpoints
print("\n" + "=" * 80)
print("اختبار endpoints الأحفاد...")
print("=" * 80)

for mapping in grandchildren_mappings:
    parent_id = mapping["parent_id"]
    parent_name = mapping["parent_name"]
    
    response = requests.get(f"{BASE_URL}/categories/{parent_id}/children")
    if response.status_code == 200:
        children = response.json()["data"]
        print(f"\n✅ [{parent_id}] {parent_name}: {len(children)} أحفاد")
        for child in children[:3]:  # Show first 3
            print(f"   • {child['name']} (ID: {child['id']})")
        if len(children) > 3:
            print(f"   ... و {len(children)-3} أخرى")
    else:
        print(f"\n❌ [{parent_id}] {parent_name}: فشل الاختبار")

print("\n" + "=" * 80)
print("🎉 انتهى!")
print("=" * 80)
