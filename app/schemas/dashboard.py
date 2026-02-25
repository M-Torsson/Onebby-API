# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========================================
# Dashboard Overview Schemas
# ========================================

class DashboardOverviewResponse(BaseModel):
    """Dashboard overview statistics response"""
    
    # Main statistics
    categories: int = Field(..., description="Total number of categories")
    brands: int = Field(..., description="Total number of brands")
    products: int = Field(..., description="Total number of products")
    revenue: float = Field(..., description="Total revenue")
    
    # Orders stats
    orders_last_week: float = Field(..., description="Orders total for last week")
    orders_last_week_change_pct: float = Field(..., description="Percentage change compared to previous week")
    
    # Sales stats (last year)
    sales_last_year: float = Field(..., description="Sales total for last year")
    sales_last_year_change_pct: float = Field(..., description="Percentage change compared to previous year")
    
    # Profit stats (last week)
    profit_last_week: float = Field(..., description="Profit for last week")
    profit_last_week_change_pct: float = Field(..., description="Percentage change compared to previous week")
    
    # Sales stats (last week)
    sales_last_week: float = Field(..., description="Sales total for last week")
    sales_last_week_change_pct: float = Field(..., description="Percentage change compared to previous week")
    
    class Config:
        json_schema_extra = {
            "example": {
                "categories": 14,
                "brands": 568,
                "products": 19857,
                "revenue": 894000.00,
                "orders_last_week": 124000.00,
                "orders_last_week_change_pct": 12.6,
                "sales_last_year": 175000.00,
                "sales_last_year_change_pct": -16.2,
                "profit_last_week": 1280.00,
                "profit_last_week_change_pct": -12.2,
                "sales_last_week": 24670.00,
                "sales_last_week_change_pct": 24.67
            }
        }


# ========================================
# Latest Products Schemas
# ========================================

class DashboardProductItem(BaseModel):
    """Product item for dashboard"""
    id: int = Field(..., description="Product ID")
    title: str = Field(..., description="Product title")
    sku: str = Field(..., description="Product SKU/reference")
    price: float = Field(..., description="Product price")
    currency: str = Field(default="EUR", description="Currency code")
    image: Optional[str] = Field(None, description="Product image URL")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 912,
                "title": "كرسي مكتبي فاخر",
                "sku": "CHAIR-912",
                "price": 149.99,
                "currency": "EUR",
                "image": "https://cdn.example.com/products/912-thumb.jpg",
                "created_at": "2026-02-24T10:35:00Z"
            }
        }


class DashboardProductsResponse(BaseModel):
    """Latest products response"""
    items: List[DashboardProductItem] = Field(..., description="List of recent products")
    meta: dict = Field(..., description="Metadata including total count")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 912,
                        "title": "كرسي مكتبي فاخر",
                        "sku": "CHAIR-912",
                        "price": 149.99,
                        "currency": "EUR",
                        "image": "https://cdn.example.com/products/912-thumb.jpg",
                        "created_at": "2026-02-24T10:35:00Z"
                    }
                ],
                "meta": {"total": 10}
            }
        }


# ========================================
# Latest Payments Schemas
# ========================================

class DashboardPaymentItem(BaseModel):
    """Order item for dashboard (showing payment info)"""
    id: int = Field(..., description="Order ID")
    customer_name: str = Field(..., description="Customer or company name")
    customer_email: str = Field(..., description="Customer email")
    amount: float = Field(..., description="Order total amount")
    currency: str = Field(default="EUR", description="Currency code")
    payment_status: str = Field(..., description="Payment status")
    payment_method: Optional[str] = Field(None, description="Payment method")
    shipping_status: str = Field(..., description="Shipping status")
    created_at: datetime = Field(..., description="Order creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 9,
                "customer_name": "CodeCore SRL",
                "customer_email": "codecore@info.com",
                "amount": 6075.00,
                "currency": "EUR",
                "payment_status": "pending",
                "payment_method": "credit_card",
                "shipping_status": "pending",
                "created_at": "2026-02-24T16:11:00Z"
            }
        }


class DashboardPaymentsResponse(BaseModel):
    """Latest orders response (with payment info)"""
    payments: List[DashboardPaymentItem] = Field(..., description="List of recent orders")
    total: int = Field(..., description="Total order count")
    
    class Config:
        json_schema_extra = {
            "example": {
                "payments": [
                    {
                        "id": 9,
                        "customer_name": "CodeCore SRL",
                        "customer_email": "codecore@info.com",
                        "amount": 6075.00,
                        "currency": "EUR",
                        "payment_status": "pending",
                        "payment_method": "credit_card",
                        "shipping_status": "pending",
                        "created_at": "2026-02-24T16:11:00Z"
                    }
                ],
                "total": 5
            }
        }


# ========================================
# Combined CRM Live Response
# ========================================

class DashboardCRMLiveResponse(BaseModel):
    """Combined dashboard data for optimal performance"""
    overview: DashboardOverviewResponse = Field(..., description="Overview statistics")
    latest_products: List[DashboardProductItem] = Field(..., description="Latest products")
    latest_payments: List[DashboardPaymentItem] = Field(..., description="Latest payments")
    
    class Config:
        json_schema_extra = {
            "example": {
                "overview": {
                    "categories": 14,
                    "brands": 568,
                    "products": 19857,
                    "revenue": 894000.00,
                    "orders_last_week": 124000.00,
                    "orders_last_week_change_pct": 12.6,
                    "sales_last_year": 175000.00,
                    "sales_last_year_change_pct": -16.2,
                    "profit_last_week": 1280.00,
                    "profit_last_week_change_pct": -12.2,
                    "sales_last_week": 24670.00,
                    "sales_last_week_change_pct": 24.67
                },
                "latest_products": [],
                "latest_payments": []
            }
        }
