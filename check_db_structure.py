# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
Check database structure and product-category relationship
"""
from sqlalchemy import create_engine, inspect, text
from app.core.config import settings


# Connect to database
engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

# Check tables
tables = inspector.get_table_names()
relevant_tables = [t for t in tables if 'product' in t or 'category' in t]
for table in relevant_tables:
    pass

# Check product_categories table
if 'product_categories' in tables:
    columns = inspector.get_columns('product_categories')
    for col in columns:
        pass
    
    # Check if there's any data
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) as count FROM product_categories"))
        count = result.fetchone()[0]
        
        if count > 0:
            result = conn.execute(text("SELECT * FROM product_categories LIMIT 5"))
            for row in result:
                pass
else:
    pass

# Check products table for category reference
columns = inspector.get_columns('products')
category_cols = [col for col in columns if 'category' in col['name'].lower()]
if category_cols:
    pass
    for col in category_cols:
        pass
else:
    pass
