# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from typing import Optional, List, Dict
from sqlalchemy.orm import Session, joinedload
from deep_translator import GoogleTranslator
from datetime import datetime

from app.models.product import (
    Product, ProductTranslation, ProductImage, ProductImageAlt,
    ProductFeature, ProductFeatureTranslation,
    ProductAttribute, ProductAttributeTranslation,
    ProductVariantAttribute, ProductVariantAttributeTranslation,
    ProductDiscount, ProductType
)
from app.models.product_variant import ProductVariant, ProductVariantImage, ProductVariantImageAlt
from app.models.category import Category, CategoryTranslation
from app.models.brand import Brand
from app.models.tax_class import TaxClass
from app.schemas.product import ProductCreate, ProductUpdate, StockUpdateInput


# ============= Helper Functions =============

def create_automatic_translation(text: str, target_lang: str) -> str:
    """Translate text from Italian to target language"""
    if target_lang == "it":
        return text
    
    try:
        translated = GoogleTranslator(source='it', target=target_lang).translate(text)
        return translated
    except Exception as e:
        # Fallback to original text if translation fails
        return text


def create_product_translations(db: Session, product: Product, translations_data: List[dict]):
    """Create product translations with automatic translation for missing languages"""
    languages = ["it", "en", "fr", "de", "ar"]
    provided_langs = {t["lang"]: t for t in translations_data}
    
    # Get Italian (source) translation
    it_translation = provided_langs.get("it")
    if not it_translation:
        # Use first available translation as source
        it_translation = translations_data[0]
    
    for lang in languages:
        if lang in provided_langs:
            # Use provided translation
            trans_data = provided_langs[lang]
            translation = ProductTranslation(
                product_id=product.id,
                lang=lang,
                title=trans_data["title"],
                sub_title=trans_data.get("sub_title"),
                simple_description=trans_data.get("simple_description"),
                meta_description=trans_data.get("meta_description")
            )
        else:
            # Auto-translate from Italian
            translation = ProductTranslation(
                product_id=product.id,
                lang=lang,
                title=create_automatic_translation(it_translation["title"], lang),
                sub_title=create_automatic_translation(it_translation.get("sub_title", ""), lang) if it_translation.get("sub_title") else None,
                simple_description=create_automatic_translation(it_translation.get("simple_description", ""), lang) if it_translation.get("simple_description") else None,
                meta_description=create_automatic_translation(it_translation.get("meta_description", ""), lang) if it_translation.get("meta_description") else None
            )
        
        db.add(translation)
    
    db.commit()


def create_product_images(db: Session, product_id: int, images_data: List[dict], is_variant: bool = False, variant_id: Optional[int] = None):
    """Create product or variant images with alt texts"""
    for img_data in images_data:
        if is_variant and variant_id:
            # Create variant image
            image = ProductVariantImage(
                variant_id=variant_id,
                url=img_data["url"],
                position=img_data.get("position", 1)
            )
            db.add(image)
            db.flush()
            
            # Create alt texts
            alt_data = img_data.get("alt", {})
            for lang, alt_text in alt_data.items():
                if alt_text:
                    alt = ProductVariantImageAlt(
                        image_id=image.id,
                        lang=lang,
                        alt_text=alt_text
                    )
                    db.add(alt)
        else:
            # Create product image
            image = ProductImage(
                product_id=product_id,
                url=img_data["url"],
                position=img_data.get("position", 1)
            )
            db.add(image)
            db.flush()
            
            # Create alt texts
            alt_data = img_data.get("alt", {})
            for lang, alt_text in alt_data.items():
                if alt_text:
                    alt = ProductImageAlt(
                        image_id=image.id,
                        lang=lang,
                        alt_text=alt_text
                    )
                    db.add(alt)
    
    db.commit()


def create_product_features(db: Session, product: Product, features_data: List[dict]):
    """Create product features with translations"""
    for feat_data in features_data:
        feature = ProductFeature(
            product_id=product.id,
            code=feat_data["code"]
        )
        db.add(feature)
        db.flush()
        
        # Create translations
        for trans_data in feat_data["translations"]:
            trans = ProductFeatureTranslation(
                feature_id=feature.id,
                lang=trans_data["lang"],
                name=trans_data["name"],
                value=trans_data["value"]
            )
            db.add(trans)
    
    db.commit()


