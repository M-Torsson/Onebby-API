# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel


class Order(BaseModel):
    """
    Order model - supports customers, companies, and guest orders
    
    Stores complete order information including user/company details,
    billing/shipping addresses, payment info, and order items.
    """
    __tablename__ = "orders"
    
    # ========== User Reference ==========
    # Foreign key to user (nullable for guest orders)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Session ID for guest orders (not logged in)
    session_id = Column(String(255), nullable=True, index=True)
    
    # User type: 'customer', 'company', 'guest'
    user_type = Column(String(50), nullable=False, default="customer")
    
    # ========== Customer/Company Information ==========
    # Store customer/company info as JSON for legal/accounting purposes
    # This preserves the data as it was at the time of order
    # (user info might change, but order info must remain constant)
    
    # For customers (reg_type = 'user'):
    # {
    #   "reg_type": "user",
    #   "title": "Sig.",
    #   "first_name": "John",
    #   "last_name": "Doe",
    #   "email": "john@example.com"
    # }
    #
    # For companies (reg_type = 'company'):
    # {
    #   "reg_type": "company",
    #   "company_name": "ABC SRL",
    #   "email": "company@example.com",
    #   "vat_number": "IT12345678901",
    #   "tax_code": "12345678901",
    #   "sdi_code": "ABCDEFG",
    #   "pec": "company@pec.it"
    # }
    customer_info = Column(JSON, nullable=False)
    
    # ========== Addresses ==========
    # Billing address (JSON copy from Address model or from checkout form)
    # {
    #   "address_type": "customer" / "company",
    #   "name": "John",
    #   "last_name": "Doe",
    #   "company_name": "ABC SRL",  (if company)
    #   "address_house_number": "Via Roma 123",
    #   "house_number": "123",
    #   "city": "Milan",
    #   "postal_code": "20100",
    #   "country": "Italy",
    #   "phone": "+39 123456789"
    # }
    billing_address = Column(JSON, nullable=False)
    
    # Shipping address (JSON, can be same as billing or different)
    shipping_address = Column(JSON, nullable=False)
    
    # ========== Financial Information ==========
    # Prices in EUR (stored as Numeric for precision)
    subtotal = Column(Numeric(10, 2), nullable=False)  # Sum of all items (products + warranties + delivery)
    shipping_cost = Column(Numeric(10, 2), nullable=False, default=0.0)
    tax = Column(Numeric(10, 2), nullable=False, default=0.0)  # IVA
    discount = Column(Numeric(10, 2), nullable=False, default=0.0)
    total_amount = Column(Numeric(10, 2), nullable=False)  # subtotal + shipping + tax - discount
    
    # Currency (default EUR)
    currency = Column(String(3), nullable=False, default="EUR")
    
    # ========== Payment Information ==========
    # Payment status: pending, processing, completed, failed, refunded, cancelled
    payment_status = Column(String(50), nullable=False, default="pending", index=True)
    
    # Payment method: paypal, scalapay, floa, stripe, bank_transfer
    payment_method = Column(String(50), nullable=True)
    
    # Payment transaction ID from payment gateway
    payment_transaction_id = Column(String(255), nullable=True)
    
    # ========== Shipping Information ==========
    # Shipping method: shippy_pro, poste_italiane, express, standard
    shipping_method = Column(String(100), nullable=True)
    
    # Shipping status: pending, processing, shipped, in_transit, delivered, cancelled, returned
    shipping_status = Column(String(50), nullable=False, default="pending", index=True)
    
    # Tracking number from shipping provider
    tracking_number = Column(String(255), nullable=True)
    
    # ========== Order Status ==========
    # Overall order status: pending, confirmed, processing, completed, cancelled, refunded
    status = Column(String(50), nullable=False, default="pending", index=True)
    
    # ========== Notes ==========
    # Customer note (from checkout)
    customer_note = Column(Text, nullable=True)
    
    # Admin note (internal use)
    admin_note = Column(Text, nullable=True)
    
    # ========== Timestamps ==========
    # Auto-managed timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Event timestamps
    paid_at = Column(DateTime(timezone=True), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # ========== Relationships ==========
    # Relationship to user (nullable for guest orders)
    user = relationship("User", backref="orders")
    
    # Relationship to order items
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status}, total={self.total_amount})>"


class OrderItem(BaseModel):
    """
    Order Item model - represents a product in an order
    
    Stores product information as it was at the time of order,
    including price, warranty option, and delivery option.
    """
    __tablename__ = "order_items"
    
    # ========== Relationships ==========
    # Foreign key to order
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Foreign key to product (for reference, but we store info below)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Foreign key to product variant (if applicable)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    
    # ========== Product Information ==========
    # Store product details as they were at time of order
    # (prices and details might change, but order must remain constant)
    
    product_title = Column(String(500), nullable=False)  # Product name
    product_sku = Column(String(100), nullable=True)  # Product SKU
    product_type = Column(String(50), nullable=True)  # simple, configurable, service, warranty
    
    # Product image (for order display)
    product_image = Column(Text, nullable=True)
    
    # ========== Pricing ==========
    quantity = Column(Integer, nullable=False, default=1)
    
    # Unit price (base product price at time of order)
    unit_price = Column(Numeric(10, 2), nullable=False)
    
    # Item subtotal (unit_price × quantity)
    # Does NOT include warranty or delivery options
    subtotal = Column(Numeric(10, 2), nullable=False)
    
    # Discount applied to this item (if any)
    discount = Column(Numeric(10, 2), nullable=False, default=0.0)
    
    # ========== Options ==========
    # Delivery option selected by customer (JSON)
    # Example:
    # {
    #   "id": 1,
    #   "title": "Delivery to floor with installation",
    #   "description": "Professional delivery and installation",
    #   "price": 339.99,
    #   "days": "3-5"
    # }
    delivery_option = Column(JSON, nullable=True)
    
    # Warranty option selected by customer (JSON)
    # Example (before Garanzia3 registration):
    # {
    #   "id": 1,
    #   "title": "GARANZIA3 - Extended Warranty 3 Years",
    #   "price": 49.90,
    #   "duration_months": 36,
    #   "image": "https://...",
    #   "contract_number": null,
    #   "pin_code": null,
    #   "registered_at": null,
    #   "registration_error": null
    # }
    #
    # After Garanzia3 registration (updated by Garanzia3Service):
    # {
    #   "id": 1,
    #   "title": "GARANZIA3 - Extended Warranty 3 Years",
    #   "price": 49.90,
    #   "duration_months": 36,
    #   "image": "https://...",
    #   "contract_number": "G3-2026-001234",  ← Added by Garanzia3
    #   "pin_code": "A1B2C3D4",               ← Added by Garanzia3
    #   "registered_at": "2026-02-23T10:35:00Z",  ← Added by Garanzia3
    #   "registration_error": null
    # }
    warranty_option = Column(JSON, nullable=True)
    
    # ========== Variant Information ==========
    # Store variant attributes (if product is configurable)
    # Example:
    # {
    #   "color": "Red",
    #   "size": "Large",
    #   "storage": "256GB"
    # }
    variant_attributes = Column(JSON, nullable=True)
    
    # ========== Timestamps ==========
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # ========== Relationships ==========
    # Relationship to order
    order = relationship("Order", back_populates="items")
    
    # Relationship to product (nullable if product is deleted)
    product = relationship("Product", backref="order_items")
    
    # Relationship to product variant (nullable)
    product_variant = relationship("ProductVariant", backref="order_items")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})>"
