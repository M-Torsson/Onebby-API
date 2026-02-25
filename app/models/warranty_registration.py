# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class WarrantyRegistration(Base):
    """
    Warranty Registration Model - Tracks warranties registered with Garanzia3
    
    After a successful payment that includes a warranty product, this model stores
    the registration details received from Garanzia3 API (transaction ID and PIN).
    """
    __tablename__ = "warranty_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ========== Order & Product References ==========
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    warranty_id = Column(Integer, ForeignKey("warranties.id", ondelete="SET NULL"), nullable=True)
    
    # ========== Customer Information ==========
    customer_name = Column(String(255), nullable=False)
    customer_lastname = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    
    # ========== Product Information ==========
    product_ean13 = Column(String(13), nullable=False, index=True)
    product_name = Column(String(500), nullable=True)
    
    # ========== Garanzia3 Response Data ==========
    g3_transaction_id = Column(String(255), unique=True, nullable=True, index=True)  # Transaction ID from G3
    g3_pin = Column(String(255), nullable=True)  # PIN code from G3
    g3_response = Column(Text, nullable=True)  # Full JSON response from G3
    
    # ========== Registration Status ==========
    status = Column(String(50), nullable=False, default="pending", index=True)
    # pending: Not yet registered
    # registered: Successfully registered with G3
    # failed: Registration failed
    # cancelled: Registration cancelled
    
    # ========== Error Tracking ==========
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    
    # ========== Testing ==========
    is_test = Column(Boolean, nullable=False, default=False)
    
    # ========== Timestamps ==========
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    registered_at = Column(DateTime(timezone=True), nullable=True)  # When registered with G3
    failed_at = Column(DateTime(timezone=True), nullable=True)  # When registration failed
    
    # ========== Relationships ==========
    order = relationship("Order", backref="warranty_registrations")
    product = relationship("Product", backref="warranty_registrations")
    warranty = relationship("Warranty", backref="registrations")
    
    def __repr__(self):
        return f"<WarrantyRegistration(id={self.id}, order_id={self.order_id}, status={self.status}, g3_transaction={self.g3_transaction_id})>"
