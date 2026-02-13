# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel


class User(BaseModel):
    """User model"""
    __tablename__ = "users"
    
    # Registration type: 'user' for customers, 'admin' for administrators
    reg_type = Column(String, default="user", nullable=False)
    
    # Title (e.g., Sig., Sig.ra, etc.)
    title = Column(String, nullable=True)
    
    # Name fields
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)  # Keep for backward compatibility
    
    # Authentication fields
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)  # Optional for customers
    hashed_password = Column(String, nullable=False)
    
    # Status fields
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
