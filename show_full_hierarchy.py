import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"

print("=" * 80)
print("تفاصيل الفئات الرئيسية - الأطفال والأحفاد")
print("=" * 80)

parent_ids = [8151, 8152, 8153, 8154, 8155, 8156, 8157, 8158]

for parent_id in parent_ids:
    print(f"\n{'='*80}")
    
    # Get parent info
    response = requests.get(f"{BASE_URL}/categories/{parent_id}")
    if response.status_code != 200:
        print(f"❌ فشل جلب الفئة {parent_id}")
        continue
    
    parent = response.json()["data"]
    print(f"📦 {parent['name']} (ID: {parent_id})")
    print('='*80)
    
    # Get children
    response = requests.get(f"{BASE_URL}/categories/{parent_id}/children")
    if response.status_code != 200:
        print(f"❌ فشل جلب الأطفال")
        continue
    
    children = response.json()["data"]
    print(f"✅ عدد الأطفال: {len(children)}\n")
    
    total_grandchildren = 0
    
    for child in children:
        child_id = child["id"]
        child_name = child["name"]
        has_children = child.get("has_children", False)
        
        if has_children:
            # Get grandchildren
            gc_response = requests.get(f"{BASE_URL}/categories/{child_id}/children")
            if gc_response.status_code == 200:
                grandchildren = gc_response.json()["data"]
                gc_count = len(grandchildren)
                total_grandchildren += gc_count
                print(f"  👶 {child_name} (ID: {child_id}) → {gc_count} أحفاد:")
                for gc in grandchildren:
                    print(f"      ▪ {gc['name']} (ID: {gc['id']})")
            else:
                print(f"  👶 {child_name} (ID: {child_id}) → has_children=true لكن فشل جلب الأحفاد!")
        else:
            print(f"  • {child_name} (ID: {child_id})")
    
    print(f"\n📊 الإحصائيات:")
    print(f"   الأطفال: {len(children)}")
    print(f"   الأحفاد: {total_grandchildren}")
    print(f"   المجموع: {len(children) + total_grandchildren}")

# Overall summary
print(f"\n{'='*80}")
print("الملخص الكامل:")
print('='*80)

response = requests.get(f"{BASE_URL}/categories?limit=500")
if response.status_code == 200:
    data = response.json()
    all_cats = data.get("data", [])
    
    parents = [c for c in all_cats if c.get("parent_id") is None]
    children = [c for c in all_cats if c.get("parent_id") is not None and any(p["id"] == c["parent_id"] for p in parents)]
    grandchildren = [c for c in all_cats if c.get("parent_id") is not None and c not in children]
    
    print(f"📦 الفئات الرئيسية: {len(parents)}")
    print(f"👶 الأطفال (Level 2): {len(children)}")
    print(f"👼 الأحفاد (Level 3): {len(grandchildren)}")
    print(f"🎯 المجموع الكلي: {len(all_cats)}")

print("\n" + "=" * 80)
print("انتهى!")
print("=" * 80)
