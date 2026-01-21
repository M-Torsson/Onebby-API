"""
إضافة Pulizia casa كطفل تحت parent 8151
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

def add_pulizia_casa():
    """إضافة Pulizia casa تحت parent 8151"""
    db: Session = next(get_db())
    
    try:
        # التحقق من parent
        parent = db.query(Category).filter(Category.id == 8151).first()
        if not parent:
            print("❌ Parent category 8151 غير موجود!")
            return
        
        print("=" * 80)
        print(f"✅ Parent Category: {parent.name} (ID: {parent.id})")
        print("=" * 80)
        
        # الاسم الجديد
        new_name = "Pulizia casa"
        
        # فحص التكرار
        existing = db.query(Category).filter(Category.name == new_name).first()
        
        if existing:
            print(f"\n⚠️  تحذير: '{new_name}' موجود مسبقاً!")
            print(f"   ID: {existing.id}")
            print(f"   Parent ID: {existing.parent_id}")
            
            if existing.parent_id == 8151:
                print(f"   ✅ موجود بالفعل تحت نفس الـ parent (8151)")
            else:
                print(f"   ⚠️  موجود تحت parent مختلف")
            
            return
        
        # إنشاء slug
        new_slug = create_slug(new_name)
        
        # التحقق من slug
        existing_slug = db.query(Category).filter(Category.slug == new_slug).first()
        if existing_slug:
            new_slug = f"{new_slug}-new"
        
        # الحصول على sort_order
        existing_children = db.query(Category).filter(Category.parent_id == 8151).all()
        max_sort_order = max([c.sort_order or 0 for c in existing_children]) if existing_children else 0
        
        # إنشاء category جديد
        new_category = Category(
            name=new_name,
            slug=new_slug,
            parent_id=8151,
            is_active=True,
            sort_order=max_sort_order + 1
        )
        
        db.add(new_category)
        db.commit()
        
        print("\n✅ تم إضافة Pulizia casa بنجاح!")
        print("=" * 80)
        print(f"  ID: {new_category.id}")
        print(f"  الاسم: {new_category.name}")
        print(f"  Slug: {new_category.slug}")
        print(f"  Parent: {parent.name} (ID: {parent.id})")
        print(f"  Sort Order: {new_category.sort_order}")
        
        # عرض جميع الأطفال
        all_children = db.query(Category).filter(Category.parent_id == 8151).order_by(Category.name).all()
        print("\n" + "=" * 80)
        print(f"📊 إجمالي الأطفال لـ {parent.name}: {len(all_children)}")
        print("=" * 80)
        for child in all_children:
            marker = "🆕" if child.id == new_category.id else "✅"
            print(f"  {marker} {child.name} (ID: {child.id})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_pulizia_casa()
