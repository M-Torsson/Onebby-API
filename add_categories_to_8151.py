"""
إضافة 4 categories جديدة تحت parent 8151
"""
from app.db.session import get_db
from app.models.category import Category
from sqlalchemy.orm import Session
import re

def create_slug(name: str) -> str:
    """إنشاء slug من الاسم"""
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def add_categories_to_8151():
    """إضافة categories جديدة تحت parent 8151"""
    db: Session = next(get_db())
    
    try:
        # التحقق من parent
        parent = db.query(Category).filter(Category.id == 8151).first()
        if not parent:
            print("❌ Parent category 8151 غير موجود!")
            return
        
        print(f"✅ Parent Category: {parent.name} (ID: {parent.id})")
        print("=" * 80)
        
        # الأسماء المطلوب إضافتها
        categories_to_add = [
            "Lavatrici incasso",
            "Lavasciuga libera installazione",
            "Lavasciuga incasso",
            "Lavastoviglie libera installazione"
        ]
        
        # الحصول على آخر sort_order
        existing_children = db.query(Category).filter(Category.parent_id == 8151).all()
        max_sort_order = max([c.sort_order or 0 for c in existing_children]) if existing_children else 0
        
        added_categories = []
        
        for idx, name in enumerate(categories_to_add, 1):
            slug = create_slug(name)
            
            # التحقق من عدم وجود slug مكرر
            existing_slug = db.query(Category).filter(Category.slug == slug).first()
            if existing_slug:
                slug = f"{slug}-{idx}"
            
            # إنشاء category جديد
            new_category = Category(
                name=name,
                slug=slug,
                parent_id=8151,
                is_active=True,
                sort_order=max_sort_order + idx
            )
            
            db.add(new_category)
            db.flush()  # للحصول على ID
            
            added_categories.append(new_category)
            print(f"✅ تمت الإضافة: ID={new_category.id} | Name={new_category.name} | Slug={new_category.slug}")
        
        # حفظ التغييرات
        db.commit()
        
        print("=" * 80)
        print(f"✅ تم إضافة {len(added_categories)} categories بنجاح!")
        print("=" * 80)
        
        # عرض ملخص
        print("\nملخص Categories المضافة:")
        for cat in added_categories:
            print(f"  ID: {cat.id} | {cat.name} | Parent: {cat.parent_id}")
        
        # عرض كل الأطفال الآن
        all_children = db.query(Category).filter(Category.parent_id == 8151).order_by(Category.sort_order).all()
        print(f"\n📊 إجمالي الأطفال لـ Category 8151: {len(all_children)}")
        for child in all_children:
            print(f"  ID: {child.id} | {child.name} | Sort: {child.sort_order}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_categories_to_8151()
