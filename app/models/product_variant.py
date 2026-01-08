from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
from app.models.product import ProductCondition, StockStatus


class ProductVariant(Base):
    """Product variant model - for configurable products"""
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    parent_product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    
    # Basic info
    reference = Column(String(100), unique=True, index=True, nullable=False)
    ean = Column(String(255), unique=True, nullable=True, index=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    condition = Column(SQLEnum(ProductCondition), default=ProductCondition.NEW)
    
    # Attributes (stored as JSON for flexibility)
    # Example: {"color": "black", "storage": "128"}
    attributes = Column(JSON, nullable=False)
    
    # Pricing
    price_list = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    
    # Stock
    stock_status = Column(SQLEnum(StockStatus), default=StockStatus.IN_STOCK)
    stock_quantity = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    parent_product = relationship("Product", back_populates="variants")
    images = relationship("ProductVariantImage", back_populates="variant", cascade="all, delete-orphan", order_by="ProductVariantImage.position")
    discounts = relationship("ProductDiscount", back_populates="variant", cascade="all, delete-orphan")


class ProductVariantImage(Base):
    """Product variant images"""
    __tablename__ = "product_variant_images"

    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(500), nullable=False)
    position = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    variant = relationship("ProductVariant", back_populates="images")
    alt_texts = relationship("ProductVariantImageAlt", back_populates="image", cascade="all, delete-orphan")


class ProductVariantImageAlt(Base):
    """Product variant image alt texts for multi-language support"""
    __tablename__ = "product_variant_image_alts"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("product_variant_images.id", ondelete="CASCADE"), nullable=False)
    lang = Column(String(5), nullable=False)
    alt_text = Column(String(255), nullable=False)
    
    # Relationships
    image = relationship("ProductVariantImage", back_populates="alt_texts")
