# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
Check categories with children from database directly
"""
from app.db.session import SessionLocal
from app.models.category import Category
from sqlalchemy import select

db = SessionLocal()

failed_ids = [8159, 8167, 8179, 8180, 8192, 8193, 8195, 8197, 8198]


all_children_ids = []

for cat_id in failed_ids:
    category = db.query(Category).filter(Category.id == cat_id).first()
    
    if category:
        pass
        
        # Get children
        children = db.query(Category).filter(Category.parent_id == cat_id).all()
        
        if children:
            pass
            for child in children:
                all_children_ids.append(child.id)
                
                # Check if child also has children (grandchildren)
                grandchildren = db.query(Category).filter(Category.parent_id == child.id).all()
                if grandchildren:
                    pass
                    for grandchild in grandchildren:
                        all_children_ids.append(grandchild.id)
        else:
            pass
    else:
        pass

db.close()


# Save to file
if all_children_ids:
    with open('all_children_to_delete.txt', 'w') as f:
        pass
        for child_id in sorted(set(all_children_ids)):
            f.write(f"{child_id}\n")
