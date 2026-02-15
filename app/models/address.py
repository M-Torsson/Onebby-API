# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Address(BaseModel):
    """Address model for both customers and companies"""
    __tablename__ = "addresses"
    
    # Foreign key to user (can be customer or company)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Address type: 'customer' for individual users, 'company' for companies
    address_type = Column(String, nullable=False)
    
    # Optional alias for the address
    alias = Column(String, nullable=True)
    
    # Name fields - for customer addresses
    name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    
    # Company name - for company addresses
    company_name = Column(String, nullable=True)
    
    # Optional company field for customer addresses
    company = Column(String, nullable=True)
    
    # Address details (required fields)
    address_house_number = Column(String, nullable=False)
    house_number = Column(String, nullable=False)
    city = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    
    # Relationship to user
    user = relationship("User", backref="addresses")
