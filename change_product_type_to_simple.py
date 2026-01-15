"""
Change product_type from configurable to simple for sample products
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.product import Product, ProductType


def main():
    print("="*60)
    print("Changing Product Type to Simple")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Product IDs
        product_ids = [35965, 35966, 35967, 35968]
        
        for product_id in product_ids:
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                old_type = product.product_type.value if product.product_type else "None"
                product.product_type = ProductType.SIMPLE
                print(f"✓ Changed product {product_id} from '{old_type}' to 'simple'")
            else:
                print(f"❌ Product {product_id} not found")
        
        # Commit changes
        db.commit()
        
        print("\n" + "="*60)
        print("✓ Product types changed successfully!")
        print("="*60)
        print("\nNow products should appear in dashboard search!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
