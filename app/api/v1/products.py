from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
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
from app.models.product import Product


router = APIRouter()


# ============= Helper Functions =============

def verify_api_key(x_api_key: str = Header(...)):
    """Verify API Key from header"""
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


def build_product_response(product: Product, lang: str) -> Dict[str, Any]:
    """Build product response based on requested language"""
    
    # Get translation for requested language
    translation = next((t for t in product.translations if t.lang == lang), None)
    if not translation:
        # Fallback to Italian
        translation = next((t for t in product.translations if t.lang == "it"), product.translations[0] if product.translations else None)
    
    if not translation:
        raise HTTPException(status_code=404, detail="Product translation not found")
    
    # Build images with language-specific alt text
    images = []
    for img in product.images:
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
    for feat in product.features:
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
    for attr in product.attributes:
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
    for var_attr in product.variant_attributes:
        var_attr_trans = next((t for t in var_attr.translations if t.lang == lang), None)
        if not var_attr_trans:
            var_attr_trans = next((t for t in var_attr.translations if t.lang == "it"), None)
        
        if var_attr_trans:
            # Extract unique options from variants
            options = []
            seen_values = set()
            for variant in product.variants:
                if variant.is_active and var_attr.code in variant.attributes:
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
    for variant in product.variants:
        if variant.is_active:
            # Build variant images
            variant_images = []
            for img in variant.images:
                alt_text = next((alt.alt_text for alt in img.alt_texts if alt.lang == lang), "")
                if not alt_text:
                    alt_text = next((alt.alt_text for alt in img.alt_texts if alt.lang == "it"), "")
                
                variant_images.append(ProductImageResponse(
                    url=img.url,
                    position=img.position,
                    alt=alt_text
                ))
            
            # Calculate discounts
            active_discounts = [d for d in variant.discounts if d.is_active]
            discount_data = []
            for disc in active_discounts:
                discount_data.append({
                    "type": disc.discount_type,
                    "value": disc.discount_value,
                    "start_date": disc.start_date,
                    "end_date": disc.end_date
                })
            
            variants.append(ProductVariantResponse(
                id=variant.id,
                reference=variant.reference,
                ean13=variant.ean13,
                is_active=variant.is_active,
                attributes=variant.attributes,
                price=PriceResponse(
                    list=variant.price_list,
                    currency=variant.currency,
                    discounts=discount_data
                ),
                stock=StockResponse(
                    status=variant.stock_status.value,
                    quantity=variant.stock_quantity
                ),
                images=variant_images
            ))
    
    # Build categories with translations
    categories = []
    for cat in product.categories:
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
    
    # Build tax
    tax = TaxClassSimple(
        id=product.tax_class.id,
        name=product.tax_class.name,
        rate=product.tax_class.rate,
        included_in_price=product.tax_included_in_price
    )
    
    # Build options (shipping services and warranties)
    options = None
    if product.product_type.value == "configurable":
        shipping_services = []
        for service in product.allowed_shipping_services:
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
                        "amount": service.price_list,
                        "currency": service.currency
                    }
                })
        
        warranties = []
        for warranty in product.allowed_warranties:
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
                        "amount": warranty.price_list,
                        "currency": warranty.currency
                    },
                    "duration_months": warranty.duration_months
                })
        
        if shipping_services or warranties:
            options = {
                "shipping_services": shipping_services,
                "warranties": warranties
            }
    
    # Build related product IDs
    related_product_ids = [rp.id for rp in product.related_products]
    
    # Build final response
    response_data = ProductResponseFull(
        id=product.id,
        product_type=product.product_type.value,
        reference=product.reference,
        ean13=product.ean13,
        is_active=product.is_active,
        date_add=product.date_add,
        date_update=product.date_update,
        brand=brand,
        tax=tax,
        categories=categories,
        condition=product.condition.value,
        title=translation.title,
        sub_title=translation.sub_title,
        simple_description=translation.simple_description,
        meta_description=translation.meta_description,
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
    limit: int = Query(50, ge=1, le=100),
    product_type: Optional[str] = Query(None, regex="^(configurable|simple|service|warranty)$"),
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    active_only: bool = Query(True),
    lang: str = Query("it", regex="^(it|en|fr|de|ar)$"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all products with optional filters
    
    - **skip**: Number of products to skip (pagination) - default: 0
    - **limit**: Maximum number of products to return (1-100) - default: 50
    - **product_type**: Filter by product type (configurable, simple, service, warranty)
    - **category_id**: Filter by category ID
    - **brand_id**: Filter by brand ID
    - **active_only**: Show only active products - default: true
    - **lang**: Language code (it, en, fr, de, ar) - default: it
    
    Requires X-API-Key header for authentication
    """
    products = crud_product.get_products(
        db=db,
        skip=skip,
        limit=limit,
        product_type=product_type,
        category_id=category_id,
        brand_id=brand_id,
        active_only=active_only
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
            
            products_list.append({
                "id": product.id,
                "reference": product.reference,
                "product_type": product.product_type.value,
                "title": translation.title,
                "sub_title": translation.sub_title,
                "price": product.price_list,
                "currency": product.currency,
                "image": first_image,
                "stock_status": product.stock_status.value,
                "is_active": product.is_active,
                "brand_id": product.brand_id,
                "date_add": product.date_add
            })
    
    return {
        "data": products_list,
        "meta": {
            "total": len(products_list),
            "skip": skip,
            "limit": limit,
            "lang": lang
        }
    }


@router.get("/v1/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    lang: str = Query("it", regex="^(it|en|fr|de|ar)$"),
    include: Optional[str] = Query(None, regex="^options$"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get product details by ID
    
    - **product_id**: Product ID
    - **lang**: Language code (it, en, fr, de, ar) - default: it
    - **include**: Include additional data (options) - optional
    
    Requires X-API-Key header for authentication
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
            "date_update": db_product.date_update
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")


@router.delete("/admin/products/{product_id}", status_code=200)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete a product by ID (soft delete - sets is_active to False)
    
    - **product_id**: Product ID to delete
    
    Note: This is a soft delete. The product will be marked as inactive
    but will remain in the database for historical records.
    
    Requires X-API-Key header for authentication
    """
    success = crud_product.delete_product(db, product_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "message": "Product deleted successfully",
        "product_id": product_id,
        "note": "Soft delete - product marked as inactive"
    }


@router.get("/v1/products/{product_id}/stock")
def get_product_stock(
    product_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
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
