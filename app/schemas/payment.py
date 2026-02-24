# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


# ========== Payment Schemas ==========

class PaymentBase(BaseModel):
    """Base schema for payment"""
    provider: str = Field(..., description="Payment provider: payplug, floa, findomestic")
    payment_method: str = Field(..., description="Payment method: credit_card, bnpl_3x, bnpl_4x, installments")
    currency: str = Field(default="EUR", description="Currency code")


class PaymentCreate(PaymentBase):
    """
    Schema for creating a payment
    
    This is called when customer chooses payment method at checkout.
    The order_id is passed separately in the API call.
    
    Note: amount is optional - if not provided, it will be taken from order.total_price
    """
    # Amount is optional - will use order.total_price if not provided
    amount: Optional[Decimal] = Field(None, gt=0, description="Payment amount in EUR (optional, defaults to order total)")
    
    # Optional metadata from frontend
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional payment metadata")
    
    # For testing purposes
    test_scenario: Optional[str] = Field(None, description="Test scenario: mock_success, mock_failure, mock_cancelled")
    
    @validator('provider')
    def validate_provider(cls, v):
        """Validate payment provider"""
        allowed_providers = ['payplug', 'floa', 'findomestic', 'mock']
        if v not in allowed_providers:
            raise ValueError(f"Invalid provider. Allowed: {', '.join(allowed_providers)}")
        return v
    
    @validator('payment_method')
    def validate_payment_method(cls, v, values):
        """Validate payment method based on provider"""
        provider = values.get('provider')
        
        if provider == 'payplug':
            if v not in ['credit_card']:
                raise ValueError("Payplug only supports 'credit_card'")
        elif provider == 'floa':
            if v not in ['bnpl_3x', 'bnpl_4x']:
                raise ValueError("Floa only supports 'bnpl_3x' or 'bnpl_4x'")
        elif provider == 'findomestic':
            if v not in ['installments']:
                raise ValueError("Findomestic only supports 'installments'")
        elif provider == 'mock':
            # Mock accepts any payment method
            pass
        
        return v


class PaymentUpdate(BaseModel):
    """
    Schema for updating a payment (Admin or Webhook)
    
    Used by:
    - Webhook handlers to update payment status
    - Admin to manually update failed payments
    """
    status: Optional[str] = Field(None, description="Payment status")
    provider_payment_id: Optional[str] = None
    provider_transaction_id: Optional[str] = None
    payment_info: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('status')
    def validate_status(cls, v):
        """Validate payment status"""
        if v is not None:
            allowed_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled', 'refunded']
            if v not in allowed_statuses:
                raise ValueError(f"Invalid status. Allowed: {', '.join(allowed_statuses)}")
        return v


class PaymentResponse(BaseModel):
    """
    Schema for payment response
    
    Returned to frontend after creating payment.
    Contains payment_url for redirect.
    """
    id: int
    order_id: int
    provider: str
    payment_method: str
    amount: Decimal
    currency: str
    status: str
    
    # Payment URL for redirect
    payment_url: Optional[str]
    
    # Provider IDs
    provider_payment_id: Optional[str]
    provider_transaction_id: Optional[str]
    
    # Payment info (card details, etc.)
    payment_info: Optional[Dict[str, Any]]
    
    # Provider-specific metadata
    provider_metadata: Optional[Dict[str, Any]]
    
    # Error info
    error_message: Optional[str]
    error_code: Optional[str]
    
    # Testing info
    is_test: bool
    test_scenario: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    processing_at: Optional[datetime]
    completed_at: Optional[datetime]
    failed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PaymentListItem(BaseModel):
    """
    Schema for payment list item (summary)
    
    Used in admin dashboard to list all payments.
    """
    id: int
    order_id: int
    provider: str
    payment_method: str
    amount: Decimal
    currency: str
    status: str
    provider_payment_id: Optional[str]
    is_test: bool
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class RefundCreate(BaseModel):
    """
    Schema for creating a refund
    
    Used by admin to refund a payment.
    """
    amount: Optional[Decimal] = Field(None, description="Refund amount. If None, full refund.")
    reason: str = Field(..., max_length=500, description="Refund reason")
    
    @validator('amount')
    def validate_amount(cls, v):
        """Validate refund amount"""
        if v is not None and v <= 0:
            raise ValueError("Refund amount must be greater than 0")
        return v


class RefundResponse(BaseModel):
    """
    Schema for refund response
    """
    payment_id: int
    refunded_amount: Decimal
    refund_transaction_id: Optional[str]
    refund_reason: str
    refunded_at: datetime
    
    class Config:
        from_attributes = True


# ========== Webhook Schemas ==========

class WebhookPayload(BaseModel):
    """
    Generic webhook payload schema
    
    Each provider has different webhook format,
    but we normalize it to this schema.
    """
    event_type: str = Field(..., description="Event type: payment.completed, payment.failed, etc.")
    provider_payment_id: str = Field(..., description="Payment ID from provider")
    status: str = Field(..., description="Payment status")
    amount: Optional[Decimal] = None
    transaction_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


# ========== Mock Payment Schemas ==========

class MockPaymentSimulation(BaseModel):
    """
    Schema for simulating payment completion (test mode only)
    
    Used in test environment to simulate webhook calls.
    """
    payment_id: int
    scenario: str = Field(..., description="Simulation scenario: success, failure, cancelled")
    error_message: Optional[str] = Field(None, description="Error message if scenario=failure")
    
    @validator('scenario')
    def validate_scenario(cls, v):
        """Validate simulation scenario"""
        allowed_scenarios = ['success', 'failure', 'cancelled']
        if v not in allowed_scenarios:
            raise ValueError(f"Invalid scenario. Allowed: {', '.join(allowed_scenarios)}")
        return v
