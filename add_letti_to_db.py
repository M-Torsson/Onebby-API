"""
Add Letti categories directly to database
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

print("=" * 80)
print("🗄️  ADDING LETTI STRUCTURE TO DATABASE")
print("=" * 80)

with engine.connect() as conn:
    # Step 1: Insert parent category
    print("\n📌 Step 1: Creating parent category Letti (ID: 500)")
    print("-" * 80)
    
    try:
        insert_parent = text("""
            INSERT INTO categories (id, name, slug, parent_id, sort_order, is_active, created_at, updated_at)
            VALUES (:id, :name, :slug, :parent_id, :sort_order, :is_active, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                slug = EXCLUDED.slug,
                parent_id = EXCLUDED.parent_id,
                sort_order = EXCLUDED.sort_order,
                is_active = EXCLUDED.is_active,
                updated_at = NOW()
        """)
        
        conn.execute(insert_parent, {
            'id': 500,
            'name': 'Letti',
            'slug': 'letti',
            'parent_id': None,
            'sort_order': 1,
            'is_active': True
        })
        conn.commit()
        print("✅ Created/Updated: Letti (ID: 500)")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    
    # Step 2: Insert child categories
    print("\n📌 Step 2: Creating child categories")
    print("-" * 80)
    
    children = [
        (501, 'Letti in Ferro Battuto', 'letti-in-ferro-battuto', 1),
        (502, 'Letti in Legno', 'letti-in-legno', 2),
    ]
    
    for cat_id, name, slug, sort_order in children:
        try:
            conn.execute(insert_parent, {
                'id': cat_id,
                'name': name,
                'slug': slug,
                'parent_id': 500,
                'sort_order': sort_order,
                'is_active': True
            })
            conn.commit()
            print(f"✅ Created/Updated: {name} (ID: {cat_id})")
        except Exception as e:
            print(f"❌ Error creating {name}: {e}")
            conn.rollback()
    
    # Step 3: Update existing categories
    print("\n📌 Step 3: Updating existing categories to be children of Letti")
    print("-" * 80)
    
    updates = [
        (746, 3),  # Letti imbottiti
        (743, 4),  # Letti a castello
        (808, 5),  # Letti a scomparsa
        (827, 6),  # Testiera per letti
    ]
    
    update_query = text("""
        UPDATE categories
        SET parent_id = :parent_id, sort_order = :sort_order, updated_at = NOW()
        WHERE id = :id
    """)
    
    for cat_id, sort_order in updates:
        try:
            result = conn.execute(update_query, {
                'id': cat_id,
                'parent_id': 500,
                'sort_order': sort_order
            })
            conn.commit()
            
            # Get category name
            name_query = text("SELECT name FROM categories WHERE id = :id")
            name_result = conn.execute(name_query, {'id': cat_id})
            name_row = name_result.fetchone()
            name = name_row[0] if name_row else f"Category {cat_id}"
            
            print(f"✅ Updated: {name} (ID: {cat_id}) -> Parent: 500, Order: {sort_order}")
        except Exception as e:
            print(f"❌ Error updating {cat_id}: {e}")
            conn.rollback()
    
    # Verify structure
    print("\n📌 Verification: Checking structure")
    print("-" * 80)
    
    verify_query = text("""
        SELECT id, name, parent_id, sort_order
        FROM categories
        WHERE id = 500 OR parent_id = 500
        ORDER BY parent_id NULLS FIRST, sort_order
    """)
    
    result = conn.execute(verify_query)
    rows = result.fetchall()
    
    print("\n└─ Letti (500)")
    for row in rows:
        if row[0] != 500:
            print(f"   ├─ {row[3]}. {row[1]} ({row[0]})")

print("\n" + "=" * 80)
print("✅ LETTI STRUCTURE COMPLETE!")
print("=" * 80)
