# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
التحقق من وجود Divani e poltrone
"""
from app.db.session import get_db
from app.models.category import Category
from sqlalchemy.orm import Session

def check_divani_e_poltrone():
    """Verify  Divani e poltrone"""
    db: Session = next(get_db())
    
    try:
        pass
        
        #   Divani e poltrone
        divani = db.query(Category).filter(Category.name == "Divani e poltrone").first()
        
        if not divani:
            pass
        else:
            pass
            
            #   parent
            if divani.parent_id:
                parent = db.query(Category).filter(Category.id == divani.parent_id).first()
                if parent:
                    pass
                    
                    #   grandparent
                    if parent.parent_id:
                        grandparent = db.query(Category).filter(Category.id == parent.parent_id).first()
                        if grandparent:
                            pass
            
            children = db.query(Category).filter(Category.parent_id == divani.id).all()
            if children:
                pass
                for child in children:
                    pass
            
            if divani.parent_id:
                parent = db.query(Category).filter(Category.id == divani.parent_id).first()
                if parent and parent.parent_id:
                    grandparent = db.query(Category).filter(Category.id == parent.parent_id).first()
                    if grandparent:
                        pass
            
        
    except Exception as e:
        import traceback
    finally:
        db.close()

if __name__ == "__main__":
    check_divani_e_poltrone()
