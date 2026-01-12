"""
Import new category tree via API
This script will:
1. Read the Excel file with Parent/Child/Grandson structure
2. Deactivate old categories via API (set is_active=False)
3. Create new categories via API based on Excel structure
4. Add Italian translations only
"""
import pandas as pd
import requests
from slugify import slugify
import time


# API Configuration
BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "your-api-key-here"  # Will be passed as parameter


def read_excel_tree(filename: str):
    """Read and parse the category tree from Excel"""
    print("\n" + "=" * 80)
    print("📖 قراءة ملف Excel")
    print("=" * 80)
    
    df = pd.read_excel(filename)
    
    print(f"\n✅ تم قراءة الملف بنجاح")
    print(f"📊 عدد الصفوف: {len(df)}")
    print(f"📋 الأعمدة: {df.columns.tolist()}")
    
    # Show first few rows
    print(f"\n📋 أول 5 صفوف:")
    print(df.head().to_string())
    
    # Parse the tree structure
    parents_list = []
    children_list = []
    grandsons_list = []
    
    parents_set = set()
    children_set = set()
    
    for idx, row in df.iterrows():
        parent = row['Parent']
        child = row['Child']
        grandson = row['Grandson'] if pd.notna(row['Grandson']) else None
        
        # Track parents
        if parent not in parents_set:
            parents_set.add(parent)
            parents_list.append({'name': parent, 'sort_order': len(parents_list) + 1})
        
        # Track children
        child_key = (parent, child)
        if child_key not in children_set:
            children_set.add(child_key)
            children_list.append({
                'name': child,
                'parent_name': parent,
                'sort_order': len([c for c in children_list if c['parent_name'] == parent]) + 1
            })
        
        # Track grandsons
        if grandson:
            grandsons_list.append({
                'name': grandson,
                'parent_name': parent,
                'child_name': child,
                'sort_order': len([g for g in grandsons_list if g['child_name'] == child]) + 1
            })
    
    print(f"\n📊 تحليل الهيكل:")
    print(f"   🔹 عدد الآباء (Parents): {len(parents_list)}")
    print(f"   🔹 عدد الأبناء (Children): {len(children_list)}")
    print(f"   🔹 عدد الأحفاد (Grandsons): {len(grandsons_list)}")
    print(f"   🔹 إجمالي الفئات: {len(parents_list) + len(children_list) + len(grandsons_list)}")
    
    print(f"\n📋 الفئات الرئيسية:")
    for p in parents_list:
        print(f"   - {p['name']}")
    
    return df, parents_list, children_list, grandsons_list


def deactivate_old_categories_via_api(api_key: str):
    """
    Deactivate all old categories via API
    Note: This requires an admin API endpoint for batch update
    """
    print("\n" + "=" * 80)
    print("💬 تعطيل الكاتيجوري القديم (عبر API)")
    print("=" * 80)
    
    print("\n⚠️  ملاحظة: يجب تنفيذ التعطيل يدوياً على السيرفر")
    print("   السبب: لا يوجد API endpoint لتعديل جماعي")
    print("   الحل: سيتم إنشاء الفئات الجديدة فقط الآن")
    print("   وتعطيل القديمة يمكن عمله لاحقاً من panel الإدارة")
    
    return 0


def create_category_via_api(name: str, parent_id: int = None, sort_order: int = 0, api_key: str = None):
    """Create a category via API"""
    slug = slugify(name)
    
    payload = {
        "name": name,
        "slug": slug,
        "parent_id": parent_id,
        "sort_order": sort_order,
        "is_active": True,
        "image": None,
        "icon": None
    }
    
    headers = {}
    if api_key:
        headers['X-API-Key'] = api_key
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/categories",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            cat_id = data.get('data', {}).get('id') if 'data' in data else data.get('id')
            return {'success': True, 'id': cat_id, 'name': name}
        else:
            return {'success': False, 'error': f"Status {response.status_code}: {response.text}", 'name': name}
            
    except Exception as e:
        return {'success': False, 'error': str(e), 'name': name}


