# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from app.db.session import SessionLocal
from app.models.category import Category

def check_categories():
    db = SessionLocal()
    try:
        # Count all categories
        total = db.query(Category).count()
        
        # Count active categories
        active = db.query(Category).filter(Category.is_active == True).count()
        
        # Count inactive categories
        inactive = db.query(Category).filter(Category.is_active == False).count()
        
        # Count by parent
        main_cats = db.query(Category).filter(Category.parent_id == None).count()
        
        child_cats = db.query(Category).filter(Category.parent_id != None).count()
        
        # Show some examples
        cats = db.query(Category).order_by(Category.id).limit(15).all()
        for cat in cats:
            status = "✅" if cat.is_active else "❌"
            parent = f"parent={cat.parent_id}" if cat.parent_id else "MAIN"
        
    finally:
        db.close()

if __name__ == "__main__":
    check_categories()
