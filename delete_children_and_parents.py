import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

# IDs to keep
KEEP_IDS = {8151, 8152, 8153, 8154, 8155, 8156, 8157, 8158, 8385}

# Categories that failed to delete (have children)
CATEGORIES_WITH_CHILDREN = [8287, 8295, 8368, 8454, 8317, 8382, 8380, 8384, 8392, 8352]

print("=" * 80)
print("حذف جميع الأطفال ثم الفئات المتبقية")
print("=" * 80)

total_deleted = 0

# Step 1: Delete all children of categories with children
for parent_id in CATEGORIES_WITH_CHILDREN:
    print(f"\n{'='*80}")
    print(f"حذف أطفال الفئة {parent_id}")
    print('='*80)
    
    # Get children
    response = requests.get(f"{BASE_URL}/categories/{parent_id}/children")
    if response.status_code != 200:
        print(f"❌ فشل جلب أطفال {parent_id}")
        continue
    
    data = response.json()
    children = data.get("data", [])
    print(f"✅ عدد الأطفال: {len(children)}")
    
    for child in children:
        child_id = child["id"]
        child_name = child["name"]
        
        print(f"  حذف: {child_name} (ID: {child_id})...", end=" ")
        
        # Check if this child also has children (grandchildren)
        if child.get("has_children", False):
            # Get grandchildren first
            gc_response = requests.get(f"{BASE_URL}/categories/{child_id}/children")
            if gc_response.status_code == 200:
                gc_data = gc_response.json()
                grandchildren = gc_data.get("data", [])
                print(f"\n    (عنده {len(grandchildren)} أحفاد، يحذفهم أولاً...)")
                
                for gc in grandchildren:
                    gc_id = gc["id"]
                    gc_name = gc["name"]
                    print(f"      حذف حفيد: {gc_name} (ID: {gc_id})...", end=" ")
                    
                    gc_del_response = requests.delete(
                        f"{BASE_URL}/categories/{gc_id}",
                        headers=headers
                    )
                    
                    if gc_del_response.status_code in [200, 204]:
                        print("✅")
                        total_deleted += 1
                    else:
                        print(f"❌")
        
        # Now delete the child
        del_response = requests.delete(
            f"{BASE_URL}/categories/{child_id}",
            headers=headers
        )
        
        if del_response.status_code in [200, 204]:
            print("✅" if not child.get("has_children", False) else "    ✅")
            total_deleted += 1
        else:
            print(f"❌" if not child.get("has_children", False) else "    ❌")

# Step 2: Delete the parent categories themselves
print(f"\n{'='*80}")
print("حذف الفئات الرئيسية المتبقية (التي كان عندها أطفال)")
print('='*80)

for parent_id in CATEGORIES_WITH_CHILDREN:
    # Get category info
    response = requests.get(f"{BASE_URL}/categories/{parent_id}", headers=headers)
    if response.status_code == 200:
        cat = response.json()["data"]
        cat_name = cat["name"]
    else:
        cat_name = f"Category {parent_id}"
    
    print(f"حذف: {cat_name} (ID: {parent_id})...", end=" ")
    
    del_response = requests.delete(
        f"{BASE_URL}/categories/{parent_id}",
        headers=headers
    )
    
    if del_response.status_code in [200, 204]:
        print("✅")
        total_deleted += 1
    else:
        print(f"❌ ({del_response.status_code})")

# Step 3: Verify remaining categories
print(f"\n{'='*80}")
print("التحقق النهائي...")
print('='*80)

response = requests.get(f"{BASE_URL}/categories?limit=500")
if response.status_code == 200:
    data = response.json()
    remaining = data.get("data", [])
    print(f"\n✅ العدد الإجمالي للفئات المتبقية: {len(remaining)}")
    print(f"✅ تم حذف: {total_deleted} فئة\n")
    
    if len(remaining) == 9:
        print("🎉 تمام! تبقى فقط الـ9 فئات المطلوبة:\n")
    else:
        print(f"⚠️ المتوقع: 9 فئات، الموجود: {len(remaining)}\n")
    
    for cat in remaining:
        marker = "✅" if cat["id"] in KEEP_IDS else "⚠️"
        print(f"{marker} {cat['name']} (ID: {cat['id']})")
else:
    print(f"❌ فشل التحقق")

print("\n" + "=" * 80)
print("انتهى!")
print("=" * 80)