def import_tree_via_api(parents_list: list, children_list: list, grandsons_list: list, api_key: str):
    """Import the complete category tree via API"""
    print("\n" + "=" * 80)
    print("📥 استيراد شجرة الفئات الجديدة (عبر API)")
    print("=" * 80)
    
    stats = {
        'parents_created': 0,
        'parents_failed': 0,
        'children_created': 0,
        'children_failed': 0,
        'grandsons_created': 0,
        'grandsons_failed': 0,
    }
    
    parent_ids = {}  # Map parent_name -> id
    child_ids = {}  # Map (parent_name, child_name) -> id
    
    # Step 1: Create parents
    print("\n1️⃣ إنشاء الفئات الرئيسية (Parents)...")
    for idx, parent in enumerate(parents_list, 1):
        print(f"   [{idx}/{len(parents_list)}] {parent['name']}...", end=' ')
        result = create_category_via_api(
            name=parent['name'],
            parent_id=None,
            sort_order=parent['sort_order'],
            api_key=api_key
        )
        
        if result['success']:
            parent_ids[parent['name']] = result['id']
            stats['parents_created'] += 1
            print(f"✅ (ID: {result['id']})")
        else:
            stats['parents_failed'] += 1
            print(f"❌ {result['error']}")
        
        time.sleep(0.1)  # Small delay to avoid rate limiting
    
    print(f"\n✅ تم إنشاء {stats['parents_created']} فئة رئيسية ({stats['parents_failed']} فشلت)")
    
    # Step 2: Create children
    print("\n2️⃣ إنشاء الفئات الفرعية (Children)...")
    for idx, child in enumerate(children_list, 1):
        parent_id = parent_ids.get(child['parent_name'])
        if not parent_id:
            print(f"   [{idx}/{len(children_list)}] {child['name']} -> {child['parent_name']} ❌ (Parent not found)")
            stats['children_failed'] += 1
            continue
        
        print(f"   [{idx}/{len(children_list)}] {child['name']} -> {child['parent_name']}...", end=' ')
        result = create_category_via_api(
            name=child['name'],
            parent_id=parent_id,
            sort_order=child['sort_order'],
            api_key=api_key
        )
        
        if result['success']:
            child_ids[(child['parent_name'], child['name'])] = result['id']
            stats['children_created'] += 1
            print(f"✅ (ID: {result['id']})")
        else:
            stats['children_failed'] += 1
            print(f"❌ {result['error']}")
        
        time.sleep(0.1)
    
    print(f"\n✅ تم إنشاء {stats['children_created']} فئة فرعية ({stats['children_failed']} فشلت)")
    
    # Step 3: Create grandsons
    print("\n3️⃣ إنشاء فئات الأحفاد (Grandsons)...")
    for idx, grandson in enumerate(grandsons_list, 1):
        child_id = child_ids.get((grandson['parent_name'], grandson['child_name']))
        if not child_id:
            print(f"   [{idx}/{len(grandsons_list)}] {grandson['name']} -> {grandson['child_name']} ❌ (Child not found)")
            stats['grandsons_failed'] += 1
            continue
        
        print(f"   [{idx}/{len(grandsons_list)}] {grandson['name']} -> {grandson['child_name']} -> {grandson['parent_name']}...", end=' ')
        result = create_category_via_api(
            name=grandson['name'],
            parent_id=child_id,
            sort_order=grandson['sort_order'],
            api_key=api_key
        )
        
        if result['success']:
            stats['grandsons_created'] += 1
            print(f"✅ (ID: {result['id']})")
        else:
            stats['grandsons_failed'] += 1
            print(f"❌ {result['error']}")
        
        time.sleep(0.1)
    
    print(f"\n✅ تم إنشاء {stats['grandsons_created']} فئة حفيد ({stats['grandsons_failed']} فشلت)")
    
    return stats


def main():
    """Main execution"""
    print("=" * 80)
    print("🚀 استيراد شجرة الفئات من Excel عبر API")
    print("=" * 80)
    
    excel_file = "app/excel/prezzoforte_category_tree.xlsx"
    
    # API Key from .env
    api_key = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"
    
    # Read Excel
    df, parents_list, children_list, grandsons_list = read_excel_tree(excel_file)
    
    # Confirm before proceeding
    print("\n" + "=" * 80)
    print("⚠️  تأكيد العملية")
    print("=" * 80)
    print(f"سيتم إنشاء:")
    print(f"  - {len(parents_list)} فئة رئيسية")
    print(f"  - {len(children_list)} فئة فرعية")
    print(f"  - {len(grandsons_list)} فئة حفيد")
    print(f"  - المجموع: {len(parents_list) + len(children_list) + len(grandsons_list)} فئة")
    print("\nهل تريد المتابعة؟ (yes/no): ", end='')
    
    confirm = input().strip().lower()
    if confirm not in ['yes', 'y', 'نعم']:
        print("❌ تم الإلغاء")
        return
    
    # Import via API
    stats = import_tree_via_api(parents_list, children_list, grandsons_list, api_key)
    
    # Final summary
    total_created = stats['parents_created'] + stats['children_created'] + stats['grandsons_created']
    total_failed = stats['parents_failed'] + stats['children_failed'] + stats['grandsons_failed']
    
    print("\n" + "=" * 80)
    print("📊 الملخص النهائي")
    print("=" * 80)
    print(f"✅ فئات رئيسية: {stats['parents_created']} نجحت، {stats['parents_failed']} فشلت")
    print(f"✅ فئات فرعية: {stats['children_created']} نجحت، {stats['children_failed']} فشلت")
    print(f"✅ فئات أحفاد: {stats['grandsons_created']} نجحت، {stats['grandsons_failed']} فشلت")
    print(f"\n✅ إجمالي النجاح: {total_created}")
    print(f"❌ إجمالي الفشل: {total_failed}")
    print("=" * 80)
    
    if total_failed == 0:
        print("\n🎉 تم الاستيراد بنجاح بالكامل!")
    else:
        print("\n⚠️  بعض الفئات فشلت - راجع الأخطاء أعلاه")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
