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
