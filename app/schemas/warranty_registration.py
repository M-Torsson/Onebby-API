# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ============= Warranty Registration Schemas =============

class WarrantyRegistrationCreate(BaseModel):
    """Schema for creating a warranty registration"""
    order_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    warranty_id: Optional[int] = Field(None, gt=0)
    
    # Customer info (optional - will use order customer if not provided)
    customer_name: Optional[str] = Field(None, max_length=255)
    customer_lastname: Optional[str] = Field(None, max_length=255)
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = Field(None, max_length=50)
    
    # Product info (optional - will be extracted from order if not provided)
    product_ean13: Optional[str] = Field(None, max_length=13)
    product_name: Optional[str] = Field(None, max_length=255)
    
    class Config:
        from_attributes = True


class WarrantyRegistrationResponse(BaseModel):
    """Schema for warranty registration response"""
    id: int
    order_id: int
    product_id: Optional[int]
    warranty_id: Optional[int]
    
    # Customer info
    customer_name: str
    customer_lastname: str
    customer_email: str
    customer_phone: str
    
    # Product info
    product_ean13: str
    product_name: Optional[str]
    
    # Garanzia3 data
    g3_transaction_id: Optional[str]
    g3_pin: Optional[str]
    
    # Status
    status: str
    error_message: Optional[str]
    error_code: Optional[str]
    is_test: bool
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    registered_at: Optional[datetime]
    failed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WarrantyRegistrationListItem(BaseModel):
    """Schema for warranty registration list item (summary)"""
    id: int
    order_id: int
    product_name: Optional[str]
    g3_transaction_id: Optional[str]
    g3_pin: Optional[str]
    status: str
    created_at: datetime
    registered_at: Optional[datetime]
    
    class Config:
        from_attributes = True
