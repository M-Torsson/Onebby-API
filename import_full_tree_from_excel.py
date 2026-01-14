"""
Import complete category tree from prezzoforte_category_tree.xlsx
Including Parents, Children, and Grandchildren
"""
import pandas as pd
import requests
import time
from slugify import slugify

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

print("=" * 100)
print("📖 قراءة الشجرة الكاملة من Excel")
print("=" * 100)

df = pd.read_excel('app/excel/prezzoforte_category_tree.xlsx')

print(f"\n✅ تم قراءة {len(df)} صف")
print(f"📊 الآباء: {len(df['Parent'].unique())}")
print(f"📊 الأبناء: {len(df['Child'].dropna().unique())}")
print(f"📊 الأحفاد: {len(df['Grandson'].dropna().unique())}")

# Get current categories from API
print(f"\n{'='*100}")
print("🔍 جلب الفئات الحالية من API")
print("=" * 100)

response = requests.get(
    f"{BASE_URL}/api/v1/categories",
    params={"limit": 200},
    timeout=30
)

current_cats = response.json()['data']
print(f"✅ الفئات الحالية: {len(current_cats)}")

# Build mapping of existing categories by name
existing_by_name = {cat['name'].lower(): cat for cat in current_cats}

# Track created IDs
parent_ids = {}
child_ids = {}

print(f"\n{'='*100}")
print("🌳 بناء الشجرة الكاملة")
print("=" * 100)

# Step 1: Ensure all parents exist
print(f"\n📂 الخطوة 1: التحقق من الآباء...")
for parent_name in df['Parent'].unique():
    parent_lower = parent_name.lower()
    
    if parent_lower in existing_by_name:
        parent_ids[parent_name] = existing_by_name[parent_lower]['id']
        print(f"  ✅ {parent_name} موجود (ID: {parent_ids[parent_name]})")
    else:
        print(f"  ⚠️  {parent_name} غير موجود!")

# Step 2: Create/get all children
print(f"\n👶 الخطوة 2: إنشاء الأبناء...")
created_children = 0
existing_children = 0

for idx, row in df.iterrows():
    parent_name = row['Parent']
    child_name = row['Child']
    
    if pd.isna(child_name):
        continue
    
    # Skip if already processed
    if child_name in child_ids:
        continue
    
    parent_id = parent_ids.get(parent_name)
    if not parent_id:
        print(f"  ❌ لا يمكن إنشاء {child_name}: الأب {parent_name} غير موجود")
        continue
    
    child_lower = child_name.lower()
    
    # Check if exists
    if child_lower in existing_by_name:
        child_ids[child_name] = existing_by_name[child_lower]['id']
        existing_children += 1
        print(f"  ✓ {child_name} موجود")
    else:
        # Create it
        try:
            payload = {
                "name": child_name,
                "parent_id": parent_id,
                "is_active": True,
                "translations": {
                    "it": {"name": child_name},
                    "en": {"name": child_name}  # Will be translated later
                }
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/categories",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()['data']
                child_ids[child_name] = result['id']
                created_children += 1
                print(f"  ✅ {child_name} (ID: {result['id']})")
                time.sleep(0.1)
            else:
                print(f"  ❌ فشل {child_name}: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ خطأ في {child_name}: {e}")

print(f"\n  📊 الأبناء: {created_children} جديد، {existing_children} موجود")

# Step 3: Create all grandchildren
print(f"\n👶👶 الخطوة 3: إنشاء الأحفاد...")
created_grandsons = 0
existing_grandsons = 0
skipped_grandsons = 0

for idx, row in df.iterrows():
    parent_name = row['Parent']
    child_name = row['Child']
    grandson_name = row['Grandson']
    
    if pd.isna(grandson_name):
        continue
    
    # Get child ID
    child_id = child_ids.get(child_name)
    if not child_id:
        skipped_grandsons += 1
        continue
    
    grandson_lower = grandson_name.lower()
    
    # Check if exists
    if grandson_lower in existing_by_name:
        existing_grandsons += 1
        print(f"  ✓ {grandson_name} موجود")
    else:
        # Create it
        try:
            payload = {
                "name": grandson_name,
                "parent_id": child_id,
                "is_active": True,
                "translations": {
                    "it": {"name": grandson_name},
                    "en": {"name": grandson_name}
                }
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/categories",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()['data']
                created_grandsons += 1
                print(f"  ✅ {grandson_name} (ID: {result['id']})")
                time.sleep(0.1)
            elif response.status_code == 409:
                existing_grandsons += 1
                print(f"  ✓ {grandson_name} موجود")
            else:
                print(f"  ❌ فشل {grandson_name}: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ خطأ في {grandson_name}: {e}")

print(f"\n  📊 الأحفاد: {created_grandsons} جديد، {existing_grandsons} موجود، {skipped_grandsons} متخطى")

# Final verification
print(f"\n{'='*100}")
print("✅ التحقق النهائي")
print("=" * 100)

response = requests.get(f"{BASE_URL}/api/v1/categories", timeout=30)
if response.status_code == 200:
    final_total = response.json()['meta']['total']
    print(f"\n📊 إجمالي الفئات الآن: {final_total}")
    print(f"📊 المطلوب: 134 (8 آباء + 84 أبناء + 42 أحفاد)")
    
    if final_total == 134:
        print(f"\n🎉 مثالي! الشجرة مكتملة 100%")
    else:
        diff = 134 - final_total
        print(f"\n⚠️  ناقص {diff} فئة")

print("=" * 100)
