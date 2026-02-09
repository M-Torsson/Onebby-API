# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

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


for id_to_check in ids_to_check:
    pass
    if id_to_check in used_ids:
        # Find the category using this ID
        existing_cat = next(cat for cat in categories if cat['id'] == id_to_check)
    else:
        pass

# Show range of existing IDs

# Find gaps in IDs that could be used
gaps = []
for i in range(1, max(used_ids)):
    pass
    if i not in used_ids:
        gaps.append(i)


# Suggest safe IDs
safe_range_start = max(used_ids) + 100
