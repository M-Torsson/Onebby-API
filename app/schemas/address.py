# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============= Customer Address Schemas =============

class CustomerAddressCreate(BaseModel):
    """Schema for creating a customer address"""
    alias: Optional[str] = Field(None, max_length=100, description="Address alias (optional)")
    name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    company: Optional[str] = Field(None, max_length=200, description="Company name (optional)")
    address_house_number: str = Field(..., min_length=1, max_length=200, description="Address and house number")
    house_number: str = Field(..., min_length=1, max_length=50, description="House number")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    postal_code: str = Field(..., min_length=1, max_length=20, description="Postal code")
    country: str = Field(..., min_length=1, max_length=100, description="Country")
    phone: str = Field(..., min_length=1, max_length=50, description="Phone number")


class CustomerAddressResponse(BaseModel):
    """Schema for customer address response"""
    id: int
    user_id: int
    address_type: str
    alias: Optional[str] = None
    name: str
    last_name: str
    company: Optional[str] = None
    address_house_number: str
    house_number: str
    city: str
    postal_code: str
    country: str
    phone: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CustomerAddressUpdate(BaseModel):
    """Schema for updating a customer address"""
    alias: Optional[str] = Field(None, max_length=100, description="Address alias")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name")
    company: Optional[str] = Field(None, max_length=200, description="Company name")
    address_house_number: Optional[str] = Field(None, min_length=1, max_length=200, description="Address and house number")
    house_number: Optional[str] = Field(None, min_length=1, max_length=50, description="House number")
    city: Optional[str] = Field(None, min_length=1, max_length=100, description="City")
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20, description="Postal code")
    country: Optional[str] = Field(None, min_length=1, max_length=100, description="Country")
    phone: Optional[str] = Field(None, min_length=1, max_length=50, description="Phone number")


# ============= Company Address Schemas =============

class CompanyAddressCreate(BaseModel):
    """Schema for creating a company address"""
    alias: Optional[str] = Field(None, max_length=100, description="Address alias (optional)")
    company_name: str = Field(..., min_length=1, max_length=200, description="Company name")
    address_house_number: str = Field(..., min_length=1, max_length=200, description="Address and house number")
    house_number: str = Field(..., min_length=1, max_length=50, description="House number")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    postal_code: str = Field(..., min_length=1, max_length=20, description="Postal code")
    country: str = Field(..., min_length=1, max_length=100, description="Country")
    phone: str = Field(..., min_length=1, max_length=50, description="Phone number")


class CompanyAddressResponse(BaseModel):
    """Schema for company address response"""
    id: int
    user_id: int
    address_type: str
    alias: Optional[str] = None
    company_name: str
    address_house_number: str
    house_number: str
    city: str
    postal_code: str
    country: str
    phone: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CompanyAddressUpdate(BaseModel):
    """Schema for updating a company address"""
    alias: Optional[str] = Field(None, max_length=100, description="Address alias")
    company_name: Optional[str] = Field(None, min_length=1, max_length=200, description="Company name")
    address_house_number: Optional[str] = Field(None, min_length=1, max_length=200, description="Address and house number")
    house_number: Optional[str] = Field(None, min_length=1, max_length=50, description="House number")
    city: Optional[str] = Field(None, min_length=1, max_length=100, description="City")
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20, description="Postal code")
    country: Optional[str] = Field(None, min_length=1, max_length=100, description="Country")
    phone: Optional[str] = Field(None, min_length=1, max_length=50, description="Phone number")