def create_product_attributes(db: Session, product: Product, attributes_data: List[dict]):
    """Create product attributes with translations"""
    for attr_data in attributes_data:
        attribute = ProductAttribute(
            product_id=product.id,
            code=attr_data["code"]
        )
        db.add(attribute)
        db.flush()
        
        # Create translations
        for trans_data in attr_data["translations"]:
            trans = ProductAttributeTranslation(
                attribute_id=attribute.id,
                lang=trans_data["lang"],
                name=trans_data["name"],
                value=trans_data["value"]
            )
            db.add(trans)
    
    db.commit()


def create_variant_attributes(db: Session, product: Product, variant_attrs_data: List[dict]):
    """Create variant attribute definitions with translations"""
    for attr_data in variant_attrs_data:
        variant_attr = ProductVariantAttribute(
            product_id=product.id,
            code=attr_data["code"]
        )
        db.add(variant_attr)
        db.flush()
        
        # Create translations
        for trans_data in attr_data["translations"]:
            trans = ProductVariantAttributeTranslation(
                variant_attribute_id=variant_attr.id,
                lang=trans_data["lang"],
                label=trans_data["label"]
            )
            db.add(trans)
    
    db.commit()


def create_product_discounts(db: Session, product_id: int, discounts_data: List[dict], variant_id: Optional[int] = None):
    """Create product or variant discounts"""
    for disc_data in discounts_data:
        discount = ProductDiscount(
            product_id=product_id if not variant_id else None,
            variant_id=variant_id,
            discount_type=disc_data["discount_type"],
            discount_value=disc_data["discount_value"],
            start_date=disc_data.get("start_date"),
            end_date=disc_data.get("end_date"),
            is_active=disc_data.get("is_active", True)
        )
        db.add(discount)
    
    db.commit()


def create_product_variants(db: Session, product: Product, variants_data: List[dict]):
    """Create product variants"""
    for var_data in variants_data:
        variant = ProductVariant(
            parent_product_id=product.id,
            reference=var_data["reference"],
            ean13=var_data.get("ean13"),
            is_active=var_data.get("is_active", True),
            condition=var_data.get("condition", "new"),
            attributes=var_data["attributes"],
            price_list=var_data["price"]["list"],
            currency=var_data["price"].get("currency", "EUR"),
            stock_status=var_data["stock"]["status"],
            stock_quantity=var_data["stock"]["quantity"]
        )
        db.add(variant)
        db.flush()
        
        # Create variant images
        if var_data.get("images"):
            create_product_images(db, product.id, var_data["images"], is_variant=True, variant_id=variant.id)
        
        # Create variant discounts
        if var_data["price"].get("discounts"):
            create_product_discounts(db, product.id, var_data["price"]["discounts"], variant_id=variant.id)
    
    db.commit()


# ============= Main CRUD Functions =============

def get_product(db: Session, product_id: int, lang: Optional[str] = None) -> Optional[Product]:
    """Get product by ID with all relationships"""
    from app.models.delivery import Delivery
    product = db.query(Product).options(
        joinedload(Product.brand),
        joinedload(Product.tax_class),
        joinedload(Product.delivery),
        joinedload(Product.categories).joinedload(Category.deliveries),
        joinedload(Product.translations),
        joinedload(Product.images).joinedload(ProductImage.alt_texts),
        joinedload(Product.features).joinedload(ProductFeature.translations),
        joinedload(Product.attributes).joinedload(ProductAttribute.translations),
        joinedload(Product.variant_attributes).joinedload(ProductVariantAttribute.translations),
        joinedload(Product.variants).joinedload(ProductVariant.images).joinedload(ProductVariantImage.alt_texts),
        joinedload(Product.discounts)
    ).filter(Product.id == product_id).first()
    
    return product


def get_product_by_reference(db: Session, reference: str) -> Optional[Product]:
    """Get product by reference"""
    return db.query(Product).filter(Product.reference == reference).first()


