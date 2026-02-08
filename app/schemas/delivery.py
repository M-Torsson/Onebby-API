# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============= Delivery Translation Schemas =============

class DeliveryTranslationInput(BaseModel):
    """Delivery translation input"""
    lang: str = Field(..., min_length=2, max_length=5)
    note: Optional[str] = None
    option_note: Optional[str] = None


class DeliveryTranslationResponse(DeliveryTranslationInput):
    """Delivery translation response"""
    id: int

    class Config:
        from_attributes = True


# ============= Delivery Schemas =============

class DeliveryCreate(BaseModel):
    """Delivery creation schema"""
    days_from: int = Field(..., ge=0)
    days_to: int = Field(..., ge=0)
    note: Optional[str] = None
    option_note: Optional[str] = None
    is_free_delivery: bool = False
    is_active: bool = True
    categories: List[int] = Field(default_factory=list)
    translations: List[DeliveryTranslationInput] = Field(default_factory=list)

    class Config:
        from_attributes = True


class DeliveryUpdate(BaseModel):
    """Delivery update schema"""
    days_from: Optional[int] = Field(None, ge=0)
    days_to: Optional[int] = Field(None, ge=0)
    note: Optional[str] = None
    option_note: Optional[str] = None
    is_free_delivery: Optional[bool] = None
    is_active: Optional[bool] = None
    categories: Optional[List[int]] = None
    translations: Optional[List[DeliveryTranslationInput]] = None

    class Config:
        from_attributes = True


class DeliveryResponse(BaseModel):
    """Delivery response schema"""
    id: int
    days_from: int
    days_to: int
    note: Optional[str] = None
    option_note: Optional[str] = None
    is_free_delivery: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    categories: List[int] = Field(default_factory=list)
    translations: List[DeliveryTranslationResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class DeliverySimple(BaseModel):
    """Simple delivery info for product response"""
    id: int
    days_from: int
    days_to: int
    is_free_delivery: bool

    class Config:
        from_attributes = True
