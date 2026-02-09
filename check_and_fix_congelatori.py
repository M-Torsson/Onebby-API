# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
Check Congelatori status
"""
from app.db.session import get_db
from app.models.category import Category
from sqlalchemy.orm import Session

def check_and_fix_congelatori():
    """Check Congelatori verticali and Congelatori"""
    db: Session = next(get_db())
    
    try:
        pass
        
        # البحث عن Congelatori verticali
        verticali = db.query(Category).filter(Category.name == "Congelatori verticali").first()
        
        # البحث عن Congelatori
        congelatori = db.query(Category).filter(Category.name == "Congelatori").first()
        
        if verticali:
            pass
            
            if congelatori:
                pass
                
                db.delete(verticali)
                db.commit()
                
            else:
                pass
                
                verticali.name = "Congelatori"
                verticali.slug = "congelatori"
                
                db.commit()
                
        else:
            pass
            
            if congelatori:
                pass
            else:
                pass
        
        
    except Exception as e:
        db.rollback()
        import traceback
    finally:
        db.close()

if __name__ == "__main__":
    check_and_fix_congelatori()
