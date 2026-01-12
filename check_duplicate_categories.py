"""
Script to check for duplicate categories in the database
"""
import sys
import os
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.db.session import SessionLocal
from app.models.category import Category, CategoryTranslation


def check_duplicates():
    """Check for duplicate categories"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("🔍 فحص التكرارات في الكاتيجوري")
        print("=" * 80)
        
        # Get all categories
        all_categories = db.query(Category).options(joinedload(Category.translations)).all()
        total = len(all_categories)
        
        print(f"\n📊 إجمالي عدد الفئات: {total}")
        print("-" * 80)
        
        # Check duplicates by name
        print("\n1️⃣ التكرار بناءً على الاسم (name):")
        print("-" * 80)
        names = [cat.name for cat in all_categories if cat.name]
        name_counter = Counter(names)
        duplicates_by_name = {name: count for name, count in name_counter.items() if count > 1}
        
        if duplicates_by_name:
            print(f"⚠️  وجدنا {len(duplicates_by_name)} أسماء مكررة:")
            for name, count in sorted(duplicates_by_name.items(), key=lambda x: x[1], reverse=True):
                print(f"   • '{name}' مكرر {count} مرات")
                # Show IDs
                cats = [cat for cat in all_categories if cat.name == name]
                ids = [cat.id for cat in cats]
                print(f"     IDs: {ids}")
        else:
            print("✅ لا يوجد تكرار في الأسماء")
        
        # Check duplicates by slug
        print("\n2️⃣ التكرار بناءً على الـ slug:")
        print("-" * 80)
        slugs = [cat.slug for cat in all_categories if cat.slug]
        slug_counter = Counter(slugs)
        duplicates_by_slug = {slug: count for slug, count in slug_counter.items() if count > 1}
        
        if duplicates_by_slug:
            print(f"⚠️  وجدنا {len(duplicates_by_slug)} slugs مكررة:")
            for slug, count in sorted(duplicates_by_slug.items(), key=lambda x: x[1], reverse=True):
                print(f"   • '{slug}' مكرر {count} مرات")
                # Show IDs
                cats = [cat for cat in all_categories if cat.slug == slug]
                ids = [cat.id for cat in cats]
                print(f"     IDs: {ids}")
        else:
            print("✅ لا يوجد تكرار في الـ slugs")
        
        # Check duplicates by name + parent_id (same name under same parent)
        print("\n3️⃣ التكرار بناءً على (الاسم + الأب):")
        print("-" * 80)
        name_parent_pairs = [(cat.name, cat.parent_id) for cat in all_categories]
        pair_counter = Counter(name_parent_pairs)
        duplicates_by_pair = {pair: count for pair, count in pair_counter.items() if count > 1}
        
        if duplicates_by_pair:
            print(f"⚠️  وجدنا {len(duplicates_by_pair)} فئات بنفس الاسم تحت نفس الأب:")
            for (name, parent_id), count in sorted(duplicates_by_pair.items(), key=lambda x: x[1], reverse=True):
                parent_text = f"Parent ID: {parent_id}" if parent_id else "بدون أب (فئة رئيسية)"
                print(f"   • '{name}' ({parent_text}) - {count} مرات")
                # Show IDs
                cats = [cat for cat in all_categories if cat.name == name and cat.parent_id == parent_id]
                ids = [cat.id for cat in cats]
                print(f"     IDs: {ids}")
        else:
            print("✅ لا يوجد تكرار في (الاسم + الأب)")
        
        # Check translation duplicates
        print("\n4️⃣ التكرار في الترجمات:")
        print("-" * 80)
        
        # Get all translations
        all_translations = db.query(CategoryTranslation).all()
        print(f"📊 إجمالي عدد الترجمات: {len(all_translations)}")
        
        # Check for duplicate translations (same category_id + lang)
        translation_pairs = [(t.category_id, t.lang) for t in all_translations]
        translation_counter = Counter(translation_pairs)
        duplicate_translations = {pair: count for pair, count in translation_counter.items() if count > 1}
        
        if duplicate_translations:
            print(f"⚠️  وجدنا {len(duplicate_translations)} ترجمات مكررة:")
            for (cat_id, lang), count in sorted(duplicate_translations.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   • Category ID {cat_id}, Language '{lang}' - {count} مرات")
                # Show translation names
                trans = [t for t in all_translations if t.category_id == cat_id and t.lang == lang]
                names = [t.name for t in trans]
                print(f"     Names: {names}")
        else:
            print("✅ لا يوجد تكرار في الترجمات")
        
        # Check for translations with duplicate names in same language
        print("\n5️⃣ التكرار في أسماء الترجمات (نفس اللغة):")
        print("-" * 80)
        for lang in ['it', 'en', 'fr', 'de', 'ar']:
            lang_translations = [t for t in all_translations if t.lang == lang]
            trans_names = [t.name for t in lang_translations if t.name]
            trans_name_counter = Counter(trans_names)
            duplicates = {name: count for name, count in trans_name_counter.items() if count > 1}
            
            if duplicates:
                print(f"\n   🌐 اللغة '{lang}' - {len(duplicates)} أسماء مكررة:")
                for name, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"      • '{name}' مكرر {count} مرات")
            else:
                print(f"   ✅ اللغة '{lang}' - لا يوجد تكرار")
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 الملخص:")
        print("=" * 80)
        print(f"✓ إجمالي الفئات: {total}")
        print(f"✓ أسماء مكررة: {len(duplicates_by_name)}")
        print(f"✓ Slugs مكررة: {len(duplicates_by_slug)}")
        print(f"✓ فئات مكررة (اسم + أب): {len(duplicates_by_pair)}")
        print(f"✓ ترجمات مكررة: {len(duplicate_translations)}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_duplicates()
