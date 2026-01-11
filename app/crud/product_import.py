"""
Product Import CRUD Operations
Handles upsert logic and database operations for product imports
"""
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from slugify import slugify

from app.models.product import (
    Product,
    ProductTranslation,
    ProductType,
    ProductCondition,
    StockStatus,
    ProductImage,
)
from app.models.brand import Brand
from app.models.category import Category, CategoryTranslation
from app.models.tax_class import TaxClass


def _clean_ean(raw: Any) -> Optional[str]:
    """Digits-only EAN; returns None if empty."""
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    digits = "".join(ch for ch in text if ch.isdigit())
    return digits or None


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


def get_or_create_uncategorized(db: Session) -> Category:
    """
    Get or create 'Uncategorized' fallback category
    Used when category creation fails to prevent product loss
    """
    uncategorized = db.query(Category).filter(
        Category.slug == "uncategorized",
        Category.parent_id == None
    ).first()
    
    if not uncategorized:
        uncategorized = Category(
            name="Uncategorized",
            slug="uncategorized",
            is_active=True,
            sort_order=9999,
            parent_id=None
        )
        db.add(uncategorized)
        db.flush()
        
        # Create translation
        translation = CategoryTranslation(
            category_id=uncategorized.id,
            lang="it",
            name="Non categorizzato",
            slug="uncategorized",
            description="Prodotti senza categoria assegnata"
        )
        db.add(translation)
        db.flush()
    
    return uncategorized


