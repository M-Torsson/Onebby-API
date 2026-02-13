# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel


class User(BaseModel):
    """User model"""
    __tablename__ = "users"
    
    # Registration type: 'user' for customers, 'company' for companies, 'admin' for administrators
    reg_type = Column(String, default="user", nullable=False)
    
    # Title (e.g., Sig., Sig.ra, etc.) - for individual users only
    title = Column(String, nullable=True)
    
    # Name fields - for individual users
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)  # Keep for backward compatibility
    
    # Company fields - for company registration
    company_name = Column(String, nullable=True)
    vat_number = Column(String, nullable=True)  # VAT/Partita IVA
    tax_code = Column(String, nullable=True)  # Codice Fiscale (required for Italian companies)
    sdi_code = Column(String, nullable=True)  # SDI Code
    pec = Column(String, nullable=True)  # PEC Email (required for Italian companies)
    
    # Company approval status - only for companies (pending/approved/rejected)
    approval_status = Column(String, default="pending", nullable=True)  # For companies only
    
    # Authentication fields
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)  # Optional for customers
    hashed_password = Column(String, nullable=False)
    
    # Status fields
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
