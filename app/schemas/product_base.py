# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============= Enums =============

class ProductTypeEnum(str, Enum):
    CONFIGURABLE = "configurable"
    SIMPLE = "simple"
    SERVICE = "service"
    WARRANTY = "warranty"


class ProductConditionEnum(str, Enum):
    NEW = "new"
    USED = "used"
    A_PLUS_PLUS = "A++"
    A_PLUS = "A+"
    B_PLUS = "B+"
    C = "C"
    F = "F"


class StockStatusEnum(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    PREORDER = "preorder"


# ============= Translation Schemas =============

class ProductTranslationInput(BaseModel):
    """Translation input for product creation"""
    lang: str = Field(..., min_length=2, max_length=5)
    title: str = Field(..., min_length=1, max_length=255)
    sub_title: Optional[str] = Field(None, max_length=500)
    simple_description: Optional[str] = Field(None, description="Supports HTML formatting (bold, italic, etc.)")
    meta_description: Optional[str] = Field(None, description="Supports HTML formatting (bold, italic, etc.)")


class ProductTranslationResponse(ProductTranslationInput):
    """Translation response"""
    id: int
    product_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= Image Schemas =============

class ImageAltInput(BaseModel):
    """Image alt text for multiple languages"""
    it: Optional[str] = None
    en: Optional[str] = None
    fr: Optional[str] = None
    de: Optional[str] = None
    ar: Optional[str] = None


class ProductImageInput(BaseModel):
    """Product image input"""
    url: str = Field(..., min_length=1, max_length=500)
    position: int = Field(1, ge=1)
    alt: ImageAltInput


class ProductImageResponse(BaseModel):
    """Product image response"""
    url: str
    position: int
    alt: str  # Will be set based on requested language

    class Config:
        from_attributes = True


# ============= Feature Schemas =============

class FeatureTranslationInput(BaseModel):
    """Feature translation input"""
    lang: str = Field(..., min_length=2, max_length=5)
    name: str = Field(..., min_length=1, max_length=255)
    value: str = Field(..., min_length=1, max_length=500)


class ProductFeatureInput(BaseModel):
    """Product feature input"""
    code: str = Field(..., min_length=1, max_length=100)
    translations: List[FeatureTranslationInput]


class ProductFeatureResponse(BaseModel):
    """Product feature response (language-specific)"""
    name: str
    value: str

    class Config:
        from_attributes = True


# ============= Attribute Schemas =============

class AttributeTranslationInput(BaseModel):
    """Attribute translation input"""
    lang: str = Field(..., min_length=2, max_length=5)
    name: str = Field(..., min_length=1, max_length=255)
    value: str = Field(..., min_length=1, max_length=500)


class ProductAttributeInput(BaseModel):
    """Product attribute input"""
    code: str = Field(..., min_length=1, max_length=100)
    translations: List[AttributeTranslationInput]


class ProductAttributeResponse(BaseModel):
    """Product attribute response (language-specific)"""
    code: str
    name: str
    value: str

    class Config:
        from_attributes = True


# ============= Variant Attribute Schemas =============

class VariantAttributeOptionInput(BaseModel):
    """Variant attribute option (used in response)"""
    value: str
    label: str


class VariantAttributeTranslationInput(BaseModel):
    """Variant attribute translation input"""
    lang: str = Field(..., min_length=2, max_length=5)
    label: str = Field(..., min_length=1, max_length=255)


class ProductVariantAttributeInput(BaseModel):
    """Product variant attribute definition input"""
    code: str = Field(..., min_length=1, max_length=100)
    translations: List[VariantAttributeTranslationInput]


class ProductVariantAttributeResponse(BaseModel):
    """Product variant attribute response with options"""
    code: str
    label: str
    options: List[VariantAttributeOptionInput]

    class Config:
        from_attributes = True


# ============= Price & Discount Schemas =============

class DiscountInput(BaseModel):
    """Discount input"""
    discount_type: str = Field(..., pattern="^(percentage|fixed)$")
    discount_value: float = Field(..., gt=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True


class PriceInput(BaseModel):
    """Price input"""
    list: float = Field(..., ge=0)
    currency: str = Field("EUR", min_length=3, max_length=3)
    discounts: List[DiscountInput] = []


class PriceResponse(BaseModel):
    """Price response"""
    list: float
    currency: str
    discounts: Optional[str] = "0"

    class Config:
        from_attributes = True


# ============= Stock Schemas =============

class StockInput(BaseModel):
    """Stock input"""
    status: StockStatusEnum
    quantity: int = Field(0, ge=0)


class StockResponse(BaseModel):
    """Stock response"""
    status: str
    quantity: int

    class Config:
        from_attributes = True


# ============= Tax Schemas =============

class TaxInput(BaseModel):
    """Tax input"""
    class_id: int = Field(..., gt=0)
    included_in_price: bool = True


# ============= Service Links Schemas =============

class ServiceLinksInput(BaseModel):
    """Service links input (for configurable products)"""
    allowed_shipping_services: List[int] = []
    allowed_warranties: List[int] = []


# ============= Variant Schemas =============

class ProductVariantInput(BaseModel):
    """Product variant input"""
    reference: str = Field(..., min_length=1, max_length=100)
    ean13: Optional[str] = Field(None, min_length=13, max_length=13)
    is_active: bool = True
    condition: ProductConditionEnum = ProductConditionEnum.NEW
    attributes: Dict[str, str]  # e.g., {"color": "black", "storage": "128"}
    price: PriceInput
    stock: StockInput
    images: List[ProductImageInput] = []

    @field_validator('ean13')
    @classmethod
    def validate_ean13(cls, v):
        if v and not v.isdigit():
            raise ValueError('EAN13 must contain only digits')
        return v


class ProductVariantResponse(BaseModel):
    """Product variant response"""
    id: int
    reference: str
    ean13: Optional[str] = None
    is_active: bool
    attributes: Dict[str, str]
    price: PriceResponse
    stock: StockResponse
    images: List[ProductImageResponse] = []

    class Config:
        from_attributes = True


# ============= Category Simple Schema =============

class CategorySimple(BaseModel):
    """Simple category response for product listings"""
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True
