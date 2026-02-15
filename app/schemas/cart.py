# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============= Cart Item Schemas =============

class CartItemAdd(BaseModel):
    """Schema for adding item to cart"""
    product_id: int = Field(..., description="Product ID")
    product_variant_id: Optional[int] = Field(None, description="Product Variant ID (optional)")
    quantity: int = Field(..., ge=1, le=100, description="Quantity (1-100)")


class CartItemUpdate(BaseModel):
    """Schema for updating cart item quantity"""
    quantity: int = Field(..., ge=1, le=100, description="New quantity (1-100)")


class CartItemResponse(BaseModel):
    """Schema for cart item in response"""
    id: int
    cart_id: int
    product_id: int
    product_variant_id: Optional[int] = None
    quantity: int
    price_at_add: Decimal
    discount_at_add: Optional[Decimal] = None
    current_price: Decimal
    current_discount: Optional[Decimal] = None
    price_changed: bool
    item_subtotal: Decimal
    item_discount: Decimal
    item_total: Decimal
    stock_available: int
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Product details
    product_name: str
    product_image: Optional[str] = None
    product_sku: Optional[str] = None
    
    # Variant details (if applicable)
    variant_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============= Cart Schemas =============

class CartCreate(BaseModel):
    """Schema for creating a cart"""
    user_id: Optional[int] = Field(None, description="User ID (optional for guest)")
    session_id: Optional[str] = Field(None, description="Session ID for guest users")


class CartResponse(BaseModel):
    """Schema for cart response"""
    id: int
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    status: str
    items: List[CartItemResponse] = []
    totals: dict
    warnings: List[dict] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CartTotals(BaseModel):
    """Schema for cart totals calculation"""
    subtotal: Decimal = Field(..., description="Sum of all items before discount")
    total_discount: Decimal = Field(..., description="Sum of all discounts")
    total: Decimal = Field(..., description="Final total after discount")
    items_count: int = Field(..., description="Total number of items")


class CartValidationResponse(BaseModel):
    """Schema for cart validation before checkout"""
    is_valid: bool
    cart_id: int
    items_count: int
    errors: List[dict] = []
    warnings: List[dict] = []
    totals: CartTotals


class CartMergeRequest(BaseModel):
    """Schema for merging guest cart with user cart"""
    session_id: str = Field(..., description="Guest session ID to merge")
    user_id: int = Field(..., description="User ID to merge into")


# ============= Cart Warning/Error Schemas =============

class CartWarning(BaseModel):
    """Schema for cart warnings"""
    item_id: Optional[int] = None
    product_id: int
    message: str
    type: str  # price_change, stock_low, out_of_stock, product_unavailable


class CartError(BaseModel):
    """Schema for cart errors"""
    item_id: Optional[int] = None
    product_id: int
    message: str
    type: str  # out_of_stock, product_not_found, insufficient_stock
