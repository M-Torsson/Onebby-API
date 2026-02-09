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
    note: Optional[str] = Field(None, max_length=750)
    option_note: Optional[str] = Field(None, max_length=750)


class DeliveryTranslationResponse(DeliveryTranslationInput):
    """Delivery translation response"""
    id: int

    class Config:
        from_attributes = True


# ============= Delivery Option Schemas =============

class DeliveryOptionInput(BaseModel):
    """Delivery option input"""
    icon: Optional[str] = None
    details: Optional[str] = None
    price: float = Field(default=0, ge=0)


class DeliveryOptionResponse(BaseModel):
    """Delivery option response"""
    id: int
    icon: Optional[str] = None
    details: Optional[str] = None
    price: float
    position: int

    class Config:
        from_attributes = True


# ============= Delivery Schemas =============

class DeliveryCreate(BaseModel):
    """Delivery creation schema"""
    days_from: int = Field(..., ge=0)
    days_to: int = Field(..., ge=0)
    note: Optional[str] = Field(None, max_length=750)
    option_note: Optional[str] = Field(None, max_length=750)
    is_free_delivery: bool = False
    is_active: bool = True
    categories: List[int] = Field(default_factory=list)
    translations: List[DeliveryTranslationInput] = Field(default_factory=list)
    options: List[DeliveryOptionInput] = Field(default_factory=list)

    class Config:
        from_attributes = True


class DeliveryUpdate(BaseModel):
    """Delivery update schema"""
    days_from: Optional[int] = Field(None, ge=0)
    days_to: Optional[int] = Field(None, ge=0)
    note: Optional[str] = Field(None, max_length=750)
    option_note: Optional[str] = Field(None, max_length=750)
    is_free_delivery: Optional[bool] = None
    is_active: Optional[bool] = None
    categories: Optional[List[int]] = None
    options: Optional[List[DeliveryOptionInput]] = None
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
    options: List[DeliveryOptionResponse] = Field(default_factory=list)
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