def count_products(
    db: Session,
    product_type: Optional[str] = None,
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    active_only: bool = False,
    search: Optional[str] = None
) -> int:
    """Count total products with filters"""
    query = db.query(Product)
    
    if product_type:
        query = query.filter(Product.product_type == product_type)
    
    if category_id:
        query = query.join(Product.categories).filter(Category.id == category_id)
    
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if search:
        # Search by ID or reference
        if search.isdigit():
            query = query.filter(Product.id == int(search))
        else:
            query = query.filter(Product.reference.ilike(f"%{search}%"))
    
    return query.count()


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    product_type: Optional[str] = None,
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    active_only: bool = False,
    search: Optional[str] = None
) -> List[Product]:
    """Get all products with filters"""
    query = db.query(Product)
    
    if product_type:
        query = query.filter(Product.product_type == product_type)
    
    if category_id:
        query = query.join(Product.categories).filter(Category.id == category_id)
    
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if search:
        # Search by ID or reference
        if search.isdigit():
            query = query.filter(Product.id == int(search))
        else:
            query = query.filter(Product.reference.ilike(f"%{search}%"))
    
    return query.offset(skip).limit(limit).all()


def create_product(db: Session, product_data: ProductCreate) -> Product:
    """Create a new product with all relationships"""
    
    # Get or use default tax class
    if product_data.tax:
        tax_class = db.query(TaxClass).filter(TaxClass.id == product_data.tax.class_id).first()
        if not tax_class:
            raise ValueError("Tax class not found")
        tax_class_id = product_data.tax.class_id
        tax_included = product_data.tax.included_in_price
    else:
        # Use first available tax class as default
        tax_class = db.query(TaxClass).first()
        if not tax_class:
            raise ValueError("No tax class found. Please create a tax class first.")
        tax_class_id = tax_class.id
        tax_included = True
    
    # Validate brand if provided
    if product_data.brand_id:
        brand = db.query(Brand).filter(Brand.id == product_data.brand_id).first()
        if not brand:
            raise ValueError("Brand not found")
    
    # Validate delivery if provided
    if product_data.delivery_id:
        from app.models.delivery import Delivery
        delivery = db.query(Delivery).filter(Delivery.id == product_data.delivery_id).first()
        if not delivery:
            raise ValueError("Delivery not found")
    
    # Validate categories
    categories = db.query(Category).filter(Category.id.in_(product_data.categories)).all()
    if len(categories) != len(product_data.categories):
        raise ValueError("One or more categories not found")
    
    # Create product
    product = Product(
        product_type=product_data.product_type,
        reference=product_data.reference,
        ean=product_data.ean,
        is_active=product_data.is_active,
        condition=product_data.condition,
        brand_id=product_data.brand_id,
        delivery_id=product_data.delivery_id,
        tax_class_id=tax_class_id,
        tax_included_in_price=tax_included,
        price_list=product_data.price.list,
        currency=product_data.price.currency,
        stock_status=product_data.stock.status,
        stock_quantity=product_data.stock.quantity,
        duration_months=product_data.duration_months,
        date_add=product_data.date_add or datetime.utcnow(),
        date_update=product_data.date_update
    )
    
    db.add(product)
    db.flush()
    
    # Add categories
    product.categories.extend(categories)
    
    # Create translations
    if product_data.translations:
        # Use provided translations
        create_product_translations(db, product, [t.dict() for t in product_data.translations])
    else:
        # Create default translation in Italian with basic info from reference
        default_translation = [{
            "lang": "it",
            "title": product_data.reference.replace("-", " ").title(),
            "sub_title": None,
            "simple_description": None,
            "meta_description": None
        }]
        create_product_translations(db, product, default_translation)
    
    # Create images
    if product_data.images:
        create_product_images(db, product.id, [img.dict() for img in product_data.images])
    
    # Create features
    if product_data.features:
        create_product_features(db, product, [f.dict() for f in product_data.features])
    
    # Create attributes
    if product_data.attributes:
        create_product_attributes(db, product, [a.dict() for a in product_data.attributes])
    
    # Create variant attributes (for configurable products)
    if product_data.variant_attributes:
        create_variant_attributes(db, product, [va.dict() for va in product_data.variant_attributes])
    
    # Create variants (for configurable products)
    if product_data.variants:
        create_product_variants(db, product, [v.dict() for v in product_data.variants])
    
    # Create discounts
    if product_data.price.discounts:
        create_product_discounts(db, product.id, [d.dict() for d in product_data.price.discounts])
    
    # Add related products
    if product_data.related_product_ids:
        related_products = db.query(Product).filter(Product.id.in_(product_data.related_product_ids)).all()
        product.related_products.extend(related_products)
    
    # Add service links (for configurable products)
    if product_data.service_links:
        if product_data.service_links.allowed_shipping_services:
            shipping_services = db.query(Product).filter(
                Product.id.in_(product_data.service_links.allowed_shipping_services),
                Product.product_type == ProductType.SERVICE
            ).all()
            product.allowed_shipping_services.extend(shipping_services)
        
        if product_data.service_links.allowed_warranties:
            warranties = db.query(Product).filter(
                Product.id.in_(product_data.service_links.allowed_warranties),
                Product.product_type == ProductType.WARRANTY
            ).all()
            product.allowed_warranties.extend(warranties)
    
    db.commit()
    db.refresh(product)
    
    # Auto-apply active campaigns to the new product
    from app.crud.discount_campaign import apply_active_campaigns_to_product
    apply_active_campaigns_to_product(db, product.id, product_data.categories)
    
    return product


