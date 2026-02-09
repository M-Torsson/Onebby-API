# Debug script to check campaign and categories
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.db.session import SessionLocal
    from app.models.category import Category
    from app.models.discount_campaign import DiscountCampaign
    from app.models.product import Product
    
    db = SessionLocal()
    
    print("=" * 60)
    print("1. Checking Telefonia categories:")
    print("=" * 60)
    telefonia_cats = db.query(Category).filter(Category.name.ilike('%telefonia%')).all()
    for cat in telefonia_cats:
        print(f"  ID: {cat.id}, Name: {cat.name}, parent_id: {cat.parent_id}")
    
    print("\n" + "=" * 60)
    print("2. Checking active discount campaigns:")
    print("=" * 60)
    campaigns = db.query(DiscountCampaign).filter(DiscountCampaign.is_active == True).all()
    for camp in campaigns:
        print(f"  Campaign ID: {camp.id}")
        print(f"  Name: {camp.name}")
        print(f"  Discount: {camp.discount_value}% ({camp.discount_type.value})")
        print(f"  Target Type: {camp.target_type.value}")
        print(f"  Target IDs: {camp.target_ids}")
        print(f"  Active: {camp.is_active}")
        print()
    
    print("=" * 60)
    print("3. Checking products in Telefonia mobile category:")
    print("=" * 60)
    
    # Try to find products linked to telefonia categories
    if telefonia_cats:
        for cat in telefonia_cats:
            if 'mobile' in cat.name.lower():
                print(f"\nCategory: {cat.name} (ID: {cat.id})")
                products = db.query(Product).join(Product.categories).filter(
                    Product.categories.any(id=cat.id),
                    Product.is_active == True
                ).all()
                print(f"  Total products found: {len(products)}")
                if len(products) > 0:
                    for prod in products[:5]:  # Show first 5
                        print(f"    - Product ID: {prod.id}, Ref: {prod.reference}")
    
    print("\n" + "=" * 60)
    print("4. Checking all subcategories of Telefonia:")
    print("=" * 60)
    
    def get_all_subcategories(category_id, db, depth=0):
        """Recursively get all subcategories"""
        results = [category_id]
        children = db.query(Category).filter(Category.parent_id == category_id).all()
        for child in children:
            results.extend(get_all_subcategories(child.id, db, depth + 1))
        return results
    
    for cat in telefonia_cats:
        if 'mobile' in cat.name.lower():
            all_cat_ids = get_all_subcategories(cat.id, db)
            print(f"\nCategory '{cat.name}' and all its subcategories:")
            print(f"  Category IDs: {all_cat_ids}")
            
            # Count products in all these categories
            products_in_all = db.query(Product).join(Product.categories).filter(
                Product.categories.any(Category.id.in_(all_cat_ids)),
                Product.is_active == True
            ).all()
            print(f"  Total products in all subcategories: {len(products_in_all)}")
    
    db.close()
    print("\n" + "=" * 60)
    print("Debug completed successfully!")
    print("=" * 60)
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
