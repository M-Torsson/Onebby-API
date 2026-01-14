import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"

# Test categories
test_cases = [
    {"id": 8382, "name": "Riscaldamento", "expected_children": 2},
    {"id": 8380, "name": "Condizionatori", "expected_children": 2},
    {"id": 8368, "name": "Televisori", "expected_children": 2},
]

print("=" * 80)
print("فحص الأحفاد للفئات")
print("=" * 80)

for test in test_cases:
    cat_id = test["id"]
    cat_name = test["name"]
    expected = test["expected_children"]
    
    print(f"\n{'='*80}")
    print(f"اختبار الفئة {cat_id} ({cat_name})")
    print('='*80)
    
    # Test /children endpoint
    response = requests.get(f"{BASE_URL}/categories/{cat_id}/children")
    if response.status_code == 200:
        data = response.json()
        children = data.get("data", [])
        print(f"✅ /children: {len(children)} أطفال")
        if children:
            for child in children:
                print(f"   • {child['name']} (ID: {child['id']})")
        else:
            print(f"   ❌ لا توجد أطفال!")
    else:
        print(f"❌ /children: فشل - {response.status_code}")
    
    # Test /subcategories endpoint
    response = requests.get(f"{BASE_URL}/categories/{cat_id}/subcategories")
    if response.status_code == 200:
        data = response.json()
        subcategories = data.get("data", [])
        print(f"✅ /subcategories: {len(subcategories)} أحفاد")
        if subcategories:
            for sub in subcategories:
                print(f"   • {sub['name']} (ID: {sub['id']})")
        else:
            print(f"   ⚠️ /subcategories فارغ (هذا طبيعي إذا كانت الفئة level 2)")
    else:
        print(f"❌ /subcategories: فشل - {response.status_code}")

print("\n" + "=" * 80)
print("ملاحظة:")
print("/subcategories يعمل فقط للفئات الرئيسية (level 1)")
print("/children يعمل لجميع المستويات")
print("=" * 80)
