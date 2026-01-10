"""
اختبار مباشر لفحص مشكلة Categories
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.category import Category, CategoryTranslation
from sqlalchemy import text

def diagnose_categories():
    """تشخيص شامل لمشكلة Categories"""
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("🔍 تشخيص مشكلة Categories")
        print("=" * 70)
        
        # 1. عدد Categories في قاعدة البيانات
        total_categories = db.query(Category).count()
        active_categories = db.query(Category).filter(Category.is_active == True).count()
        
        print(f"\n📊 إحصائيات:")
        print(f"   - إجمالي Categories: {total_categories}")
        print(f"   - Categories النشطة: {active_categories}")
        print(f"   - Categories غير النشطة: {total_categories - active_categories}")
        
        # 2. عرض جميع Categories
        print(f"\n📋 جميع الـ Categories:")
        print(f"{'ID':<5} {'Name':<30} {'Slug':<30} {'Active':<8} {'Parent':<8}")
        print("-" * 90)
        
        all_cats = db.query(Category).order_by(Category.id).all()
        for cat in all_cats:
            print(f"{cat.id:<5} {cat.name:<30} {cat.slug:<30} {str(cat.is_active):<8} {str(cat.parent_id):<8}")
        
        # 3. البحث عن Pellet/Pellets
        print(f"\n🔍 البحث عن Pellet/Pellets:")
        pellet_cats = db.query(Category).filter(
            Category.name.ilike('%pellet%')
        ).all()
        
        if pellet_cats:
            for cat in pellet_cats:
                print(f"\n✅ وجدنا: {cat.name}")
                print(f"   ID: {cat.id}")
                print(f"   Slug: {cat.slug}")
                print(f"   Active: {cat.is_active}")
                print(f"   Parent ID: {cat.parent_id}")
                print(f"   Created: {cat.created_at}")
                
                # تحقق من الترجمات
                translations = db.query(CategoryTranslation).filter(
                    CategoryTranslation.category_id == cat.id
                ).all()
                
                print(f"   Translations: {len(translations)}")
                for trans in translations:
                    print(f"      - {trans.lang}: {trans.name}")
                
                # تحقق من has_children
                children = db.query(Category).filter(Category.parent_id == cat.id).count()
                print(f"   Children count: {children}")
        else:
            print("❌ لم نجد أي category يحتوي على 'pellet'")
        
        # 4. اختبار الـ query الفعلي المستخدم في API
        print(f"\n🧪 اختبار Query الفعلي (مثل API):")
        from app.crud import category as crud_category
        
        # Test get_all_categories
        api_cats = crud_category.get_all_categories(
            db, 
            lang="en", 
            active_only=True,
            skip=0,
            limit=100
        )
        
        print(f"   Categories من get_all_categories: {len(api_cats)}")
        for cat in api_cats:
            if 'pellet' in cat.name.lower():
                print(f"   ✅ Pellet موجود: {cat.name} (ID: {cat.id})")
        
        # 5. تحقق من المشاكل المحتملة
        print(f"\n⚠️  فحص المشاكل المحتملة:")
        
        # Categories بدون slug
        no_slug = db.query(Category).filter(Category.slug == None).count()
        if no_slug > 0:
            print(f"   ❌ {no_slug} categories بدون slug!")
        else:
            print(f"   ✅ جميع categories لديها slug")
        
        # Categories بدون ترجمات
        cats_without_trans = []
        for cat in all_cats:
            trans_count = db.query(CategoryTranslation).filter(
                CategoryTranslation.category_id == cat.id
            ).count()
            if trans_count == 0:
                cats_without_trans.append(cat.name)
        
        if cats_without_trans:
            print(f"   ❌ Categories بدون ترجمات: {', '.join(cats_without_trans)}")
        else:
            print(f"   ✅ جميع categories لديها ترجمات")
        
        # 6. اختبار SQL مباشر
        print(f"\n🔧 اختبار SQL المباشر:")
        result = db.execute(text("""
            SELECT c.id, c.name, c.slug, c.is_active, c.parent_id,
                   COUNT(ct.id) as translation_count
            FROM categories c
            LEFT JOIN category_translations ct ON c.id = ct.category_id
            WHERE c.name ILIKE '%pellet%'
            GROUP BY c.id, c.name, c.slug, c.is_active, c.parent_id
        """))
        
        rows = result.fetchall()
        if rows:
            for row in rows:
                print(f"   ID: {row[0]}, Name: {row[1]}, Active: {row[3]}, Translations: {row[5]}")
        else:
            print(f"   ❌ SQL لم يجد Pellet!")
        
        print("\n" + "=" * 70)
        print("✅ انتهى التشخيص")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    diagnose_categories()
