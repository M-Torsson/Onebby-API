# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from app.models.discount_campaign import DiscountCampaign, TargetTypeEnum
from app.models.product import Product, ProductDiscount
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


def get_campaigns(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    is_active: Optional[bool] = None
) -> List[DiscountCampaign]:
    """Get all campaigns with pagination"""
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
    """Delete a campaign"""
    db_campaign = get_campaign(db, campaign_id)
    if not db_campaign:
        return False
    
    db.delete(db_campaign)
    db.commit()
    return True


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
        # Products in category
        if not campaign.target_ids or len(campaign.target_ids) == 0:
            return {"success": False, "message": "No target category specified"}
        
        category_id = campaign.target_ids[0]
        products = db.query(Product).join(Product.categories).filter(
            Product.categories.any(id=category_id),
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
    
    # Apply discount to products
    products_updated = 0
    
    for product in products:
        # Check if discount already exists for this product from this campaign
        existing_discount = db.query(ProductDiscount).filter(
            ProductDiscount.product_id == product.id,
            ProductDiscount.is_active == True
        ).first()
        
        if existing_discount:
            # Update existing discount
            existing_discount.discount_type = campaign.discount_type.value
            existing_discount.discount_value = campaign.discount_value
            existing_discount.start_date = campaign.start_date
            existing_discount.end_date = campaign.end_date
        else:
            # Create new discount
            new_discount = ProductDiscount(
                product_id=product.id,
                discount_type=campaign.discount_type.value,
                discount_value=campaign.discount_value,
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
        products = db.query(Product).join(Product.categories).filter(
            Product.categories.any(id=category_id)
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
