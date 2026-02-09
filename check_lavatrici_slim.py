# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
التحقق من وجود Lavatrici Slim في قاعدة البيانات
"""
from app.db.session import get_db
from app.models.category import Category
from sqlalchemy.orm import Session

def check_lavatrici_slim():
    """Verify  Lavatrici Slim"""
    db: Session = next(get_db())
    
    try:
        #   Lavatrici Slim
        lavatrici_slim = db.query(Category).filter(Category.name == "Lavatrici Slim").first()
        
        
        if not lavatrici_slim:
            return
        
        
        #   parent
        if lavatrici_slim.parent_id:
            parent = db.query(Category).filter(Category.id == lavatrici_slim.parent_id).first()
            if parent:
                pass
                
                #   grandparent
                if parent.parent_id:
                    grandparent = db.query(Category).filter(Category.id == parent.parent_id).first()
                    if grandparent:
                        pass
        
        
        if lavatrici_slim.parent_id:
            parent = db.query(Category).filter(Category.id == lavatrici_slim.parent_id).first()
            if parent and parent.parent_id:
                grandparent = db.query(Category).filter(Category.id == parent.parent_id).first()
                if grandparent:
                    pass
            elif parent:
                pass
        
        
    except Exception as e:
        import traceback
    finally:
        db.close()

if __name__ == "__main__":
    check_lavatrici_slim()