def get_or_create_category_path(db: Session, category_path: List[str]) -> Optional[Category]:
    """
    Get or create category hierarchy from path
    Example: ["Electronics", "Smartphones"] creates parent "Electronics" and child "Smartphones"
    Returns the leaf category (last in path)
    
    Fallback strategy: On persistent FK errors, returns Uncategorized category
    This ensures products are never lost due to category creation issues
    """
    if not category_path:
        return get_or_create_uncategorized(db)
    
    parent_category = None
    
    for category_name in category_path:
        if not category_name or not category_name.strip():
            continue
        
        category_name = category_name.strip()
        
        # Generate unique slug based on full path to avoid conflicts
        if parent_category:
            # Child category: include parent slug in the unique slug
            base_slug = slugify(category_name)
            slug = f"{slugify(parent_category.name)}-{base_slug}"
        else:
            # Root category: use simple slug
            slug = slugify(category_name)
        
        # Try to find existing category by slug and parent
        parent_id = parent_category.id if parent_category else None
        query = db.query(Category).filter(
            Category.slug == slug,
            Category.parent_id == parent_id
        )
        category = query.first()
        
        if not category:
            # Attempt to create category with retry logic
            retry_count = 0
            max_retries = 2
            
            while retry_count < max_retries:
                try:
                    # GUARD: Verify parent exists in DB before creating child
                    if parent_id:
                        parent_exists = db.query(Category.id).filter(Category.id == parent_id).scalar()
                        if not parent_exists:
                            # Parent missing - fallback to Uncategorized
                            return get_or_create_uncategorized(db)
                    
                    # Create new category
                    category = Category(
                        name=category_name,
                        slug=slug,
                        is_active=True,
                        sort_order=0,
                        parent_id=parent_id
                    )
                    db.add(category)
                    db.flush()  # ✅ IMMEDIATE FLUSH to get real ID in same transaction
                    
                    # Create default Italian translation
                    translation = CategoryTranslation(
                        category_id=category.id,
                        lang="it",
                        name=category_name,
                        slug=slug,
                        description=None
                    )
                    db.add(translation)
                    db.flush()  # Flush translation too
                    
                    # Success - break retry loop
                    break
                    
                except IntegrityError as e:
                    # Rollback the failed transaction
                    db.rollback()
                    
                    error_msg = str(e.orig).lower()
                    
                    # Check if it's a FK constraint error (parent not found)
                    if 'foreign key' in error_msg or 'parent_id' in error_msg:
                        retry_count += 1
                        if retry_count >= max_retries:
                            # FALLBACK: Return Uncategorized instead of failing
                            return get_or_create_uncategorized(db)
                        
                        # Rebuild from scratch with fresh queries
                        if parent_id:
                            parent_category = db.query(Category).filter(Category.id == parent_id).first()
                            if not parent_category:
                                # Parent lost - fallback
                                return get_or_create_uncategorized(db)
                        continue
                    
                    # Slug conflict - try to fetch existing category
                    category = db.query(Category).filter(
                        Category.slug == slug,
                        Category.parent_id == parent_id
                    ).first()
                    
                    if not category:
                        # Try by name and parent
                        category = db.query(Category).filter(
                            Category.name == category_name,
                            Category.parent_id == parent_id
                        ).first()
                    
                    if not category:
                        # Last resort: create with unique suffix
                        import time
                        unique_slug = f"{slug}-{int(time.time() * 1000) % 10000}"
                        try:
                            category = Category(
                                name=category_name,
                                slug=unique_slug,
                                is_active=True,
                                sort_order=0,
                                parent_id=parent_id
                            )
                            db.add(category)
                            db.flush()  # Flush immediately
                        except IntegrityError:
                            # Even unique slug failed - fallback
                            db.rollback()
                            return get_or_create_uncategorized(db)
                    
                    # Success - break retry loop
                    break
        
        # Important: Ensure category is attached and has valid ID
        if category:
            if category not in db:
                # Category might be detached after rollback - re-fetch
                category = db.query(Category).filter(Category.id == category.id).first()
            
            # Final verification: ensure category has ID
            if not category or not category.id:
                return get_or_create_uncategorized(db)
        
        parent_category = category
    
    return parent_category if parent_category else get_or_create_uncategorized(db)


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
    dry_run: bool = False,
    log_sample: bool = False
) -> tuple[str, Optional[Product], bool]:
    """
    Upsert product by EAN
    Returns: (action, product, existed_before) where action is 'created' or 'updated'
    """
    ean = _clean_ean(product_data.get("ean"))
    if not ean:
        raise ValueError("EAN is required")
    
    # Check if product exists
    existing_product = db.query(Product).filter(Product.ean == ean).first()
    # Temporary fallback: some legacy rows stored EAN in reference
    if not existing_product:
        existing_product = db.query(Product).filter(Product.reference == ean).first()
    existed_before = existing_product is not None
    
    # Log sample (first 5 products)
    if log_sample:
        from app.core.logging import logger
        logger.info(f"[SAMPLE] EAN: {ean} | Existed: {existed_before} | Title: {product_data.get('title', 'N/A')[:50]}")
    
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
        
        incoming_ref = product_data.get("reference")
        if incoming_ref:
            ref_conflict = db.query(Product).filter(Product.reference == incoming_ref).first()
            if ref_conflict:
                raise ValueError(f"Reference '{incoming_ref}' already exists")
        # Use provided reference or fallback to EAN
        reference_value = incoming_ref or ean
        
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
            reference=reference_value,
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
    
    return action, product, existed_before


