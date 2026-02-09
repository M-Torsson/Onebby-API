# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
Check for duplicate categories via API
"""
import requests
from collections import Counter

# API Configuration
BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "your-api-key-here"  # Add your API key

def check_duplicates_via_api():
    """Check for duplicates by fetching all categories from API"""
    
    # Fetch all categories
    
    try:
        # Get all categories with max limit (500 per request)
        all_categories = []
        skip = 0
        limit = 500
        
        while True:
            response = requests.get(
                f"{BASE_URL}/api/v1/categories",
                params={
                    "skip": skip,
                    "limit": limit,
                    "lang": "it",
                    "active_only": False
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return
            
            data = response.json()
            categories = data.get("data", [])
            meta = data.get("meta", {})
            total = meta.get("total", 0)
            
            all_categories.extend(categories)
            
            
            # Check if we have all categories
            if not meta.get("has_next", False) or len(categories) == 0:
                break
            
            skip += limit
        
        categories = all_categories
        
        
        # Check duplicates by name
        names = [cat["name"] for cat in categories if cat.get("name")]
        name_counter = Counter(names)
        duplicates_by_name = {name: count for name, count in name_counter.items() if count > 1}
        
        if duplicates_by_name:
            pass
            for name, count in sorted(duplicates_by_name.items(), key=lambda x: x[1], reverse=True)[:20]:
                # Show IDs
                cats = [cat for cat in categories if cat.get("name") == name]
                ids = [cat["id"] for cat in cats]
                parent_ids = [cat.get("parent_id") for cat in cats]
        else:
            pass
        
        # Check duplicates by slug
        slugs = [cat["slug"] for cat in categories if cat.get("slug")]
        slug_counter = Counter(slugs)
        duplicates_by_slug = {slug: count for slug, count in slug_counter.items() if count > 1}
        
        if duplicates_by_slug:
            pass
            for slug, count in sorted(duplicates_by_slug.items(), key=lambda x: x[1], reverse=True)[:20]:
                # Show IDs
                cats = [cat for cat in categories if cat.get("slug") == slug]
                ids = [cat["id"] for cat in cats]
                names = [cat["name"] for cat in cats]
        else:
            pass
        
        # Check duplicates by name + parent_id
        name_parent_pairs = [(cat["name"], cat.get("parent_id")) for cat in categories]
        pair_counter = Counter(name_parent_pairs)
        duplicates_by_pair = {pair: count for pair, count in pair_counter.items() if count > 1}
        
        if duplicates_by_pair:
            pass
            for (name, parent_id), count in sorted(duplicates_by_pair.items(), key=lambda x: x[1], reverse=True)[:20]:
                parent_text = f"Parent ID: {parent_id}" if parent_id else "بدون أب (فئة رئيسية)"
                # Show IDs
                cats = [cat for cat in categories if cat["name"] == name and cat.get("parent_id") == parent_id]
                ids = [cat["id"] for cat in cats]
        else:
            pass
        
        # Check main categories only
        main_categories = [cat for cat in categories if not cat.get("parent_id")]
        
        main_names = [cat["name"] for cat in main_categories]
        main_name_counter = Counter(main_names)
        main_duplicates = {name: count for name, count in main_name_counter.items() if count > 1}
        
        if main_duplicates:
            pass
            for name, count in sorted(main_duplicates.items(), key=lambda x: x[1], reverse=True):
                cats = [cat for cat in main_categories if cat["name"] == name]
                ids = [cat["id"] for cat in cats]
        else:
            pass
        
        # Check child categories
        child_categories = [cat for cat in categories if cat.get("parent_id")]
        
        # Summary
        
        # Save to JSON file
        import json
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"categories_backup_from_api_{timestamp}.json"
        
        backup_data = {
            "backup_date": datetime.now().isoformat(),
            "total_categories": len(categories),
            "categories": categories,
            "meta": {
                "main_categories": len(main_categories),
                "child_categories": len(child_categories),
                "duplicates_by_name": len(duplicates_by_name),
                "duplicates_by_slug": len(duplicates_by_slug)
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        
        return categories
        
    except requests.exceptions.RequestException as e:
        return []
    except Exception as e:
        import traceback


if __name__ == "__main__":
    check_duplicates_via_api()
