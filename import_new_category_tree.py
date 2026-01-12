"""
Import new category tree from Excel file
This script will:
1. Read the Excel file with Parent/Child/Grandson structure
2. Comment out (deactivate) old categories by setting is_active=False
3. Create new categories based on the Excel structure
4. Add Italian translations only
"""
import sys
import os
import pandas as pd
from slugify import slugify

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.category import Category, CategoryTranslation


def comment_out_old_categories(db: Session):
    """
    Comment out (deactivate) all old categories instead of deleting them
    """
    print("\n" + "=" * 80)
    print("💬 تعليق على الكاتيجوري القديم (تعطيل بدون حذف)")
    print("=" * 80)
    
    # Get all active categories
    old_categories = db.query(Category).filter(Category.is_active == True).all()
    count = len(old_categories)
    
    if count == 0:
        print("✅ لا يوجد فئات نشطة للتعطيل")
        return 0
    
    print(f"\n📊 وجدنا {count} فئة نشطة سيتم تعطيلها...")
    
    # Deactivate all old categories
    for cat in old_categories:
        cat.is_active = False
        # Add prefix to name to mark as old
        if not cat.name.startswith("[OLD] "):
            cat.name = f"[OLD] {cat.name}"
        if cat.slug and not cat.slug.startswith("old-"):
            cat.slug = f"old-{cat.slug}"
    
    db.commit()
    
    print(f"✅ تم تعطيل {count} فئة قديمة (تم إضافة [OLD] للأسماء)")
    print("   ⚠️  لم يتم حذف أي بيانات - فقط تعطيل")
    
    return count


def read_excel_tree(filename: str):
    """Read and parse the category tree from Excel"""
    print("\n" + "=" * 80)
    print("📖 قراءة ملف Excel")
    print("=" * 80)
    
    df = pd.read_excel(filename)
    
    print(f"\n✅ تم قراءة الملف بنجاح")
    print(f"📊 عدد الصفوف: {len(df)}")
    print(f"📋 الأعمدة: {df.columns.tolist()}")
    
    # Parse the tree structure
    parents = {}  # {name: None} - will be filled with Category objects
    children = {}  # {(parent_name, child_name): None}
    grandsons = {}  # {(parent_name, child_name, grandson_name): None}
    
    for idx, row in df.iterrows():
        parent = row['Parent']
        child = row['Child']
        grandson = row['Grandson'] if pd.notna(row['Grandson']) else None
        
        # Track parent
        if parent not in parents:
            parents[parent] = None
        
        # Track child
        child_key = (parent, child)
        if child_key not in children:
            children[child_key] = None
        
        # Track grandson
        if grandson:
            grandson_key = (parent, child, grandson)
            if grandson_key not in grandsons:
                grandsons[grandson_key] = None
    
    print(f"\n📊 تحليل الهيكل:")
    print(f"   🔹 عدد الآباء (Parents): {len(parents)}")
    print(f"   🔹 عدد الأبناء (Children): {len(children)}")
    print(f"   🔹 عدد الأحفاد (Grandsons): {len(grandsons)}")
    print(f"   🔹 إجمالي الفئات: {len(parents) + len(children) + len(grandsons)}")
    
    return df, parents, children, grandsons


def create_category(db: Session, name: str, parent_id: int = None, sort_order: int = 0):
    """Create a single category with Italian translation"""
    slug = slugify(name)
    
    # Check if category already exists with same name and parent
    existing = db.query(Category).filter(
        Category.name == name,
        Category.parent_id == parent_id,
        Category.is_active == True
    ).first()
    
    if existing:
        print(f"   ⚠️  الفئة '{name}' موجودة مسبقاً (ID: {existing.id})")
        return existing
    
    # Create category
    category = Category(
        name=name,
        slug=slug,
        parent_id=parent_id,
        sort_order=sort_order,
        is_active=True,
        image=None,
        icon=None
    )
    
    db.add(category)
    db.flush()  # Get the ID
    
    # Create Italian translation
    translation = CategoryTranslation(
        category_id=category.id,
        lang='it',
        name=name,
        slug=slug,
        description=None
    )
    
    db.add(translation)
    
    return category


