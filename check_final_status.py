"""
Get final status and detailed report
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"

print("=" * 80)
print("📊 التقرير النهائي")
print("=" * 80)

# Get product count
response = requests.get(
    f"{BASE_URL}/api/v1/products",
    params={"limit": 500, "active_only": False},
    timeout=60
)

if response.status_code == 200:
    data = response.json()
    total = data['meta']['total']
    products = data['data']
    
    print(f"\n📦 المنتجات:")
    print(f"   • إجمالي المنتجات: {total}")
    
    # Sample check for categories
    print(f"\n🔍 فحص عينة (أول {len(products)} منتج):")
    
    # Get detailed info for first 20
    electronics_sample = 0
    furniture_sample = 0
    with_category = 0
    without_category = 0
    
    electronics_keywords = [
        'lavatrice', 'frigorifero', 'forno', 'microonde', 'lavastoviglie',
        'tv', 'computer', 'notebook', 'tablet', 'smartphone'
    ]
    
    furniture_keywords = [
        'sedia', 'tavolo', 'letto', 'armadio', 'mobile', 'divano'
    ]
    
    for product in products[:100]:
        # Get full details
        detail_response = requests.get(
            f"{BASE_URL}/api/v1/products/{product['id']}",
            timeout=10
        )
        
        if detail_response.status_code == 200:
            detailed = detail_response.json()['data']
            
            if detailed.get('categories'):
                with_category += 1
            else:
                without_category += 1
            
            title = detailed.get('title', '').lower()
            
            is_electronics = any(kw in title for kw in electronics_keywords)
            is_furniture = any(kw in title for kw in furniture_keywords)
            
            if is_electronics:
                electronics_sample += 1
            if is_furniture:
                furniture_sample += 1
    
    print(f"   • منتجات لها فئة: {with_category}")
    print(f"   • منتجات بدون فئة: {without_category}")
    print(f"   • إلكترونيات (تقريباً): {electronics_sample}")
    print(f"   • أثاث (تقريباً): {furniture_sample}")
    
    print(f"\n📊 التقدير الكامل:")
    total_with_cat = int((with_category / 100) * total)
    total_electronics = int((electronics_sample / 100) * total)
    total_furniture = int((furniture_sample / 100) * total)
    
    print(f"   • منتجات لها فئة: ~{total_with_cat}")
    print(f"   • إلكترونيات: ~{total_electronics}")
    print(f"   • أثاث: ~{total_furniture}")

else:
    print(f"❌ خطأ: {response.status_code}")

print("\n" + "=" * 80)
