# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# ========== OrderItem Schemas ==========

class OrderItemBase(BaseModel):
    """Base schema for order item"""
    product_id: int
    product_variant_id: Optional[int] = None
    quantity: int = Field(ge=1, description="Quantity must be at least 1")
    delivery_option: Optional[Dict[str, Any]] = None
    warranty_option: Optional[Dict[str, Any]] = None


class OrderItemCreate(OrderItemBase):
    """Schema for creating an order item (from cart)"""
    pass


class OrderItemResponse(BaseModel):
    """Schema for order item response"""
    id: int
    order_id: int
    product_id: Optional[int]
    product_variant_id: Optional[int]
    
    # Product info
    product_title: str
    product_sku: Optional[str]
    product_type: Optional[str]
    product_image: Optional[str]
    
    # Pricing
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    discount: Decimal
    
    # Options
    delivery_option: Optional[Dict[str, Any]]
    warranty_option: Optional[Dict[str, Any]]
    variant_attributes: Optional[Dict[str, Any]]
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ========== Order Schemas ==========

class OrderBase(BaseModel):
    """Base schema for order"""
    customer_note: Optional[str] = Field(None, max_length=1000)


class OrderCreate(OrderBase):
    """
    Schema for creating an order from cart
    
    This is used during checkout process.
    All user/company and address information is collected from:
    - Logged-in user data (if user_id exists)
    - Checkout form (for guest checkout or override)
    """
    payment_method: str = Field(..., description="Payment method: paypal, scalapay, floa, etc.")
    
    # Customer info (for guest checkout or override)
    # If user is logged in, this can be auto-filled from user profile
    customer_info: Dict[str, Any] = Field(..., description="Customer or company information")
    
    # Addresses
    billing_address: Dict[str, Any] = Field(..., description="Billing address")
    shipping_address: Dict[str, Any] = Field(..., description="Shipping address")
    
    # Shipping method
    shipping_method: Optional[str] = Field(None, description="Shipping method: standard, express, etc.")
    
    @validator('customer_info')
    def validate_customer_info(cls, v):
        """Validate customer_info structure"""
        reg_type = v.get('reg_type')
        
        if reg_type == 'user':
            # Customer validation
            required_fields = ['reg_type', 'first_name', 'last_name', 'email']
            for field in required_fields:
                if not v.get(field):
                    raise ValueError(f"Customer info missing required field: {field}")
        
        elif reg_type == 'company':
            # Company validation
            required_fields = ['reg_type', 'company_name', 'email', 'vat_number', 'sdi_code']
            for field in required_fields:
                if not v.get(field):
                    raise ValueError(f"Company info missing required field: {field}")
        
        else:
            raise ValueError(f"Invalid reg_type: {reg_type}. Must be 'user' or 'company'")
        
        return v
    
    @validator('billing_address', 'shipping_address')
    def validate_address(cls, v):
        """Validate address structure"""
        required_fields = ['address_house_number', 'house_number', 'city', 'postal_code', 'country', 'phone']
        
        for field in required_fields:
            if not v.get(field):
                raise ValueError(f"Address missing required field: {field}")
        
        # Check for customer or company address
        address_type = v.get('address_type')
        if address_type == 'customer':
            if not v.get('name') or not v.get('last_name'):
                raise ValueError("Customer address requires 'name' and 'last_name'")
        elif address_type == 'company':
            if not v.get('company_name'):
                raise ValueError("Company address requires 'company_name'")
        
        return v


class OrderUpdate(BaseModel):
    """
    Schema for updating an order (Admin only)
    
    Used by admin to update order status, tracking, notes, etc.
    """
    status: Optional[str] = Field(None, description="Order status")
    payment_status: Optional[str] = Field(None, description="Payment status")
    shipping_status: Optional[str] = Field(None, description="Shipping status")
    tracking_number: Optional[str] = Field(None, max_length=255, description="Tracking number")
    admin_note: Optional[str] = Field(None, max_length=2000, description="Admin notes")
    shipping_method: Optional[str] = Field(None, description="Shipping method")