def import_category_tree(db: Session, df: pd.DataFrame, parents: dict, children: dict, grandsons: dict):
    """Import the complete category tree"""
    print("\n" + "=" * 80)
    print("📥 استيراد شجرة الفئات الجديدة")
    print("=" * 80)
    
    stats = {
        'parents_created': 0,
        'children_created': 0,
        'grandsons_created': 0,
        'total_created': 0
    }
    
    # Step 1: Create all parent categories
    print("\n1️⃣ إنشاء الفئات الرئيسية (Parents)...")
    parent_names = sorted(parents.keys())
    for idx, parent_name in enumerate(parent_names, 1):
        cat = create_category(db, parent_name, parent_id=None, sort_order=idx)
        parents[parent_name] = cat
        stats['parents_created'] += 1
        print(f"   ✅ [{idx}/{len(parent_names)}] {parent_name} (ID: {cat.id})")
    
    db.commit()
    print(f"\n✅ تم إنشاء {stats['parents_created']} فئة رئيسية")
    
    # Step 2: Create all child categories
    print("\n2️⃣ إنشاء الفئات الفرعية (Children)...")
    # Get unique children with their parent
    children_dict = {}
    for idx, row in df.iterrows():
        parent_name = row['Parent']
        child_name = row['Child']
        if (parent_name, child_name) not in children_dict:
            children_dict[(parent_name, child_name)] = True
    
    child_count = 0
    for (parent_name, child_name) in sorted(children_dict.keys()):
        parent_cat = parents[parent_name]
        child_count += 1
        cat = create_category(db, child_name, parent_id=parent_cat.id, sort_order=child_count)
        children[(parent_name, child_name)] = cat
        stats['children_created'] += 1
        print(f"   ✅ [{child_count}/{len(children_dict)}] {child_name} -> {parent_name} (ID: {cat.id})")
    
    db.commit()
    print(f"\n✅ تم إنشاء {stats['children_created']} فئة فرعية")
    
    # Step 3: Create all grandson categories
    print("\n3️⃣ إنشاء فئات الأحفاد (Grandsons)...")
    grandson_count = 0
    for idx, row in df.iterrows():
        parent_name = row['Parent']
        child_name = row['Child']
        grandson_name = row['Grandson'] if pd.notna(row['Grandson']) else None
        
        if grandson_name:
            child_cat = children[(parent_name, child_name)]
            grandson_count += 1
            cat = create_category(db, grandson_name, parent_id=child_cat.id, sort_order=grandson_count)
            grandsons[(parent_name, child_name, grandson_name)] = cat
            stats['grandsons_created'] += 1
            print(f"   ✅ [{grandson_count}/{len(grandsons)}] {grandson_name} -> {child_name} -> {parent_name} (ID: {cat.id})")
    
    db.commit()
    print(f"\n✅ تم إنشاء {stats['grandsons_created']} فئة حفيد")
    
    stats['total_created'] = stats['parents_created'] + stats['children_created'] + stats['grandsons_created']
    
    return stats


def main():
    """Main execution"""
    print("=" * 80)
    print("🚀 استيراد شجرة الفئات من ملف Excel")
    print("=" * 80)
    
    excel_file = "app/excel/prezzoforte_category_tree.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ الملف غير موجود: {excel_file}")
        return
    
    db = SessionLocal()
    
    try:
        # Step 1: Comment out old categories
        old_count = comment_out_old_categories(db)
        
        # Step 2: Read Excel file
        df, parents, children, grandsons = read_excel_tree(excel_file)
        
        # Step 3: Import new tree
        stats = import_category_tree(db, df, parents, children, grandsons)
        
        # Final summary
        print("\n" + "=" * 80)
        print("📊 الملخص النهائي")
        print("=" * 80)
        print(f"✅ الفئات القديمة المعطلة: {old_count}")
        print(f"✅ فئات رئيسية جديدة (Parents): {stats['parents_created']}")
        print(f"✅ فئات فرعية جديدة (Children): {stats['children_created']}")
        print(f"✅ فئات أحفاد جديدة (Grandsons): {stats['grandsons_created']}")
        print(f"✅ إجمالي الفئات الجديدة: {stats['total_created']}")
        print("=" * 80)
        print("\n✅ تم الاستيراد بنجاح!")
        print("⚠️  ملاحظة: الفئات القديمة لم يتم حذفها - فقط تعطيلها")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
