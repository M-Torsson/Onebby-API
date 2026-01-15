import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

# Database connection
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor(cursor_factory=RealDictCursor)

print("=" * 80)
print("Checking Category 8287")
print("=" * 80)

# Check if category exists
cur.execute("""
    SELECT id, name, slug, parent_id, sort_order, is_active, created_at, updated_at
    FROM categories 
    WHERE id = 8287
""")
result = cur.fetchone()

if result:
    print("\n✅ Category Found:")
    print(f"ID: {result['id']}")
    print(f"Name: {result['name']}")
    print(f"Slug: {result['slug']}")
    print(f"Parent ID: {result['parent_id']}")
    print(f"Sort Order: {result['sort_order']}")
    print(f"Is Active: {result['is_active']}")
    print(f"Created: {result['created_at']}")
    print(f"Updated: {result['updated_at']}")
    
    if not result['is_active']:
        print("\n⚠️  WARNING: Category is NOT ACTIVE (is_active = false)")
        print("\nTo activate it, run this SQL:")
        print(f"UPDATE categories SET is_active = true, updated_at = NOW() WHERE id = 8287;")
    
    # Check if it has children
    cur.execute("""
        SELECT COUNT(*) as count
        FROM categories 
        WHERE parent_id = 8287
    """)
    children_count = cur.fetchone()['count']
    print(f"\nChildren Count: {children_count}")
    
    if children_count > 0:
        cur.execute("""
            SELECT id, name, slug, is_active, parent_id
            FROM categories 
            WHERE parent_id = 8287
            ORDER BY sort_order
        """)
        children = cur.fetchall()
        print("\nChildren:")
        for child in children:
            status = "✅" if child['is_active'] else "❌"
            print(f"  {status} ID: {child['id']}, Name: {child['name']}, Active: {child['is_active']}")
else:
    print("\n❌ Category 8287 NOT FOUND in database")
    print("\nSearching for similar IDs...")
    cur.execute("""
        SELECT id, name, slug, parent_id, is_active
        FROM categories 
        WHERE id BETWEEN 8280 AND 8290
        ORDER BY id
    """)
    similar = cur.fetchall()
    if similar:
        print("\nCategories with similar IDs:")
        for cat in similar:
            status = "✅" if cat['is_active'] else "❌"
            print(f"  {status} ID: {cat['id']}, Name: {cat['name']}, Parent: {cat['parent_id']}")
    else:
        print("No categories found in range 8280-8290")

cur.close()
conn.close()
print("\n" + "=" * 80)
