import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"

print("=" * 80)
print("التحقق من جميع الفئات - الأطفال والأحفاد")
print("=" * 80)

# Get all categories
print("\n📋 جلب جميع الفئات...")
response = requests.get(f"{BASE_URL}/categories?limit=500")
if response.status_code != 200:
    print(f"❌ فشل: {response.status_code}")
    exit(1)

data = response.json()
all_categories = data.get("data", [])
total = data.get("meta", {}).get("total", 0)
print(f"✅ تم جلب {total} فئة")

# Filter categories with children
categories_with_children = [cat for cat in all_categories if cat.get("has_children", False)]
print(f"\n📊 الفئات التي عندها أطفال: {len(categories_with_children)}")

# Check each category with children
print(f"\n{'='*80}")
print("فحص كل فئة عندها أطفال...")
print('='*80)

issues = []
success_count = 0

for cat in categories_with_children:
    cat_id = cat["id"]
    cat_name = cat["name"]
    parent_id = cat.get("parent_id")
    
    # Determine level
    if parent_id is None:
        level = "Level 1 (Parent)"
    elif any(c["id"] == parent_id and c.get("parent_id") is None for c in all_categories):
        level = "Level 2 (Child)"
    else:
        level = "Level 3 (Grandson)"
    
    print(f"\n{cat_name} (ID: {cat_id}) - {level}")
    
    # Test /children endpoint
    response = requests.get(f"{BASE_URL}/categories/{cat_id}/children")
    if response.status_code == 200:
        children_data = response.json()
        children = children_data.get("data", [])
        if len(children) > 0:
            print(f"  ✅ /children: {len(children)} أطفال")
            for child in children[:3]:
                print(f"     • {child['name']} (ID: {child['id']})")
            if len(children) > 3:
                print(f"     ... و {len(children)-3} آخرين")
            success_count += 1
        else:
            print(f"  ⚠️ /children: فارغ! (has_children=true لكن لا توجد أطفال)")
            issues.append(f"{cat_name} (ID: {cat_id}) - /children فارغ")
    else:
        print(f"  ❌ /children: فشل ({response.status_code})")
        issues.append(f"{cat_name} (ID: {cat_id}) - /children فشل")

# Summary
print(f"\n{'='*80}")
print("النتيجة النهائية:")
print('='*80)
print(f"✅ الفئات التي تعمل: {success_count}/{len(categories_with_children)}")
print(f"❌ مشاكل: {len(issues)}")

if issues:
    print("\n⚠️ الفئات التي فيها مشاكل:")
    for issue in issues:
        print(f"  • {issue}")
else:
    print("\n🎉 جميع الفئات تعمل بشكل صحيح!")

# Test main parent categories for subcategories
print(f"\n{'='*80}")
print("اختبار /subcategories للفئات الرئيسية:")
print('='*80)

parent_categories = [cat for cat in all_categories if cat.get("parent_id") is None]
for parent in parent_categories:
    parent_id = parent["id"]
    parent_name = parent["name"]
    
    response = requests.get(f"{BASE_URL}/categories/{parent_id}/subcategories")
    if response.status_code == 200:
        subs_data = response.json()
        subs = subs_data.get("data", [])
        print(f"✅ {parent_name} (ID: {parent_id}): {len(subs)} subcategories")
    else:
        print(f"❌ {parent_name} (ID: {parent_id}): فشل ({response.status_code})")

print("\n" + "=" * 80)
print("انتهى!")
print("=" * 80)
