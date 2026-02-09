"""Search for product with title 'Test 2'"""
from app.db.session import SessionLocal
from app.models.product import Product
from app.models.product_translation import ProductTranslation

db = SessionLocal()

try:
    # Search in product translations for 'Test 2'
    translations = db.query(ProductTranslation).filter(
        ProductTranslation.title.ilike('%Test 2%')
    ).all()
    
    if translations:
        print(f"\n✅ Found {len(translations)} translation(s) with 'Test 2':\n")
        for trans in translations:
            product = db.query(Product).filter(Product.id == trans.product_id).first()
            if product:
                print(f"Product ID: {product.id}")
                print(f"Reference: {product.reference}")
                print(f"EAN: {product.ean}")
                print(f"Title ({trans.lang}): {trans.title}")
                print(f"Active: {product.is_active}")
                print(f"Stock: {product.stock_quantity}")
                print(f"Price: {product.price_list}")
                print("-" * 50)
    else:
        print("\n❌ No products found with title 'Test 2'\n")
        
        # Search also by reference
        products = db.query(Product).filter(
            Product.reference.ilike('%Test%')
        ).all()
        
        if products:
            print(f"\nFound {len(products)} product(s) with 'Test' in reference:\n")
            for prod in products:
                trans = db.query(ProductTranslation).filter(
                    ProductTranslation.product_id == prod.id,
                    ProductTranslation.lang == 'it'
                ).first()
                
                print(f"Product ID: {prod.id}")
                print(f"Reference: {prod.reference}")
                print(f"Title: {trans.title if trans else 'N/A'}")
                print("-" * 50)

finally:
    db.close()
