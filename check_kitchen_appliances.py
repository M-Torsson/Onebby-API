import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"

# Kitchen appliances = Elettrodomestici cucina = ID 8155
CATEGORY_ID = 8155

print("=" * 80)
print(f"فحص الفئة 8155 (Elettrodomestici cucina / Kitchen appliances)")
print("=" * 80)

# Get category info
response = requests.get(f"{BASE_URL}/categories/{CATEGORY_ID}")
if response.status_code == 200:
    data = response.json()["data"]
    print(f"\n✅ الفئة: {data['name']}")
    print(f"   ID: {data['id']}")
    print(f"   Has Children: {data['has_children']}")
else:
    print(f"❌ فشل جلب الفئة")
    exit(1)

# Get children
print(f"\n{'='*80}")
print("الأطفال (Children):")
print('='*80)

response = requests.get(f"{BASE_URL}/categories/{CATEGORY_ID}/children")
if response.status_code == 200:
    data = response.json()
    children = data.get("data", [])
    
    if len(children) == 0:
        print("❌ لا توجد أطفال!")
    else:
        print(f"✅ عدد الأطفال: {len(children)}\n")
        
        for child in children:
            print(f"  • {child['name']} (ID: {child['id']}) - has_children: {child['has_children']}")
            
            # Check for grandchildren
            if child['has_children']:
                gc_response = requests.get(f"{BASE_URL}/categories/{child['id']}/children")
                if gc_response.status_code == 200:
                    gc_data = gc_response.json()
                    grandchildren = gc_data.get("data", [])
                    if grandchildren:
                        print(f"    الأحفاد ({len(grandchildren)}):")
                        for gc in grandchildren:
                            print(f"      ▪ {gc['name']} (ID: {gc['id']})")
else:
    print(f"❌ فشل جلب الأطفال: {response.status_code}")

# Try subcategories endpoint
print(f"\n{'='*80}")
print("اختبار /subcategories:")
print('='*80)

response = requests.get(f"{BASE_URL}/categories/{CATEGORY_ID}/subcategories")
if response.status_code == 200:
    data = response.json()
    subs = data.get("data", [])
    
    if len(subs) == 0:
        print("❌ لا توجد subcategories!")
    else:
        print(f"✅ عدد الـ subcategories: {len(subs)}\n")
        for sub in subs:
            print(f"  • {sub['name']} (ID: {sub['id']})")
else:
    print(f"❌ فشل: {response.status_code}")

print("\n" + "=" * 80)
print("انتهى!")
print("=" * 80)
