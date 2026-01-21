"""
إضافة Lavatrici Slim كطفل رابع تحت Lavatrici
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

def add_lavatrici_slim_as_child():
    """إضافة Lavatrici Slim كطفل مباشر تحت Lavatrici"""
    db: Session = next(get_db())
    
    try:
        # البحث عن Lavatrici
        lavatrici = db.query(Category).filter(
            Category.parent_id == 8151,
            Category.name == "Lavatrici"
        ).first()
        
        if not lavatrici:
            print("❌ لم يتم العثور على category باسم 'Lavatrici'")
            return
        
        print("=" * 80)
        print(f"✅ تم العثور على Category: {lavatrici.name} (ID: {lavatrici.id})")
        print("=" * 80)
        
        # عرض الأطفال الحاليين
        current_children = db.query(Category).filter(Category.parent_id == lavatrici.id).all()
        print(f"\n📂 الأطفال الحاليين ({len(current_children)}):")
        for child in current_children:
            print(f"   {child.id} - {child.name}")
        
        # فحص إذا كان Lavatrici Slim موجود كطفل
        new_child_name = "Lavatrici Slim"
        existing_child = db.query(Category).filter(
            Category.parent_id == lavatrici.id,
            Category.name == new_child_name
        ).first()
        
        if existing_child:
            print(f"\n✅ '{new_child_name}' موجود بالفعل كطفل تحت Lavatrici (ID: {existing_child.id})")
            return
        
        # فحص إذا كان موجود في مكان آخر
        existing_elsewhere = db.query(Category).filter(Category.name == new_child_name).first()
        if existing_elsewhere:
            print(f"\n⚠️  '{new_child_name}' موجود في قاعدة البيانات:")
            print(f"   ID: {existing_elsewhere.id}")
            print(f"   Parent ID: {existing_elsewhere.parent_id}")
            
            # حذفه من المكان القديم
            print(f"\n🔄 سيتم نقله من Parent {existing_elsewhere.parent_id} إلى Parent {lavatrici.id}")
            existing_elsewhere.parent_id = lavatrici.id
            
            # تحديث sort_order
            max_sort_order = max([c.sort_order or 0 for c in current_children]) if current_children else 0
            existing_elsewhere.sort_order = max_sort_order + 1
            
            db.commit()
            
            print("\n✅ تم نقل Lavatrici Slim بنجاح!")
            print(f"   ID: {existing_elsewhere.id}")
            print(f"   Parent الجديد: {lavatrici.name} (ID: {lavatrici.id})")
        else:
            # إنشاء جديد
            new_slug = create_slug(new_child_name)
            
            # التحقق من slug
            existing_slug = db.query(Category).filter(Category.slug == new_slug).first()
            if existing_slug:
                new_slug = f"{new_slug}-child"
            
            # الحصول على sort_order
            max_sort_order = max([c.sort_order or 0 for c in current_children]) if current_children else 0
            
            new_child = Category(
                name=new_child_name,
                slug=new_slug,
                parent_id=lavatrici.id,
                is_active=True,
                sort_order=max_sort_order + 1
            )
            
            db.add(new_child)
            db.commit()
            
            print("\n✅ تم إضافة Lavatrici Slim بنجاح!")
            print(f"   ID: {new_child.id}")
            print(f"   Parent: {lavatrici.name} (ID: {lavatrici.id})")
        
        # عرض الأطفال النهائيين
        final_children = db.query(Category).filter(Category.parent_id == lavatrici.id).order_by(Category.sort_order).all()
        print("\n" + "=" * 80)
        print(f"📊 إجمالي الأطفال الآن ({len(final_children)}):")
        print("=" * 80)
        for child in final_children:
            print(f"   {child.id} - {child.name}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_lavatrici_slim_as_child()
