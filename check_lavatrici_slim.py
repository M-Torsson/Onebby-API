"""
التحقق من وجود Lavatrici Slim في قاعدة البيانات
"""
from app.db.session import get_db
from app.models.category import Category
from sqlalchemy.orm import Session

def check_lavatrici_slim():
    """التحقق من وجود Lavatrici Slim"""
    db: Session = next(get_db())
    
    try:
        # البحث عن Lavatrici Slim
        lavatrici_slim = db.query(Category).filter(Category.name == "Lavatrici Slim").first()
        
        print("=" * 80)
        print("🔍 البحث عن: Lavatrici Slim")
        print("=" * 80)
        
        if not lavatrici_slim:
            print("❌ لم يتم العثور على 'Lavatrici Slim' في قاعدة البيانات!")
            return
        
        print("✅ تم العثور على Lavatrici Slim:")
        print(f"  ID: {lavatrici_slim.id}")
        print(f"  الاسم: {lavatrici_slim.name}")
        print(f"  Slug: {lavatrici_slim.slug}")
        print(f"  Parent ID: {lavatrici_slim.parent_id}")
        print(f"  Is Active: {lavatrici_slim.is_active}")
        print(f"  Sort Order: {lavatrici_slim.sort_order}")
        
        # البحث عن parent
        if lavatrici_slim.parent_id:
            parent = db.query(Category).filter(Category.id == lavatrici_slim.parent_id).first()
            if parent:
                print(f"\n👤 Parent (الأب):")
                print(f"  ID: {parent.id}")
                print(f"  الاسم: {parent.name}")
                print(f"  Parent ID: {parent.parent_id}")
                
                # البحث عن grandparent
                if parent.parent_id:
                    grandparent = db.query(Category).filter(Category.id == parent.parent_id).first()
                    if grandparent:
                        print(f"\n👴 Grandparent (الجد):")
                        print(f"  ID: {grandparent.id}")
                        print(f"  الاسم: {grandparent.name}")
        
        print("\n" + "=" * 80)
        print("📊 الهيكل الكامل:")
        print("=" * 80)
        
        if lavatrici_slim.parent_id:
            parent = db.query(Category).filter(Category.id == lavatrici_slim.parent_id).first()
            if parent and parent.parent_id:
                grandparent = db.query(Category).filter(Category.id == parent.parent_id).first()
                if grandparent:
                    print(f"  {grandparent.id} ({grandparent.name})")
                    print(f"    └── {parent.id} ({parent.name})")
                    print(f"         └── {lavatrici_slim.id} ({lavatrici_slim.name}) ✅")
            elif parent:
                print(f"  {parent.id} ({parent.name})")
                print(f"    └── {lavatrici_slim.id} ({lavatrici_slim.name}) ✅")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_lavatrici_slim()
