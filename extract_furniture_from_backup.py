"""
Extract furniture categories from backup JSON file
"""
import json

# Load backup file
with open('categories_backup_from_api_20260112_185707.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

categories = data.get('categories', [])

# Furniture related keywords in Italian
FURNITURE_KEYWORDS = [
    'mobili',           # furniture
    'arredamento',      # furnishing
    'divani',           # sofas
    'letti',            # beds
    'armadi',           # wardrobes
    'tavoli',           # tables
    'sedie',            # chairs
    'scaffali',         # shelves
    'librerie',         # bookcases
    'cassettiere',      # chest of drawers
    'comodini',         # nightstands
    'credenze',         # sideboards
    'scrivania',        # desk
    'scrivanie',        # desks
    'poltrone',         # armchairs
    'soggiorno',        # living room
    'camera da letto',  # bedroom
    'camera letto',     # bedroom
    'sala da pranzo',   # dining room
    'bagno',            # bathroom (for bathroom furniture)
    'ingresso',         # entrance
    'ufficio',          # office
    'componenti',       # components for furniture
    'ferramenta',       # hardware for furniture
    'piedi',            # furniture legs
]

print("🔍 Extracting furniture categories from backup...")
print("=" * 80)

furniture_categories = []

for cat in categories:
    name = cat.get('name', '').lower()
    
    # Check if it's furniture related
    is_furniture = any(keyword in name for keyword in FURNITURE_KEYWORDS)
    
    # Additional check: exclude mobility/transport furniture
    if 'mobilit' in name and 'elettrica' in name:
        is_furniture = False
    if 'giochi' in name:
        is_furniture = False
    
    if is_furniture:
        furniture_categories.append(cat)

# Sort by parent_id and name
furniture_categories.sort(key=lambda x: (x.get('parent_id') or 0, x.get('name', '')))

print(f"\n📊 Found {len(furniture_categories)} furniture categories\n")
print("=" * 80)

# Group by parent
root_categories = [c for c in furniture_categories if c.get('parent_id') is None]
child_categories = [c for c in furniture_categories if c.get('parent_id') is not None]

print(f"\n🏠 ROOT FURNITURE CATEGORIES ({len(root_categories)}):")
print("-" * 80)
for cat in root_categories:
    print(f"ID: {cat['id']:5} | {cat['name']}")

print(f"\n📦 CHILD FURNITURE CATEGORIES ({len(child_categories)}):")
print("-" * 80)
for cat in child_categories:
    parent_id = cat.get('parent_id', 'N/A')
    print(f"ID: {cat['id']:5} | Parent: {parent_id:5} | {cat['name']}")

# Save to file
output_file = "furniture_categories_list.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("FURNITURE CATEGORIES - EXTRACTED FROM BACKUP\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"ROOT CATEGORIES ({len(root_categories)}):\n")
    f.write("-" * 80 + "\n")
    for cat in root_categories:
        f.write(f"ID: {cat['id']:5} | {cat['name']}\n")
    
    f.write(f"\n\nCHILD CATEGORIES ({len(child_categories)}):\n")
    f.write("-" * 80 + "\n")
    for cat in child_categories:
        parent_id = cat.get('parent_id', 'N/A')
        f.write(f"ID: {cat['id']:5} | Parent: {parent_id:5} | {cat['name']}\n")
    
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("FURNITURE CATEGORY IDs ONLY:\n")
    f.write("-" * 80 + "\n")
    for cat in furniture_categories:
        f.write(f"{cat['id']}\n")
    
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("FURNITURE CATEGORY NAMES ONLY:\n")
    f.write("-" * 80 + "\n")
    for cat in furniture_categories:
        f.write(f"{cat['name']}\n")
    
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("DETAILED FURNITURE CATEGORIES:\n")
    f.write("-" * 80 + "\n")
    for cat in furniture_categories:
        f.write(f"\nID: {cat['id']}\n")
        f.write(f"Name: {cat['name']}\n")
        f.write(f"Slug: {cat.get('slug', 'N/A')}\n")
        f.write(f"Parent ID: {cat.get('parent_id', 'N/A')}\n")
        f.write(f"Sort Order: {cat.get('sort_order', 'N/A')}\n")
        f.write("-" * 40 + "\n")

print(f"\n✅ Results saved to: {output_file}")
print(f"\n📋 Summary:")
print(f"   - Total furniture categories: {len(furniture_categories)}")
print(f"   - Root categories: {len(root_categories)}")
print(f"   - Child categories: {len(child_categories)}")

# Also create a simple list
simple_file = "furniture_names_simple.txt"
with open(simple_file, 'w', encoding='utf-8') as f:
    f.write("FURNITURE CATEGORY NAMES\n")
    f.write("=" * 80 + "\n\n")
    for cat in furniture_categories:
        f.write(f"{cat['name']}\n")

print(f"✅ Simple list saved to: {simple_file}")
