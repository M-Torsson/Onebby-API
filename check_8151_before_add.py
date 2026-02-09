# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""Check category 8151 before adding new names"""
from app.db.session import get_db
from app.models.category import Category
from sqlalchemy.orm import Session

def check_category_8151():
    """Check category 8151 and verify names to be added"""
    db: Session = next(get_db())
    
    try:
        # Check main category
        parent_category = db.query(Category).filter(Category.id == 8151).first()
        
        if not parent_category:
            return
        
        # Names to add
        new_names = [
            "Lavatrici incasso",
            "Lavasciuga libera installazione",
            "Lavasciuga incasso",
            "Lavastoviglie libera installazione"
        ]
        
        # Check current children
        current_children = db.query(Category).filter(Category.parent_id == 8151).all()
        
        # Check for duplicates
        
        conflicts_found = False
        current_names = [child.name.lower() for child in current_children]
        
        for new_name in new_names:
            if new_name.lower() in current_names:
                conflicts_found = True
            else:
                # Check in entire database
                existing = db.query(Category).filter(Category.name == new_name).first()
                if existing:
                    conflicts_found = True
        
    except Exception as e:
        pass
    finally:
        db.close()

if __name__ == "__main__":
    check_category_8151()