def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
    """Update a product with comprehensive support for all fields"""
    product = get_product(db, product_id)
    if not product:
        return None
    
    update_data = product_data.model_dump(exclude_unset=True)
    
    # Track if categories are being updated
    categories_updated = False
    updated_category_ids = None
    
    # Handle categories update
    if "categories" in update_data:
        category_ids = update_data.pop("categories")
        # Validate all categories exist
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        if len(categories) != len(category_ids):
            raise ValueError("One or more categories not found")
        product.categories = categories
        categories_updated = True
        updated_category_ids = category_ids
    
    # Handle tax class update
    if "tax_class_id" in update_data:
        tax_class = db.query(TaxClass).filter(TaxClass.id == update_data["tax_class_id"]).first()
        if not tax_class:
            raise ValueError("Tax class not found")
    
    # Handle brand update
    if "brand_id" in update_data and update_data["brand_id"]:
        brand = db.query(Brand).filter(Brand.id == update_data["brand_id"]).first()
        if not brand:
            raise ValueError("Brand not found")
    
    # Handle delivery update
    if "delivery_id" in update_data and update_data["delivery_id"]:
        from app.models.delivery import Delivery
        delivery = db.query(Delivery).filter(Delivery.id == update_data["delivery_id"]).first()
        if not delivery:
            raise ValueError("Delivery not found")
    
    # Handle translations update (replace all)
    if "translations" in update_data:
        translations_data = update_data.pop("translations")
        # Delete existing translations
        db.query(ProductTranslation).filter(ProductTranslation.product_id == product_id).delete()
        # Create new translations
        create_product_translations(db, product, [t.dict() if hasattr(t, 'dict') else t for t in translations_data])
    
    # Handle images update (replace all)
    if "images" in update_data:
        images_data = update_data.pop("images")
        # Delete existing images and alt texts
        db.query(ProductImageAlt).filter(
            ProductImageAlt.image_id.in_(
                db.query(ProductImage.id).filter(ProductImage.product_id == product_id)
            )
        ).delete(synchronize_session=False)
        db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
        # Create new images
        create_product_images(db, product_id, [img.dict() if hasattr(img, 'dict') else img for img in images_data])
    
    # Handle features update (replace all)
    if "features" in update_data:
        features_data = update_data.pop("features")
        # Delete existing features and translations
        feature_ids = db.query(ProductFeature.id).filter(ProductFeature.product_id == product_id).all()
        if feature_ids:
            feature_ids = [f[0] for f in feature_ids]
            db.query(ProductFeatureTranslation).filter(ProductFeatureTranslation.feature_id.in_(feature_ids)).delete(synchronize_session=False)
        db.query(ProductFeature).filter(ProductFeature.product_id == product_id).delete()
        # Create new features
        create_product_features(db, product, [f.dict() if hasattr(f, 'dict') else f for f in features_data])
    
    # Handle attributes update (replace all)
    if "attributes" in update_data:
        attributes_data = update_data.pop("attributes")
        # Delete existing attributes and translations
        attr_ids = db.query(ProductAttribute.id).filter(ProductAttribute.product_id == product_id).all()
        if attr_ids:
            attr_ids = [a[0] for a in attr_ids]
            db.query(ProductAttributeTranslation).filter(ProductAttributeTranslation.attribute_id.in_(attr_ids)).delete(synchronize_session=False)
        db.query(ProductAttribute).filter(ProductAttribute.product_id == product_id).delete()
        # Create new attributes
        create_product_attributes(db, product, [a.dict() if hasattr(a, 'dict') else a for a in attributes_data])
    
    # Handle related products update
    if "related_product_ids" in update_data:
        related_ids = update_data.pop("related_product_ids")
        # Validate related products exist
        related_products = db.query(Product).filter(Product.id.in_(related_ids)).all()
        product.related_products = related_products
    
    # Handle service links update
    if "service_links" in update_data:
        service_links = update_data.pop("service_links")
        if service_links:
            # Clear existing links
            product.shipping_services.clear()
            product.warranties.clear()
            
            # Add new shipping services
            if hasattr(service_links, 'shipping_service_ids') and service_links.shipping_service_ids:
                shipping_services = db.query(Product).filter(
                    Product.id.in_(service_links.shipping_service_ids),
                    Product.product_type == ProductType.SERVICE
                ).all()
                product.shipping_services = shipping_services
            
            # Add new warranties
            if hasattr(service_links, 'warranty_ids') and service_links.warranty_ids:
                warranties = db.query(Product).filter(
                    Product.id.in_(service_links.warranty_ids),
                    Product.product_type == ProductType.WARRANTY
                ).all()
                product.warranties = warranties
    
    # Handle variants update (for configurable products only)
    if "variants" in update_data:
        variants_data = update_data.pop("variants")
        
        # Only process variants for configurable products, ignore for others
        if product.product_type == ProductType.CONFIGURABLE and variants_data:
            # Delete existing variants
            db.query(ProductVariant).filter(ProductVariant.parent_product_id == product_id).delete()
            # Create new variants
            create_product_variants(db, product, [v.dict() if hasattr(v, 'dict') else v for v in variants_data])
    
    # Update simple fields
    for field, value in update_data.items():
        setattr(product, field, value)
    
    product.date_update = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    # Auto-apply active campaigns if categories were updated
    if categories_updated:
        from app.crud.discount_campaign import apply_active_campaigns_to_product
        apply_active_campaigns_to_product(db, product_id, updated_category_ids)
    
    return product


