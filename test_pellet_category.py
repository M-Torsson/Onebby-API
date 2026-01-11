"""
اختبار سريع لإنشاء category "Pellet" والتحقق من ظهوره في API
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.crud import category as crud_category
from app.schemas.category import CategoryCreate

def test_create_and_verify():
    """إنشاء category Pellet والتحقق من ظهوره"""
    db = SessionLocal()
    
    try:
        print("=" * 50)
        print("اختبار إنشاء Category: Pellet")
        print("=" * 50)
        
        # 1. البحث عن category موجود باسم Pellet
        existing = db.query(crud_category.Category).filter(
            crud_category.Category.name == "Pellet"
        ).first()
        
        if existing:
            print(f"✓ Category موجود بالفعل: ID={existing.id}, Active={existing.is_active}")
            category_id = existing.id
        else:
            # 2. إنشاء category جديد
            print("\nإنشاء category جديد...")
            category_data = CategoryCreate(
                name="Pellet",
                slug="pellet",
                is_active=True,
                sort_order=1,
                parent_id=None
            )
            
            new_category = crud_category.create_category(db, category_data)
            category_id = new_category.id
            print(f"✓ تم إنشاء Category: ID={new_category.id}")
        
        # 3. التحقق من الترجمات
        print("\n" + "=" * 50)
        print("التحقق من الترجمات")
        print("=" * 50)
        
        translations = db.query(crud_category.CategoryTranslation).filter(
            crud_category.CategoryTranslation.category_id == category_id
        ).all()
        
        print(f"عدد الترجمات: {len(translations)}")
        for t in translations:
            print(f"  - {t.lang}: {t.name} (slug: {t.slug})")
        
        # 4. التحقق من ظهوره في get_all_categories
        print("\n" + "=" * 50)
        print("التحقق من ظهوره في get_all_categories")
        print("=" * 50)
        
        all_categories = crud_category.get_all_categories(
            db, 
            lang="it", 
            active_only=True
        )
        
        pellet_found = any(c.id == category_id for c in all_categories)
        print(f"عدد Categories: {len(all_categories)}")
        print(f"Pellet موجود؟ {'✓ نعم' if pellet_found else '✗ لا'}")
        
        # 5. التحقق من ظهوره في get_main_categories
        print("\n" + "=" * 50)
        print("التحقق من ظهوره في get_main_categories")
        print("=" * 50)
        
        main_categories = crud_category.get_main_categories(db, lang="it")
        pellet_in_main = any(c.id == category_id for c in main_categories)
        
        print(f"عدد Main Categories: {len(main_categories)}")
        print(f"Pellet موجود في Main؟ {'✓ نعم' if pellet_in_main else '✗ لا'}")
        
        # 6. عرض تفاصيل الـ category
        print("\n" + "=" * 50)
        print("تفاصيل Pellet Category")
        print("=" * 50)
        
        pellet = crud_category.get_category(db, category_id)
        if pellet:
            print(f"ID: {pellet.id}")
            print(f"Name: {pellet.name}")
            print(f"Slug: {pellet.slug}")
            print(f"Active: {pellet.is_active}")
            print(f"Parent ID: {pellet.parent_id}")
            print(f"Sort Order: {pellet.sort_order}")
            print(f"Has Children: {pellet.has_children}")
        
        print("\n" + "=" * 50)
        print("✓ الاختبار اكتمل بنجاح!")
        print("=" * 50)
        print("\nالآن يمكنك اختبار API من Postman:")
        print(f"GET http://localhost:8000/v1/categories?lang=it")
        print(f"GET http://localhost:8000/v1/categories?lang=it&parent_only=true")
        
    except Exception as e:
        print(f"\n✗ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    test_create_and_verify()
