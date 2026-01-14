"""
Complete product categorization plan
"""
import requests
import json

BASE_URL = "https://onebby-api.onrender.com"

print("=" * 80)
print("📋 خطة تصنيف المنتجات الكاملة")
print("=" * 80)

print("\n🔍 الطريقة:")
print("   1. جمع ALL الفئات القديمة من المنتجات (عينة كبيرة)")
print("   2. إنشاء Mapping يدوي من الفئات القديمة → الجديدة")
print("   3. قراءة كل منتج وتحديث فئاته")

# Step 1: Get sample of products with details
print("\n" + "=" * 80)
print("1️⃣ جمع عينة من المنتجات مع تفاصيلها")
print("=" * 80)

old_categories_found = {}

# Get first 100 products (one by one to see their categories)
print("\n⏳ جمع أول 100 منتج...")
response = requests.get(
    f"{BASE_URL}/api/v1/products",
    params={"skip": 0, "limit": 100, "active_only": False},
    timeout=60
)

if response.status_code == 200:
    product_list = response.json()['data']
    print(f"✅ تم جلب {len(product_list)} منتج من القائمة")
    
    # Now get details for each
    print(f"\n⏳ جلب تفاصيل كل منتج...")
    checked = 0
    for product in product_list[:20]:  # Check first 20 in detail
        product_id = product['id']
        detail_response = requests.get(
            f"{BASE_URL}/api/v1/products/{product_id}",
            timeout=10
        )
        
        if detail_response.status_code == 200:
            detailed_product = detail_response.json()['data']
            categories = detailed_product.get('categories', [])
            
            if categories:
                for cat in categories:
                    cat_id = cat['id']
                    cat_name = cat['name']
                    if cat_id not in old_categories_found:
                        old_categories_found[cat_id] = cat_name
                        print(f"   📁 وجدنا: {cat_name} (ID: {cat_id})")
        
        checked += 1
        if checked % 5 == 0:
            print(f"      ... {checked}/20")

print(f"\n✅ إجمالي الفئات القديمة الفريدة: {len(old_categories_found)}")

# Show all found
if old_categories_found:
    print(f"\n📋 قائمة الفئات القديمة:")
    for cat_id, cat_name in old_categories_found.items():
        print(f"   • {cat_name} (ID: {cat_id})")

# Get new categories
print("\n" + "=" * 80)
print("2️⃣ الفئات الجديدة المتاحة")
print("=" * 80)

response = requests.get(
    f"{BASE_URL}/api/v1/categories",
    params={"limit": 500},
    timeout=30
)

new_categories = []
if response.status_code == 200:
    new_categories = response.json()['data']
    print(f"✅ {len(new_categories)} فئة جديدة")
    
    # Group by parent
    parents = [c for c in new_categories if not c.get('parent_id')]
    print(f"\n📁 الفئات الرئيسية:")
    for parent in parents:
        print(f"   • {parent['name']}")

print("\n" + "=" * 80)
print("3️⃣ التوصية")
print("=" * 80)

print(f"\n✅ نعم، أستطيع المتابعة!")
print(f"\nالطريقة:")
print(f"   1. سأقوم بجمع ALL الفئات القديمة من عينة أكبر (1000+ منتج)")
print(f"   2. إنشاء mapping يدوي/تلقائي من القديمة → الجديدة")
print(f"   3. لكل منتج:")
print(f"      • قراءة الفئة القديمة")
print(f"      • إيجاد المطابقة في الجديدة")  
print(f"      • تحديث المنتج بالفئة الجديدة عبر API")

print(f"\n⚠️  ملاحظة: سأحتاج endpoint لتحديث categories المنتج")
print(f"   هل يوجد PUT /api/admin/products/{{id}}/categories ؟")

print("\n" + "=" * 80)
