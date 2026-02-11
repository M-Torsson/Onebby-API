# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from app.models.discount_campaign import DiscountCampaign, TargetTypeEnum
from app.models.product import Product, ProductDiscount, ProductTranslation, ProductImage
from app.models.category import Category
from app.schemas.discount_campaign import DiscountCampaignCreate, DiscountCampaignUpdate


# ============= Campaign CRUD =============

def create_campaign(db: Session, campaign: DiscountCampaignCreate) -> DiscountCampaign:
    """Create a new discount campaign"""
    db_campaign = DiscountCampaign(
        name=campaign.name,
        description=campaign.description,
        discount_type=campaign.discount_type,
        discount_value=campaign.discount_value,
        target_type=campaign.target_type,
        target_ids=campaign.target_ids,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        is_active=campaign.is_active
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


def get_campaign(db: Session, campaign_id: int) -> Optional[DiscountCampaign]:
    """Get campaign by ID"""
    return db.query(DiscountCampaign).filter(DiscountCampaign.id == campaign_id).first()


def update_expired_campaigns(db: Session) -> dict:
    """
    Automatically update is_active to False for campaigns that have passed end_date
    Returns count of updated campaigns
    """
    now = datetime.now()
    
    # Find active campaigns that have expired
    expired_campaigns = db.query(DiscountCampaign).filter(
        DiscountCampaign.is_active == True,
        DiscountCampaign.end_date.isnot(None),
        DiscountCampaign.end_date < now
    ).all()
    
    updated_count = 0
    
    for campaign in expired_campaigns:
        # Update campaign status
        campaign.is_active = False
        
        # Update all product discounts for this campaign
        db.query(ProductDiscount).filter(
            ProductDiscount.campaign_id == campaign.id
        ).update({"is_active": False}, synchronize_session=False)
        
        updated_count += 1
    
    if updated_count > 0:
        db.commit()
    
    return {
        "success": True,
        "updated_campaigns": updated_count
    }


def get_campaigns(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    is_active: Optional[bool] = None
) -> List[DiscountCampaign]:
    """Get all campaigns with pagination"""
    # Auto-update expired campaigns
    update_expired_campaigns(db)
    
    query = db.query(DiscountCampaign)
    
    if is_active is not None:
        query = query.filter(DiscountCampaign.is_active == is_active)
    
    return query.order_by(DiscountCampaign.created_at.desc()).offset(skip).limit(limit).all()


def count_campaigns(db: Session, is_active: Optional[bool] = None) -> int:
    """Count campaigns"""
    query = db.query(DiscountCampaign)
    
    if is_active is not None:
        query = query.filter(DiscountCampaign.is_active == is_active)
    
    return query.count()


def update_campaign(
    db: Session,
    campaign_id: int,
    campaign_update: DiscountCampaignUpdate
) -> Optional[DiscountCampaign]:
    """Update a campaign"""
    db_campaign = get_campaign(db, campaign_id)
    if not db_campaign:
        return None
    
    update_data = campaign_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_campaign, field, value)
    
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


def delete_campaign(db: Session, campaign_id: int) -> bool:
    """Delete a campaign and all its applied discounts"""
    db_campaign = get_campaign(db, campaign_id)
    if not db_campaign:
        return False
    
    # First, delete all product discounts linked to this campaign
    db.query(ProductDiscount).filter(
        ProductDiscount.campaign_id == campaign_id
    ).delete(synchronize_session=False)
    
    # Then delete the campaign itself
    db.delete(db_campaign)
    db.commit()
    return True


# ============= Auto-apply Campaigns to New Products =============