def delete_product(db: Session, product_id: int) -> bool:
    """Delete a product permanently (hard delete)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return False
    
    # Hard delete - permanently remove from database
    db.delete(product)
    db.commit()
    return True


def update_product_stock(db: Session, product_id: int, stock_data: StockUpdateInput) -> Optional[Product]:
    """Update product stock"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    
    if stock_data.stock_status:
        product.stock_status = stock_data.stock_status
    
    if stock_data.stock_quantity is not None:
        product.stock_quantity = stock_data.stock_quantity
        
        # Auto-update status based on quantity
        if stock_data.stock_quantity == 0:
            product.stock_status = "out_of_stock"
        elif stock_data.stock_quantity <= 5:
            product.stock_status = "low_stock"
        else:
            product.stock_status = "in_stock"
    
    product.date_update = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    return product


def update_variant_stock(db: Session, variant_id: int, stock_data: StockUpdateInput) -> Optional[ProductVariant]:
    """Update variant stock"""
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        return None
    
    if stock_data.stock_status:
        variant.stock_status = stock_data.stock_status
    
    if stock_data.stock_quantity is not None:
        variant.stock_quantity = stock_data.stock_quantity
        
        # Auto-update status based on quantity
        if stock_data.stock_quantity == 0:
            variant.stock_status = "out_of_stock"
        elif stock_data.stock_quantity <= 5:
            variant.stock_status = "low_stock"
        else:
            variant.stock_status = "in_stock"
    
    db.commit()
    db.refresh(variant)
    return variant


