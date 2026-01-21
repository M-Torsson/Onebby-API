"""
إضافة حفيد FRIGORIFERI INCASSO تحت Frigoriferi
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

def add_frigoriferi_incasso_grandchild():
    """إضافة حفيد FRIGORIFERI INCASSO تحت Frigoriferi"""
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
        print(f"   Parent ID: {frigoriferi.parent_id}")
        print("=" * 80)
        
        # البحث عن أطفال Frigoriferi
        children = db.query(Category).filter(Category.parent_id == frigoriferi.id).all()
        
        print(f"\n📂 أطفال Frigoriferi ({len(children)}):")
        if children:
            for child in children:
                print(f"   ID: {child.id} | {child.name}")
                
                # البحث عن أحفاد كل طفل
                grandchildren = db.query(Category).filter(Category.parent_id == child.id).all()
                if grandchildren:
                    print(f"      🔹 أحفاده ({len(grandchildren)}):")
                    for gc in grandchildren:
                        print(f"         ID: {gc.id} | {gc.name}")
        else:
            print("   لا يوجد أطفال")
        
        # يجب أن يكون هناك على الأقل طفل واحد لإضافة حفيد
        if not children:
            print("\n❌ لا يمكن إضافة حفيد بدون وجود طفل (child)")
            print("   يجب إنشاء طفل أولاً تحت Frigoriferi")
            return
        
        # الحفيد الجديد
        new_grandchild_name = "FRIGORIFERI INCASSO"
        
        # فحص إذا كان الحفيد موجود
        existing = db.query(Category).filter(Category.name == new_grandchild_name).first()
        
        if existing:
            print(f"\n⚠️  تحذير: '{new_grandchild_name}' موجود مسبقاً (ID: {existing.id}, Parent: {existing.parent_id})")
            return
        
        # سنضيف تحت أول طفل
        target_child = children[0]
        
        print("\n" + "=" * 80)
        print(f"💡 سيتم إضافة '{new_grandchild_name}' تحت: {target_child.name} (ID: {target_child.id})")
        print("=" * 80)
        
        # إنشاء الحفيد الجديد
        new_slug = create_slug(new_grandchild_name)
        
        # التحقق من عدم تكرار الـ slug
        existing_slug = db.query(Category).filter(Category.slug == new_slug).first()
        if existing_slug:
            new_slug = f"{new_slug}-new"
        
        # الحصول على آخر sort_order
        existing_grandchildren = db.query(Category).filter(Category.parent_id == target_child.id).all()
        max_sort_order = max([gc.sort_order or 0 for gc in existing_grandchildren]) if existing_grandchildren else 0
        
        new_grandchild = Category(
            name=new_grandchild_name,
            slug=new_slug,
            parent_id=target_child.id,
            is_active=True,
            sort_order=max_sort_order + 1
        )
        
        db.add(new_grandchild)
        db.commit()
        
        print("\n" + "=" * 80)
        print("✅ تم إضافة الحفيد الجديد بنجاح!")
        print("=" * 80)
        print(f"  ID: {new_grandchild.id}")
        print(f"  الاسم: {new_grandchild.name}")
        print(f"  Slug: {new_grandchild.slug}")
        print(f"  Parent (Child): {target_child.name} (ID: {target_child.id})")
        print(f"  Grandparent: {frigoriferi.name} (ID: {frigoriferi.id})")
        
        # عرض الهيكل النهائي
        print("\n" + "=" * 80)
        print("📊 الهيكل النهائي:")
        print("=" * 80)
        for child in children:
            gcs = db.query(Category).filter(Category.parent_id == child.id).all()
            print(f"\n  {child.name} (ID: {child.id})")
            if gcs:
                for gc in gcs:
                    print(f"    └── {gc.name} (ID: {gc.id})")
            else:
                print(f"    └── (لا يوجد أحفاد)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_frigoriferi_incasso_grandchild()
