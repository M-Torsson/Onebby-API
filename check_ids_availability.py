"""
Check if IDs 500 and 501 are available for new categories
"""
import json

# Load backup file
with open('categories_backup_from_api_20260112_185707.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

categories = data.get('categories', [])

# Check IDs
ids_to_check = [500, 501]
used_ids = [cat['id'] for cat in categories]

print("=" * 80)
print("🔍 CHECKING ID AVAILABILITY")
print("=" * 80)

for id_to_check in ids_to_check:
    if id_to_check in used_ids:
        # Find the category using this ID
        existing_cat = next(cat for cat in categories if cat['id'] == id_to_check)
        print(f"\n❌ ID {id_to_check} is ALREADY USED:")
        print(f"   Name: {existing_cat['name']}")
        print(f"   Slug: {existing_cat.get('slug', 'N/A')}")
        print(f"   Parent ID: {existing_cat.get('parent_id', 'Root')}")
    else:
        print(f"\n✅ ID {id_to_check} is AVAILABLE")

# Show range of existing IDs
print("\n" + "=" * 80)
print("📊 EXISTING ID STATISTICS:")
print("=" * 80)
print(f"Minimum ID: {min(used_ids)}")
print(f"Maximum ID: {max(used_ids)}")
print(f"Total categories: {len(used_ids)}")

# Find gaps in IDs that could be used
gaps = []
for i in range(1, max(used_ids)):
    if i not in used_ids:
        gaps.append(i)

print(f"\n📋 Available ID gaps (first 20): {gaps[:20]}")

# Suggest safe IDs
safe_range_start = max(used_ids) + 100
print(f"\n💡 SAFE ID RANGE SUGGESTION:")
print(f"   Use IDs from {safe_range_start} onwards")
print(f"   Suggested for 'Letti': {safe_range_start}")
print(f"   Suggested for 'Letti in Ferro Battuto': {safe_range_start + 1}")