def get_products_by_category(db: Session, category_id: int, lang: str = "it") -> List[dict]:
    """Get simple products by category ID with all required fields"""
    
    # Get category to check parent_id
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return []
    
    # Query simple products that belong to this category
    products = db.query(Product).join(
        Product.categories
    ).filter(
        Category.id == category_id,
        Product.product_type == ProductType.SIMPLE
    ).options(
        joinedload(Product.translations),
        joinedload(Product.images),
        joinedload(Product.categories),
        joinedload(Product.tax_class),
        joinedload(Product.discounts)
    ).all()
    
    result = []
    for product in products:
        # Get translation for requested language
        translation = next(
            (t for t in product.translations if t.lang == lang),
            next((t for t in product.translations if t.lang == "it"), None)
        )
        
        if not translation:
            continue
        
        # Get first image
        image_url = product.images[0].url if product.images else None
        
        # Get the specific child category name for this product
        product_category = next(
            (c for c in product.categories if c.id == category_id),
            None
        )
        
        child_category_name = ""
        child_slug = ""
        if product_category:
            cat_translation = next(
                (t for t in product_category.translations if t.lang == lang),
                next((t for t in product_category.translations if t.lang == "it"), None)
            )
            if cat_translation:
                child_category_name = cat_translation.name
                child_slug = cat_translation.slug
        
        # Calculate discount percentage
        active_discount = next(
            (d for d in product.discounts if d.is_active),
            None
        )
        discount_str = f"{int(active_discount.discount_percentage)}%" if active_discount else "0"
        
        # Get tax rate
        tax_rate = product.tax_class.rate if product.tax_class else 0
        tax_str = f"{int(tax_rate)}%"
        
        result.append({
            "id": product.id,
            "child_category": child_category_name,
            "slug": child_slug,
            "image": image_url,
            "brand_id": product.brand_id,
            "condition": product.condition.value,
            "quantity": product.stock_quantity,
            "title": translation.title,
            "sub_title": translation.sub_title,
            "simple_description": translation.simple_description,
            "is_active": product.is_active,
            "price": {
                "price": product.price_list or 0.0,
                "currency": product.currency or "EUR",
                "discounts": discount_str,
                "tax_role": tax_str
            },
            "parent_id": category.parent_id
        })
    
    return result


# ============= Get Recent Products =============

def get_recent_products(db: Session, limit: int = 15) -> List[dict]:
    """
    Get recently added products
    Sorted by date_add (newest first)
    Returns compact JSON format
    """
    # Query recent products
    products = db.query(Product).filter(
        Product.is_active == True
    ).order_by(
        Product.date_add.desc()
    ).limit(limit).all()
    
    result = []
    
    for product in products:
        # Get Italian translation (preferred)
        translation = db.query(ProductTranslation).filter(
            ProductTranslation.product_id == product.id,
            ProductTranslation.lang == "it"
        ).first()
        
        if not translation:
            # Fallback to first available translation
            translation = db.query(ProductTranslation).filter(
                ProductTranslation.product_id == product.id
            ).first()
        
        title = translation.title if translation else "Untitled"
        
        # Get first image
        image = db.query(ProductImage).filter(
            ProductImage.product_id == product.id
        ).order_by(ProductImage.position).first()
        
        image_url = image.url if image else None
        
        # Get first category with Italian translation
        category_name = None
        if product.categories:
            first_category = product.categories[0]
            category_translation = db.query(CategoryTranslation).filter(
                CategoryTranslation.category_id == first_category.id,
                CategoryTranslation.lang == "it"
            ).first()
            
            if category_translation:
                category_name = category_translation.name
            else:
                category_name = first_category.name
        
        result.append({
            "id": product.id,
            "title": title,
            "reference": product.reference,
            "price": product.price_list or 0.0,
            "image": image_url,
            "category": category_name,
            "date_add": product.date_add.isoformat() if product.date_add else None
        })
    
    return result

