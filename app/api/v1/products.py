# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Dict, Any
from collections import defaultdict
import re
from app.db.session import get_db
from app.core.config import settings
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductResponseFull,
    StockUpdateInput, StockUpdateResponse
)
from app.schemas.product_base import (
    ProductImageResponse, ProductFeatureResponse, ProductAttributeResponse,
    ProductVariantAttributeResponse, ProductVariantResponse,
    PriceResponse, StockResponse, CategorySimple
)
from app.schemas.brand_tax import BrandSimple, TaxClassSimple
from app.crud import product as crud_product
from app.models.product import Product, ProductTranslation
from app.models.category import Category


router = APIRouter()


# ============= Helper Functions =============

def verify_api_key(x_api_key: str = Header(...)):
    """Verify API Key from header"""
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from text"""
    if not text:
        return ""
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    # Replace multiple spaces/newlines with single space
    clean_text = re.sub(r'\s+', ' ', clean_text)
    return clean_text.strip()


def build_product_response(product: Product, lang: str) -> Dict[str, Any]:
    """Build product response based on requested language"""
    
    # Get translation for requested language
    translation = None
    if product.translations:
        translation = next((t for t in product.translations if t.lang == lang), None)
        if not translation:
            # Fallback to Italian
            translation = next((t for t in product.translations if t.lang == "it"), None)
        if not translation:
            # Last fallback: use first available
            translation = product.translations[0] if product.translations else None
    
    if not translation:
        raise HTTPException(status_code=404, detail="Product translation not found")
    
    # Build images with language-specific alt text
    images = []
    if product.images:
        for img in product.images:
            alt_text = ""
            if img.alt_texts:
                alt_text = next((alt.alt_text for alt in img.alt_texts if alt.lang == lang), "")
                if not alt_text:
                    alt_text = next((alt.alt_text for alt in img.alt_texts if alt.lang == "it"), "")
            
            images.append(ProductImageResponse(
                url=img.url,
                position=img.position,
                alt=alt_text
            ))
    
    # Build features with language-specific translations
    features = []
    if product.features:
        for feat in product.features:
            feat_trans = None
            if feat.translations:
                feat_trans = next((t for t in feat.translations if t.lang == lang), None)
                if not feat_trans:
                    feat_trans = next((t for t in feat.translations if t.lang == "it"), None)
            
            if feat_trans:
                features.append(ProductFeatureResponse(
                    name=feat_trans.name,
                    value=feat_trans.value
                ))
    
    # Build attributes with language-specific translations
    attributes = []
    if product.attributes:
        for attr in product.attributes:
            attr_trans = None
            if attr.translations:
                attr_trans = next((t for t in attr.translations if t.lang == lang), None)
                if not attr_trans:
                    attr_trans = next((t for t in attr.translations if t.lang == "it"), None)
            
            if attr_trans:
                attributes.append(ProductAttributeResponse(
                    code=attr.code,
                    name=attr_trans.name,
                    value=attr_trans.value
                ))
    
    # Build variant attributes with language-specific labels and options
    variant_attributes = []
    if product.variant_attributes:
        for var_attr in product.variant_attributes:
            var_attr_trans = None
            if var_attr.translations:
                var_attr_trans = next((t for t in var_attr.translations if t.lang == lang), None)
                if not var_attr_trans:
                    var_attr_trans = next((t for t in var_attr.translations if t.lang == "it"), None)
            
            if var_attr_trans:
                # Extract unique options from variants
                options = []
                seen_values = set()
                if product.variants:
                    for variant in product.variants:
                        if variant.is_active and variant.attributes and var_attr.code in variant.attributes:
                            value = variant.attributes[var_attr.code]
                            if value not in seen_values:
                                seen_values.add(value)
                                options.append({
                                    "value": value,
                                    "label": value.title()  # Simple formatting
                                })
                
                variant_attributes.append(ProductVariantAttributeResponse(
                    code=var_attr.code,
                    label=var_attr_trans.label,
                    options=options
                ))
    
    # Build variants
    variants = []
    if product.variants:
        for variant in product.variants:
            if variant.is_active:
                # Build variant images
                variant_images = []
                if variant.images:
                    for img in variant.images:
                        alt_text = ""
                        if img.alt_texts:
                            alt_text = next((alt.alt_text for alt in img.alt_texts if alt.lang == lang), "")
                            if not alt_text:
                                alt_text = next((alt.alt_text for alt in img.alt_texts if alt.lang == "it"), "")
                        
                        variant_images.append(ProductImageResponse(
                            url=img.url,
                            position=img.position,
                            alt=alt_text
                        ))
                
                # Calculate discounts - Get best discount based on priority
                discount_percentage = "0"
                if variant.discounts:
                    active_discounts = [d for d in variant.discounts if d.is_active]
                    if active_discounts:
                        # Sort by priority (desc) then by discount_value (desc)
                        # Higher priority wins, if equal priority then higher discount wins
                        best_discount = max(active_discounts, 
                                          key=lambda d: (d.priority, d.discount_value))
                        
                        if best_discount.discount_type == "percentage":
                            discount_percentage = f"{int(best_discount.discount_value)}%"
                        elif best_discount.discount_type == "amount":
                            # Calculate percentage from amount
                            if variant.price_list and variant.price_list > 0:
                                percentage = (best_discount.discount_value / variant.price_list) * 100
                                discount_percentage = f"{int(percentage)}%"
                
                variants.append(ProductVariantResponse(
                    id=variant.id,
                    reference=variant.reference,
                    ean13=variant.ean or "",
                    is_active=variant.is_active,
                    attributes=variant.attributes or {},
                    price=PriceResponse(
                        list=variant.price_list or 0.0,
                        currency=variant.currency or "EUR",
                        discounts=discount_percentage
                    ),
                    stock=StockResponse(
                        status=variant.stock_status.value if variant.stock_status else "out_of_stock",
                        quantity=variant.stock_quantity or 0
                    ),
                    images=variant_images
                ))
    
    # Build categories with translations
    categories = []
    if product.categories:
        for cat in product.categories:
            cat_trans = None
            if cat.translations:
                cat_trans = next((t for t in cat.translations if t.lang == lang), None)
                if not cat_trans:
                    cat_trans = next((t for t in cat.translations if t.lang == "it"), None)
            
            if cat_trans:
                categories.append(CategorySimple(
                    id=cat.id,
                    name=cat_trans.name,
                    slug=cat_trans.slug
                ))
    
    # Build brand
    brand = None
    if product.brand:
        brand = BrandSimple(
            id=product.brand.id,
            name=product.brand.name,
            image=product.brand.image
        )
    
    # Build delivery
    delivery = None
    if product.delivery:
        # Product has direct delivery assigned
        from app.schemas.delivery import DeliverySimple
        delivery = DeliverySimple(
            id=product.delivery.id,
            days_from=product.delivery.days_from,
            days_to=product.delivery.days_to,
            is_free_delivery=product.delivery.is_free_delivery
        )
    elif product.categories:
        # Check if any category has a delivery assigned
        from app.models.delivery import Delivery
        for category in product.categories:
            if category.deliveries:
                # Use the first active delivery found for this category
                active_delivery = next((d for d in category.deliveries if d.is_active), None)
                if active_delivery:
                    from app.schemas.delivery import DeliverySimple
                    delivery = DeliverySimple(
                        id=active_delivery.id,
                        days_from=active_delivery.days_from,
                        days_to=active_delivery.days_to,
                        is_free_delivery=active_delivery.is_free_delivery
                    )
                    break  # Use first found delivery
    
    # Build warranty
    warranty = None
    if product.warranty:
        # Product has direct warranty assigned
        from app.schemas.warranty import WarrantySimple
        warranty = WarrantySimple(
            id=product.warranty.id,
            title=product.warranty.title,
            price=round(product.warranty.price / 100, 2),
            image=product.warranty.image
        )
    elif product.categories:
        # Check if any category has a warranty assigned
        from app.models.warranty import Warranty
        for category in product.categories:
            if category.warranties:
                # Use the first active warranty found for this category
                active_warranty = next((w for w in category.warranties if w.is_active), None)
                if active_warranty:
                    from app.schemas.warranty import WarrantySimple
                    warranty = WarrantySimple(
                        id=active_warranty.id,
                        title=active_warranty.title,
                        price=round(active_warranty.price / 100, 2),
                        image=active_warranty.image
                    )
                    break  # Use first found warranty
    
    # Build tax - with null safety
    tax = None
    if product.tax_class:
        tax = TaxClassSimple(
            id=product.tax_class.id,
            name=product.tax_class.name,
            rate=product.tax_class.rate,
            included_in_price=product.tax_included_in_price
        )
    
    # Build options (shipping services and warranties)
    options = None
    if product.product_type and product.product_type.value == "configurable":
        shipping_services = []
        if product.allowed_shipping_services:
            for service in product.allowed_shipping_services:
                service_trans = None
                if service.translations:
                    service_trans = next((t for t in service.translations if t.lang == lang), None)
                    if not service_trans:
                        service_trans = next((t for t in service.translations if t.lang == "it"), None)
                
                if service_trans:
                    shipping_services.append({
                        "id": service.id,
                        "type": "shipping_service",
                        "title": service_trans.title,
                        "description": service_trans.simple_description or "",
                        "price": {
                            "amount": service.price_list or 0.0,
                        "currency": service.currency
                    }
                })
        
        warranties = []
        if product.allowed_warranties:
            for warranty in product.allowed_warranties:
                warranty_trans = None
                if warranty.translations:
                    warranty_trans = next((t for t in warranty.translations if t.lang == lang), None)
                    if not warranty_trans:
                        warranty_trans = next((t for t in warranty.translations if t.lang == "it"), None)
                
                if warranty_trans:
                    warranties.append({
                        "id": warranty.id,
                        "type": "warranty",
                        "title": warranty_trans.title,
                        "description": warranty_trans.simple_description or "",
                        "price": {
                            "amount": warranty.price_list or 0.0,
                            "currency": warranty.currency or "EUR"
                        },
                        "duration_months": warranty.duration_months or 0
                    })
        
        if shipping_services or warranties:
            options = {
                "shipping_services": shipping_services,
                "warranties": warranties
            }
    
    # Build related product IDs
    related_product_ids = []
    if product.related_products:
        related_product_ids = [rp.id for rp in product.related_products]
    
    # Build price - Get best discount based on priority
    discount_percentage = "0"
    if product.discounts:
        active_discounts = [d for d in product.discounts if d.is_active]
        if active_discounts:
            # Sort by priority (desc) then by discount_value (desc)
            # Higher priority wins, if equal priority then higher discount wins
            best_discount = max(active_discounts, 
                              key=lambda d: (d.priority, d.discount_value))
            
            if best_discount.discount_type == "percentage":
                discount_percentage = f"{int(best_discount.discount_value)}%"
            elif best_discount.discount_type == "amount":
                # Calculate percentage from amount
                if product.price_list and product.price_list > 0:
                    percentage = (best_discount.discount_value / product.price_list) * 100
                    discount_percentage = f"{int(percentage)}%"
    
    price_response = PriceResponse(
        list=product.price_list or 0.0,
        currency=product.currency or "EUR",
        discounts=discount_percentage
    )
    
    # Build stock
    stock_response = StockResponse(
        status=product.stock_status.value if product.stock_status else "out_of_stock",
        quantity=product.stock_quantity or 0
    )
    
    # Build final response
    response_data = ProductResponseFull(
        id=product.id,
        # product_type=product.product_type.value if product.product_type else "simple",  #  
        reference=product.reference or "",
        ean13=product.ean or "",
        is_active=product.is_active if product.is_active is not None else True,
        date_add=product.date_add,
        date_update=product.date_update,
        brand=brand,
        delivery=delivery,
        warranty=warranty,
        tax=tax,
        price=price_response,
        stock=stock_response,
        categories=categories,
        condition=product.condition.value if product.condition else "new",
        title=translation.title or "",
        sub_title=translation.sub_title or "",
        simple_description=strip_html_tags(translation.simple_description or ""),
        meta_description=translation.meta_description or "",
        images=images,
        features=features,
        attributes=attributes,
        related_product_ids=related_product_ids,
        variant_attributes=variant_attributes,
        variants=variants,
        options=options
    )
    
    return response_data


# ============= Endpoints =============

@router.post("/admin/products", response_model=dict, status_code=201)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new product (configurable, simple, service, or warranty)
    
    Requires X-API-Key header for authentication
    """
    try:
        # Check if reference already exists
        existing = crud_product.get_product_by_reference(db, product.reference)
        if existing:
            raise HTTPException(status_code=400, detail="Product with this reference already exists")
        
        # Create product
        db_product = crud_product.create_product(db, product)
        
        return {
            "message": "Product created successfully",
            "product_id": db_product.id,
            "reference": db_product.reference
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")


@router.get("/v1/products")
def get_all_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    product_type: Optional[str] = Query(None, regex="^(configurable|simple|service|warranty)$"),
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    active_only: bool = Query(True),
    search: Optional[str] = Query(None),
    lang: str = Query("it", regex="^(it|en|fr|de|ar)$"),
    db: Session = Depends(get_db)
):
    """
    Get all products with pagination and optional filters
    
    - **skip**: Number of products to skip (pagination) - default: 0
    - **limit**: Maximum number of products per page (1-500) - default: 50
    - **product_type**: Filter by product type (configurable, simple, service, warranty)
    - **category_id**: Filter by category ID
    - **brand_id**: Filter by brand ID
    - **active_only**: Show only active products - default: true
    - **search**: Search by product ID or reference
    - **lang**: Language code (it, en, fr, de, ar) - default: it
    
    Public endpoint - No API Key required
    """
    # Get total count
    total = crud_product.count_products(
        db=db,
        product_type=product_type,
        category_id=category_id,
        brand_id=brand_id,
        active_only=active_only,
        search=search
    )
    
    # Get products for current page
    products = crud_product.get_products(
        db=db,
        skip=skip,
        limit=limit,
        product_type=product_type,
        category_id=category_id,
        brand_id=brand_id,
        active_only=active_only,
        search=search
    )
    
    # Build simple product list
    products_list = []
    for product in products:
        # Get translation for requested language
        translation = next((t for t in product.translations if t.lang == lang), None)
        if not translation:
            translation = next((t for t in product.translations if t.lang == "it"), product.translations[0] if product.translations else None)
        
        if translation:
            # Get first image
            first_image = None
            if product.images:
                img = product.images[0]
                alt_text = next((alt.alt_text for alt in img.alt_texts if alt.lang == lang), "")
                first_image = img.url
            
            # Build tax
            tax_data = None
            if product.tax_class:
                tax_data = {
                    "id": product.tax_class.id,
                    "name": product.tax_class.name,
                    "rate": product.tax_class.rate,
                    "included_in_price": product.tax_included_in_price
                }
            
            # Calculate discount - Get best discount based on priority
            discount_percentage = "0"
            if product.discounts:
                active_discounts = [d for d in product.discounts if d.is_active]
                if active_discounts:
                    # Sort by priority (desc) then by discount_value (desc)
                    # Higher priority wins, if equal priority then higher discount wins
                    best_discount = max(active_discounts, 
                                      key=lambda d: (d.priority, d.discount_value))
                    
                    if best_discount.discount_type == "percentage":
                        discount_percentage = f"{int(best_discount.discount_value)}%"
                    elif best_discount.discount_type == "amount" and product.price_list and product.price_list > 0:
                        percentage = (best_discount.discount_value / product.price_list) * 100
                        discount_percentage = f"{int(percentage)}%"
            
            # Build features
            features_list = []
            if product.features:
                for feat in product.features:
                    feat_trans = next((t for t in feat.translations if t.lang == lang), None)
                    if not feat_trans:
                        feat_trans = next((t for t in feat.translations if t.lang == "it"), None)
                    if feat_trans:
                        features_list.append({
                            "name": feat_trans.name,
                            "value": feat_trans.value
                        })
            
            # Build attributes
            attributes_list = []
            if product.attributes:
                for attr in product.attributes:
                    attr_trans = next((t for t in attr.translations if t.lang == lang), None)
                    if not attr_trans:
                        attr_trans = next((t for t in attr.translations if t.lang == "it"), None)
                    if attr_trans:
                        attributes_list.append({
                            "code": attr.code,
                            "name": attr_trans.name,
                            "value": attr_trans.value
                        })
            
            products_list.append({
                "id": product.id,
                "reference": product.reference,
                "product_type": product.product_type.value,
                "title": translation.title,
                "simple_description": strip_html_tags(translation.simple_description or ""),
                "image": first_image,
                "is_active": product.is_active,
                "date_add": product.date_add,
                "tax": tax_data,
                "price": {
                    "list": product.price_list or 0.0,
                    "currency": product.currency or "EUR",
                    "discounts": discount_percentage
                },
                "stock": {
                    "status": product.stock_status.value,
                    "quantity": product.stock_quantity or 0
                },
                "features": features_list,
                "attributes": attributes_list
            })
    
    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit  # Ceiling division
    current_page = (skip // limit) + 1
    
    return {
        "data": products_list,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "page": current_page,
            "total_pages": total_pages,
            "has_next": skip + limit < total,
            "has_prev": skip > 0,
            "lang": lang
        }
    }


