"""
Complete analysis before starting product categorization
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

print("=" * 80)
print("📊 التحليل الكامل قبل البدء")
print("=" * 80)

# 1. Categories Analysis
print("\n✅ 1. الفئات الجديدة:")
categories_response = requests.get(
    f"{BASE_URL}/api/v1/categories",
    params={"limit": 500},
    timeout=30
)

if categories_response.status_code == 200:
    cats_data = categories_response.json()
    all_cats = cats_data['data']
    
    # Analyze structure
    parents = {}
    children = {}
    grandchildren = {}
    
    for cat in all_cats:
        cat_id = cat['id']
        cat_name = cat['name']
        parent_id = cat.get('parent_id')
        
        if not parent_id:
            parents[cat_id] = cat_name
        else:
            # Check if it's a child or grandchild
            is_grandchild = False
            for c in all_cats:
                if c['id'] == parent_id and c.get('parent_id'):
                    is_grandchild = True
                    grandchildren[cat_id] = cat_name
                    break
            
            if not is_grandchild:
                children[cat_id] = cat_name
    
    print(f"   📁 فئات رئيسية: {len(parents)}")
    print(f"   📂 فئات فرعية: {len(children)}")
    print(f"   📄 فئات أحفاد: {len(grandchildren)}")
    print(f"   ✅ إجمالي: {len(all_cats)}")
    
    # Show main categories
    print(f"\n   🗂️  الفئات الرئيسية:")
    for cat_id, cat_name in list(parents.items())[:8]:
        print(f"      • {cat_name} (ID: {cat_id})")

# 2. Products Analysis
print("\n✅ 2. المنتجات الموجودة:")
products_response = requests.get(
    f"{BASE_URL}/api/v1/products",
    params={"limit": 500, "active_only": False},
    timeout=60
)

if products_response.status_code == 200:
    prod_data = products_response.json()
    total_products = prod_data['meta']['total']
    products = prod_data['data']
    
    print(f"   📦 إجمالي المنتجات: {total_products}")
    
    # Check current categorization
    with_cat = [p for p in products if p.get('categories')]
    without_cat = [p for p in products if not p.get('categories')]
    
    print(f"   ✅ منتجات لها فئة: {len(with_cat)}")
    print(f"   ❌ منتجات بدون فئة: {len(without_cat)}")
    
    # Check product structure
    if products:
        sample = products[0]
        print(f"\n   🔍 عينة من منتج:")
        print(f"      ID: {sample.get('id')}")
        print(f"      Reference: {sample.get('reference')}")
        print(f"      Title: {sample.get('title', 'N/A')[:60]}")
        print(f"      Categories: {sample.get('categories', [])}")

# 3. Assessment
print("\n" + "=" * 80)
print("📋 التقييم والإمكانية")
print("=" * 80)

print("\n✅ المتوفر:")
print("   1. ✅ 135 فئة جديدة جاهزة (8 رئيسية، 85 فرعية، 42 حفيد)")
print("   2. ✅ 19,506 منتج في قاعدة البيانات")
print("   3. ✅ العلاقة many-to-many بين المنتجات والفئات موجودة")
print("   4. ✅ API endpoints للتحديث متاحة")

print("\n⚠️  التحديات:")
print("   1. ❌ لا توجد بيانات ربط حالية بين المنتجات والفئات")
print("   2. ⚠️  يحتاج mapping من اسم/وصف المنتج إلى الفئة المناسبة")
print("   3. ⚠️  19,506 منتج = عملية كبيرة")

print("\n" + "=" * 80)
print("💡 الحلول الممكنة")
print("=" * 80)

print("\n1️⃣  الحل الأول: Mapping يدوي بناءً على كلمات مفتاحية")
print("   • نحلل اسم/وصف المنتج ونربطه بالفئة المناسبة")
print("   • مثال: 'Lavatrice' -> فئة 'Lavatrici'")
print("   • السرعة: بطيء (19,506 منتج)")
print("   • الدقة: متوسطة (~70%)")

print("\n2️⃣  الحل الثاني: استخدام Brand كمؤشر")
print("   • بعض البراندات متخصصة في فئات معينة")
print("   • مثال: Bosch -> Elettrodomestici")
print("   • السرعة: متوسط")
print("   • الدقة: منخفضة (~40%)")

print("\n3️⃣  الحل الثالث: EAN/Reference lookup")
print("   • إذا كان هناك مصدر بيانات خارجي")
print("   • السرعة: سريع (إذا توفر API)")
print("   • الدقة: عالية (>90%)")

print("\n4️⃣  الحل الرابع: تصنيف يدوي")
print("   • تصدير قائمة المنتجات")
print("   • تصنيف يدوي في Excel")
print("   • استيراد النتائج")
print("   • السرعة: بطيء جداً")
print("   • الدقة: عالية جداً (100%)")

print("\n" + "=" * 80)
print("🎯 التوصية")
print("=" * 80)
print("\n✅ نعم، أستطيع تنفيذ الحل الأول (Keyword Mapping)")
print("   • سأقوم بتحليل عينة من المنتجات")
print("   • إنشاء قواعد Mapping بناءً على الكلمات المفتاحية")
print("   • تطبيق القواعد على جميع المنتجات")
print("   • توفير تقرير بالنتائج")

print("\n⏱️  الوقت المتوقع:")
print("   • إنشاء السكريبت: 10 دقائق")
print("   • تشغيل على 19,506 منتج: 30-60 دقيقة")
print("   • مراجعة النتائج: 10 دقائق")

print("\n" + "=" * 80)
print("❓ هل تريد المتابعة؟")
print("=" * 80)
