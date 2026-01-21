"""
إضافة Clima تحت 8151 مع 4 أحفاد
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

def add_clima_with_children():
    """إضافة Clima تحت 8151 مع الأحفاد"""
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
        
        # التحقق من وجود Clima
        existing_clima = db.query(Category).filter(
            Category.parent_id == 8151,
            Category.name == "Clima"
        ).first()
        
        if existing_clima:
            print(f"\n✅ 'Clima' موجود بالفعل (ID: {existing_clima.id})")
            clima = existing_clima
        else:
            # إنشاء Clima
            clima_slug = create_slug("Clima")
            
            # التحقق من slug
            existing_slug = db.query(Category).filter(Category.slug == clima_slug).first()
            if existing_slug:
                clima_slug = f"{clima_slug}-new"
            
            # الحصول على sort_order
            existing_children = db.query(Category).filter(Category.parent_id == 8151).all()
            max_sort_order = max([c.sort_order or 0 for c in existing_children]) if existing_children else 0
            
            clima = Category(
                name="Clima",
                slug=clima_slug,
                parent_id=8151,
                is_active=True,
                sort_order=max_sort_order + 1
            )
            
            db.add(clima)
            db.flush()
            
            print(f"\n✅ تمت إضافة Clima (ID: {clima.id})")
        
        # الأحفاد المطلوب إضافتها
        grandchildren = [
            "Climatizzatori fissi",
            "Condizionatori portatili",
            "Deumidificatori",
            "Ventilatori"
        ]
        
        print("\n" + "=" * 80)
        print(f"📋 الأحفاد المطلوب إضافتها ({len(grandchildren)}):")
        for name in grandchildren:
            print(f"   - {name}")
        print("=" * 80)
        
        # إضافة الأحفاد
        added_count = 0
        skipped_count = 0
        
        # الحصول على آخر sort_order
        existing_grandchildren = db.query(Category).filter(Category.parent_id == clima.id).all()
        max_sort_order = max([c.sort_order or 0 for c in existing_grandchildren]) if existing_grandchildren else 0
        
        print("\n🔄 جاري الإضافة...")
        
        for idx, name in enumerate(grandchildren, 1):
            # فحص التكرار
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
                parent_id=clima.id,
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
        all_children = db.query(Category).filter(Category.parent_id == clima.id).order_by(Category.sort_order).all()
        
        print(f"\n📊 إجمالي أطفال Clima: {len(all_children)}")
        print("=" * 80)
        print("🌳 الهيكل:")
        print(f"  {parent.id} ({parent.name})")
        print(f"    └── {clima.id} (Clima)")
        for child in all_children:
            print(f"         └── {child.id} ({child.name})")
        print("=" * 80)
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_clima_with_children()
