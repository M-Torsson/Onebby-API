# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
Script to check for duplicate categories in the database
"""
import sys
import os
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.db.session import SessionLocal
from app.models.category import Category, CategoryTranslation


def check_duplicates():
    """Check for duplicate categories"""
    db = SessionLocal()
    
    try:
        pass
        
        # Get all categories
        all_categories = db.query(Category).options(joinedload(Category.translations)).all()
        total = len(all_categories)
        
        
        # Check duplicates by name
        names = [cat.name for cat in all_categories if cat.name]
        name_counter = Counter(names)
        duplicates_by_name = {name: count for name, count in name_counter.items() if count > 1}
        
        if duplicates_by_name:
            pass
            for name, count in sorted(duplicates_by_name.items(), key=lambda x: x[1], reverse=True):
                # Show IDs
                cats = [cat for cat in all_categories if cat.name == name]
                ids = [cat.id for cat in cats]
        else:
            pass
        
        # Check duplicates by slug
        slugs = [cat.slug for cat in all_categories if cat.slug]
        slug_counter = Counter(slugs)
        duplicates_by_slug = {slug: count for slug, count in slug_counter.items() if count > 1}
        
        if duplicates_by_slug:
            pass
            for slug, count in sorted(duplicates_by_slug.items(), key=lambda x: x[1], reverse=True):
                # Show IDs
                cats = [cat for cat in all_categories if cat.slug == slug]
                ids = [cat.id for cat in cats]
        else:
            pass
        
        # Check duplicates by name + parent_id (same name under same parent)
        name_parent_pairs = [(cat.name, cat.parent_id) for cat in all_categories]
        pair_counter = Counter(name_parent_pairs)
        duplicates_by_pair = {pair: count for pair, count in pair_counter.items() if count > 1}
        
        if duplicates_by_pair:
            pass
            for (name, parent_id), count in sorted(duplicates_by_pair.items(), key=lambda x: x[1], reverse=True):
                parent_text = f"Parent ID: {parent_id}" if parent_id else "بدون أب (فئة رئيسية)"
                # Show IDs
                cats = [cat for cat in all_categories if cat.name == name and cat.parent_id == parent_id]
                ids = [cat.id for cat in cats]
        else:
            pass
        
        # Check translation duplicates
        
        # Get all translations
        all_translations = db.query(CategoryTranslation).all()
        
        # Check for duplicate translations (same category_id + lang)
        translation_pairs = [(t.category_id, t.lang) for t in all_translations]
        translation_counter = Counter(translation_pairs)
        duplicate_translations = {pair: count for pair, count in translation_counter.items() if count > 1}
        
        if duplicate_translations:
            pass
            for (cat_id, lang), count in sorted(duplicate_translations.items(), key=lambda x: x[1], reverse=True)[:10]:
                # Show translation names
                trans = [t for t in all_translations if t.category_id == cat_id and t.lang == lang]
                names = [t.name for t in trans]
        else:
            pass
        
        # Check for translations with duplicate names in same language
        for lang in ['it', 'en', 'fr', 'de', 'ar']:
            lang_translations = [t for t in all_translations if t.lang == lang]
            trans_names = [t.name for t in lang_translations if t.name]
            trans_name_counter = Counter(trans_names)
            duplicates = {name: count for name, count in trans_name_counter.items() if count > 1}
            
            if duplicates:
                pass
                for name, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:5]:
                    pass
            else:
                pass
        
        # Summary
        
    except Exception as e:
        import traceback
    finally:
        db.close()


if __name__ == "__main__":
    check_duplicates()