def apply_active_campaigns_to_product(db: Session, product_id: int, category_ids: List[int] = None) -> dict:
    """
    Automatically apply active campaigns to a product based on its categories, brand, or "ALL" campaigns
    This should be called when creating or updating a product to ensure discounts are applied
    
    Args:
        db: Database session
        product_id: Product ID to apply campaigns to
        category_ids: Optional list of category IDs (if not provided, will fetch from product)
    
    Returns:
        Dict with success status and number of campaigns applied
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"success": False, "message": "Product not found", "campaigns_applied": 0}
    
    if not product.is_active:
        return {"success": True, "message": "Product is inactive, skipping campaigns", "campaigns_applied": 0}
    
    # Get category IDs if not provided
    if category_ids is None:
        category_ids = [cat.id for cat in product.categories]
    
    # Find all active campaigns that match this product
    active_campaigns = db.query(DiscountCampaign).filter(
        DiscountCampaign.is_active == True
    ).all()
    
    campaigns_applied = 0
    
    for campaign in active_campaigns:
        should_apply = False
        
        # Check if campaign applies to this product
        if campaign.target_type == TargetTypeEnum.ALL:
            should_apply = True
        
        elif campaign.target_type == TargetTypeEnum.PRODUCTS:
            if campaign.target_ids and product_id in campaign.target_ids:
                should_apply = True
        
        elif campaign.target_type == TargetTypeEnum.CATEGORY:
            if campaign.target_ids and len(campaign.target_ids) > 0:
                campaign_category_id = campaign.target_ids[0]
                
                # Get all subcategories recursively
                def get_all_subcategory_ids(cat_id, db_session):
                    """Recursively get all subcategory IDs"""
                    from app.models.category import Category
                    category_ids_list = [cat_id]
                    children = db_session.query(Category).filter(Category.parent_id == cat_id).all()
                    for child in children:
                        category_ids_list.extend(get_all_subcategory_ids(child.id, db_session))
                    return category_ids_list
                
                all_campaign_category_ids = get_all_subcategory_ids(campaign_category_id, db)
                
                # Check if product is in any of the campaign categories
                if any(cat_id in all_campaign_category_ids for cat_id in category_ids):
                    should_apply = True
        
        elif campaign.target_type == TargetTypeEnum.BRAND:
            if campaign.target_ids and len(campaign.target_ids) > 0:
                if product.brand_id == campaign.target_ids[0]:
                    should_apply = True
        
        # Apply the campaign if conditions are met
        if should_apply:
            # Check if discount already exists for this campaign
            existing_discount = db.query(ProductDiscount).filter(
                ProductDiscount.product_id == product_id,
                ProductDiscount.campaign_id == campaign.id,
                ProductDiscount.is_active == True
            ).first()
            
            if existing_discount:
                # Update existing discount
                existing_discount.discount_type = campaign.discount_type.value
                existing_discount.discount_value = campaign.discount_value
                existing_discount.priority = campaign.priority
                existing_discount.start_date = campaign.start_date
                existing_discount.end_date = campaign.end_date
            else:
                # Create new discount
                new_discount = ProductDiscount(
                    product_id=product_id,
                    discount_type=campaign.discount_type.value,
                    discount_value=campaign.discount_value,
                    campaign_id=campaign.id,
                    priority=campaign.priority,
                    start_date=campaign.start_date,
                    end_date=campaign.end_date,
                    is_active=True
                )
                db.add(new_discount)
            
            campaigns_applied += 1
    
    if campaigns_applied > 0:
        db.commit()
    
    return {
        "success": True,
        "message": f"Applied {campaigns_applied} active campaign(s) to product",
        "campaigns_applied": campaigns_applied
    }


# ============= Apply Campaign to Products =============

def apply_campaign_to_products(db: Session, campaign_id: int) -> dict:
    """Apply discount campaign to products based on target_type"""
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        return {"success": False, "message": "Campaign not found"}
    
    # Get target products
    products = []
    
    if campaign.target_type == TargetTypeEnum.ALL:
        # All products
        products = db.query(Product).filter(Product.is_active == True).all()
    
    elif campaign.target_type == TargetTypeEnum.PRODUCTS:
        # Specific products
        if not campaign.target_ids:
            return {"success": False, "message": "No target products specified"}
        products = db.query(Product).filter(
            Product.id.in_(campaign.target_ids),
            Product.is_active == True
        ).all()
    
    elif campaign.target_type == TargetTypeEnum.CATEGORY:
        # Products in category (including all subcategories)
        if not campaign.target_ids or len(campaign.target_ids) == 0:
            return {"success": False, "message": "No target category specified"}
        
        category_id = campaign.target_ids[0]
        
        # Get all subcategories recursively
        def get_all_subcategory_ids(cat_id, db_session):
            """Recursively get all subcategory IDs"""
            from app.models.category import Category
            category_ids = [cat_id]
            children = db_session.query(Category).filter(Category.parent_id == cat_id).all()
            for child in children:
                category_ids.extend(get_all_subcategory_ids(child.id, db_session))
            return category_ids
        
        all_category_ids = get_all_subcategory_ids(category_id, db)
        
        # Get products from all categories (parent + all subcategories)
        products = db.query(Product).join(Product.categories).filter(
            Product.categories.any(Category.id.in_(all_category_ids)),
            Product.is_active == True
        ).all()
    
    elif campaign.target_type == TargetTypeEnum.BRAND:
        # Products of brand
        if not campaign.target_ids or len(campaign.target_ids) == 0:
            return {"success": False, "message": "No target brand specified"}
        
        brand_id = campaign.target_ids[0]
        products = db.query(Product).filter(
            Product.brand_id == brand_id,
            Product.is_active == True
        ).all()
    
    if not products:
        return {"success": False, "message": "No products found matching criteria"}
    
    # Apply discount to products with priority handling
    products_updated = 0
    
    for product in products:
        # Check if discount already exists for this specific campaign
        existing_campaign_discount = db.query(ProductDiscount).filter(
            ProductDiscount.product_id == product.id,
            ProductDiscount.campaign_id == campaign.id,
            ProductDiscount.is_active == True
        ).first()
        
        if existing_campaign_discount:
            # Update existing discount from same campaign
            existing_campaign_discount.discount_type = campaign.discount_type.value
            existing_campaign_discount.discount_value = campaign.discount_value
            existing_campaign_discount.priority = campaign.priority
            existing_campaign_discount.start_date = campaign.start_date
            existing_campaign_discount.end_date = campaign.end_date
        else:
            # Create new discount (will coexist with other campaigns)
            new_discount = ProductDiscount(
                product_id=product.id,
                discount_type=campaign.discount_type.value,
                discount_value=campaign.discount_value,
                campaign_id=campaign.id,
                priority=campaign.priority,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                is_active=campaign.is_active
            )
            db.add(new_discount)
        
        products_updated += 1
    
    db.commit()
    
    return {
        "success": True,
        "products_updated": products_updated,
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "target_type": campaign.target_type.value
    }


def remove_campaign_discounts(db: Session, campaign_id: int) -> dict:
    """Remove all discounts applied by a campaign"""
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        return {"success": False, "message": "Campaign not found"}
    
    # Get affected products
    products = []
    
    if campaign.target_type == TargetTypeEnum.ALL:
        products = db.query(Product).all()
    elif campaign.target_type == TargetTypeEnum.PRODUCTS:
        products = db.query(Product).filter(Product.id.in_(campaign.target_ids)).all()
    elif campaign.target_type == TargetTypeEnum.CATEGORY:
        category_id = campaign.target_ids[0]
        
        # Get all subcategories recursively
        def get_all_subcategory_ids(cat_id, db_session):
            """Recursively get all subcategory IDs"""
            from app.models.category import Category
            category_ids = [cat_id]
            children = db_session.query(Category).filter(Category.parent_id == cat_id).all()
            for child in children:
                category_ids.extend(get_all_subcategory_ids(child.id, db_session))
            return category_ids
        
        all_category_ids = get_all_subcategory_ids(category_id, db)
        
        # Get products from all categories (parent + all subcategories)
        products = db.query(Product).join(Product.categories).filter(
            Product.categories.any(Category.id.in_(all_category_ids))
        ).all()
    elif campaign.target_type == TargetTypeEnum.BRAND:
        brand_id = campaign.target_ids[0]
        products = db.query(Product).filter(Product.brand_id == brand_id).all()
    
    # Remove discounts
    products_updated = 0
    for product in products:
        discounts = db.query(ProductDiscount).filter(
            ProductDiscount.product_id == product.id
        ).all()
        
        for discount in discounts:
            db.delete(discount)
        
        if discounts:
            products_updated += 1
    
    db.commit()
    
    return {
        "success": True,
        "products_updated": products_updated,
        "message": f"Removed discounts from {products_updated} products"
    }


# ============= Get Products with Discount =============

def get_campaign_products(
    db: Session,
    campaign_id: int,
    skip: int = 0,
    limit: int = 50,
    sort_by_discount: bool = True
) -> dict:
    """
    Get all products that have discount from this campaign
    
    Args:
        campaign_id: Campaign ID
        skip: Number of products to skip (pagination)
        limit: Max products to return
        sort_by_discount: Sort by discount value (highest first)
    
    Returns:
        Dict with products and campaign info
    """
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        return {"success": False, "message": "Campaign not found"}
    
    # Get products with discount from this campaign
    from sqlalchemy.orm import joinedload
    
    products_query = db.query(Product).join(ProductDiscount).filter(
        ProductDiscount.campaign_id == campaign_id,
        ProductDiscount.is_active == True,
        Product.is_active == True
    ).options(
        joinedload(Product.categories),
        joinedload(Product.translations)
    )
    
    # Count total before pagination
    total_products = products_query.count()
    
    # Apply pagination
    products_query = products_query.offset(skip).limit(limit)
    
    products = products_query.all()
    
    # Build response with discount calculations
    products_data = []
    
    for product in products:
        # Get the discount for this campaign
        discount = db.query(ProductDiscount).filter(
            ProductDiscount.product_id == product.id,
            ProductDiscount.campaign_id == campaign_id
        ).first()
        
        if not discount:
            continue
        
        # Calculate discount
        price_list = product.price_list or 0
        
        if discount.discount_type == "percentage":
            discount_amount = price_list * (discount.discount_value / 100)
            discount_percentage = discount.discount_value
        else:  # fixed_amount
            discount_amount = discount.discount_value
            discount_percentage = (discount_amount / price_list * 100) if price_list > 0 else 0
        
        final_price = max(0, price_list - discount_amount)
        
        # Get product title (prefer Italian)
        title = "Untitled"
        it_translation = next((t for t in product.translations if t.lang == "it"), None)
        if it_translation:
            title = it_translation.title
        elif product.translations:
            title = product.translations[0].title
        
        # Get first image
        image = None
        if product.images:
            image = product.images[0].url
        
        # Get category IDs
        category_ids = [cat.id for cat in product.categories]
        
        products_data.append({
            "id": product.id,
            "reference": product.reference,
            "ean": product.ean,
            "title": title,
            "image": image,
            "price_list": price_list,
            "currency": product.currency or "EUR",
            "discount_type": discount.discount_type,
            "discount_value": discount.discount_value,
            "discount_percentage": round(discount_percentage, 2),
            "discount_amount": round(discount_amount, 2),
            "final_price": round(final_price, 2),
            "is_active": product.is_active,
            "stock_status": product.stock_status.value,
            "stock_quantity": product.stock_quantity,
            "categories": category_ids
        })
    
    # Sort by discount percentage (highest first) if requested
    if sort_by_discount:
        products_data.sort(key=lambda x: x["discount_percentage"], reverse=True)
    
    return {
        "success": True,
        "campaign_id": campaign.id,
        "campaign_name": campaign.name,
        "discount_type": campaign.discount_type.value,
        "discount_value": campaign.discount_value,
        "target_type": campaign.target_type.value,
        "total_products": total_products,
        "products": products_data,
        "meta": {
            "total": total_products,
            "skip": skip,
            "limit": limit,
            "page": (skip // limit) + 1,
            "total_pages": (total_products + limit - 1) // limit if limit > 0 else 0,
            "has_next": skip + limit < total_products,
            "has_prev": skip > 0
        }
    }


# ============= Get All Discounted Products =============

def get_all_discounted_products(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> dict:
    """
    Get all products with active discounts from all campaigns
    Sorted by discount percentage (highest first)
    Only includes discounts within valid date range
    """
    # Auto-update expired campaigns
    update_expired_campaigns(db)
    
    from sqlalchemy.orm import joinedload
    from sqlalchemy import and_, or_
    from datetime import datetime
    
    now = datetime.now()
    
    # Get all products with active discounts within date range
    products_query = db.query(Product).join(ProductDiscount).filter(
        ProductDiscount.is_active == True,
        Product.is_active == True,
        # Check date range
        or_(ProductDiscount.start_date.is_(None), ProductDiscount.start_date <= now),
        or_(ProductDiscount.end_date.is_(None), ProductDiscount.end_date >= now)
    ).options(
        joinedload(Product.translations)
    ).distinct()
    
    # Count total
    total_products = products_query.count()
    
    # Apply pagination
    products_query = products_query.offset(skip).limit(limit)
    products = products_query.all()
    
    # Build response
    products_data = []
    
    for product in products:
        # Get all active discounts for this product within date range
        discounts = db.query(ProductDiscount).filter(
            ProductDiscount.product_id == product.id,
            ProductDiscount.is_active == True,
            or_(ProductDiscount.start_date.is_(None), ProductDiscount.start_date <= now),
            or_(ProductDiscount.end_date.is_(None), ProductDiscount.end_date >= now)
        ).all()
        
        if not discounts:
            continue
        
        # Find the highest discount
        best_discount = None
        best_percentage = 0
        
        price_list = product.price_list or 0
        
        for discount in discounts:
            if discount.discount_type == "percentage":
                percentage = discount.discount_value
            else:  # fixed_amount
                percentage = (discount.discount_value / price_list * 100) if price_list > 0 else 0
            
            if percentage > best_percentage:
                best_percentage = percentage
                best_discount = discount
        
        if not best_discount:
            continue
        
        # Calculate final price
        if best_discount.discount_type == "percentage":
            discount_amount = price_list * (best_discount.discount_value / 100)
        else:
            discount_amount = best_discount.discount_value
        
        final_price = max(0, price_list - discount_amount)
        
        # Get product title
        title = "Untitled"
        it_translation = next((t for t in product.translations if t.lang == "it"), None)
        if it_translation:
            title = it_translation.title
        elif product.translations:
            title = product.translations[0].title
        
        # Get campaign info
        campaign = db.query(DiscountCampaign).filter(
            DiscountCampaign.id == best_discount.campaign_id
        ).first()
        
        products_data.append({
            "product_id": product.id,
            "title": title,
            "reference": product.reference,
            "price": price_list,
            "discount": round(best_percentage, 1),
            "final_price": round(final_price, 2),
            "campaign_id": best_discount.campaign_id,
            "campaign_name": campaign.name if campaign else None
        })
    
    # Sort by discount percentage (highest first)
    products_data.sort(key=lambda x: x["discount"], reverse=True)
    
    return {
        "success": True,
        "total": total_products,
        "products": products_data,
        "meta": {
            "total": total_products,
            "skip": skip,
            "limit": limit,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "has_next": skip + limit < total_products,
            "has_prev": skip > 0
        }
    }


def get_highest_discount_products(db: Session) -> dict:
    """
    Get products with the highest discount only (maximum 5 products)
    Returns only products from the highest discount percentage available
    """
    # Auto-update expired campaigns
    update_expired_campaigns(db)
    
    from sqlalchemy.orm import joinedload
    from sqlalchemy import and_, or_
    from datetime import datetime
    
    now = datetime.now()
    
    # Get all products with active discounts within date range
    products_query = db.query(Product).join(ProductDiscount).filter(
        ProductDiscount.is_active == True,
        Product.is_active == True,
        # Check date range
        or_(ProductDiscount.start_date.is_(None), ProductDiscount.start_date <= now),
        or_(ProductDiscount.end_date.is_(None), ProductDiscount.end_date >= now)
    ).options(
        joinedload(Product.translations)
    ).distinct()
    
    products = products_query.all()
    
    # Build list with all products and their discounts
    all_products_data = []
    
    for product in products:
        # Get all active discounts for this product within date range
        discounts = db.query(ProductDiscount).filter(
            ProductDiscount.product_id == product.id,
            ProductDiscount.is_active == True,
            or_(ProductDiscount.start_date.is_(None), ProductDiscount.start_date <= now),
            or_(ProductDiscount.end_date.is_(None), ProductDiscount.end_date >= now)
        ).all()
        
        if not discounts:
            continue
        
        # Find the highest discount for this product
        best_discount = None
        best_percentage = 0
        
        price_list = product.price_list or 0
        
        for discount in discounts:
            if discount.discount_type == "percentage":
                percentage = discount.discount_value
            else:  # fixed_amount
                percentage = (discount.discount_value / price_list * 100) if price_list > 0 else 0
            
            if percentage > best_percentage:
                best_percentage = percentage
                best_discount = discount
        
        if not best_discount or best_percentage == 0:
            continue
        
        # Calculate final price
        if best_discount.discount_type == "percentage":
            discount_amount = price_list * (best_discount.discount_value / 100)
        else:
            discount_amount = best_discount.discount_value
        
        final_price = max(0, price_list - discount_amount)
        
        # Get product title
        title = "Untitled"
        it_translation = next((t for t in product.translations if t.lang == "it"), None)
        if it_translation:
            title = it_translation.title
        elif product.translations:
            title = product.translations[0].title
        
        # Get campaign info
        campaign = db.query(DiscountCampaign).filter(
            DiscountCampaign.id == best_discount.campaign_id
        ).first()
        
        # Get first image
        image = db.query(ProductImage).filter(
            ProductImage.product_id == product.id
        ).order_by(ProductImage.position).first()
        
        image_url = image.url if image else None
        
        all_products_data.append({
            "product_id": product.id,
            "title": title,
            "reference": product.reference,
            "price": price_list,
            "discount": round(best_percentage, 1),
            "final_price": round(final_price, 2),
            "image": image_url,
            "campaign_id": best_discount.campaign_id,
            "campaign_name": campaign.name if campaign else None
        })
    
    # Sort by discount percentage (highest first)
    all_products_data.sort(key=lambda x: x["discount"], reverse=True)
    
    # Get the highest discount percentage
    if not all_products_data:
        return {
            "success": True,
            "total": 0,
            "products": [],
            "highest_discount": None
        }
    
    highest_discount_percentage = all_products_data[0]["discount"]
    
    # Filter to get only products with the highest discount
    highest_discount_products = [
        p for p in all_products_data 
        if p["discount"] == highest_discount_percentage
    ]
    
    # Return only 5 products maximum
    result_products = highest_discount_products[:5]
    
    return {
        "success": True,
        "total": len(result_products),
        "products": result_products,
        "highest_discount": highest_discount_percentage
    }
