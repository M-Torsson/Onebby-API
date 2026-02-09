# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============= Warranty Translation Schemas =============

class WarrantyTranslationInput(BaseModel):
    """Warranty translation input"""
    lang: str = Field(..., min_length=2, max_length=5)
    title: Optional[str] = Field(None, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=500)
    meta_description: Optional[str] = None


class WarrantyTranslationResponse(WarrantyTranslationInput):
    """Warranty translation response"""
    id: int

    class Config:
        from_attributes = True


# ============= Warranty Feature Schemas =============

class WarrantyFeatureInput(BaseModel):
    """Warranty feature input"""
    key: str = Field(..., max_length=255)
    value: str


class WarrantyFeatureResponse(BaseModel):
    """Warranty feature response"""
    id: int
    key: str
    value: str
    position: int

    class Config:
        from_attributes = True


# ============= Warranty Schemas =============

class WarrantyCreate(BaseModel):
    """Warranty creation schema"""
    title: str = Field(..., max_length=255)
    subtitle: Optional[str] = Field(None, max_length=500)
    meta_description: Optional[str] = None
    price: int = Field(..., ge=0)
    image: Optional[str] = None
    is_active: bool = True
    categories: List[int] = Field(default_factory=list)
    translations: List[WarrantyTranslationInput] = Field(default_factory=list)
    features: List[WarrantyFeatureInput] = Field(default_factory=list)

    class Config:
        from_attributes = True


class WarrantyUpdate(BaseModel):
    """Warranty update schema"""
    title: Optional[str] = Field(None, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=500)
    meta_description: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    image: Optional[str] = None
    is_active: Optional[bool] = None
    categories: Optional[List[int]] = None
    features: Optional[List[WarrantyFeatureInput]] = None
    translations: Optional[List[WarrantyTranslationInput]] = None

    class Config:
        from_attributes = True


class WarrantyResponse(BaseModel):
    """Warranty response schema"""
    id: int
    title: str
    subtitle: Optional[str] = None
    meta_description: Optional[str] = None
    price: int
    image: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    categories: List[int] = Field(default_factory=list)
    features: List[WarrantyFeatureResponse] = Field(default_factory=list)
    translations: List[WarrantyTranslationResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class WarrantySimple(BaseModel):
    """Simple warranty info for product response"""
    id: int
    title: str
    price: float
    image: Optional[str] = None

    class Config:
        from_attributes = True
