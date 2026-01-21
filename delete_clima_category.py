"""
حذف category Clima مع جميع أطفاله وأحفاده
"""
from app.db.session import get_db
from app.models.category import Category
from sqlalchemy.orm import Session

def delete_clima_category():
    """حذف Clima مع جميع الأطفال والأحفاد"""
    db: Session = next(get_db())
    
    try:
        # البحث عن Clima
        clima = db.query(Category).filter(Category.name == "Clima").first()
        
        if not clima:
            print("=" * 80)
            print("❌ لم يتم العثور على category باسم 'Clima'")
            print("=" * 80)
            return
        
        print("=" * 80)
        print(f"✅ تم العثور على: {clima.name} (ID: {clima.id})")
        print(f"   Parent ID: {clima.parent_id}")
        print("=" * 80)
        
        # جمع جميع الأطفال والأحفاد
        def get_all_descendants(parent_id):
            """جمع جميع الأطفال والأحفاد بشكل تكراري"""
            descendants = []
            children = db.query(Category).filter(Category.parent_id == parent_id).all()
            
            for child in children:
                descendants.append(child)
                # جمع أحفاد هذا الطفل
                descendants.extend(get_all_descendants(child.id))
            
            return descendants
        
        # جمع جميع الأطفال والأحفاد
        all_descendants = get_all_descendants(clima.id)
        
        print(f"\n📊 إحصائيات:")
        print(f"   الأطفال والأحفاد: {len(all_descendants)}")
        
        # عرض الهيكل
        print("\n🌳 الهيكل الكامل الذي سيتم حذفه:")
        print("=" * 80)
        print(f"❌ {clima.id} - {clima.name} (الرئيسي)")
        
        # عرض الأطفال المباشرين
        direct_children = db.query(Category).filter(Category.parent_id == clima.id).all()
        for child in direct_children:
            print(f"   ❌ {child.id} - {child.name}")
            
            # عرض أحفاد كل طفل
            grandchildren = db.query(Category).filter(Category.parent_id == child.id).all()
            for grandchild in grandchildren:
                print(f"      ❌ {grandchild.id} - {grandchild.name}")
        
        # تأكيد الحذف
        print("\n" + "=" * 80)
        print(f"⚠️  سيتم حذف {len(all_descendants) + 1} categories (1 رئيسي + {len(all_descendants)} أطفال/أحفاد)")
        print("=" * 80)
        
        # حذف الأحفاد أولاً (من الأسفل للأعلى)
        print("\n🗑️  جاري الحذف...")
        
        deleted_count = 0
        
        # حذف من الأسفل للأعلى
        for desc in reversed(all_descendants):
            print(f"   🗑️  حذف: {desc.name} (ID: {desc.id})")
            db.delete(desc)
            deleted_count += 1
        
        # حذف الـ category الرئيسي
        print(f"   🗑️  حذف: {clima.name} (ID: {clima.id}) - الرئيسي")
        db.delete(clima)
        deleted_count += 1
        
        db.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ تم حذف {deleted_count} categories بنجاح!")
        print("=" * 80)
        print(f"   ❌ Clima (ID: {clima.id})")
        print(f"   ❌ جميع الأطفال والأحفاد ({len(all_descendants)})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    delete_clima_category()
