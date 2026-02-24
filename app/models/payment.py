# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel


class Payment(BaseModel):
    """
    Payment model - tracks all payment transactions
    
    Supports multiple payment providers:
    - Payplug (Credit Card)
    - Floa (Buy Now Pay Later - 3X & 4X)
    - Findomestic (Installments)
    
    Works in two modes:
    - test: Mock mode for development/testing
    - production: Real payment gateway integration
    """
    __tablename__ = "payments"
    
    # ========== Order Reference ==========
    # Foreign key to order
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ========== Payment Provider ==========
    # Payment provider: payplug, floa, findomestic
    provider = Column(String(50), nullable=False, index=True)
    
    # Payment method: credit_card, bnpl_3x, bnpl_4x, installments
    payment_method = Column(String(50), nullable=False)
    
    # ========== Payment Information ==========
    # Amount to be paid (in EUR)
    amount = Column(Numeric(10, 2), nullable=False)
    
    # Currency (default EUR)
    currency = Column(String(3), nullable=False, default="EUR")
    
    # Payment status: pending, processing, completed, failed, cancelled, refunded
    status = Column(String(50), nullable=False, default="pending", index=True)
    
    # ========== Provider Data ==========
    # Provider payment ID (from payment gateway)
    provider_payment_id = Column(String(255), nullable=True, unique=True, index=True)
    
    # Provider transaction ID
    provider_transaction_id = Column(String(255), nullable=True)
    
    # Payment URL (redirect customer to payment page)
    payment_url = Column(Text, nullable=True)
    
    # ========== Payment Details ==========
    # Provider metadata (JSON - provider-specific data)
    # For Payplug: {hosted_payment: {...}, card: {...}}
    # For Floa: {plan: "3x", installments: [...], bnpl_details: {...}}
    # For Findomestic: {installments: 12, monthly_rate: 1.4%, ...}
    provider_metadata = Column(JSON, nullable=True)
    
    # Customer payment info (card last 4 digits, etc.)
    # Example: {card_last4: "1234", card_brand: "Visa", card_country: "IT"}
    payment_info = Column(JSON, nullable=True)
    
    # ========== Status Tracking ==========
    # Error message (if payment failed)
    error_message = Column(Text, nullable=True)
    
    # Error code (provider-specific)
    error_code = Column(String(100), nullable=True)
    
    # ========== Testing & Development ==========
    # Is this a test payment? (for development/staging)
    is_test = Column(Boolean, nullable=False, default=False)
    
    # Test mode identifier (for mock payments)
    # Example: "mock_success", "mock_failure", "mock_cancelled"
    test_scenario = Column(String(50), nullable=True)
    
    # ========== Refund Information ==========
    # Refunded amount (if partial refund)
    refunded_amount = Column(Numeric(10, 2), nullable=True, default=0.0)
    
    # Refund reason
    refund_reason = Column(Text, nullable=True)
    
    # Refund transaction ID
    refund_transaction_id = Column(String(255), nullable=True)
    
    # ========== Timestamps ==========
    # Auto-managed timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Event timestamps (track state changes precisely)
    processing_at = Column(DateTime(timezone=True), nullable=True)  # When payment started processing
    completed_at = Column(DateTime(timezone=True), nullable=True)   # When payment completed
    failed_at = Column(DateTime(timezone=True), nullable=True)      # When payment failed
    cancelled_at = Column(DateTime(timezone=True), nullable=True)   # When payment cancelled
    refunded_at = Column(DateTime(timezone=True), nullable=True)    # When payment refunded
    
    # ========== Relationships ==========
    # Relationship to order
    order = relationship("Order", backref="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, provider={self.provider}, status={self.status}, amount={self.amount})>"
