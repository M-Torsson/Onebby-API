# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, DateTime, func, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Cart(BaseModel):
    """Cart model for storing user shopping carts"""
    __tablename__ = "carts"
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    # Session ID for guest users (not logged in)
    session_id = Column(String, nullable=True, index=True)
    
    # Cart status: active, completed, abandoned
    status = Column(String, default="active", nullable=False, index=True)
    
    # Expiration date for abandoned carts
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(BaseModel):
    """Cart Item model for storing products in cart"""
    __tablename__ = "cart_items"
    
    # Foreign key to cart
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    
    # Foreign key to product
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    
    # Foreign key to product variant (optional)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    
    # Quantity of product
    quantity = Column(Integer, nullable=False, default=1)
    
    # Price at the time of adding to cart (to track price changes)
    price_at_add = Column(Numeric(10, 2), nullable=False)
    
    # Discount at the time of adding to cart (optional)
    discount_at_add = Column(Numeric(10, 2), nullable=True, default=0)
    
    # Delivery option selected by user (optional, JSON format)
    # Example: {"option": "delivery to floor with installation", "price": 339.99}
    delivery_option = Column(JSON, nullable=True)
    
    # Warranty option selected by user (optional, JSON format)
    # Example: {"id": 1, "title": "GARANZIA3", "image": "url", "price": 49.9}
    warranty_option = Column(JSON, nullable=True)
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", backref="cart_items")
    product_variant = relationship("ProductVariant", backref="cart_items")
