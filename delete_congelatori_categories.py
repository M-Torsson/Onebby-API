"""
حذف Congelatori verticali و Congelatori orizzontali
"""
from app.db.session import get_db
from app.models.category import Category
from sqlalchemy.orm import Session

def delete_congelatori_categories():
    """حذف categories Congelatori verticali و Congelatori orizzontali"""
    db: Session = next(get_db())
    
    try:
        print("=" * 80)
        print("🔍 البحث عن Categories المطلوب حذفها")
        print("=" * 80)
        
        # البحث عن الـ categories
        to_delete = []
        
        # Congelatori verticali
        cat1 = db.query(Category).filter(
            Category.parent_id == 8151,
            Category.name == "Congelatori verticali"
        ).first()
        
        if cat1:
            to_delete.append(cat1)
            print(f"✅ تم العثور على: {cat1.name} (ID: {cat1.id})")
        else:
            print("ℹ️  'Congelatori verticali' غير موجود (ربما تم تغييره مسبقاً)")
        
        # Congelatori orizzontali
        cat2 = db.query(Category).filter(
            Category.parent_id == 8151,
            Category.name == "Congelatori orizzontali"
        ).first()
        
        if cat2:
            to_delete.append(cat2)
            print(f"✅ تم العثور على: {cat2.name} (ID: {cat2.id})")
        else:
            print("ℹ️  'Congelatori orizzontali' غير موجود")
        
        # التحقق من Congelatori
        congelatori = db.query(Category).filter(
            Category.parent_id == 8151,
            Category.name == "Congelatori"
        ).first()
        
        if congelatori:
            print(f"\n✅ 'Congelatori' موجود وسيبقى (ID: {congelatori.id})")
        else:
            print("\n⚠️  تحذير: 'Congelatori' غير موجود!")
        
        if not to_delete:
            print("\n" + "=" * 80)
            print("ℹ️  لا توجد categories للحذف")
            print("=" * 80)
            return
        
        # فحص إذا كانت هناك أطفال أو منتجات
        print("\n" + "=" * 80)
        print("🔍 فحص الأطفال والمنتجات")
        print("=" * 80)
        
        for cat in to_delete:
            children = db.query(Category).filter(Category.parent_id == cat.id).all()
            if children:
                print(f"⚠️  '{cat.name}' لديه {len(children)} أطفال:")
                for child in children:
                    print(f"     - {child.name} (ID: {child.id})")
        
        # الحذف
        print("\n" + "=" * 80)
        print("🗑️  الحذف")
        print("=" * 80)
        
        deleted_ids = []
        for cat in to_delete:
            print(f"🗑️  حذف: {cat.name} (ID: {cat.id})")
            deleted_ids.append((cat.id, cat.name))
            db.delete(cat)
        
        db.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ تم حذف {len(deleted_ids)} categories بنجاح!")
        print("=" * 80)
        
        for cat_id, cat_name in deleted_ids:
            print(f"   ❌ {cat_name} (ID: {cat_id})")
        
        # عرض Categories المتبقية تحت 8151
        remaining = db.query(Category).filter(Category.parent_id == 8151).order_by(Category.name).all()
        print("\n" + "=" * 80)
        print(f"📊 Categories المتبقية تحت Grandi elettrodomestici ({len(remaining)}):")
        print("=" * 80)
        for cat in remaining:
            print(f"   ✅ {cat.name} (ID: {cat.id})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    delete_congelatori_categories()
