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
print("🔍 فحص المنتجات في قاعدة البيانات - حالة EAN")
print("=" * 100)

with engine.connect() as conn:
    # Get total products count
    total_products = conn.execute(text("SELECT COUNT(*) FROM products")).fetchone()[0]
    print(f"\n📊 إجمالي المنتجات في قاعدة البيانات: {total_products}")
    
    # Count products WITHOUT EAN (NULL or empty)
    products_without_ean = conn.execute(
        text("SELECT COUNT(*) FROM products WHERE ean IS NULL OR ean = ''")
    ).fetchone()[0]
    
    # Count products WITH EAN
    products_with_ean = total_products - products_without_ean
    
    print(f"\n{'=' * 100}")
    print("📈 إحصائيات EAN:")
    print(f"{'=' * 100}")
    print(f"✅ منتجات لها EAN: {products_with_ean} ({products_with_ean*100/total_products:.1f}%)")
    print(f"❌ منتجات بدون EAN: {products_without_ean} ({products_without_ean*100/total_products:.1f}%)")
    
    # Get some examples of products without EAN
    if products_without_ean > 0:
        print(f"\n{'=' * 100}")
        print(f"📋 أمثلة على المنتجات بدون EAN (أول 20):")
        print(f"{'=' * 100}\n")
        
        products = conn.execute(text("""
            SELECT 
                p.id, 
                p.reference, 
                p.ean,
                pt.title,
                p.price_list,
                p.stock_status
            FROM products p
            LEFT JOIN product_translations pt ON p.id = pt.product_id AND pt.lang = 'it'
            WHERE p.ean IS NULL OR p.ean = ''
            ORDER BY p.id DESC
            LIMIT 20
        """)).fetchall()
        
        for idx, product in enumerate(products, 1):
            product_id = product[0]
            reference = product[1]
            ean = product[2] if product[2] else "NULL"
            title = product[3] if product[3] else "No title"
            price = product[4]
            stock = product[5]
            
            print(f"{idx}. ID={product_id} | Ref={reference} | EAN={ean}")
            print(f"   {title[:80]}...")
            print(f"   Price: {price} EUR | Stock: {stock}\n")
    
    # Get some examples of products WITH EAN
    print(f"\n{'=' * 100}")
    print(f"📋 أمثلة على المنتجات مع EAN (أول 10):")
    print(f"{'=' * 100}\n")
    
    products_with = conn.execute(text("""
        SELECT 
            p.id, 
            p.reference, 
            p.ean,
            pt.title
        FROM products p
        LEFT JOIN product_translations pt ON p.id = pt.product_id AND pt.lang = 'it'
        WHERE p.ean IS NOT NULL AND p.ean != ''
        ORDER BY p.id DESC
        LIMIT 10
    """)).fetchall()
    
    for idx, product in enumerate(products_with, 1):
        product_id = product[0]
        reference = product[1]
        ean = product[2]
        title = product[3] if product[3] else "No title"
        
        print(f"{idx}. ID={product_id} | Ref={reference} | EAN={ean}")
        print(f"   {title[:80]}...\n")
    
    # Check if reference and EAN are the same
    print(f"\n{'=' * 100}")
    print(f"🔄 تحليل إضافي:")
    print(f"{'=' * 100}")
    
    same_ref_ean = conn.execute(
        text("SELECT COUNT(*) FROM products WHERE reference = ean AND ean IS NOT NULL")
    ).fetchone()[0]
    
    different_ref_ean = conn.execute(
        text("SELECT COUNT(*) FROM products WHERE reference != ean AND ean IS NOT NULL")
    ).fetchone()[0]
    
    print(f"🔹 منتجات لها نفس Reference و EAN: {same_ref_ean}")
    print(f"🔹 منتجات لها Reference مختلف عن EAN: {different_ref_ean}")
    
    print(f"\n{'=' * 100}")
    print(f"🏁 النتيجة النهائية:")
    print(f"{'=' * 100}")
    
    if products_without_ean == 0:
        print("✅✅✅ جميع المنتجات لها EAN! ✅✅✅")
    elif products_without_ean < total_products * 0.1:
        print(f"✅ معظم المنتجات لها EAN (أقل من 10% بدون EAN)")
    elif products_without_ean < total_products * 0.5:
        print(f"⚠️ حوالي {products_without_ean*100/total_products:.0f}% من المنتجات بدون EAN")
    else:
        print(f"❌ أكثر من 50% من المنتجات بدون EAN!")
    
    print(f"\n📊 الملخص:")
    print(f"   • إجمالي المنتجات: {total_products}")
    print(f"   • مع EAN: {products_with_ean} ({products_with_ean*100/total_products:.1f}%)")
    print(f"   • بدون EAN: {products_without_ean} ({products_without_ean*100/total_products:.1f}%)")
    print(f"{'=' * 100}\n")
