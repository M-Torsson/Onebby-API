"""
Check database structure and product-category relationship
"""
from sqlalchemy import create_engine, inspect, text
from app.core.config import settings

print("=" * 80)
print("🔍 فحص قاعدة البيانات")
print("=" * 80)

# Connect to database
engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

# Check tables
print("\n1️⃣ الجداول الموجودة:")
tables = inspector.get_table_names()
relevant_tables = [t for t in tables if 'product' in t or 'category' in t]
for table in relevant_tables:
    print(f"   ✅ {table}")

# Check product_categories table
if 'product_categories' in tables:
    print("\n2️⃣ جدول product_categories:")
    columns = inspector.get_columns('product_categories')
    print(f"   الأعمدة:")
    for col in columns:
        print(f"      - {col['name']} ({col['type']})")
    
    # Check if there's any data
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) as count FROM product_categories"))
        count = result.fetchone()[0]
        print(f"\n   📊 عدد الربط الموجود: {count}")
        
        if count > 0:
            result = conn.execute(text("SELECT * FROM product_categories LIMIT 5"))
            print(f"\n   🔍 أمثلة:")
            for row in result:
                print(f"      Product: {row[0]}, Category: {row[1]}")
else:
    print("\n❌ جدول product_categories غير موجود!")

# Check products table for category reference
print("\n3️⃣ جدول products:")
columns = inspector.get_columns('products')
category_cols = [col for col in columns if 'category' in col['name'].lower()]
if category_cols:
    print(f"   أعمدة الفئات:")
    for col in category_cols:
        print(f"      - {col['name']} ({col['type']})")
else:
    print("   ✅ لا يوجد عمود category_id مباشر (علاقة many-to-many عبر product_categories)")

print("\n" + "=" * 80)
print("✅ انتهى الفحص")
print("=" * 80)
