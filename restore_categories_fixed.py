import pandas as pd
import requests
from slugify import slugify

BASE_URL = "https://onebby-api.onrender.com/api/v1"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

EXCEL_FILE = "app/excel/prezzoforte_category_tree.xlsx"

print("=" * 80)
print("إعادة استيراد جميع الفئات من Excel")
print("=" * 80)

# Read Excel file
print("\n📖 قراءة ملف Excel...")
df = pd.read_excel(EXCEL_FILE)
print(f"✅ تم قراءة {len(df)} صف")

# Get existing categories
print("\n📋 جلب الفئات الموجودة...")
response = requests.get(f"{BASE_URL}/categories?limit=500")
existing_categories = {}
if response.status_code == 200:
    data = response.json()
    for cat in data.get("data", []):
        existing_categories[cat["name"]] = cat["id"]
    print(f"✅ تم جلب {len(existing_categories)} فئة موجودة")

# Create mapping: name -> id
category_map = existing_categories.copy()

# Step 1: Verify parent categories exist
print(f"\n{'='*80}")
print("Step 1: التحقق من الفئات الرئيسية (Parents)")
print('='*80)

parents = df['Parent'].unique()
for parent_name in parents:
    if pd.isna(parent_name):
        continue
    
    if parent_name in category_map:
        print(f"✅ {parent_name} (ID: {category_map[parent_name]})")
    else:
        print(f"⚠️ {parent_name} غير موجود!")

# Step 2: Create all children
print(f"\n{'='*80}")
print("Step 2: إنشاء الأطفال (Children)")
print('='*80)

created_children = 0
for _, row in df.iterrows():
    parent_name = row['Parent']
    child_name = row['Child']
    
    if pd.isna(child_name):
        continue
    
    if child_name in category_map:
        print(f"⏭️ {child_name} موجود بالفعل (ID: {category_map[child_name]})")
        continue
    
    parent_id = category_map.get(parent_name)
    if not parent_id:
        print(f"⚠️ لم يتم العثور على الفئة الرئيسية: {parent_name}")
        continue
    
    data = {
        "name": child_name,
        "slug": slugify(child_name),
        "parent_id": parent_id,
        "sort_order": 0,
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/categories", json=data, headers=headers)
    if response.status_code in [200, 201]:
        result = response.json()
        cat_id = result.get("data", {}).get("id")
        category_map[child_name] = cat_id
        created_children += 1
        print(f"✅ {child_name} (ID: {cat_id}) -> تحت {parent_name} ({parent_id})")
    else:
        error_text = response.text[:200]
        print(f"❌ فشل إنشاء {child_name}: {response.status_code} - {error_text}")

print(f"\n✅ تم إنشاء {created_children} طفل جديد")

# Step 3: Create all grandsons
print(f"\n{'='*80}")
print("Step 3: إنشاء الأحفاد (Grandsons)")
print('='*80)

created_grandsons = 0
for _, row in df.iterrows():
    child_name = row['Child']
    grandson_name = row['Grandson']
    
    if pd.isna(grandson_name):
        continue
    
    if grandson_name in category_map:
        print(f"⏭️ {grandson_name} موجود بالفعل (ID: {category_map[grandson_name]})")
        continue
    
    child_id = category_map.get(child_name)
    if not child_id:
        print(f"⚠️ لم يتم العثور على الفئة الفرعية: {child_name}")
        continue
    
    data = {
        "name": grandson_name,
        "slug": slugify(grandson_name),
        "parent_id": child_id,
        "sort_order": 0,
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/categories", json=data, headers=headers)
    if response.status_code in [200, 201]:
        result = response.json()
        cat_id = result.get("data", {}).get("id")
        category_map[grandson_name] = cat_id
        created_grandsons += 1
        print(f"✅ {grandson_name} (ID: {cat_id}) -> تحت {child_name} ({child_id})")
    else:
        error_text = response.text[:200]
        print(f"❌ فشل إنشاء {grandson_name}: {response.status_code} - {error_text}")

print(f"\n✅ تم إنشاء {created_grandsons} حفيد جديد")

# Verification
print(f"\n{'='*80}")
print("التحقق النهائي...")
print('='*80)

response = requests.get(f"{BASE_URL}/categories?limit=500")
if response.status_code == 200:
    data = response.json()
    total = data.get("meta", {}).get("total", 0)
    print(f"\n🎉 العدد الإجمالي للفئات: {total}")
    print(f"   المتوقع: 134")
    
    if total == 134:
        print("\n✅✅✅ تم استعادة جميع الفئات بنجاح! ✅✅✅")
    elif total < 134:
        print(f"\n⚠️ لا يزال ينقص {134 - total} فئة")
    else:
        print(f"\n⚠️ الفئات أكثر من المتوقع بـ {total - 134}")
else:
    print(f"❌ فشل التحقق")

print("\n" + "=" * 80)
print("انتهى!")
print("=" * 80)
