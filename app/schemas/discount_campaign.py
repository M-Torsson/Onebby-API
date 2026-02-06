# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DiscountTypeEnum(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"


class TargetTypeEnum(str, Enum):
    PRODUCTS = "products"
    CATEGORY = "category"
    BRAND = "brand"
    ALL = "all"


# ============= Create Schema =============

class DiscountCampaignCreate(BaseModel):
    """Create discount campaign"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    
    discount_type: DiscountTypeEnum
    discount_value: float = Field(..., gt=0)
    
    target_type: TargetTypeEnum
    target_ids: Optional[List[int]] = None  # Required for products/category/brand, null for all
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    is_active: bool = True
    auto_apply: bool = True  # Auto-apply campaign to products after creation
    priority: int = Field(default=1, ge=1, le=10)  # Priority level (1-10, higher = more important)

    @field_validator('discount_value')
    @classmethod
    def validate_discount_value(cls, v, info):
        discount_type = info.data.get('discount_type')
        if discount_type == DiscountTypeEnum.PERCENTAGE and v > 100:
            raise ValueError('Percentage discount cannot exceed 100%')
        return v

    @field_validator('target_ids')
    @classmethod
    def validate_target_ids(cls, v, info):
        target_type = info.data.get('target_type')
        if target_type in [TargetTypeEnum.PRODUCTS, TargetTypeEnum.CATEGORY, TargetTypeEnum.BRAND]:
            if not v or len(v) == 0:
                raise ValueError(f'target_ids required for target_type: {target_type}')
        return v

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        start_date = info.data.get('start_date')
        if start_date and v and v < start_date:
            raise ValueError('end_date must be after start_date')
        return v


# ============= Update Schema =============

class DiscountCampaignUpdate(BaseModel):
    """Update discount campaign"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    
    discount_type: Optional[DiscountTypeEnum] = None
    discount_value: Optional[float] = Field(None, gt=0)
    
    target_type: Optional[TargetTypeEnum] = None
    target_ids: Optional[List[int]] = None
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=10)


# ============= Response Schema =============

class DiscountCampaignResponse(BaseModel):
    """Discount campaign response"""
    id: int
    name: str
    description: Optional[str] = None
    
    discount_type: str
    discount_value: float
    
    target_type: str
    target_ids: Optional[List[int]] = None
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    is_active: bool
    priority: int
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= Apply Campaign Response =============

class ApplyCampaignResponse(BaseModel):
    """Response after applying campaign to products"""
    campaign_id: int
    campaign_name: str
    products_updated: int
    target_type: str
    message: str
