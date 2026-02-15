# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
Change product_type from configurable to simple for sample products
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.product import Product, ProductType


def main():
    pass
    
    db = SessionLocal()
    try:
        # Product IDs
        product_ids = [35965, 35966, 35967, 35968]
        
        for product_id in product_ids:
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                old_type = product.product_type.value if product.product_type else "None"
                product.product_type = ProductType.SIMPLE
            else:
                pass
        
        # Commit changes
        db.commit()
        
        
    except Exception as e:
        db.rollback()
        import traceback
    finally:
        db.close()


if __name__ == "__main__":
    main()
