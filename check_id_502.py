"""
Check if ID 502 is available
"""
import json

# Load backup file
with open('categories_backup_from_api_20260112_185707.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

categories = data.get('categories', [])
used_ids = [cat['id'] for cat in categories]

print("=" * 80)
print("🔍 CHECKING ID 502")
print("=" * 80)

if 502 in used_ids:
    existing_cat = next(cat for cat in categories if cat['id'] == 502)
    print(f"\n❌ ID 502 is ALREADY USED:")
    print(f"   Name: {existing_cat['name']}")
    print(f"   Slug: {existing_cat.get('slug', 'N/A')}")
    print(f"   Parent ID: {existing_cat.get('parent_id', 'Root')}")
else:
    print(f"\n✅ ID 502 is AVAILABLE")

print("\n" + "=" * 80)
print("📋 SUMMARY - IDs to use:")
print("=" * 80)
print("✅ ID 500 - Letti (Parent)")
print("✅ ID 501 - Letti in Ferro Battuto (Child)")
print("✅ ID 502 - Letti in Legno (Child)")
