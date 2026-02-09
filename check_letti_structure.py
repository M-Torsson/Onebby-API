# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

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


for cat_id in child_ids:
    existing = next((cat for cat in categories if cat['id'] == cat_id), None)
    if existing:
        pass
    else:
        pass

for i, cat_id in enumerate(child_ids, 1):
    existing = next((cat for cat in categories if cat['id'] == cat_id), None)
    if existing:
        pass
    else:
        pass
        if cat_id == 501:
            pass
        elif cat_id == 502:
            pass
