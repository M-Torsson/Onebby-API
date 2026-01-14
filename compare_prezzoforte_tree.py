"""
Compare current API categories with prezzoforte_category_tree.xlsx
"""
import pandas as pd
import requests

print("=" * 100)
print("📖 قراءة ملف prezzoforte_category_tree.xlsx")
print("=" * 100)

# Read the Excel file
df = pd.read_excel('app/excel/prezzoforte_category_tree.xlsx')

print(f"\n✅ تم قراءة الملف بنجاح")
print(f"📊 عدد الصفوف: {len(df)}")
print(f"📋 الأعمدة: {df.columns.tolist()}")

print(f"\n{'='*100}")
print("📋 أول 15 صف:")
print("=" * 100)
print(df.head(15).to_string())

print(f"\n{'='*100}")
print("📊 تحليل بنية الشجرة في الملف:")
print("=" * 100)

# Parse structure
parents = df['Parent'].dropna().unique()
children = df['Child'].dropna().unique()
grandsons = df['Grandson'].dropna().unique()

print(f"\n📂 الآباء (Parents): {len(parents)}")
for parent in parents:
    print(f"   • {parent}")

print(f"\n👶 الأبناء (Children): {len(children)}")
print(f"👶👶 الأحفاد (Grandsons): {len(grandsons)}")

# Count total categories in file
total_categories_in_file = len(parents) + len(children) + len(grandsons)
print(f"\n📊 إجمالي الفئات في الملف: {total_categories_in_file}")

# Show structure for each parent
print(f"\n{'='*100}")
print("🌳 البنية الكاملة:")
print("=" * 100)

for parent in parents:
    parent_rows = df[df['Parent'] == parent]
    parent_children = parent_rows['Child'].dropna().unique()
    
    print(f"\n📂 {parent} ({len(parent_children)} أطفال)")
    
    for child in parent_children:
        child_rows = parent_rows[parent_rows['Child'] == child]
        child_grandsons = child_rows['Grandson'].dropna().unique()
        
        if len(child_grandsons) > 0:
            print(f"   └─ {child} ({len(child_grandsons)} أحفاد)")
            for grandson in child_grandsons[:3]:
                print(f"      └─ {grandson}")
            if len(child_grandsons) > 3:
                print(f"      └─ ... و {len(child_grandsons) - 3} أخرى")
        else:
            print(f"   └─ {child}")

# Compare with current API
print(f"\n{'='*100}")
print("🔍 مقارنة مع API الحالي:")
print("=" * 100)

response = requests.get(
    "https://onebby-api.onrender.com/api/v1/categories",
    params={"limit": 200},
    timeout=30
)

current_cats = response.json()['data']
current_parents = [c for c in current_cats if c['parent_id'] is None]

print(f"\n📊 الإحصائيات:")
print(f"   • في Excel: {total_categories_in_file} فئة")
print(f"   • في API: {len(current_cats)} فئة")
print(f"   • الفرق: {abs(total_categories_in_file - len(current_cats))}")

print(f"\n📂 الآباء:")
print(f"   • في Excel: {len(parents)}")
print(f"   • في API: {len(current_parents)}")

print(f"\n{'='*100}")
print("📋 الآباء في Excel vs API:")
print("=" * 100)

# Map Excel parents to API
api_parent_names = {c['name'].lower(): c for c in current_parents}

for parent in parents:
    parent_lower = parent.lower()
    # Try to find match
    match_found = False
    for api_name in api_parent_names.keys():
        if parent_lower in api_name or api_name in parent_lower:
            print(f"✅ {parent} → {api_parent_names[api_name]['name']}")
            match_found = True
            break
    
    if not match_found:
        print(f"❌ {parent} → غير موجود في API")

print("=" * 100)
