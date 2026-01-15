from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.api.dependencies import verify_api_key
from app.crud import discount_campaign as crud_campaign
from app.schemas.discount_campaign import (
    DiscountCampaignCreate,
    DiscountCampaignUpdate,
    DiscountCampaignResponse,
    ApplyCampaignResponse
)

router = APIRouter()


@router.post("/admin/discounts", response_model=DiscountCampaignResponse, status_code=201)
def create_discount_campaign(
    campaign: DiscountCampaignCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new discount campaign
    
    - **name**: Campaign name
    - **discount_type**: "percentage" or "fixed_amount"
    - **discount_value**: Discount value (e.g., 15 for 15%)
    - **target_type**: "products", "category", "brand", or "all"
    - **target_ids**: List of IDs (products, category, or brand)
    - **start_date**: Start date (optional)
    - **end_date**: End date (optional)
    - **is_active**: Active status (default: true)
    
    Requires X-API-Key header for authentication
    """
    try:
        db_campaign = crud_campaign.create_campaign(db, campaign)
        return db_campaign
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating campaign: {str(e)}")


@router.get("/admin/discounts", response_model=dict)
def get_discount_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all discount campaigns with pagination
    
    - **skip**: Number of campaigns to skip (pagination)
    - **limit**: Maximum number of campaigns per page
    - **is_active**: Filter by active status (optional)
    
    Requires X-API-Key header for authentication
    """
    total = crud_campaign.count_campaigns(db, is_active=is_active)
    campaigns = crud_campaign.get_campaigns(db, skip=skip, limit=limit, is_active=is_active)
    
    total_pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return {
        "data": campaigns,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "page": current_page,
            "total_pages": total_pages,
            "has_next": skip + limit < total,
            "has_prev": skip > 0
        }
    }


@router.get("/admin/discounts/{campaign_id}", response_model=DiscountCampaignResponse)
def get_discount_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get discount campaign by ID
    
    Requires X-API-Key header for authentication
    """
    campaign = crud_campaign.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.put("/admin/discounts/{campaign_id}", response_model=DiscountCampaignResponse)
def update_discount_campaign(
    campaign_id: int,
    campaign_update: DiscountCampaignUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update a discount campaign
    
    All fields are optional - only provide fields you want to update
    
    Requires X-API-Key header for authentication
    """
    try:
        db_campaign = crud_campaign.update_campaign(db, campaign_id, campaign_update)
        if not db_campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return db_campaign
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating campaign: {str(e)}")


@router.delete("/admin/discounts/{campaign_id}", status_code=200)
def delete_discount_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete a discount campaign
    
    Note: This will NOT remove discounts already applied to products.
    Use POST /admin/discounts/{campaign_id}/remove first if needed.
    
    Requires X-API-Key header for authentication
    """
    success = crud_campaign.delete_campaign(db, campaign_id)
    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "message": "Campaign deleted successfully",
        "campaign_id": campaign_id
    }


@router.post("/admin/discounts/{campaign_id}/apply", response_model=ApplyCampaignResponse)
def apply_discount_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Apply discount campaign to products
    
    This will:
    - Find all products matching the campaign target (products/category/brand/all)
    - Create or update ProductDiscount entries for each product
    - Apply the discount value and dates from the campaign
    
    Requires X-API-Key header for authentication
    """
    result = crud_campaign.apply_campaign_to_products(db, campaign_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return ApplyCampaignResponse(
        campaign_id=result["campaign_id"],
        campaign_name=result["campaign_name"],
        products_updated=result["products_updated"],
        target_type=result["target_type"],
        message=f"Successfully applied discount to {result['products_updated']} products"
    )


@router.post("/admin/discounts/{campaign_id}/remove", response_model=dict)
def remove_discount_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Remove discounts applied by this campaign
    
    This will remove ProductDiscount entries for all products targeted by this campaign
    
    Requires X-API-Key header for authentication
    """
    result = crud_campaign.remove_campaign_discounts(db, campaign_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return {
        "message": result["message"],
        "products_updated": result["products_updated"]
    }
