"""
Add categories to the sample products
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.product import Product
from app.models.category import Category


def main():
    print("="*60)
    print("Adding Categories to Sample Products")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Product IDs
        ac_id = 35965
        washer_id = 35966
        tv_id = 35967
        fridge_id = 35968
        
        # Category IDs from database
        clima_category_id = 8154  # Clima - for AC
        grandi_elettro_id = 8151  # Grandi elettrodomestici - for Washer and Fridge
        audio_video_id = 8153     # Audio video - for TV
        
        # Get categories
        clima_category = db.query(Category).filter(Category.id == clima_category_id).first()
        grandi_category = db.query(Category).filter(Category.id == grandi_elettro_id).first()
        av_category = db.query(Category).filter(Category.id == audio_video_id).first()
        
        # Get products
        ac_product = db.query(Product).filter(Product.id == ac_id).first()
        washer_product = db.query(Product).filter(Product.id == washer_id).first()
        tv_product = db.query(Product).filter(Product.id == tv_id).first()
        fridge_product = db.query(Product).filter(Product.id == fridge_id).first()
        
        # Add categories
        if ac_product and clima_category:
            if clima_category not in ac_product.categories:
                ac_product.categories.append(clima_category)
                print(f"✓ Added 'Clima' category to AC product (ID: {ac_id})")
            else:
                print(f"⚠ AC product already has this category")
        else:
            print(f"❌ AC product or Clima category not found")
        
        if washer_product and grandi_category:
            if grandi_category not in washer_product.categories:
                washer_product.categories.append(grandi_category)
                print(f"✓ Added 'Grandi elettrodomestici' category to Washer product (ID: {washer_id})")
            else:
                print(f"⚠ Washer product already has this category")
        else:
            print(f"❌ Washer product or category not found")
        
        if tv_product and av_category:
            if av_category not in tv_product.categories:
                tv_product.categories.append(av_category)
                print(f"✓ Added 'Audio video' category to TV product (ID: {tv_id})")
            else:
                print(f"⚠ TV product already has this category")
        else:
            print(f"❌ TV product or category not found")
        
        if fridge_product and grandi_category:
            if grandi_category not in fridge_product.categories:
                fridge_product.categories.append(grandi_category)
                print(f"✓ Added 'Grandi elettrodomestici' category to Fridge product (ID: {fridge_id})")
            else:
                print(f"⚠ Fridge product already has this category")
        else:
            print(f"❌ Fridge product or category not found")
        
        # Commit changes
        db.commit()
        
        print("\n" + "="*60)
        print("✓ Categories added successfully!")
        print("="*60)
        print("\nNow check your dashboard - products should appear!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
