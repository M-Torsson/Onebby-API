"""
تغيير اسم category من Congelatori verticali إلى Congelatori
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

def update_congelatori_name():
    """تغيير اسم Congelatori verticali إلى Congelatori"""
    db: Session = next(get_db())
    
    try:
        # البحث عن category باسم Congelatori verticali
        category = db.query(Category).filter(
            Category.parent_id == 8151,
            Category.name == "Congelatori verticali"
        ).first()
        
        if not category:
            print("❌ لم يتم العثور على category باسم 'Congelatori verticali' تحت parent 8151")
            return
        
        print("=" * 80)
        print("تم العثور على Category:")
        print(f"  ID: {category.id}")
        print(f"  الاسم القديم: {category.name}")
        print(f"  Slug القديم: {category.slug}")
        print(f"  Parent ID: {category.parent_id}")
        print("=" * 80)
        
        # الاسم الجديد
        new_name = "Congelatori"
        new_slug = create_slug(new_name)
        
        # التحقق من عدم وجود اسم أو slug مكرر
        existing_name = db.query(Category).filter(
            Category.name == new_name,
            Category.id != category.id
        ).first()
        
        if existing_name:
            print(f"⚠️  تحذير: اسم '{new_name}' موجود مسبقاً (ID: {existing_name.id})")
            print(f"   لا يمكن التحديث بسبب التعارض!")
            return
        
        existing_slug = db.query(Category).filter(
            Category.slug == new_slug,
            Category.id != category.id
        ).first()
        
        if existing_slug:
            print(f"⚠️  تحذير: Slug '{new_slug}' موجود مسبقاً (ID: {existing_slug.id})")
            new_slug = f"{new_slug}-{category.id}"
            print(f"   سيتم استخدام: {new_slug}")
        
        # تحديث الاسم والـ slug
        category.name = new_name
        category.slug = new_slug
        
        db.commit()
        
        print("\n✅ تم التحديث بنجاح!")
        print(f"  ID: {category.id}")
        print(f"  الاسم الجديد: {category.name}")
        print(f"  Slug الجديد: {category.slug}")
        print("=" * 80)
        
    except Exception as e:
        db.rollback()
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    update_congelatori_name()