def import_products_batch(
    db: Session,
    products_data: List[Dict[str, Any]],
    dry_run: bool = False,
    batch_index: int = 0
) -> Dict[str, Any]:
    """
    Import a batch of products
    Returns: statistics dict with created, updated, errors, samples
    """
    stats = {
        "created": 0,
        "updated": 0,
        "errors": [],
        "samples": []  # First 5 imports
    }
    
    for product_data in products_data:
        try:
            # Log sample for first batch only
            log_sample = (batch_index == 0 and len(stats["samples"]) < 5)
            
            action, product, existed_before = upsert_product(db, product_data, dry_run, log_sample)
            
            # Add to samples (first 5)
            if log_sample:
                stats["samples"].append({
                    "ean": product_data.get("ean"),
                    "existed_before": existed_before,
                    "action": action,
                    "title": product_data.get("title", "")[:50]
                })
            
            if action == "created":
                stats["created"] += 1
            elif action == "updated":
                stats["updated"] += 1
        
        except IntegrityError as e:
            db.rollback()
            stats["errors"].append({
                "row_number": product_data.get("row_number", 0),
                "ean": product_data.get("ean"),
                "reason": "integrity_error",
                "details": str(e.orig)
            })
        
        except Exception as e:
            db.rollback()
            stats["errors"].append({
                "row_number": product_data.get("row_number", 0),
                "ean": product_data.get("ean"),
                "reason": "processing_error",
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


# ============ Enrichment (fill missing fields only) ============

def enrich_product(
    db: Session,
    product_data: Dict[str, Any],
    dry_run: bool = False,
    log_sample: bool = False,
) -> tuple[bool, Optional[Product], List[str]]:
    """
    Enrich an existing product by EAN. Returns (matched, product, updated_fields).

    Rules:
    - Skip if product not found.
    - Do NOT touch stock or categories.
    - Do NOT overwrite non-empty fields (fill-if-empty only).
    - Price updated only if provided AND current price_list is null.
    """
    ean = _clean_ean(product_data.get("ean"))
    if not ean:
        raise ValueError("EAN is required")

    product = db.query(Product).filter(Product.ean == ean).first()
    if not product:
        product = db.query(Product).filter(Product.reference == ean).first()
    if not product:
        return False, None, []

    updated_fields: List[str] = []

    # Translation (Italian)
    translation = db.query(ProductTranslation).filter(
        ProductTranslation.product_id == product.id,
        ProductTranslation.lang == "it",
    ).first()
    if not translation:
        translation = ProductTranslation(
            product_id=product.id,
            lang="it",
            title=product_data.get("title") or product.reference,
            simple_description=product_data.get("description"),
        )
        db.add(translation)
        updated_fields.append("translation_created")
    else:
        if (not translation.title) and product_data.get("title"):
            translation.title = product_data["title"]
            updated_fields.append("title")
        if (not translation.simple_description) and product_data.get("description"):
            translation.simple_description = product_data["description"]
            updated_fields.append("description")

    # Price: set only if DB empty and new value present
    if product.price_list is None and product_data.get("price") is not None:
        product.price_list = product_data["price"]
        updated_fields.append("price")

    # Brand: set only if DB empty
    if product.brand_id is None and product_data.get("brand_name"):
        brand = get_or_create_brand(db, product_data["brand_name"])
        if brand:
            product.brand_id = brand.id
            updated_fields.append("brand")

    # Images: add only if product has no images yet
    image_urls = product_data.get("image_urls") or []
    if image_urls and not product.images:
        for pos, url in enumerate(image_urls, start=1):
            db.add(ProductImage(product_id=product.id, url=url, position=pos))
        updated_fields.append("images")

    if updated_fields and not dry_run:
        db.flush()

    return True, product, updated_fields


def enrich_products_batch(
    db: Session,
    products_data: List[Dict[str, Any]],
    dry_run: bool = False,
    batch_index: int = 0,
) -> Dict[str, Any]:
    """Batch enrichment using EAN as key (no creations)."""
    stats = {
        "matched": 0,
        "skipped": 0,
        "errors": [],
        "matched_samples": [],
        "skipped_samples": [],
    }

    for product_data in products_data:
        try:
            log_sample = batch_index == 0 and len(stats["matched_samples"]) < 5
            matched, product, updated_fields = enrich_product(db, product_data, dry_run, log_sample)

            if not matched:
                stats["skipped"] += 1
                if len(stats["skipped_samples"]) < 5:
                    stats["skipped_samples"].append({
                        "ean": product_data.get("ean"),
                        "reason": "not_found",
                        "details": "EAN not found in DB",
                    })
                continue

            if updated_fields:
                stats["matched"] += 1
                if log_sample:
                    stats["matched_samples"].append({
                        "ean": product_data.get("ean"),
                        "updated_fields": updated_fields,
                        "title": product_data.get("title"),
                    })
            else:
                stats["skipped"] += 1
                if len(stats["skipped_samples"]) < 5:
                    stats["skipped_samples"].append({
                        "ean": product_data.get("ean"),
                        "reason": "no_updates",
                        "details": "All target fields already populated",
                    })

        except Exception as e:
            db.rollback()
            stats["errors"].append({
                "row_number": product_data.get("row_number", 0),
                "ean": product_data.get("ean"),
                "reason": "processing_error",
                "details": str(e),
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
