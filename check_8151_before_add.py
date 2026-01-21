"""
فحص category 8151 قبل إضافة الأسماء الجديدة
"""
from app.db.session import get_db
from app.models.category import Category
from sqlalchemy.orm import Session

def check_category_8151():
    """فحص category 8151 والتحقق من الأسماء المطلوب إضافتها"""
    db: Session = next(get_db())
    
    try:
        # فحص category الرئيسي
        parent_category = db.query(Category).filter(Category.id == 8151).first()
        
        print("=" * 80)
        print("فحص Category 8151")
        print("=" * 80)
        
        if not parent_category:
            print("❌ ERROR: Category 8151 غير موجود في قاعدة البيانات!")
            return
        
        print(f"✅ تم العثور على Category الرئيسي:")
        print(f"   ID: {parent_category.id}")
        print(f"   الاسم: {parent_category.name}")
        print(f"   Parent ID: {parent_category.parent_id}")
        print(f"   Is Active: {parent_category.is_active}")
        
        # الأسماء المطلوب إضافتها
        new_names = [
            "Lavatrici incasso",
            "Lavasciuga libera installazione",
            "Lavasciuga incasso",
            "Lavastoviglie libera installazione"
        ]
        
        print("\n" + "=" * 80)
        print("الأسماء المطلوب إضافتها:")
        print("=" * 80)
        for name in new_names:
            print(f"  - {name}")
        
        # فحص الأطفال الحاليين
        current_children = db.query(Category).filter(Category.parent_id == 8151).all()
        
        print("\n" + "=" * 80)
        print(f"الأطفال الحاليين لـ Category 8151 ({len(current_children)}):")
        print("=" * 80)
        
        if current_children:
            for child in current_children:
                print(f"  ID: {child.id} - {child.name}")
        else:
            print("  لا يوجد أطفال حالياً")
        
        # فحص التكرار
        print("\n" + "=" * 80)
        print("فحص التكرار:")
        print("=" * 80)
        
        conflicts_found = False
        current_names = [child.name.lower() for child in current_children]
        
        for new_name in new_names:
            if new_name.lower() in current_names:
                print(f"❌ تعارض: '{new_name}' موجود مسبقاً!")
                conflicts_found = True
            else:
                # فحص في كل قاعدة البيانات
                existing = db.query(Category).filter(Category.name == new_name).first()
                if existing:
                    print(f"⚠️  تحذير: '{new_name}' موجود في قاعدة البيانات بـ ID: {existing.id} (Parent: {existing.parent_id})")
                    conflicts_found = True
                else:
                    print(f"✅ '{new_name}' - لا يوجد تعارض")
        
        print("\n" + "=" * 80)
        if conflicts_found:
            print("❌ تم العثور على تعارض! لا يمكن الإضافة بدون حل التعارض")
        else:
            print("✅ لا يوجد تعارض - يمكن الإضافة بأمان")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_category_8151()