class OrderResponse(BaseModel):
    """
    Schema for order response (full details)
    
    Used when fetching a single order with all details.
    """
    id: int
    
    # User reference
    user_id: Optional[int]
    user_type: str
    
    # Customer/Company info
    customer_info: Dict[str, Any]
    
    # Addresses
    billing_address: Dict[str, Any]
    shipping_address: Dict[str, Any]
    
    # Financial
    subtotal: Decimal
    shipping_cost: Decimal
    tax: Decimal
    discount: Decimal
    total_amount: Decimal
    currency: str
    
    # Payment
    payment_status: str
    payment_method: Optional[str]
    payment_transaction_id: Optional[str]
    payment_info: Optional[Dict[str, Any]]  # New field
    
    # Shipping
    shipping_method: Optional[str]
    shipping_status: str
    tracking_number: Optional[str]
    
    # Status
    status: str
    
    # Notes
    customer_note: Optional[str]
    admin_note: Optional[str]
    
    # Items
    items: List[OrderItemResponse]
    
    # Timestamps
    order_date: Optional[str]  # New field
    created_at: datetime
    updated_at: Optional[datetime]
    paid_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """
    Schema for order list response (summary)
    
    Used for list views (e.g., admin order list, customer order history).
    Excludes items and detailed info for performance.
    """
    id: int
    
    # User reference
    user_id: Optional[int]
    user_type: str
    
    # Customer info (minimal)
    customer_email: Optional[str] = Field(None, description="Customer email extracted from customer_info")
    customer_name: Optional[str] = Field(None, description="Customer or company name")
    
    # Financial
    total_amount: Decimal
    currency: str
    
    # Status
    status: str
    payment_status: str
    payment_method: Optional[str]
    shipping_status: str
    
    # Additional info
    items_count: int = Field(description="Number of items in order")
    has_warranty: bool = Field(description="Whether order contains items with warranty")
    
    # Timestamps
    created_at: datetime
    paid_at: Optional[datetime]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class OrderStatsResponse(BaseModel):
    """
    Schema for order statistics (Admin dashboard)
    """
    total_orders: int
    total_revenue: Decimal
    
    # By status
    pending_orders: int
    confirmed_orders: int
    completed_orders: int
    cancelled_orders: int
    
    # By payment
    unpaid_orders: int
    paid_orders: int
    
    # By shipping
    pending_shipment: int
    shipped_orders: int
    delivered_orders: int
    
    # Warranty stats
    orders_with_warranty: int
    warranty_revenue: Decimal


# ========== Garanzia3 Integration Schemas ==========

class Garanzia3RegistrationRequest(BaseModel):
    """
    Schema for Garanzia3 warranty registration request
    
    Used when registering warranty with Garanzia3 web service.
    """
    order_id: int
    order_item_id: int
    customer_email: EmailStr
    customer_name: str
    product_info: Dict[str, Any]
    warranty_code: str
    purchase_date: str


class Garanzia3RegistrationResponse(BaseModel):
    """
    Schema for Garanzia3 warranty registration response
    
    Response from Garanzia3 web service after registration.
    """
    contract_number: str
    pin_code: str
    status: str
    message: Optional[str] = None


class WarrantyUpdateRequest(BaseModel):
    """
    Schema for manually updating warranty info in order item
    
    Used by admin to manually update warranty details
    (e.g., if automatic registration failed).
    """
    contract_number: str
    pin_code: str
    registered_at: Optional[datetime] = None


# ========== New Direct Order API Schemas ==========

class WarrantyOption(BaseModel):
    """Warranty option for order item"""
    title: str = Field(..., description="Warranty title")
    cost: Decimal = Field(..., ge=0, description="Warranty cost")


class DeliveryOption(BaseModel):
    """Delivery option for order item"""
    title: str = Field(..., description="Delivery option title")
    cost: Decimal = Field(..., ge=0, description="Delivery cost")


class OrderItemDirect(BaseModel):
    """Order item for direct order creation (new API)"""
    product_id: int = Field(..., description="Product ID")
    qty: int = Field(..., ge=1, le=1000, description="Quantity")
    warranty: Optional[WarrantyOption] = Field(None, description="Warranty option (optional)")
    delivery_opt: Optional[DeliveryOption] = Field(None, description="Delivery option (optional)")


class PaymentInfo(BaseModel):
    """Payment information for order"""
    payment_type: str = Field(..., description="Payment type (e.g., PayPal, Card)")
    payment_status: str = Field(..., description="Payment status (successful, pending, failed)")
    invoice_num: int = Field(..., description="Invoice number")
    payment_id: int = Field(..., description="Payment ID")


class OrderTotal(BaseModel):
    """Order total breakdown"""
    sub_total: Decimal = Field(..., ge=0, description="Subtotal (products only)")
    warranty: Decimal = Field(..., ge=0, description="Total warranty cost")
    shipping: Decimal = Field(..., ge=0, description="Total shipping cost")
    total: Decimal = Field(..., ge=0, description="Grand total")


class OrderCreateDirect(BaseModel):
    """
    Schema for creating an order directly (new API - no cart needed)
    
    This is the new format requested for order creation.
    Total will be calculated automatically by the system.
    """
    user_id: int = Field(..., description="User ID (required - no guest users)")
    reg_type: str = Field(..., description="Registration type (customer or company)")
    address_id: int = Field(..., description="Address ID from addresses table")
    order_date: str = Field(..., description="Custom order date")
    customer_note: Optional[str] = Field(None, max_length=1000, description="Customer note")
    payment_info: PaymentInfo = Field(..., description="Payment information")
    items: List[OrderItemDirect] = Field(..., min_items=1, description="Order items (at least 1)")
    
    @validator('reg_type')
    def validate_reg_type(cls, v):
        """Validate reg_type"""
        if v not in ['customer', 'company']:
            raise ValueError("reg_type must be 'customer' or 'company'")
        return v
