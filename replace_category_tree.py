"""
Complete Category Tree Replacement Script
1. Deactivate all old categories
2. Import new tree from Excel
"""
import requests
import pandas as pd
from slugify import slugify
import time

# API Configuration
BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

def deactivate_all_old_categories():
    """Step 1: Deactivate all old categories via API"""
    print("=" * 80)
    print("1️⃣ تعطيل جميع الفئات القديمة")
    print("=" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/categories/deactivate-all",
            headers={"X-API-Key": API_KEY},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ {data['message']}")
            print(f"📊 عدد الفئات المعطلة: {data['deactivated_count']}")
            return True
        else:
            print(f"\n❌ فشل: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        return False


def read_excel_tree():
    """Read the category tree from Excel"""
    print("\n" + "=" * 80)
    print("2️⃣ قراءة ملف Excel")
    print("=" * 80)
    
    df = pd.read_excel("app/excel/prezzoforte_category_tree.xlsx")
    
    print(f"\n✅ تم قراءة {len(df)} صف من الملف")
    
    # Parse structure
    parents_list = []
    children_list = []
    grandsons_list = []
    
    parents_set = set()
    children_set = set()
    
    for idx, row in df.iterrows():
        parent = row['Parent']
        child = row['Child']
        grandson = row['Grandson'] if pd.notna(row['Grandson']) else None
        
        if parent not in parents_set:
            parents_set.add(parent)
            parents_list.append({'name': parent, 'sort_order': len(parents_list) + 1})
        
        child_key = (parent, child)
        if child_key not in children_set:
            children_set.add(child_key)
            children_list.append({
                'name': child,
                'parent_name': parent,
                'sort_order': len([c for c in children_list if c['parent_name'] == parent]) + 1
            })
        
        if grandson:
            grandsons_list.append({
                'name': grandson,
                'parent_name': parent,
                'child_name': child,
                'sort_order': len([g for g in grandsons_list if g['child_name'] == child]) + 1
            })
    
    print(f"   🔹 {len(parents_list)} فئة رئيسية")
    print(f"   🔹 {len(children_list)} فئة فرعية")
    print(f"   🔹 {len(grandsons_list)} فئة حفيد")
    print(f"   🔹 المجموع: {len(parents_list) + len(children_list) + len(grandsons_list)}")
    
    return parents_list, children_list, grandsons_list


def create_category_via_api(name, parent_id=None, sort_order=0):
    """Create a single category via API"""
    slug = slugify(name)
    
    payload = {
        "name": name,
        "slug": slug,
        "parent_id": parent_id,
        "sort_order": sort_order,
        "is_active": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/categories",
            json=payload,
            headers={"X-API-Key": API_KEY},
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            cat_id = data.get('data', {}).get('id') if 'data' in data else data.get('id')
            return {'success': True, 'id': cat_id}
        else:
            return {'success': False, 'error': response.text}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}


def import_new_tree(parents_list, children_list, grandsons_list):
    """Step 3: Import new category tree"""
    print("\n" + "=" * 80)
    print("3️⃣ استيراد الشجرة الجديدة")
    print("=" * 80)
    
    stats = {'created': 0, 'failed': 0}
    parent_ids = {}
    child_ids = {}
    
    # Create parents
    print("\n▶️ إنشاء الفئات الرئيسية...")
    for idx, parent in enumerate(parents_list, 1):
        result = create_category_via_api(parent['name'], None, parent['sort_order'])
        if result['success']:
            parent_ids[parent['name']] = result['id']
            stats['created'] += 1
            print(f"   ✅ [{idx}/{len(parents_list)}] {parent['name']}")
        else:
            stats['failed'] += 1
            print(f"   ❌ [{idx}/{len(parents_list)}] {parent['name']}: {result['error']}")
        time.sleep(0.1)
    
    # Create children
    print("\n▶️ إنشاء الفئات الفرعية...")
    for idx, child in enumerate(children_list, 1):
        parent_id = parent_ids.get(child['parent_name'])
        if parent_id:
            result = create_category_via_api(child['name'], parent_id, child['sort_order'])
            if result['success']:
                child_ids[(child['parent_name'], child['name'])] = result['id']
                stats['created'] += 1
                print(f"   ✅ [{idx}/{len(children_list)}] {child['name']}")
            else:
                stats['failed'] += 1
                print(f"   ❌ [{idx}/{len(children_list)}] {child['name']}: {result['error']}")
        else:
            stats['failed'] += 1
            print(f"   ❌ [{idx}/{len(children_list)}] {child['name']}: Parent not found")
        time.sleep(0.1)
    
    # Create grandsons
    print("\n▶️ إنشاء فئات الأحفاد...")
    for idx, grandson in enumerate(grandsons_list, 1):
        child_id = child_ids.get((grandson['parent_name'], grandson['child_name']))
        if child_id:
            result = create_category_via_api(grandson['name'], child_id, grandson['sort_order'])
            if result['success']:
                stats['created'] += 1
                print(f"   ✅ [{idx}/{len(grandsons_list)}] {grandson['name']}")
            else:
                stats['failed'] += 1
                print(f"   ❌ [{idx}/{len(grandsons_list)}] {grandson['name']}: {result['error']}")
        else:
            stats['failed'] += 1
            print(f"   ❌ [{idx}/{len(grandsons_list)}] {grandson['name']}: Parent not found")
        time.sleep(0.1)
    
    return stats


def main():
    """Main execution"""
    print("=" * 80)
    print("🚀 استبدال شجرة الفئات بالكامل")
    print("=" * 80)
    print("\nهذا السكريبت سوف:")
    print("  1️⃣ يعطل جميع الفئات القديمة (لا يحذفها)")
    print("  2️⃣ يقرأ الشجرة الجديدة من Excel")
    print("  3️⃣ ينشئ الفئات الجديدة")
    print("\n" + "=" * 80)
    
    # Step 1: Deactivate old
    if not deactivate_all_old_categories():
        print("\n❌ فشل تعطيل الفئات القديمة. توقف.")
        return
    
    # Step 2: Read Excel
    parents_list, children_list, grandsons_list = read_excel_tree()
    
    # Confirm
    print("\n" + "=" * 80)
    print("⚠️  تأكيد")
    print("=" * 80)
    total = len(parents_list) + len(children_list) + len(grandsons_list)
    print(f"سيتم إنشاء {total} فئة جديدة")
    print("\nهل تريد المتابعة؟ (yes/no): ", end='')
    
    confirm = input().strip().lower()
    if confirm not in ['yes', 'y', 'نعم']:
        print("❌ تم الإلغاء")
        return
    
    # Step 3: Import new tree
    stats = import_new_tree(parents_list, children_list, grandsons_list)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 الملخص النهائي")
    print("=" * 80)
    print(f"✅ تم إنشاء: {stats['created']} فئة")
    print(f"❌ فشل: {stats['failed']} فئة")
    print("=" * 80)
    
    if stats['failed'] == 0:
        print("\n🎉 تم الاستبدال بنجاح!")
        print("✅ الآن لديك فقط الشجرة الجديدة في الداشبورد")
    else:
        print("\n⚠️  بعض الفئات فشلت - راجع الأخطاء أعلاه")


if __name__ == "__main__":
    main()
