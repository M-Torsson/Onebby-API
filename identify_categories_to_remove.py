"""
Check all categories and find furniture ones to remove
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

print("=" * 100)
print("🔍 فحص جميع الفئات")
print("=" * 100)

# Get all categories
response = requests.get(
    f"{BASE_URL}/api/v1/categories",
    timeout=60
)

if response.status_code != 200:
    print(f"❌ خطأ: {response.status_code}")
    exit(1)

categories = response.json()['data']
print(f"\n📦 إجمالي الفئات: {len(categories)}\n")

furniture_keywords = [
    'porta tv', 'mobile tv', 'tavol', 'sedi', 'divani', 'letti',
    'armadi', 'comodini', 'mobile', 'arredamento', 'guanciali',
    'poltrone', 'scaffali', 'librerie', 'scrivanie', 'cassettiere'
]

electronics_parents = [
    'grandi elettrodomestici', 'elettrodomestici incasso', 
    'audio video', 'clima', 'elettrodomestici cucina',
    'cura della persona', 'informatica', 'telefonia'
]

furniture_categories = []
old_categories = []
new_electronics_categories = []

for cat in categories:
    cat_name = cat.get('name', '').lower()
    parent_name = cat.get('parent', {}).get('name', '').lower() if cat.get('parent') else ''
    
    # Check if it's furniture
    is_furniture = any(kw in cat_name for kw in furniture_keywords)
    
    # Check if it's from new electronics tree
    is_new_electronics = any(parent in cat_name or parent in parent_name for parent in electronics_parents)
    
    if is_furniture:
        furniture_categories.append(cat)
    elif is_new_electronics or any(parent.lower() in parent_name for parent in electronics_parents):
        new_electronics_categories.append(cat)
    else:
        # Old categories (not furniture, not new electronics)
        if cat_name not in [p.lower() for p in electronics_parents]:
            old_categories.append(cat)

print(f"🏷️ تصنيف الفئات:")
print(f"   • فئات إلكترونيات جديدة: {len(new_electronics_categories)}")
print(f"   • فئات أثاث: {len(furniture_categories)}")
print(f"   • فئات قديمة أخرى: {len(old_categories)}")

print(f"\n{'='*100}")
print(f"🪑 فئات الأثاث للحذف ({len(furniture_categories)}):")
print(f"{'='*100}")
for cat in furniture_categories[:20]:  # Show first 20
    parent_info = ""
    if cat.get('parent'):
        parent_info = f" ← {cat['parent'].get('name', 'N/A')}"
    print(f"   • [{cat['id']}] {cat.get('name', 'N/A')}{parent_info}")

if len(furniture_categories) > 20:
    print(f"   ... و {len(furniture_categories) - 20} فئة أخرى")

print(f"\n{'='*100}")
print(f"📱 فئات الإلكترونيات الجديدة ({len(new_electronics_categories)}):")
print(f"{'='*100}")
for cat in new_electronics_categories[:20]:
    parent_info = ""
    if cat.get('parent'):
        parent = cat['parent']
        if parent.get('parent'):
            parent_info = f" ← {parent.get('name', 'N/A')} ← {parent['parent'].get('name', 'N/A')}"
        else:
            parent_info = f" ← {parent.get('name', 'N/A')}"
    print(f"   • [{cat['id']}] {cat.get('name', 'N/A')}{parent_info}")

if len(new_electronics_categories) > 20:
    print(f"   ... و {len(new_electronics_categories) - 20} فئة أخرى")

print(f"\n{'='*100}")
print(f"🗂️ فئات قديمة أخرى ({len(old_categories)}):")
print(f"{'='*100}")
for cat in old_categories[:20]:
    parent_info = ""
    if cat.get('parent'):
        parent_info = f" ← {cat['parent'].get('name', 'N/A')}"
    print(f"   • [{cat['id']}] {cat.get('name', 'N/A')}{parent_info}")

if len(old_categories) > 20:
    print(f"   ... و {len(old_categories) - 20} فئة أخرى")

print(f"\n{'='*100}")
print("💾 حفظ IDs...")

# Save furniture IDs to delete
with open('furniture_category_ids.txt', 'w', encoding='utf-8') as f:
    for cat in furniture_categories:
        f.write(f"{cat['id']}\n")

# Save old category IDs (might need to remove these too)
with open('old_category_ids.txt', 'w', encoding='utf-8') as f:
    for cat in old_categories:
        f.write(f"{cat['id']}\n")

print(f"✅ تم حفظ:")
print(f"   • furniture_category_ids.txt ({len(furniture_categories)} IDs)")
print(f"   • old_category_ids.txt ({len(old_categories)} IDs)")
print("=" * 100)
