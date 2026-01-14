"""
Analyze old categories and create migration strategy
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"

print("=" * 80)
print("🔍 تحليل الفئات القديمة والجديدة")
print("=" * 80)

# 1. Get old categories (from products)
print("\n1️⃣ جمع الفئات القديمة من المنتجات:")
old_categories = {}
unique_old_cats = set()

# Sample products to find old categories
for skip in range(0, 1000, 500):  # Check first 1000 products
    response = requests.get(
        f"{BASE_URL}/api/v1/products",
        params={"skip": skip, "limit": 500, "active_only": False},
        timeout=60
    )
    
    if response.status_code == 200:
        products = response.json()['data']
        for product in products:
            if product.get('categories'):
                for cat in product['categories']:
                    cat_id = cat['id']
                    cat_name = cat['name']
                    if cat_id not in old_categories:
                        old_categories[cat_id] = cat_name
                        unique_old_cats.add(cat_name.lower())

print(f"   ✅ وجدنا {len(old_categories)} فئة قديمة فريدة")
print(f"\n   🗂️  بعض الفئات القديمة:")
for cat_id, cat_name in list(old_categories.items())[:10]:
    print(f"      • {cat_name} (ID: {cat_id})")

# 2. Get new categories
print("\n2️⃣ الفئات الجديدة:")
response = requests.get(
    f"{BASE_URL}/api/v1/categories",
    params={"limit": 500},
    timeout=30
)

new_categories = {}
if response.status_code == 200:
    cats = response.json()['data']
    for cat in cats:
        new_categories[cat['id']] = {
            'name': cat['name'],
            'slug': cat['slug'],
            'parent_id': cat.get('parent_id')
        }
    print(f"   ✅ {len(new_categories)} فئة جديدة")

# 3. Try to match
print("\n3️⃣ محاولة المطابقة:")
matches = []
no_match = []

for old_id, old_name in old_categories.items():
    found = False
    old_name_lower = old_name.lower()
    
    # Try exact match
    for new_id, new_cat in new_categories.items():
        if new_cat['name'].lower() == old_name_lower:
            matches.append({
                'old_id': old_id,
                'old_name': old_name,
                'new_id': new_id,
                'new_name': new_cat['name'],
                'match_type': 'exact'
            })
            found = True
            break
    
    # Try partial match
    if not found:
        for new_id, new_cat in new_categories.items():
            new_name_lower = new_cat['name'].lower()
            if old_name_lower in new_name_lower or new_name_lower in old_name_lower:
                matches.append({
                    'old_id': old_id,
                    'old_name': old_name,
                    'new_id': new_id,
                    'new_name': new_cat['name'],
                    'match_type': 'partial'
                })
                found = True
                break
    
    if not found:
        no_match.append({'old_id': old_id, 'old_name': old_name})

print(f"   ✅ مطابقات تامة/جزئية: {len(matches)}")
print(f"   ⚠️  بدون مطابقة: {len(no_match)}")

# Show matches
if matches:
    print(f"\n   🔗 بعض المطابقات:")
    for match in matches[:5]:
        print(f"      {match['old_name']} (ID: {match['old_id']}) → {match['new_name']} (ID: {match['new_id']}) [{match['match_type']}]")

# Show non-matches
if no_match:
    print(f"\n   ⚠️  فئات قديمة بدون مطابقة:")
    for nm in no_match[:5]:
        print(f"      • {nm['old_name']} (ID: {nm['old_id']})")

print("\n" + "=" * 80)
print("📋 الاستنتاج")
print("=" * 80)

print(f"\n✅ الطريقة المثلى:")
print(f"   1. قراءة جميع المنتجات ({19506} منتج)")
print(f"   2. لكل منتج، النظر إلى الفئات القديمة")
print(f"   3. استخدام جدول mapping للربط بالفئة الجديدة")
print(f"   4. تحديث المنتج عبر API")

print(f"\n📊 الإحصائيات:")
print(f"   • معدل المطابقة: {len(matches)}/{len(old_categories)} ({len(matches)*100//len(old_categories) if old_categories else 0}%)")
print(f"   • منتجات محتمل تحديثها: ~{19506 * len(matches) // len(old_categories) if old_categories else 0}")

print("\n" + "=" * 80)