@router.get("/v1/products/recent")
def get_recent_products(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get recently added products (exactly 15 products)
    Sorted by date_add (newest first)
    
    Returns compact JSON:
    - id
    - title
    - reference
    - price
    - image
    - category
    - date_add
    """
    products = crud_product.get_recent_products(db, limit=15)
    
    return {
        "success": True,
        "total": len(products),
        "products": products
    }


@router.get("/v1/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    lang: str = Query("it", regex="^(it|en|fr|de|ar)$"),
    include: Optional[str] = Query(None, regex="^options$"),
    db: Session = Depends(get_db)
):
    """
    Get product details by ID
    
    - **product_id**: Product ID
    - **lang**: Language code (it, en, fr, de, ar) - default: it
    - **include**: Include additional data (options) - optional
    
    Public endpoint - No API Key required
    """
    product = crud_product.get_product(db, product_id, lang)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if not product.is_active:
        raise HTTPException(status_code=404, detail="Product not available")
    
    # Build response
    product_data = build_product_response(product, lang)
    
    return ProductResponse(
        data=product_data,
        meta={
            "requested_lang": lang,
            "resolved_lang": lang
        }
    )


@router.put("/admin/products/{product_id}")
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update a product by ID
    
    - **product_id**: Product ID to update
    - **product**: Product update data (all fields optional)
    
    You can update any combination of:
    - Basic info (is_active, brand_id, condition)
    - Tax and pricing (tax_class_id, price_list, currency)
    - Stock (stock_status, stock_quantity)
    - Categories (replace all)
    - Images (replace all)
    - Features (replace all)
    - Attributes (replace all)
    - Translations (replace all)
    - Variants (replace all - configurable products only)
    - Related products (replace all)
    - Service links (replace all)
    
    Requires X-API-Key header for authentication
    """
    try:
        # Update product
        db_product = crud_product.update_product(db, product_id, product)
        
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            "message": "Product updated successfully",
            "product_id": db_product.id,
            "reference": db_product.reference,
            "date_update": db_product.date_update,
            "stock_quantity": db_product.stock_quantity  # إضافة للتأكد
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Error updating product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")


@router.delete("/admin/products/{product_id}", status_code=200)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete a product by ID permanently
    
    - **product_id**: Product ID to delete
    
    Note: This is a hard delete. The product will be permanently removed
    from the database and cannot be recovered.
    
    Requires X-API-Key header for authentication
    """
    success = crud_product.delete_product(db, product_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "message": "Product deleted permanently",
        "product_id": product_id,
        "note": "Hard delete - product removed from database"
    }


@router.get("/v1/products/{product_id}/stock")
def get_product_stock(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get product stock information by ID
    
    - **product_id**: Product ID
    
    Returns only stock-related information for the product
    
    Requires X-API-Key header for authentication
    """
    product = crud_product.get_product(db, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "product_id": product.id,
        "reference": product.reference,
        "stock_status": product.stock_status.value,
        "stock_quantity": product.stock_quantity,
        "is_active": product.is_active
    }


    
    return {
        "message": "Product deleted successfully",
        "product_id": product_id,
        "note": "Soft delete - product marked as inactive"
    }


@router.put("/admin/products/{product_id}/stock", response_model=StockUpdateResponse)
def update_product_stock(
    product_id: int,
    stock_data: StockUpdateInput,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update product stock
    
    Requires X-API-Key header for authentication
    """
    product = crud_product.update_product_stock(db, product_id, stock_data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return StockUpdateResponse(
        id=product.id,
        reference=product.reference,
        ean=product.ean,
        stock_status=product.stock_status.value,
        stock_quantity=product.stock_quantity,
        updated_at=product.date_update or product.created_at
    )


@router.put("/admin/variants/{variant_id}/stock", response_model=dict)
def update_variant_stock(
    variant_id: int,
    stock_data: StockUpdateInput,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update variant stock
    
    Requires X-API-Key header for authentication
    """
    variant = crud_product.update_variant_stock(db, variant_id, stock_data)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    return {
        "id": variant.id,
        "reference": variant.reference,
        "stock_status": variant.stock_status.value,
        "stock_quantity": variant.stock_quantity,
        "updated_at": variant.updated_at
    }


@router.post("/admin/products/process-duplicates-and-categorize")
def process_duplicates_and_categorize(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Process all products:
    1. Find and remove duplicates (by EAN, Reference, Name)
    2. Classify products (electronics vs furniture)
    3. Update electronics with new categories
    4. Return detailed report
    
    Requires X-API-Key header for authentication
    """
    
    report = {
        'total_products_initial': 0,
        'duplicates_found': 0,
        'duplicates_deleted': 0,
        'total_products_final': 0,
        'electronics_count': 0,
        'furniture_count': 0,
        'electronics_updated': 0,
        'errors': []
    }
    
    try:
        # Step 1: Get all products
        all_products = db.query(Product).all()
        report['total_products_initial'] = len(all_products)
        
        # Step 2: Find duplicates
        by_ean = defaultdict(list)
        by_ref = defaultdict(list)
        by_name = defaultdict(list)
        
        for product in all_products:
            if product.ean:
                by_ean[product.ean.strip()].append(product)
            if product.reference:
                by_ref[product.reference.strip()].append(product)
            
            # Get Italian translation for name comparison
            translation = next((t for t in product.translations if t.lang == "it"), None)
            if translation and translation.title:
                by_name[translation.title.strip().lower()].append(product)
        
        # Find duplicate groups
        duplicate_groups = []
        seen_ids = set()
        
        for ean, products in by_ean.items():
            if len(products) > 1:
                ids = tuple(sorted(p.id for p in products))
                if ids not in seen_ids:
                    duplicate_groups.append(products)
                    seen_ids.add(ids)
        
        for ref, products in by_ref.items():
            if len(products) > 1:
                ids = tuple(sorted(p.id for p in products))
                if ids not in seen_ids:
                    duplicate_groups.append(products)
                    seen_ids.add(ids)
        
        for name, products in by_name.items():
            if len(products) > 1:
                ids = tuple(sorted(p.id for p in products))
                if ids not in seen_ids:
                    duplicate_groups.append(products)
                    seen_ids.add(ids)
        
        report['duplicates_found'] = len(duplicate_groups)
        
        # Step 3: Remove duplicates (keep best one)
        def score_product(p):
            score = 0
            score += len(p.images) * 10
            translation = next((t for t in p.translations if t.lang == "it"), None)
            if translation:
                score += len(translation.simple_description or '') / 100
            score += len(p.features) * 5
            score += len(p.attributes) * 5
            return score
        
        deleted_ids = []
        for group in duplicate_groups:
            # Keep the best, delete others
            best = max(group, key=score_product)
            to_delete = [p for p in group if p.id != best.id]
            
            for product in to_delete:
                try:
                    db.delete(product)
                    deleted_ids.append(product.id)
                except Exception as e:
                    report['errors'].append(f"Failed to delete product {product.id}: {str(e)}")
        
        db.commit()
        report['duplicates_deleted'] = len(deleted_ids)
        
        # Step 4: Re-query products after deletion
        all_products = db.query(Product).all()
        report['total_products_final'] = len(all_products)
        
        # Step 5: Classify products
        electronics_keywords = [
            'lavatrice', 'frigorifero', 'forno', 'microonde', 'lavastoviglie',
            'congelatore', 'condizionatore', 'tv', 'televisore', 'monitor',
            'computer', 'notebook', 'tablet', 'smartphone', 'cellulare',
            'fotocamera', 'stampante', 'scanner', 'router', 'modem',
            'cuffie', 'altoparlante', 'soundbar', 'lettore', 'decoder',
            'asciugatrice', 'aspirapolvere', 'ventilatore', 'stufa',
            'climatizzatore', 'deumidificatore', 'purificatore', 'cappa'
        ]
        
        furniture_keywords = [
            'sedia', 'tavolo', 'letto', 'armadio', 'mobile', 'porta',
            'divano', 'poltrona', 'scaffale', 'libreria', 'consolle',
            'comodino', 'cassettiera', 'guardaroba', 'parete', 'soggiorno',
            'pensile', 'anta', 'guanciale', 'materasso', 'rete'
        ]
        
        electronics = []
        furniture = []
        
        for product in all_products:
            translation = next((t for t in product.translations if t.lang == "it"), None)
            if not translation:
                continue
            
            text = f"{translation.title or ''} {translation.simple_description or ''}".lower()
            
            is_electronics = any(kw in text for kw in electronics_keywords)
            is_furniture = any(kw in text for kw in furniture_keywords)
            
            if is_electronics and not is_furniture:
                electronics.append(product)
            elif is_furniture:
                furniture.append(product)
        
        report['electronics_count'] = len(electronics)
        report['furniture_count'] = len(furniture)
        
        # Step 6: Get new categories
        new_categories = db.query(Category).filter(Category.is_active == True).all()
        
        # Create mapping from old category names to new category IDs
        category_mapping = {}
        for new_cat in new_categories:
            cat_name_lower = new_cat.name.lower()
            category_mapping[cat_name_lower] = new_cat.id
        
        # Step 7: Update electronics only
        updated_count = 0
        for product in electronics:
            try:
                old_categories = product.categories
                if not old_categories:
                    continue
                
                # Try to map old category to new one
                new_cat_ids = []
                for old_cat in old_categories:
                    old_name_lower = old_cat.name.lower()
                    
                    # Try exact match
                    if old_name_lower in category_mapping:
                        new_cat_ids.append(category_mapping[old_name_lower])
                    else:
                        # Try partial match
                        for new_name, new_id in category_mapping.items():
                            if old_name_lower in new_name or new_name in old_name_lower:
                                new_cat_ids.append(new_id)
                                break
                
                if new_cat_ids:
                    # Clear old categories and add new ones
                    product.categories.clear()
                    for cat_id in new_cat_ids:
                        new_cat = db.query(Category).get(cat_id)
                        if new_cat:
                            product.categories.append(new_cat)
                    updated_count += 1
                    
            except Exception as e:
                report['errors'].append(f"Failed to update product {product.id}: {str(e)}")
        
        db.commit()
        report['electronics_updated'] = updated_count
        
        return {
            "success": True,
            "message": "Processing completed",
            "report": report
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/admin/products/search-by-title")
def search_products_by_title(
    title: str = Query(..., min_length=1, description="Search term for product title"),
    lang: str = Query("it", regex="^(it|en|fr|de|ar)$"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Search products by title (case-insensitive partial match)
    
    - **title**: Search term
    - **lang**: Language code for translations - default: it
    - **limit**: Maximum results - default: 20
    
    Requires X-API-Key header for authentication
    """
    
    # Search in translations
    translations = db.query(ProductTranslation).filter(
        ProductTranslation.lang == lang,
        ProductTranslation.title.ilike(f'%{title}%')
    ).limit(limit).all()
    
    results = []
    for trans in translations:
        product = db.query(Product).filter(Product.id == trans.product_id).first()
        if product:
            results.append({
                "id": product.id,
                "reference": product.reference,
                "ean": product.ean,
                "title": trans.title,
                "sub_title": trans.sub_title,
                "is_active": product.is_active,
                "stock_quantity": product.stock_quantity,
                "stock_status": product.stock_status.value if product.stock_status else None,
                "price_list": product.price_list,
                "currency": product.currency,
                "brand_id": product.brand_id,
                "product_type": product.product_type.value if product.product_type else None
            })
    
    return {
        "total": len(results),
        "search_term": title,
        "lang": lang,
        "results": results
    }


@router.get("/v1/products/search")
def quick_search_products(
    q: str = Query(..., min_length=1, description="Search term (ID, title, or reference)"),
    lang: str = Query("it", regex="^(it|en|fr|de|ar)$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Quick search for products by ID, title, or reference
    
    - **q**: Search term (product ID, title, or reference)
    - **lang**: Language code for translations - default: it
    - **limit**: Maximum results - default: 10
    
    Public endpoint - No API Key required
    """
    
    results = []
    search_type = None
    
    # Check if search term is a number (ID search)
    if q.isdigit():
        search_type = "id"
        product = db.query(Product).filter(Product.id == int(q)).first()
        if product:
            translation = next((t for t in product.translations if t.lang == lang), None)
            if not translation and product.translations:
                translation = product.translations[0]
            
            if translation:
                results.append({
                    "id": product.id,
                    "reference": product.reference,
                    "ean": product.ean,
                    "title": translation.title,
                    "sub_title": translation.sub_title,
                    "is_active": product.is_active,
                    "stock_quantity": product.stock_quantity,
                    "stock_status": product.stock_status.value if product.stock_status else None,
                    "price_list": product.price_list,
                    "currency": product.currency,
                    "brand_id": product.brand_id,
                    "product_type": product.product_type.value if product.product_type else None
                })
    else:
        # Search by title
        search_type = "title_or_reference"
        translations = db.query(ProductTranslation).filter(
            ProductTranslation.lang == lang,
            ProductTranslation.title.ilike(f'%{q}%')
        ).limit(limit).all()
        
        for trans in translations:
            product = db.query(Product).filter(Product.id == trans.product_id).first()
            if product:
                results.append({
                    "id": product.id,
                    "reference": product.reference,
                    "ean": product.ean,
                    "title": trans.title,
                    "sub_title": trans.sub_title,
                    "is_active": product.is_active,
                    "stock_quantity": product.stock_quantity,
                    "stock_status": product.stock_status.value if product.stock_status else None,
                    "price_list": product.price_list,
                    "currency": product.currency,
                    "brand_id": product.brand_id,
                    "product_type": product.product_type.value if product.product_type else None
                })
        
        # If no results from title search, search by reference
        if not results:
            products = db.query(Product).filter(
                Product.reference.ilike(f'%{q}%')
            ).limit(limit).all()
            
            for product in products:
                translation = next((t for t in product.translations if t.lang == lang), None)
                if not translation and product.translations:
                    translation = product.translations[0]
                
                if translation:
                    results.append({
                        "id": product.id,
                        "reference": product.reference,
                        "ean": product.ean,
                        "title": translation.title,
                        "sub_title": translation.sub_title,
                        "is_active": product.is_active,
                        "stock_quantity": product.stock_quantity,
                        "stock_status": product.stock_status.value if product.stock_status else None,
                        "price_list": product.price_list,
                        "currency": product.currency,
                        "brand_id": product.brand_id,
                        "product_type": product.product_type.value if product.product_type else None
                    })
    
    return {
        "total": len(results),
        "search_term": q,
        "search_type": search_type,
        "lang": lang,
        "results": results
    }

