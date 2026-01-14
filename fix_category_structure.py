"""
Fix category structure issues:
1. Move Home Cinema under Televisori
2. Move specified categories under 8151
3. Update has_children flags
"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

print("=" * 100)
print("اصلاح بنية الفئات")
print("=" * 100)

# Step 1: Move Home Cinema under Televisori
print("\n1. نقل Home Cinema تحت Televisori...")
try:
    response = requests.put(
        f"{BASE_URL}/api/v1/categories/8454",
        headers=headers,
        json={"parent_id": 8368},
        timeout=30
    )
    if response.status_code == 200:
        print("   ✅ تم نقل Home Cinema")
    else:
        print(f"   ❌ فشل: {response.status_code}")
except Exception as e:
    print(f"   ❌ خطأ: {e}")

# Step 2: Move categories to parent 8151
print("\n2. نقل الفئات إلى 8151...")
categories_to_move = [8287, 8288, 8294, 8289, 8291, 8292, 8290]

for cat_id in categories_to_move:
    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/categories/{cat_id}",
            headers=headers,
            json={"parent_id": 8151},
            timeout=30
        )
        if response.status_code == 200:
            cat_name = response.json()['data'].get('name', cat_id)
            print(f"   ✅ {cat_id} ({cat_name})")
        else:
            print(f"   ❌ {cat_id}: {response.status_code}")
        time.sleep(0.1)
    except Exception as e:
        print(f"   ❌ {cat_id}: {e}")

# Step 3: Update has_children for all categories
print("\n3. تحديث has_children لجميع الفئات...")
print("   جاري جلب جميع الفئات...")

response = requests.get(f"{BASE_URL}/api/v1/categories", params={"limit": 200}, timeout=30)
all_cats = response.json()['data']

print(f"   وجد {len(all_cats)} فئة")

# Build parent -> children mapping
children_count = {}
for cat in all_cats:
    parent_id = cat.get('parent_id')
    if parent_id:
        children_count[parent_id] = children_count.get(parent_id, 0) + 1

# Update categories that need fixing
print("   جاري التحديث...")
updated = 0
errors = 0

for cat in all_cats:
    cat_id = cat['id']
    has_children_actual = cat_id in children_count and children_count[cat_id] > 0
    has_children_db = cat.get('has_children', False)
    
    # Only update if mismatch
    if has_children_actual != has_children_db:
        try:
            response = requests.put(
                f"{BASE_URL}/api/v1/categories/{cat_id}",
                headers=headers,
                json={"has_children": has_children_actual},
                timeout=30
            )
            if response.status_code == 200:
                updated += 1
                status = "✓" if has_children_actual else "✗"
                print(f"   {status} {cat['name']} → {has_children_actual}")
            else:
                errors += 1
            time.sleep(0.05)
        except Exception as e:
            errors += 1

print(f"\n   📊 تم التحديث: {updated}, أخطاء: {errors}")

# Verification
print(f"\n{'='*100}")
print("✅ التحقق النهائي")
print("=" * 100)

# Check Home Cinema
response = requests.get(f"{BASE_URL}/api/v1/categories/8454/children", timeout=30)
if response.status_code == 200:
    hc_children = response.json()['data']
    print(f"\n📺 Home Cinema: {len(hc_children)} أطفال")
    for child in hc_children[:3]:
        print(f"   • {child['name']}")
    if len(hc_children) > 3:
        print(f"   ... و {len(hc_children) - 3} أخرى")

# Check 8151
response = requests.get(f"{BASE_URL}/api/v1/categories/8151/children", timeout=30)
if response.status_code == 200:
    parent_children = response.json()['data']
    print(f"\n🏠 الفئة 8151: {len(parent_children)} أطفال")
    for child in parent_children[:5]:
        print(f"   • {child['name']}")
    if len(parent_children) > 5:
        print(f"   ... و {len(parent_children) - 5} أخرى")

print("\n" + "=" * 100)
print("✅ تم الإصلاح!")
print("=" * 100)
