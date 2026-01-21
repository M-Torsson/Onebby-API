"""
إضافة FRIGORIFERI INCASSO كطفل تحت Frigoriferi (حفيد لـ 8151)
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

def add_frigoriferi_incasso():
    """إضافة FRIGORIFERI INCASSO كطفل تحت Frigoriferi"""
    db: Session = next(get_db())
    
    try:
        # البحث عن Frigoriferi
        frigoriferi = db.query(Category).filter(
            Category.parent_id == 8151,
            Category.name == "Frigoriferi"
        ).first()
        
        if not frigoriferi:
            print("❌ لم يتم العثور على category باسم 'Frigoriferi'")
            return
        
        print("=" * 80)
        print(f"✅ تم العثور على Category: {frigoriferi.name} (ID: {frigoriferi.id})")
        print(f"   Parent ID: {frigoriferi.parent_id} (Grandi elettrodomestici)")
        print("=" * 80)
        
        # الحفيد الجديد
        new_child_name = "FRIGORIFERI INCASSO"
        
        # فحص إذا كان موجود
        existing = db.query(Category).filter(Category.name == new_child_name).first()
        
        if existing:
            print(f"\n⚠️  تحذير: '{new_child_name}' موجود مسبقاً (ID: {existing.id}, Parent: {existing.parent_id})")
            return
        
        # إنشاء الـ slug
        new_slug = create_slug(new_child_name)
        
        # التحقق من عدم تكرار الـ slug
        existing_slug = db.query(Category).filter(Category.slug == new_slug).first()
        if existing_slug:
            new_slug = f"{new_slug}-new"
        
        # الحصول على آخر sort_order
        existing_children = db.query(Category).filter(Category.parent_id == frigoriferi.id).all()
        max_sort_order = max([c.sort_order or 0 for c in existing_children]) if existing_children else 0
        
        # إنشاء الـ category الجديد
        new_category = Category(
            name=new_child_name,
            slug=new_slug,
            parent_id=frigoriferi.id,
            is_active=True,
            sort_order=max_sort_order + 1
        )
        
        db.add(new_category)
        db.commit()
        
        print("\n" + "=" * 80)
        print("✅ تم إضافة الحفيد بنجاح!")
        print("=" * 80)
        print(f"  ID: {new_category.id}")
        print(f"  الاسم: {new_category.name}")
        print(f"  Slug: {new_category.slug}")
        print(f"  Parent: {frigoriferi.name} (ID: {frigoriferi.id})")
        print(f"  Grandparent: Grandi elettrodomestici (ID: 8151)")
        print("\n📊 الهيكل:")
        print(f"  8151 (Grandi elettrodomestici)")
        print(f"    └── {frigoriferi.id} ({frigoriferi.name})")
        print(f"         └── {new_category.id} ({new_category.name}) 🆕")
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_frigoriferi_incasso()
