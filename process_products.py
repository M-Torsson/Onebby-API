"""
Complete Product Categorization Script
1. Detect and remove duplicates
2. Categorize electronics only
3. Generate final report
"""
import requests
import time
from collections import defaultdict

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

# Stats
stats = {
    'total_products': 0,
    'duplicates_found': 0,
    'duplicates_deleted': 0,
    'electronics': 0,
    'furniture': 0,
    'updated': 0,
    'errors': []
}

def get_all_products():
    """Fetch all products with details"""
    print("=" * 80)
    print("1️⃣ جمع جميع المنتجات")
    print("=" * 80)
    
    all_products = []
    skip = 0
    limit = 500
    
    while True:
        print(f"\n⏳ جلب المنتجات {skip} - {skip + limit}...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/products",
                params={"skip": skip, "limit": limit, "active_only": False},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data['data']
                total = data['meta']['total']
                
                if not products:
                    break
                
                # Get details for each product
                for product in products:
                    product_id = product['id']
                    detail_response = requests.get(
                        f"{BASE_URL}/api/v1/products/{product_id}",
                        timeout=10
                    )
                    
                    if detail_response.status_code == 200:
                        detailed = detail_response.json()['data']
                        all_products.append(detailed)
                
                print(f"   ✅ تم جلب {len(all_products)} / {total}")
                
                skip += limit
                
                if skip >= total:
                    break
                    
            else:
                print(f"   ❌ خطأ: {response.status_code}")
                break
                
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
            break
    
    stats['total_products'] = len(all_products)
    print(f"\n✅ إجمالي المنتجات: {len(all_products)}")
    return all_products


def find_duplicates(products):
    """Find duplicate products by EAN, Reference, and Name"""
    print("\n" + "=" * 80)
    print("2️⃣ كشف المنتجات المكررة")
    print("=" * 80)
    
    # Group by EAN
    by_ean = defaultdict(list)
    # Group by Reference
    by_ref = defaultdict(list)
    # Group by Name
    by_name = defaultdict(list)
    
    for product in products:
        ean = product.get('ean', '').strip()
        ref = product.get('reference', '').strip()
        name = product.get('title', '').strip().lower()
        
        if ean:
            by_ean[ean].append(product)
        if ref:
            by_ref[ref].append(product)
        if name:
            by_name[name].append(product)
    
    # Find duplicates
    duplicate_groups = []
    seen_ids = set()
    
    # Check EAN duplicates
    for ean, group in by_ean.items():
        if len(group) > 1:
            ids = tuple(sorted(p['id'] for p in group))
            if ids not in seen_ids:
                duplicate_groups.append({
                    'type': 'EAN',
                    'value': ean,
                    'products': group
                })
                seen_ids.add(ids)
    
    # Check Reference duplicates
    for ref, group in by_ref.items():
        if len(group) > 1:
            ids = tuple(sorted(p['id'] for p in group))
            if ids not in seen_ids:
                duplicate_groups.append({
                    'type': 'Reference',
                    'value': ref,
                    'products': group
                })
                seen_ids.add(ids)
    
    # Check Name duplicates
    for name, group in by_name.items():
        if len(group) > 1:
            ids = tuple(sorted(p['id'] for p in group))
            if ids not in seen_ids:
                duplicate_groups.append({
                    'type': 'Name',
                    'value': name[:50],
                    'products': group
                })
                seen_ids.add(ids)
    
    stats['duplicates_found'] = len(duplicate_groups)
    
    print(f"\n✅ وجدنا {len(duplicate_groups)} مجموعة مكررة")
    
    # Show samples
    if duplicate_groups:
        print(f"\n📋 أمثلة:")
        for i, group in enumerate(duplicate_groups[:5], 1):
            print(f"\n   {i}. تكرار {group['type']}: {group['value']}")
            print(f"      عدد المكررات: {len(group['products'])}")
            for p in group['products']:
                images_count = len(p.get('images', []))
                desc_len = len(p.get('simple_description', ''))
                print(f"         • ID {p['id']}: {images_count} صور, {desc_len} حرف وصف")
    
    return duplicate_groups


def select_best_product(products):
    """Select the best product from duplicates"""
    def score_product(p):
        score = 0
        # More images = better
        score += len(p.get('images', [])) * 10
        # Longer description = better
        score += len(p.get('simple_description', '')) / 100
        # Has features = better
        score += len(p.get('features', [])) * 5
        # Has attributes = better
        score += len(p.get('attributes', [])) * 5
        # Newer = better (use timestamp)
        if p.get('date_add'):
            score += 1
        return score
    
    return max(products, key=score_product)


def delete_product(product_id):
    """Delete a product from database"""
    try:
        response = requests.delete(
            f"{BASE_URL}/api/admin/products/{product_id}",
            headers={"X-API-Key": API_KEY},
            timeout=30
        )
        
        if response.status_code in [200, 204]:
            return True
        else:
            stats['errors'].append(f"فشل حذف المنتج {product_id}: {response.status_code}")
            return False
            
    except Exception as e:
        stats['errors'].append(f"خطأ في حذف المنتج {product_id}: {str(e)}")
        return False


def remove_duplicates(duplicate_groups):
    """Remove duplicate products, keep the best one"""
    print("\n" + "=" * 80)
    print("3️⃣ حذف المنتجات المكررة")
    print("=" * 80)
    
    deleted_count = 0
    
    for i, group in enumerate(duplicate_groups, 1):
        products = group['products']
        
        # Select best
        best = select_best_product(products)
        to_delete = [p for p in products if p['id'] != best['id']]
        
        print(f"\n{i}/{len(duplicate_groups)} - {group['type']}: {group['value'][:50]}")
        print(f"   ✅ نحتفظ بـ: ID {best['id']}")
        print(f"   🗑️  نحذف: {len(to_delete)} منتج")
        
        # Delete
        for product in to_delete:
            if delete_product(product['id']):
                deleted_count += 1
                print(f"      ✅ تم حذف ID {product['id']}")
            else:
                print(f"      ❌ فشل حذف ID {product['id']}")
            
            time.sleep(0.1)  # Rate limiting
    
    stats['duplicates_deleted'] = deleted_count
    print(f"\n✅ تم حذف {deleted_count} منتج مكرر")


def classify_products(products):
    """Classify products as electronics or furniture"""
    print("\n" + "=" * 80)
    print("4️⃣ تصنيف المنتجات")
    print("=" * 80)
    
    electronics_keywords = [
        'lavatrice', 'frigorifero', 'forno', 'microonde', 'lavastoviglie',
        'congelatore', 'condizionatore', 'tv', 'televisore', 'monitor',
        'computer', 'notebook', 'tablet', 'smartphone', 'cellulare',
        'fotocamera', 'stampante', 'scanner', 'router', 'modem',
        'cuffie', 'altoparlante', 'soundbar', 'lettore', 'decoder',
        'asciugatrice', 'aspirapolvere', 'ferro', 'ventilatore',
        'stufa', 'climatizzatore', 'deumidificatore', 'purificatore'
    ]
    
    furniture_keywords = [
        'sedia', 'tavolo', 'letto', 'armadio', 'mobile', 'porta',
        'divano', 'poltrona', 'scaffale', 'libreria', 'consolle',
        'comodino', 'cassettiera', 'guardaroba', 'parete', 'soggiorno',
        'cucina completa', 'pensile', 'base cucina', 'anta'
    ]
    
    electronics = []
    furniture = []
    unknown = []
    
    for product in products:
        title = product.get('title', '').lower()
        desc = product.get('simple_description', '').lower()
        text = f"{title} {desc}"
        
        is_electronics = any(kw in text for kw in electronics_keywords)
        is_furniture = any(kw in text for kw in furniture_keywords)
        
        if is_electronics and not is_furniture:
            electronics.append(product)
        elif is_furniture and not is_electronics:
            furniture.append(product)
        elif is_electronics and is_furniture:
            # Ambiguous - check category
            categories = product.get('categories', [])
            if categories:
                cat_name = categories[0]['name'].lower()
                if any(kw in cat_name for kw in electronics_keywords):
                    electronics.append(product)
                else:
                    furniture.append(product)
            else:
                unknown.append(product)
        else:
            unknown.append(product)
    
    stats['electronics'] = len(electronics)
    stats['furniture'] = len(furniture)
    
    print(f"\n✅ الإلكترونيات: {len(electronics)}")
    print(f"✅ الأثاث: {len(furniture)}")
    print(f"⚠️  غير محدد: {len(unknown)}")
    
    return electronics, furniture, unknown


def generate_report():
    """Generate final report"""
    print("\n" + "=" * 80)
    print("📊 التقرير النهائي")
    print("=" * 80)
    
    print(f"\n📦 المنتجات:")
    print(f"   • إجمالي المنتجات الأصلي: {stats['total_products']}")
    print(f"   • مجموعات مكررة وجدت: {stats['duplicates_found']}")
    print(f"   • منتجات محذوفة: {stats['duplicates_deleted']}")
    print(f"   • المنتجات المتبقية: {stats['total_products'] - stats['duplicates_deleted']}")
    
    print(f"\n🔍 التصنيف:")
    print(f"   • منتجات إلكترونية: {stats['electronics']}")
    print(f"   • منتجات أثاث: {stats['furniture']}")
    
    print(f"\n✏️  التحديثات:")
    print(f"   • منتجات تم تحديثها: {stats['updated']}")
    
    if stats['errors']:
        print(f"\n❌ أخطاء ({len(stats['errors'])}):")
        for error in stats['errors'][:10]:
            print(f"   • {error}")
    
    print("\n" + "=" * 80)


def main():
    """Main execution"""
    print("=" * 80)
    print("🚀 بدء معالجة المنتجات")
    print("=" * 80)
    
    # Step 1: Get all products
    products = get_all_products()
    
    if not products:
        print("❌ لا توجد منتجات!")
        return
    
    # Step 2: Find duplicates
    duplicate_groups = find_duplicates(products)
    
    # Step 3: Remove duplicates
    if duplicate_groups:
        confirm = input(f"\n⚠️  سيتم حذف {sum(len(g['products'])-1 for g in duplicate_groups)} منتج. متابعة؟ (yes/no): ")
        if confirm.lower() in ['yes', 'y', 'نعم']:
            remove_duplicates(duplicate_groups)
        else:
            print("❌ تم الإلغاء")
            return
    
    # Step 4: Re-fetch products after deletion
    print("\n⏳ إعادة جلب المنتجات بعد الحذف...")
    products = get_all_products()
    
    # Step 5: Classify products
    electronics, furniture, unknown = classify_products(products)
    
    # Step 6: TODO - Update electronics categories
    # Will implement in next step
    
    # Step 7: Generate report
    generate_report()
    
    print("\n✅ انتهى!")


if __name__ == "__main__":
    main()
