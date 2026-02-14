# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=6, max_length=72)


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=72)


class UserInDB(UserBase):
    """User schema as stored in database"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """User schema for API responses"""
    pass


# Token Schemas
class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    user_id: int  # User/Customer/Company ID


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[int] = None
    username: Optional[str] = None


# Login Schema
class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str


# ============= Customer Registration Schemas =============

class CustomerRegisterRequest(BaseModel):
    """Customer registration request schema"""
    reg_type: str = Field(default="user", description="Registration type (user/admin)")
    title: str = Field(..., max_length=20, description="Title (e.g., Sig., Sig.ra)")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, max_length=72, description="Password")


class CustomerResponse(BaseModel):
    """Customer response schema"""
    id: int
    reg_type: str
    title: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CustomerLoginRequest(BaseModel):
    """Customer login request schema"""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")


# ============= Company Registration Schemas =============

class CompanyRegisterRequest(BaseModel):
    """Company registration request schema"""
    reg_type: str = Field(default="company", description="Registration type (must be 'company')")
    company_name: str = Field(..., min_length=1, max_length=200, description="Company name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, max_length=72, description="Password")
    vat_number: str = Field(..., min_length=1, max_length=50, description="VAT Number / Partita IVA")
    tax_code: Optional[str] = Field(None, max_length=50, description="Tax Code / Codice Fiscale (required for Italian companies)")
    sdi_code: str = Field(..., min_length=1, max_length=20, description="SDI Code")
    pec: Optional[str] = Field(None, max_length=100, description="PEC Email (required for Italian companies)")
    
    @classmethod
    def validate_italian_company(cls, values):
        """Validate that Italian companies have required fields"""
        # If tax_code is provided, assume it's an Italian company and require pec
        if values.get('tax_code') and not values.get('pec'):
            raise ValueError('PEC is required for Italian companies (when tax_code is provided)')
        # If pec is provided, assume it's an Italian company and require tax_code
        if values.get('pec') and not values.get('tax_code'):
            raise ValueError('Tax code is required for Italian companies (when PEC is provided)')
        return values


class CompanyResponse(BaseModel):
    """Company response schema"""
    id: int
    reg_type: str
    company_name: Optional[str] = None
    email: EmailStr
    vat_number: Optional[str] = None
    tax_code: Optional[str] = None
    sdi_code: Optional[str] = None
    pec: Optional[str] = None
    approval_status: Optional[str] = None  # pending/approved/rejected
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CompanyLoginRequest(BaseModel):
    """Company login request schema"""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")


# ============= Update Schemas =============

class CustomerUpdateRequest(BaseModel):
    """Customer update request schema"""
    title: Optional[str] = Field(None, max_length=20, description="Title")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    password: Optional[str] = Field(None, min_length=6, max_length=72, description="Password")


class CompanyUpdateRequest(BaseModel):
    """Company update request schema"""
    company_name: Optional[str] = Field(None, min_length=1, max_length=200, description="Company name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    password: Optional[str] = Field(None, min_length=6, max_length=72, description="Password")
    vat_number: Optional[str] = Field(None, min_length=1, max_length=50, description="VAT Number")
    tax_code: Optional[str] = Field(None, max_length=50, description="Tax Code")
    sdi_code: Optional[str] = Field(None, min_length=1, max_length=20, description="SDI Code")
    pec: Optional[str] = Field(None, max_length=100, description="PEC Email")
    approval_status: Optional[str] = Field(None, description="Approval status (pending/approved/rejected)")
