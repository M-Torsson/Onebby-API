"""
Check existing categories and prepare to add new Letti category structure
"""
import json

# Load backup file
with open('categories_backup_from_api_20260112_185707.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

categories = data.get('categories', [])

# IDs to check
child_ids = [746, 501, 502, 743, 808, 827]
parent_id = 500

print("=" * 80)
print("🔍 CHECKING EXISTING CATEGORIES")
print("=" * 80)

for cat_id in child_ids:
    existing = next((cat for cat in categories if cat['id'] == cat_id), None)
    if existing:
        print(f"\n✅ ID {cat_id} EXISTS:")
        print(f"   Name: {existing['name']}")
        print(f"   Current Parent: {existing.get('parent_id', 'Root (null)')}")
        print(f"   Slug: {existing.get('slug', 'N/A')}")
    else:
        print(f"\n🆕 ID {cat_id} is NEW - needs to be created")

print("\n" + "=" * 80)
print("📋 PLAN:")
print("=" * 80)
print(f"1. Create Parent Category: Letti (ID: {parent_id})")
print(f"2. Create/Update child categories with parent_id = {parent_id}:")
for i, cat_id in enumerate(child_ids, 1):
    existing = next((cat for cat in categories if cat['id'] == cat_id), None)
    if existing:
        print(f"   {i}. Update ID {cat_id}: {existing['name']} -> set parent to {parent_id}")
    else:
        if cat_id == 501:
            print(f"   {i}. Create ID {cat_id}: Letti in Ferro Battuto")
        elif cat_id == 502:
            print(f"   {i}. Create ID {cat_id}: Letti in Legno")
