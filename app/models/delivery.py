# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


# Association table for delivery-category many-to-many relationship
delivery_categories = Table(
    'delivery_categories',
    Base.metadata,
    Column('delivery_id', Integer, ForeignKey('deliveries.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)


class Delivery(Base):
    """Delivery options model"""
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    
    # Delivery time estimation
    days_from = Column(Integer, nullable=False, default=0)
    days_to = Column(Integer, nullable=False, default=0)
    
    # General note
    note = Column(Text, nullable=True)
    
    # Option note
    option_note = Column(Text, nullable=True)
    
    # Free delivery flag
    is_free_delivery = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    categories = relationship("Category", secondary=delivery_categories, backref="deliveries")
    products = relationship("Product", back_populates="delivery")
    translations = relationship("DeliveryTranslation", back_populates="delivery", cascade="all, delete-orphan")
    options = relationship("DeliveryOption", back_populates="delivery", cascade="all, delete-orphan", order_by="DeliveryOption.position")


class DeliveryOption(Base):
    """Delivery options (like: standard, express, with installation)"""
    __tablename__ = "delivery_options"

    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id", ondelete="CASCADE"), nullable=False)
    
    icon = Column(String(500), nullable=True)
    details = Column(Text, nullable=True)
    price = Column(Float, nullable=False, default=0)
    position = Column(Integer, nullable=False, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    delivery = relationship("Delivery", back_populates="options")


class DeliveryTranslation(Base):
    """Delivery translations for multi-language support"""
    __tablename__ = "delivery_translations"

    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id", ondelete="CASCADE"), nullable=False)
    lang = Column(String(5), nullable=False)  # it, en, fr, de, ar
    
    # Translatable fields
    note = Column(Text, nullable=True)
    option_note = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    delivery = relationship("Delivery", back_populates="translations")
