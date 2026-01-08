from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


# Association table for product-category many-to-many relationship
product_categories = Table(
    'product_categories',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)


# Association table for related products
product_related = Table(
    'product_related',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id', ondelete='CASCADE'), primary_key=True),
    Column('related_product_id', Integer, ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
)


# Association table for allowed shipping services
product_shipping_services = Table(
    'product_shipping_services',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id', ondelete='CASCADE'), primary_key=True),
    Column('service_id', Integer, ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
)


# Association table for allowed warranties
product_warranties = Table(
    'product_warranties',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id', ondelete='CASCADE'), primary_key=True),
    Column('warranty_id', Integer, ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
)


class ProductType(str, enum.Enum):
    """Product types enumeration"""
    CONFIGURABLE = "configurable"  # Product with variants
    SIMPLE = "simple"              # Regular product
    SERVICE = "service"            # Service product (shipping, installation)
    WARRANTY = "warranty"          # Warranty product


class ProductCondition(str, enum.Enum):
    """Product condition enumeration"""
    NEW = "new"
    USED = "used"
    A_PLUS_PLUS = "A++"
    A_PLUS = "A+"
    B_PLUS = "B+"
    C = "C"
    F = "F"


class StockStatus(str, enum.Enum):
    """Stock status enumeration"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    PREORDER = "preorder"


class Product(Base):
    """Product model - supports configurable, simple, service, and warranty products"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_type = Column(SQLEnum(ProductType), nullable=False, default=ProductType.SIMPLE)
    
    # Basic info
    reference = Column(String(100), unique=True, index=True, nullable=False)
    ean = Column(String(255), unique=True, nullable=True, index=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    condition = Column(SQLEnum(ProductCondition), default=ProductCondition.NEW)
    
    # Foreign keys
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    tax_class_id = Column(Integer, ForeignKey("tax_classes.id"), nullable=False)
    
    # Tax settings
    tax_included_in_price = Column(Boolean, default=True)
    
    # Pricing
    price_list = Column(Float, nullable=True)
    currency = Column(String(3), default="EUR")
    
    # Stock
    stock_status = Column(SQLEnum(StockStatus), default=StockStatus.IN_STOCK)
    stock_quantity = Column(Integer, default=0)
    
    # For service/warranty products
    duration_months = Column(Integer, nullable=True)  # For warranties
    
    # Timestamps
    date_add = Column(DateTime(timezone=True), server_default=func.now())
    date_update = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    brand = relationship("Brand", back_populates="products")
    tax_class = relationship("TaxClass", back_populates="products")
    categories = relationship("Category", secondary=product_categories, backref="products")
    translations = relationship("ProductTranslation", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.position")
    features = relationship("ProductFeature", back_populates="product", cascade="all, delete-orphan")
    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")
    variants = relationship("ProductVariant", back_populates="parent_product", cascade="all, delete-orphan")
    variant_attributes = relationship("ProductVariantAttribute", back_populates="product", cascade="all, delete-orphan")
    discounts = relationship("ProductDiscount", back_populates="product", cascade="all, delete-orphan")
    
    # Related products (self-referential many-to-many)
    related_products = relationship(
        "Product",
        secondary=product_related,
        primaryjoin=id == product_related.c.product_id,
        secondaryjoin=id == product_related.c.related_product_id,
        backref="related_to"
    )
    
    # Service links
    allowed_shipping_services = relationship(
        "Product",
        secondary=product_shipping_services,
        primaryjoin=id == product_shipping_services.c.product_id,
        secondaryjoin=id == product_shipping_services.c.service_id,
        backref="used_by_products_shipping"
    )
    
    allowed_warranties = relationship(
        "Product",
        secondary=product_warranties,
        primaryjoin=id == product_warranties.c.product_id,
        secondaryjoin=id == product_warranties.c.warranty_id,
        backref="used_by_products_warranty"
    )


class ProductTranslation(Base):
    """Product translations for multi-language support"""
    __tablename__ = "product_translations"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    lang = Column(String(5), nullable=False)  # it, en, fr, de, ar
    
    title = Column(String(255), nullable=False)
    sub_title = Column(String(500), nullable=True)
    simple_description = Column(Text, nullable=True)
    meta_description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="translations")


class ProductImage(Base):
    """Product images"""
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(500), nullable=False)
    position = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="images")
    alt_texts = relationship("ProductImageAlt", back_populates="image", cascade="all, delete-orphan")


class ProductImageAlt(Base):
    """Product image alt texts for multi-language support"""
    __tablename__ = "product_image_alts"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("product_images.id", ondelete="CASCADE"), nullable=False)
    lang = Column(String(5), nullable=False)
    alt_text = Column(String(255), nullable=False)
    
    # Relationships
    image = relationship("ProductImage", back_populates="alt_texts")


class ProductFeature(Base):
    """Product features (specifications)"""
    __tablename__ = "product_features"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="features")
    translations = relationship("ProductFeatureTranslation", back_populates="feature", cascade="all, delete-orphan")


class ProductFeatureTranslation(Base):
    """Product feature translations"""
    __tablename__ = "product_feature_translations"

    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("product_features.id", ondelete="CASCADE"), nullable=False)
    lang = Column(String(5), nullable=False)
    name = Column(String(255), nullable=False)
    value = Column(String(500), nullable=False)
    
    # Relationships
    feature = relationship("ProductFeature", back_populates="translations")


class ProductAttribute(Base):
    """Product attributes"""
    __tablename__ = "product_attributes"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="attributes")
    translations = relationship("ProductAttributeTranslation", back_populates="attribute", cascade="all, delete-orphan")


class ProductAttributeTranslation(Base):
    """Product attribute translations"""
    __tablename__ = "product_attribute_translations"

    id = Column(Integer, primary_key=True, index=True)
    attribute_id = Column(Integer, ForeignKey("product_attributes.id", ondelete="CASCADE"), nullable=False)
    lang = Column(String(5), nullable=False)
    name = Column(String(255), nullable=False)
    value = Column(String(500), nullable=False)
    
    # Relationships
    attribute = relationship("ProductAttribute", back_populates="translations")


class ProductVariantAttribute(Base):
    """Variant attributes definition (e.g., color, storage)"""
    __tablename__ = "product_variant_attributes"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="variant_attributes")
    translations = relationship("ProductVariantAttributeTranslation", back_populates="variant_attribute", cascade="all, delete-orphan")


class ProductVariantAttributeTranslation(Base):
    """Variant attribute translations (label)"""
    __tablename__ = "product_variant_attribute_translations"

    id = Column(Integer, primary_key=True, index=True)
    variant_attribute_id = Column(Integer, ForeignKey("product_variant_attributes.id", ondelete="CASCADE"), nullable=False)
    lang = Column(String(5), nullable=False)
    label = Column(String(255), nullable=False)
    
    # Relationships
    variant_attribute = relationship("ProductVariantAttribute", back_populates="translations")


class ProductDiscount(Base):
    """Product discounts"""
    __tablename__ = "product_discounts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True)
    
    discount_type = Column(String(20), nullable=False)  # "percentage" or "fixed"
    discount_value = Column(Float, nullable=False)
    
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="discounts")
    variant = relationship("ProductVariant", back_populates="discounts")
