# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.session import Base


class DiscountTypeEnum(str, enum.Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"


class TargetTypeEnum(str, enum.Enum):
    PRODUCTS = "products"  # قائمة منتجات محددة
    CATEGORY = "category"  # كاتيغوري واحد
    BRAND = "brand"        # براند واحد
    ALL = "all"           # كل المنتجات


class DiscountCampaign(Base):
    """Discount campaigns that can be applied to products, categories, or brands"""
    __tablename__ = "discount_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    
    # Campaign info
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    
    # Discount details
    discount_type = Column(SQLEnum(DiscountTypeEnum), nullable=False)
    discount_value = Column(Float, nullable=False)
    
    # Target
    target_type = Column(SQLEnum(TargetTypeEnum), nullable=False)
    target_ids = Column(JSON, nullable=True)  # List of IDs [35965, 35966] or [8154]
    
    # Date range
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    created_by = Column(Integer, nullable=True)  # User ID who created the campaign

    def __repr__(self):
        return f"<DiscountCampaign(id={self.id}, name='{self.name}', type={self.discount_type}, value={self.discount_value})>"
