"""
Compare current categories with Excel file
"""
import pandas as pd
import requests

# Read Excel file
print("=" * 100)
print("📖 قراءة ملف Excel")
print("=" * 100)

df = pd.read_excel('categories_export_20260112_155343.xlsx')

print(f"\n✅ تم قراءة الملف")
print(f"📊 عدد الصفوف: {len(df)}")
print(f"📋 الأعمدة: {df.columns.tolist()}")

print(f"\n{'='*100}")
print("📋 أول 20 صف من الملف:")
print("=" * 100)
print(df.head(20).to_string())

print(f"\n{'='*100}")
print("📊 إحصائيات الملف:")
print("=" * 100)

# Count parents, children, grandchildren
parents = df[df['Parent'].notna() & df['Child'].isna() & df['Grandson'].isna()]
children = df[df['Parent'].notna() & df['Child'].notna() & df['Grandson'].isna()]
grandchildren = df[df['Parent'].notna() & df['Child'].notna() & df['Grandson'].notna()]

print(f"   • الآباء (Parents): {len(parents)}")
print(f"   • الأبناء (Children): {len(children)}")
print(f"   • الأحفاد (Grandchildren): {len(grandchildren)}")
print(f"   • المجموع: {len(df)}")

# Get unique values
unique_parents = df['Parent'].dropna().unique()
unique_children = df['Child'].dropna().unique()
unique_grandsons = df['Grandson'].dropna().unique()

print(f"\n{'='*100}")
print(f"📊 القيم الفريدة:")
print("=" * 100)
print(f"   • آباء فريدون: {len(unique_parents)}")
print(f"   • أبناء فريدون: {len(unique_children)}")
print(f"   • أحفاد فريدون: {len(unique_grandsons)}")

# Show structure
print(f"\n{'='*100}")
print("🌳 بنية الشجرة في الملف:")
print("=" * 100)

for parent in unique_parents[:5]:
    parent_children = df[df['Parent'] == parent]['Child'].dropna().unique()
    print(f"\n📂 {parent} ({len(parent_children)} أطفال)")
    for child in parent_children[:3]:
        child_grandchildren = df[(df['Parent'] == parent) & (df['Child'] == child)]['Grandson'].dropna().unique()
        if len(child_grandchildren) > 0:
            print(f"   • {child} ({len(child_grandchildren)} أحفاد)")
        else:
            print(f"   • {child}")

# Compare with API
print(f"\n{'='*100}")
print("🔍 مقارنة مع API الحالي:")
print("=" * 100)

response = requests.get("https://onebby-api.onrender.com/api/v1/categories", params={"limit": 200}, timeout=30)
current_cats = response.json()['data']

print(f"\n   • في Excel: {len(df)} فئة")
print(f"   • في API: {len(current_cats)} فئة")
print(f"   • الفرق: {abs(len(df) - len(current_cats))} فئة")

# Check if structure matches
current_parents = [c for c in current_cats if c['parent_id'] is None]
print(f"\n   • آباء في Excel: {len(unique_parents)}")
print(f"   • آباء في API: {len(current_parents)}")

print("=" * 100)
