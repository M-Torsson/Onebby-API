# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


# Association table for warranty-category many-to-many relationship
warranty_categories = Table(
    'warranty_categories',
    Base.metadata,
    Column('warranty_id', Integer, ForeignKey('warranties.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)


class Warranty(Base):
    """Warranty options model"""
    __tablename__ = "warranties"

    id = Column(Integer, primary_key=True, index=True)
    
    # Main fields
    title = Column(String(255), nullable=False)
    subtitle = Column(String(500), nullable=True)
    meta_description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False, default=0)
    image = Column(Text, nullable=True)  # URL to image
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    categories = relationship("Category", secondary=warranty_categories, backref="warranties")
    products = relationship("Product", back_populates="warranty")
    translations = relationship("WarrantyTranslation", back_populates="warranty", cascade="all, delete-orphan")
    features = relationship("WarrantyFeature", back_populates="warranty", cascade="all, delete-orphan", order_by="WarrantyFeature.position")


class WarrantyFeature(Base):
    """Warranty features (key-value pairs)"""
    __tablename__ = "warranty_features"

    id = Column(Integer, primary_key=True, index=True)
    warranty_id = Column(Integer, ForeignKey("warranties.id", ondelete="CASCADE"), nullable=False)
    
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    position = Column(Integer, nullable=False, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    warranty = relationship("Warranty", back_populates="features")


class WarrantyTranslation(Base):
    """Warranty translations for multi-language support"""
    __tablename__ = "warranty_translations"

    id = Column(Integer, primary_key=True, index=True)
    warranty_id = Column(Integer, ForeignKey("warranties.id", ondelete="CASCADE"), nullable=False)
    lang = Column(String(5), nullable=False)  # it, en, fr, de, ar
    
    # Translatable fields
    title = Column(String(255), nullable=True)
    subtitle = Column(String(500), nullable=True)
    meta_description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    warranty = relationship("Warranty", back_populates="translations")
