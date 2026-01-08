from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from app.schemas.product_base import (
    ProductTypeEnum, ProductConditionEnum,
    ProductTranslationInput, ProductImageInput,
    ProductFeatureInput, ProductAttributeInput,
    ProductVariantAttributeInput, ProductVariantInput,
    TaxInput, PriceInput, StockInput, ServiceLinksInput,
    ProductImageResponse, ProductFeatureResponse, ProductAttributeResponse,
    ProductVariantAttributeResponse, ProductVariantResponse,
    PriceResponse, StockResponse, CategorySimple
)
from app.schemas.brand_tax import BrandSimple, TaxClassSimple


# ============= Product Create Schema =============

class ProductCreate(BaseModel):
    """Product creation schema (POST request)"""
    product_type: ProductTypeEnum
    
    # Basic info
    reference: str = Field(..., min_length=1, max_length=100)
    ean: Optional[str] = Field(None, max_length=255)
    
    # Status
    is_active: bool = True
    date_add: Optional[datetime] = None
    date_update: Optional[datetime] = None
    
    # Brand
    brand_id: Optional[int] = None
    
    # Tax (optional - will use default tax class if not provided)
    tax: Optional[TaxInput] = None
    
    # Pricing
    price: PriceInput
    
    # Condition
    condition: ProductConditionEnum = ProductConditionEnum.NEW
    
    # Categories
    categories: List[int] = Field(..., min_items=1)
    
    # Stock
    stock: StockInput
    
    # Images
    images: List[ProductImageInput] = []
    
    # Features
    features: List[ProductFeatureInput] = []
    
    # Attributes
    attributes: List[ProductAttributeInput] = []
    
    # Related products
    related_product_ids: List[int] = []
    
    # Service links (for configurable products)
    service_links: Optional[ServiceLinksInput] = None
    
    # Translations (optional - if not provided, will use default language)
    translations: Optional[List[ProductTranslationInput]] = None
    
    # Variant attributes (for configurable products only)
    variant_attributes: List[ProductVariantAttributeInput] = []
    
    # Variants (for configurable products only)
    variants: List[ProductVariantInput] = []
    
    # For service/warranty products
    duration_months: Optional[int] = None

    @field_validator('ean')
    @classmethod
    def validate_ean(cls, v):
        if v and not v.strip():
            raise ValueError('EAN cannot be empty')
        return v.strip() if v else None

    @field_validator('variants')
    @classmethod
    def validate_variants(cls, v, info):
        if info.data.get('product_type') == ProductTypeEnum.CONFIGURABLE and not v:
            raise ValueError('Configurable products must have at least one variant')
        return v

    @field_validator('variant_attributes')
    @classmethod
    def validate_variant_attributes(cls, v, info):
        if info.data.get('product_type') == ProductTypeEnum.CONFIGURABLE and not v:
            raise ValueError('Configurable products must have variant_attributes defined')
        return v


# ============= Product Update Schema =============

class ProductUpdate(BaseModel):
    """Product update schema - all fields optional"""
    # Status
    is_active: Optional[bool] = None
    
    # Brand
    brand_id: Optional[int] = None
    
    # Tax
    tax_class_id: Optional[int] = None
    tax_included_in_price: Optional[bool] = None
    
    # Pricing
    price_list: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=3)
    
    # Condition
    condition: Optional[ProductConditionEnum] = None
    
    # Categories
    categories: Optional[List[int]] = None
    
    # Stock
    stock_status: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    
    # Images (replace all)
    images: Optional[List[ProductImageInput]] = None
    
    # Features (replace all)
    features: Optional[List[ProductFeatureInput]] = None
    
    # Attributes (replace all)
    attributes: Optional[List[ProductAttributeInput]] = None
    
    # Related products (replace all)
    related_product_ids: Optional[List[int]] = None
    
    # Service links
    service_links: Optional[ServiceLinksInput] = None
    
    # Translations (replace all)
    translations: Optional[List[ProductTranslationInput]] = None
    
    # Variants (replace all - configurable products only)
    variants: Optional[List[ProductVariantInput]] = None
    
    # Duration (service/warranty products)
    duration_months: Optional[int] = None


# ============= Product Response Schemas =============

class ProductResponseFull(BaseModel):
    """Full product response (GET request)"""
    id: int
    product_type: str
    
    # Basic info
    reference: str
    ean13: Optional[str] = None
    
    # Status
    is_active: bool
    date_add: datetime
    date_update: Optional[datetime] = None
    
    # Brand
    brand: Optional[BrandSimple] = None
    
    # Tax
    tax: TaxClassSimple
    
    # Pricing
    price: PriceResponse
    
    # Stock
    stock: StockResponse
    
    # Categories
    categories: List[CategorySimple] = []
    
    # Condition
    condition: str
    
    # Translations (language-specific)
    title: str
    sub_title: Optional[str] = None
    simple_description: Optional[str] = None
    meta_description: Optional[str] = None
    
    # Images
    images: List[ProductImageResponse] = []
    
    # Features
    features: List[ProductFeatureResponse] = []
    
    # Attributes
    attributes: List[ProductAttributeResponse] = []
    
    # Related products
    related_product_ids: List[int] = []
    
    # Variant attributes (for configurable products)
    variant_attributes: List[ProductVariantAttributeResponse] = []
    
    # Variants (for configurable products)
    variants: List[ProductVariantResponse] = []
    
    # Options (shipping services and warranties)
    options: Optional[dict] = None

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    """Product response wrapper"""
    data: ProductResponseFull
    meta: dict

    class Config:
        from_attributes = True


# ============= Stock Update Schema =============

class StockUpdateInput(BaseModel):
    """Stock update input"""
    stock_status: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)


class StockUpdateResponse(BaseModel):
    """Stock update response"""
    id: int
    reference: str
    stock_status: str
    stock_quantity: int
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= Category Products Schema =============

class ProductPriceSimple(BaseModel):
    """Simple price response for category products"""
    price: float
    currency: str
    discounts: str  # e.g. "10%" or "0"
    tax_role: str   # e.g. "22%"


class CategoryProductItem(BaseModel):
    """Product item in category products list"""
    id: int
    child_category: str
    slug: str
    image: Optional[str] = None
    brand_id: Optional[int] = None
    condition: str
    quantity: int
    title: str
    sub_title: Optional[str] = None
    simple_description: Optional[str] = None
    is_active: bool
    price: ProductPriceSimple


class CategoryProductsResponse(BaseModel):
    """Response for category products"""
    data: List[CategoryProductItem]
    meta: dict
