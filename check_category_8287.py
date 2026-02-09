# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

# Database connection
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor(cursor_factory=RealDictCursor)


# Check if category exists
cur.execute("""
    SELECT id, name, slug, parent_id, sort_order, is_active, created_at, updated_at
    FROM categories 
    WHERE id = 8287
""")
result = cur.fetchone()

if result:
    pass
    
    if not result['is_active']:
        pass
    
    # Check if it has children
    cur.execute("""
        SELECT COUNT(*) as count
        FROM categories 
        WHERE parent_id = 8287
    """)
    children_count = cur.fetchone()['count']
    
    if children_count > 0:
        cur.execute("""
            SELECT id, name, slug, is_active, parent_id
            FROM categories 
            WHERE parent_id = 8287
            ORDER BY sort_order
        """)
        children = cur.fetchall()
        for child in children:
            status = "✅" if child['is_active'] else "❌"
else:
    cur.execute("""
        SELECT id, name, slug, parent_id, is_active
        FROM categories 
        WHERE id BETWEEN 8280 AND 8290
        ORDER BY id
    """)
    similar = cur.fetchall()
    if similar:
        pass
        for cat in similar:
            status = "✅" if cat['is_active'] else "❌"
    else:
        pass

cur.close()
conn.close()
