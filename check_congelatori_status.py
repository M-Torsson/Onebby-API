"""
التحقق من وجود Congelatori verticali في قاعدة البيانات
"""
from app.db.session import get_db
from app.models.category import Category
from sqlalchemy.orm import Session

def check_congelatori_status():
    """التحقق من جميع categories التي تحتوي على كلمة Congelatori"""
    db: Session = next(get_db())
    
    try:
        print("=" * 80)
        print("🔍 البحث عن جميع Categories التي تحتوي على 'Congelatori'")
        print("=" * 80)
        
        # البحث في كل قاعدة البيانات
        all_congelatori = db.query(Category).filter(
            Category.name.like('%Congelatori%')
        ).all()
        
        if not all_congelatori:
            print("❌ لم يتم العثور على أي category يحتوي على 'Congelatori'")
            return
        
        print(f"\n📊 تم العثور على {len(all_congelatori)} categories:")
        print("=" * 80)
        
        for cat in all_congelatori:
            print(f"\n✅ ID: {cat.id}")
            print(f"   الاسم: {cat.name}")
            print(f"   Slug: {cat.slug}")
            print(f"   Parent ID: {cat.parent_id}")
            print(f"   Is Active: {cat.is_active}")
            
            # البحث عن parent
            if cat.parent_id:
                parent = db.query(Category).filter(Category.id == cat.parent_id).first()
                if parent:
                    print(f"   Parent Name: {parent.name}")
            
            # البحث عن أطفال
            children = db.query(Category).filter(Category.parent_id == cat.id).all()
            if children:
                print(f"   الأطفال ({len(children)}):")
                for child in children:
                    print(f"     - {child.name} (ID: {child.id})")
        
        print("\n" + "=" * 80)
        print("📋 ملخص:")
        print("=" * 80)
        
        # التحقق من كل اسم على حدة
        verticali = db.query(Category).filter(Category.name == "Congelatori verticali").first()
        orizzontali = db.query(Category).filter(Category.name == "Congelatori orizzontali").first()
        congelatori = db.query(Category).filter(Category.name == "Congelatori").first()
        
        if verticali:
            print(f"❌ 'Congelatori verticali' موجود (ID: {verticali.id}) - يجب حذفه!")
        else:
            print("✅ 'Congelatori verticali' غير موجود")
        
        if orizzontali:
            print(f"❌ 'Congelatori orizzontali' موجود (ID: {orizzontali.id}) - يجب حذفه!")
        else:
            print("✅ 'Congelatori orizzontali' غير موجود")
        
        if congelatori:
            print(f"✅ 'Congelatori' موجود (ID: {congelatori.id}) - صحيح ✓")
        else:
            print("❌ 'Congelatori' غير موجود - يجب إنشاؤه!")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_congelatori_status()
