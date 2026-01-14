from app.db.session import SessionLocal
from app.models.category import Category

def check_categories():
    db = SessionLocal()
    try:
        # Count all categories
        total = db.query(Category).count()
        print(f"✅ Total categories in DB: {total}")
        
        # Count active categories
        active = db.query(Category).filter(Category.is_active == True).count()
        print(f"✅ Active categories: {active}")
        
        # Count inactive categories
        inactive = db.query(Category).filter(Category.is_active == False).count()
        print(f"❌ Inactive categories: {inactive}")
        
        # Count by parent
        main_cats = db.query(Category).filter(Category.parent_id == None).count()
        print(f"📁 Main categories (parent_id = null): {main_cats}")
        
        child_cats = db.query(Category).filter(Category.parent_id != None).count()
        print(f"📂 Child categories (have parent): {child_cats}")
        
        # Show some examples
        print("\n--- Sample categories (first 15) ---")
        cats = db.query(Category).order_by(Category.id).limit(15).all()
        for cat in cats:
            status = "✅" if cat.is_active else "❌"
            parent = f"parent={cat.parent_id}" if cat.parent_id else "MAIN"
            print(f"{status} ID:{cat.id} | {cat.name} | {parent}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_categories()
