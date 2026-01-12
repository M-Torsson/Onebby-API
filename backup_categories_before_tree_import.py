"""
Backup current categories before importing new tree structure
"""
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import joinedload
from app.db.session import SessionLocal
from app.models.category import Category, CategoryTranslation


def backup_categories():
    """Backup all current categories to JSON file"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("📦 عمل نسخة احتياطية من الكاتيجوري")
        print("=" * 80)
        
        # Get all categories with translations
        categories = db.query(Category).options(joinedload(Category.translations)).all()
        
        print(f"\n✅ تم العثور على {len(categories)} فئة")
        
        # Convert to dict
        backup_data = {
            "backup_date": datetime.now().isoformat(),
            "total_categories": len(categories),
            "categories": []
        }
        
        for cat in categories:
            cat_data = {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "image": cat.image,
                "icon": cat.icon,
                "sort_order": cat.sort_order,
                "is_active": cat.is_active,
                "parent_id": cat.parent_id,
                "created_at": cat.created_at.isoformat() if cat.created_at else None,
                "updated_at": cat.updated_at.isoformat() if cat.updated_at else None,
                "translations": []
            }
            
            # Add translations
            for trans in cat.translations:
                cat_data["translations"].append({
                    "id": trans.id,
                    "lang": trans.lang,
                    "name": trans.name,
                    "slug": trans.slug,
                    "description": trans.description
                })
            
            backup_data["categories"].append(cat_data)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"categories_backup_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ تم حفظ النسخة الاحتياطية في: {filename}")
        print(f"📊 عدد الفئات: {len(categories)}")
        
        # Show summary
        main_cats = [c for c in categories if not c.parent_id]
        child_cats = [c for c in categories if c.parent_id]
        
        print(f"\n📋 ملخص:")
        print(f"   - فئات رئيسية: {len(main_cats)}")
        print(f"   - فئات فرعية: {len(child_cats)}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    backup_categories()
