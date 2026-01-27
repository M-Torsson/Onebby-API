# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============= Brand Schemas =============

class BrandBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: Optional[str] = None
    image: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = None
    image: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class BrandResponse(BrandBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BrandSimple(BaseModel):
    """Simple brand response for product listings"""
    id: int
    name: str
    image: Optional[str] = None

    class Config:
        from_attributes = True


# ============= Tax Class Schemas =============

class TaxClassBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    rate: float = Field(..., ge=0, le=100)  # 0-100%
    is_active: bool = True


class TaxClassCreate(TaxClassBase):
    pass


class TaxClassUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    rate: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class TaxClassResponse(TaxClassBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaxClassSimple(BaseModel):
    """Simple tax class response for product listings"""
    class_id: int = Field(..., alias="id")
    name: str
    rate: float
    included_in_price: bool

    class Config:
        from_attributes = True
        populate_by_name = True
