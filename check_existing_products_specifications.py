import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

print("=" * 100)
print("🔍 فحص المنتجات الموجودة في قاعدة البيانات والمواصفات الخاصة بها")
print("=" * 100)

with engine.connect() as conn:
    # Get total products count
    total_products = conn.execute(text("SELECT COUNT(*) FROM products")).fetchone()[0]
    print(f"\n📊 إجمالي المنتجات في قاعدة البيانات: {total_products}")
    
    # Get sample products with their details
    print(f"\n{'=' * 100}")
    print("📋 عينة من المنتجات مع تفاصيلها:")
    print(f"{'=' * 100}\n")
    
    # Get 10 random products
    products = conn.execute(text("""
        SELECT 
            id, 
            reference, 
            ean,
            product_type,
            is_active,
            price_list,
            stock_status,
            stock_quantity
        FROM products 
        ORDER BY RANDOM() 
        LIMIT 10
    """)).fetchall()
    
    products_with_specs = 0
    products_with_translations = 0
    products_with_features = 0
    products_with_attributes = 0
    products_with_images = 0
    
    for idx, product in enumerate(products, 1):
        product_id = product[0]
        reference = product[1]
        ean = product[2]
        product_type = product[3]
        
        print(f"{'─' * 100}")
        print(f"🔹 المنتج #{idx}: ID={product_id} | Reference={reference} | EAN={ean}")
        print(f"   النوع: {product_type} | السعر: {product[5]} EUR | المخزون: {product[6]}")
        
        # Check translations
        translations = conn.execute(text("""
            SELECT lang, title, sub_title, simple_description
            FROM product_translations 
            WHERE product_id = :product_id
        """), {"product_id": product_id}).fetchall()
        
        if translations:
            products_with_translations += 1
            print(f"   ✅ الترجمات: {len(translations)} لغة")
            for trans in translations:
                title_preview = trans[1][:50] if trans[1] else "لا يوجد"
                print(f"      - {trans[0]}: {title_preview}...")
        else:
            print(f"   ❌ لا توجد ترجمات")
        
        # Check features (المواصفات - specifications)
        features = conn.execute(text("""
            SELECT 
                pf.code,
                pft.lang,
                pft.name,
                pft.value
            FROM product_features pf
            LEFT JOIN product_feature_translations pft ON pf.id = pft.feature_id
            WHERE pf.product_id = :product_id
            ORDER BY pf.code, pft.lang
        """), {"product_id": product_id}).fetchall()
        
        if features:
            products_with_features += 1
            products_with_specs += 1
            print(f"   ✅ المواصفات (Features): {len(features)} مواصفة")
            # Group by code
            feature_codes = set([f[0] for f in features])
            for code in list(feature_codes)[:3]:  # Show first 3
                feat_items = [f for f in features if f[0] == code]
                print(f"      - {code}:")
                for f in feat_items[:2]:  # Show 2 languages max
                    print(f"         [{f[1]}] {f[2]}: {f[3]}")
            if len(feature_codes) > 3:
                print(f"      ... و {len(feature_codes) - 3} مواصفة أخرى")
        else:
            print(f"   ❌ لا توجد مواصفات (Features)")
        
        # Check attributes (الخصائص)
        attributes = conn.execute(text("""
            SELECT 
                pa.code,
                pat.lang,
                pat.name,
                pat.value
            FROM product_attributes pa
            LEFT JOIN product_attribute_translations pat ON pa.id = pat.attribute_id
            WHERE pa.product_id = :product_id
            ORDER BY pa.code, pat.lang
        """), {"product_id": product_id}).fetchall()
        
        if attributes:
            products_with_attributes += 1
            print(f"   ✅ الخصائص (Attributes): {len(attributes)} خاصية")
            # Group by code
            attr_codes = set([a[0] for a in attributes])
            for code in list(attr_codes)[:3]:  # Show first 3
                attr_items = [a for a in attributes if a[0] == code]
                print(f"      - {code}:")
                for a in attr_items[:2]:  # Show 2 languages max
                    print(f"         [{a[1]}] {a[2]}: {a[3]}")
            if len(attr_codes) > 3:
                print(f"      ... و {len(attr_codes) - 3} خاصية أخرى")
        else:
            print(f"   ❌ لا توجد خصائص (Attributes)")
        
        # Check images
        images = conn.execute(text("""
            SELECT url, position
            FROM product_images 
            WHERE product_id = :product_id
            ORDER BY position
        """), {"product_id": product_id}).fetchall()
        
        if images:
            products_with_images += 1
            print(f"   ✅ الصور: {len(images)} صورة")
        else:
            print(f"   ❌ لا توجد صور")
        
        print()
    
    print(f"\n{'=' * 100}")
    print("📊 ملخص إحصائي للعينة (10 منتجات):")
    print(f"{'=' * 100}")
    print(f"✅ منتجات لها ترجمات: {products_with_translations}/10 ({products_with_translations*10}%)")
    print(f"✅ منتجات لها مواصفات (Features): {products_with_features}/10 ({products_with_features*10}%)")
    print(f"✅ منتجات لها خصائص (Attributes): {products_with_attributes}/10 ({products_with_attributes*10}%)")
    print(f"✅ منتجات لها صور: {products_with_images}/10 ({products_with_images*10}%)")
    
    # Now check overall statistics
    print(f"\n{'=' * 100}")
    print("📊 إحصائيات شاملة لكل المنتجات:")
    print(f"{'=' * 100}")
    
    # Count products with translations
    products_with_trans_total = conn.execute(text("""
        SELECT COUNT(DISTINCT product_id) FROM product_translations
    """)).fetchone()[0]
    print(f"✅ منتجات لها ترجمات: {products_with_trans_total}/{total_products} ({products_with_trans_total*100/total_products:.1f}%)")
    
    # Count products with features
    products_with_feat_total = conn.execute(text("""
        SELECT COUNT(DISTINCT product_id) FROM product_features
    """)).fetchone()[0]
    print(f"✅ منتجات لها مواصفات (Features): {products_with_feat_total}/{total_products} ({products_with_feat_total*100/total_products:.1f}%)")
    
    # Count total features
    total_features = conn.execute(text("""
        SELECT COUNT(*) FROM product_features
    """)).fetchone()[0]
    print(f"   📝 إجمالي المواصفات: {total_features}")
    
    # Count products with attributes
    products_with_attr_total = conn.execute(text("""
        SELECT COUNT(DISTINCT product_id) FROM product_attributes
    """)).fetchone()[0]
    print(f"✅ منتجات لها خصائص (Attributes): {products_with_attr_total}/{total_products} ({products_with_attr_total*100/total_products:.1f}%)")
    
    # Count total attributes
    total_attributes = conn.execute(text("""
        SELECT COUNT(*) FROM product_attributes
    """)).fetchone()[0]
    print(f"   📝 إجمالي الخصائص: {total_attributes}")
    
    # Count products with images
    products_with_img_total = conn.execute(text("""
        SELECT COUNT(DISTINCT product_id) FROM product_images
    """)).fetchone()[0]
    print(f"✅ منتجات لها صور: {products_with_img_total}/{total_products} ({products_with_img_total*100/total_products:.1f}%)")
    
    # Count total images
    total_images = conn.execute(text("""
        SELECT COUNT(*) FROM product_images
    """)).fetchone()[0]
    print(f"   📝 إجمالي الصور: {total_images}")
    
    # Show some common feature codes
    print(f"\n{'=' * 100}")
    print("📋 أمثلة على المواصفات الموجودة (Top 10):")
    print(f"{'=' * 100}")
    
    common_features = conn.execute(text("""
        SELECT 
            pf.code,
            COUNT(DISTINCT pf.product_id) as product_count,
            COUNT(pft.id) as translation_count
        FROM product_features pf
        LEFT JOIN product_feature_translations pft ON pf.id = pft.feature_id
        GROUP BY pf.code
        ORDER BY product_count DESC
        LIMIT 10
    """)).fetchall()
    
    if common_features:
        for feat in common_features:
            # Get sample values
            sample = conn.execute(text("""
                SELECT pft.name, pft.value, pft.lang
                FROM product_features pf
                JOIN product_feature_translations pft ON pf.id = pft.feature_id
                WHERE pf.code = :code
                LIMIT 1
            """), {"code": feat[0]}).fetchone()
            
            if sample:
                print(f"   • {feat[0]}: موجود في {feat[1]} منتج")
                print(f"     مثال: {sample[0]} = {sample[1]} (لغة: {sample[2]})")
    else:
        print("   ❌ لا توجد مواصفات في أي منتج")
    
    print(f"\n{'=' * 100}")
    print("🏁 النتيجة النهائية:")
    print(f"{'=' * 100}")
    
    if products_with_feat_total == 0 and products_with_attr_total == 0:
        print("❌❌❌ المنتجات الحالية لا تحتوي على مواصفات تفصيلية!")
        print("⚠️  قاعدة البيانات تحتوي على المنتجات الأساسية فقط بدون المواصفات المفصلة")
    elif products_with_feat_total < total_products * 0.5:
        print(f"⚠️⚠️⚠️ أقل من 50% من المنتجات لها مواصفات!")
        print(f"📊 فقط {products_with_feat_total} من {total_products} منتج لديه مواصفات")
    else:
        print(f"✅✅✅ معظم المنتجات تحتوي على مواصفات!")
        print(f"📊 {products_with_feat_total} من {total_products} منتج لديه مواصفات")
    
    print(f"{'=' * 100}\n")
