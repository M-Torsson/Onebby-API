"""
إضافة أحفاد تحت Pulizia casa
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

def add_pulizia_casa_grandchildren():
    """إضافة أحفاد تحت Pulizia casa"""
    db: Session = next(get_db())
    
    try:
        # البحث عن Pulizia casa
        pulizia_casa = db.query(Category).filter(
            Category.parent_id == 8151,
            Category.name == "Pulizia casa"
        ).first()
        
        if not pulizia_casa:
            print("❌ لم يتم العثور على category باسم 'Pulizia casa'")
            return
        
        print("=" * 80)
        print(f"✅ تم العثور على: {pulizia_casa.name} (ID: {pulizia_casa.id})")
        print(f"   Parent: Grandi elettrodomestici (8151)")
        print("=" * 80)
        
        # الأحفاد المطلوب إضافتها
        grandchildren_to_add = [
            "Aspirapolvere",
            "Scope elettriche",
            "Lavapavimenti",
            "Ferri da stiro"
        ]
        
        print(f"\n📋 الأحفاد المطلوب إضافتها ({len(grandchildren_to_add)}):")
        for name in grandchildren_to_add:
            print(f"   - {name}")
        
        # فحص الأطفال الحاليين
        current_children = db.query(Category).filter(Category.parent_id == pulizia_casa.id).all()
        print(f"\n📂 الأطفال الحاليين: {len(current_children)}")
        
        # الحصول على آخر sort_order
        max_sort_order = max([c.sort_order or 0 for c in current_children]) if current_children else 0
        
        print("\n" + "=" * 80)
        print("🔄 جاري الإضافة...")
        print("=" * 80)
        
        added_count = 0
        skipped_count = 0
        
        for idx, name in enumerate(grandchildren_to_add, 1):
            # فحص إذا كان موجود
            existing = db.query(Category).filter(Category.name == name).first()
            
            if existing:
                print(f"⚠️  تخطي: '{name}' - موجود مسبقاً (ID: {existing.id})")
                skipped_count += 1
                continue
            
            # إنشاء slug
            slug = create_slug(name)
            
            # التحقق من slug
            existing_slug = db.query(Category).filter(Category.slug == slug).first()
            if existing_slug:
                slug = f"{slug}-{idx}"
            
            # إنشاء category
            new_category = Category(
                name=name,
                slug=slug,
                parent_id=pulizia_casa.id,
                is_active=True,
                sort_order=max_sort_order + idx
            )
            
            db.add(new_category)
            db.flush()
            
            print(f"✅ تمت الإضافة: ID={new_category.id} | {new_category.name}")
            added_count += 1
        
        db.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ تم إضافة {added_count} أحفاد بنجاح!")
        if skipped_count > 0:
            print(f"⚠️  تم تخطي {skipped_count} (موجودة مسبقاً)")
        print("=" * 80)
        
        # عرض الهيكل النهائي
        all_children = db.query(Category).filter(Category.parent_id == pulizia_casa.id).order_by(Category.sort_order).all()
        
        print(f"\n📊 إجمالي أطفال Pulizia casa: {len(all_children)}")
        print("=" * 80)
        print("🌳 الهيكل:")
        print(f"  8151 (Grandi elettrodomestici)")
        print(f"    └── {pulizia_casa.id} (Pulizia casa)")
        for child in all_children:
            print(f"         └── {child.id} ({child.name})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_pulizia_casa_grandchildren()
