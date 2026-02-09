# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
Check if ID 502 is available
"""
import json

# Load backup file
with open('categories_backup_from_api_20260112_185707.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

categories = data.get('categories', [])
used_ids = [cat['id'] for cat in categories]


if 502 in used_ids:
    existing_cat = next(cat for cat in categories if cat['id'] == 502)
else:
    pass
