"""
Product Import CRUD Operations
Handles upsert logic and database operations for product imports
"""
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from slugify import slugify

from app.models.product import Product, ProductTranslation, ProductType, ProductCondition, StockStatus
from app.models.brand import Brand
from app.models.category import Category, CategoryTranslation
from app.models.tax_class import TaxClass


def get_or_create_brand(db: Session, brand_name: str) -> Optional[Brand]:
    """Get existing brand or create new one by name"""
    if not brand_name:
        return None
    
    # Try to find existing brand
    brand = db.query(Brand).filter(Brand.name == brand_name).first()
    
    if not brand:
        # Create new brand
        brand = Brand(
            name=brand_name,
            slug=slugify(brand_name),
            is_active=True,
            sort_order=0
        )
        db.add(brand)
        db.flush()
    
    return brand


def get_or_create_category_path(db: Session, category_path: List[str]) -> Optional[Category]:
    """
    Get or create category hierarchy from path
    Example: ["Electronics", "Smartphones"] creates parent "Electronics" and child "Smartphones"
    Returns the leaf category (last in path)
    """
    if not category_path:
        return None
    
    parent_category = None
    
    for category_name in category_path:
        if not category_name or not category_name.strip():
            continue
        
        category_name = category_name.strip()
        slug = slugify(category_name)
        
        # Try to find existing category
        query = db.query(Category).filter(
            Category.slug == slug,
            Category.parent_id == (parent_category.id if parent_category else None)
        )
        category = query.first()
        
        if not category:
            # Create new category
            category = Category(
                name=category_name,
                slug=slug,
                is_active=True,
                sort_order=0,
                parent_id=parent_category.id if parent_category else None
            )
            db.add(category)
            db.flush()
            
            # Create default Italian translation
            translation = CategoryTranslation(
                category_id=category.id,
                lang="it",
                name=category_name,
                slug=slug,
                description=None
            )
            db.add(translation)
            db.flush()
        
        parent_category = category
    
    return parent_category


def get_or_create_default_tax_class(db: Session) -> TaxClass:
    """Get or create default tax class (22%)"""
    tax_class = db.query(TaxClass).filter(TaxClass.name == "Standard VAT (22%)").first()
    
    if not tax_class:
        tax_class = TaxClass(
            name="Standard VAT (22%)",
            rate=22.0,
            is_active=True
        )
        db.add(tax_class)
        db.flush()
    
    return tax_class


def upsert_product(
    db: Session,
    product_data: Dict[str, Any],
    dry_run: bool = False
) -> tuple[str, Optional[Product]]:
    """
    Upsert product by EAN
    Returns: (action, product) where action is 'created', 'updated', or 'error'
    """
    ean = product_data.get("ean")
    if not ean:
        return "error", None
    
    # Check if product exists
    existing_product = db.query(Product).filter(Product.ean == ean).first()
    
    if existing_product:
        # Update existing product
        action = "updated"
        product = existing_product
        
        # Update only fields that are present in product_data
        if product_data.get("title"):
            # Update translations
            translation = db.query(ProductTranslation).filter(
                ProductTranslation.product_id == product.id,
                ProductTranslation.lang == "it"
            ).first()
            
            if translation:
                translation.title = product_data["title"]
                if product_data.get("description"):
                    translation.simple_description = product_data["description"]
            else:
                # Create translation if doesn't exist
                translation = ProductTranslation(
                    product_id=product.id,
                    lang="it",
                    title=product_data["title"],
                    simple_description=product_data.get("description")
                )
                db.add(translation)
        
        # Update price if provided
        if product_data.get("price") is not None:
            product.price_list = product_data["price"]
        
        # Update stock if provided
        if product_data.get("stock") is not None:
            product.stock_quantity = product_data["stock"]
            # Update stock status
            if product_data["stock"] > 0:
                product.stock_status = StockStatus.IN_STOCK
            else:
                product.stock_status = StockStatus.OUT_OF_STOCK
        
        # Update brand if provided
        if product_data.get("brand_name"):
            brand = get_or_create_brand(db, product_data["brand_name"])
            if brand:
                product.brand_id = brand.id
        
        # Update categories if provided
        if product_data.get("category_path"):
            category = get_or_create_category_path(db, product_data["category_path"])
            if category:
                # Clear existing categories and add new one
                product.categories = [category]
        
    else:
        # Create new product
        action = "created"
        
        # Check for reference conflict (safety check)
        existing_ref = db.query(Product).filter(Product.reference == ean).first()
        if existing_ref:
            # Reference already exists - skip to avoid conflict
            return "error", None
        
        # Get or create brand
        brand = None
        if product_data.get("brand_name"):
            brand = get_or_create_brand(db, product_data["brand_name"])
        
        # Get or create category
        category = None
        if product_data.get("category_path"):
            category = get_or_create_category_path(db, product_data["category_path"])
        
        # Get default tax class
        tax_class = get_or_create_default_tax_class(db)
        
        # Determine stock status
        stock_quantity = product_data.get("stock", 0)
        stock_status = StockStatus.IN_STOCK if stock_quantity > 0 else StockStatus.OUT_OF_STOCK
        
        # Create product
        product = Product(
            product_type=ProductType.SIMPLE,
            reference=ean,  # Use EAN as reference
            ean=ean,
            is_active=True,
            condition=ProductCondition.NEW,
            brand_id=brand.id if brand else None,
            tax_class_id=tax_class.id,
            tax_included_in_price=False,
            price_list=product_data.get("price"),  # NULL if missing
            currency="EUR",
            stock_status=stock_status,
            stock_quantity=stock_quantity
        )
        
        db.add(product)
        db.flush()
        
        # Add category
        if category:
            product.categories = [category]
        
        # Create Italian translation
        translation = ProductTranslation(
            product_id=product.id,
            lang="it",
            title=product_data.get("title", ""),
            simple_description=product_data.get("description")
        )
        db.add(translation)
    
    if not dry_run:
        db.flush()
    
    return action, product


def import_products_batch(
    db: Session,
    products_data: List[Dict[str, Any]],
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Import a batch of products
    Returns: statistics dict with created, updated, errors counts
    """
    stats = {
        "created": 0,
        "updated": 0,
        "errors": []
    }
    
    for product_data in products_data:
        try:
            action, product = upsert_product(db, product_data, dry_run)
            
            if action == "created":
                stats["created"] += 1
            elif action == "updated":
                stats["updated"] += 1
            elif action == "error":
                stats["errors"].append({
                    "row_number": product_data.get("row_number", 0),
                    "reason": "upsert_failed",
                    "details": "Failed to upsert product"
                })
        
        except IntegrityError as e:
            db.rollback()
            stats["errors"].append({
                "row_number": product_data.get("row_number", 0),
                "reason": "integrity_error",
                "details": str(e.orig)
            })
        
        except Exception as e:
            db.rollback()
            stats["errors"].append({
                "row_number": product_data.get("row_number", 0),
                "reason": "unexpected_error",
                "details": str(e)
            })
    
    if not dry_run:
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
    else:
        db.rollback()
    
    return stats
