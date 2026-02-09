# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
التحقق من وجود Congelatori verticali في قاعدة البيانات
"""
from app.db.session import get_db
from app.models.category import Category
from sqlalchemy.orm import Session

def check_congelatori_status():
    """Verify  categories     Congelatori"""
    db: Session = next(get_db())
    
    try:
        pass
        
        all_congelatori = db.query(Category).filter(
            Category.name.like('%Congelatori%')
        ).all()
        
        if not all_congelatori:
            return
        
        
        for cat in all_congelatori:
            pass
            
            #   parent
            if cat.parent_id:
                parent = db.query(Category).filter(Category.id == cat.parent_id).first()
                if parent:
                    pass
            
            children = db.query(Category).filter(Category.parent_id == cat.id).all()
            if children:
                pass
                for child in children:
                    pass
        
        
        verticali = db.query(Category).filter(Category.name == "Congelatori verticali").first()
        orizzontali = db.query(Category).filter(Category.name == "Congelatori orizzontali").first()
        congelatori = db.query(Category).filter(Category.name == "Congelatori").first()
        
        if verticali:
            pass
        else:
            pass
        
        if orizzontali:
            pass
        else:
            pass
        
        if congelatori:
            pass
        else:
            pass
        
        
    except Exception as e:
        import traceback
    finally:
        db.close()

if __name__ == "__main__":
    check_congelatori_status()
