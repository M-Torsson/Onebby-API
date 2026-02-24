# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime

from app.models.payment import Payment
from app.models.order import Order
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.services.payment import PaymentFactory, PaymentProviderError


class CRUDPayment:
    """
    CRUD operations for Payment model
    
    Handles all database operations for payments including:
    - Creating payments
    - Updating payment status
    - Retrieving payment information
    - Processing refunds
    """
    
    def create(
        self,
        db: Session,
        *,
        order_id: int,
        payment_in: PaymentCreate
    ) -> Payment:
        """
        Create a new payment record
        
        Args:
            db: Database session
            order_id: Order ID
            payment_in: Payment creation schema
        
        Returns:
            Created Payment object
        """
        
        # Create payment object
        payment = Payment(
            order_id=order_id,
            provider=payment_in.provider,
            payment_method=payment_in.payment_method,
            amount=payment_in.amount,
            currency=payment_in.currency,
            status='pending',
            provider_metadata=payment_in.metadata,
            is_test=payment_in.provider == 'mock' or payment_in.test_scenario is not None,
            test_scenario=payment_in.test_scenario
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        return payment
    
    async def initiate_payment(
        self,
        db: Session,
        *,
        order_id: int,
        payment_in: PaymentCreate,
        return_url: str,
        cancel_url: str,
        webhook_url: str
    ) -> Payment:
        """
        Create payment and initiate with provider
        
        This method:
        1. Creates payment record in DB
        2. Calls payment provider to create payment
        3. Updates payment record with provider response
        
        Args:
            db: Database session
            order_id: Order ID
            payment_in: Payment creation schema
            return_url: URL to redirect after success
            cancel_url: URL to redirect after cancel
            webhook_url: URL for webhook notifications
        
        Returns:
            Payment object with payment_url
        
        Raises:
            PaymentProviderError: If provider fails
        """
        
        # Get order
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        # Create payment record
        payment = self.create(db, order_id=order_id, payment_in=payment_in)
        
        try:
            # Get payment provider
            provider = PaymentFactory.create(payment_in.provider)
            
            # Prepare customer info
            customer_info = order.customer_info
            
            # Create payment with provider
            provider_response = await provider.create_payment(
                order_id=order_id,
                amount=payment_in.amount,
                currency=payment_in.currency,
                payment_method=payment_in.payment_method,
                customer_info=customer_info,
                return_url=return_url,
                cancel_url=cancel_url,
                webhook_url=webhook_url,
                metadata=payment_in.metadata
            )
            
            # Update payment with provider response
            payment.provider_payment_id = provider_response.get('provider_payment_id')
            payment.payment_url = provider_response.get('payment_url')
            payment.status = provider_response.get('status', 'pending')
            payment.provider_metadata = provider_response.get('metadata', payment.provider_metadata)
            
            # Mark as processing
            if payment.status == 'processing':
                payment.processing_at = datetime.now()
            
            db.commit()
            db.refresh(payment)
            
            return payment
        
        except Exception as e:
            # Update payment with error
            payment.status = 'failed'
            payment.error_message = str(e)
            payment.failed_at = datetime.now()
            db.commit()
            raise
    
    def get(self, db: Session, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        return db.query(Payment).filter(Payment.id == payment_id).first()
    
    def get_by_provider_id(self, db: Session, provider_payment_id: str) -> Optional[Payment]:
        """Get payment by provider payment ID"""
        return db.query(Payment).filter(
            Payment.provider_payment_id == provider_payment_id
        ).first()
    
    def get_by_order(self, db: Session, order_id: int) -> List[Payment]:
        """Get all payments for an order"""
        return db.query(Payment).filter(Payment.order_id == order_id).order_by(Payment.created_at.desc()).all()
    
    def get_latest_by_order(self, db: Session, order_id: int) -> Optional[Payment]:
        """Get latest payment for an order"""
        return db.query(Payment).filter(
            Payment.order_id == order_id
        ).order_by(Payment.created_at.desc()).first()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        is_test: Optional[bool] = None
    ) -> List[Payment]:
        """
        Get multiple payments with optional filters
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records
            provider: Filter by provider
            status: Filter by status
            is_test: Filter by test mode
        
        Returns:
            List of Payment objects
        """
        
        query = db.query(Payment)
        
        if provider:
            query = query.filter(Payment.provider == provider)
        
        if status:
            query = query.filter(Payment.status == status)
        
        if is_test is not None:
            query = query.filter(Payment.is_test == is_test)
        
        return query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    def update(
        self,
        db: Session,
        *,
        payment: Payment,
        payment_in: PaymentUpdate
    ) -> Payment:
        """
        Update payment
        
        Args:
            db: Database session
            payment: Payment object to update
            payment_in: Payment update schema
        
        Returns:
            Updated Payment object
        """
        
        update_data = payment_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(payment, field, value)
        
        # Update timestamps based on status
        if payment_in.status:
            now = datetime.now()
            if payment_in.status == 'processing' and not payment.processing_at:
                payment.processing_at = now
            elif payment_in.status == 'completed' and not payment.completed_at:
                payment.completed_at = now
            elif payment_in.status == 'failed' and not payment.failed_at:
                payment.failed_at = now
            elif payment_in.status == 'cancelled' and not payment.cancelled_at:
                payment.cancelled_at = now
        
        db.commit()
        db.refresh(payment)
        
        return payment
    
    async def check_status(
        self,
        db: Session,
        payment: Payment
    ) -> Payment:
        """
        Check payment status with provider
        
        Args:
            db: Database session
            payment: Payment object
        
        Returns:
            Updated Payment object
        """
        
        if not payment.provider_payment_id:
            return payment
        
        try:
            # Get payment provider
            provider = PaymentFactory.create(payment.provider)
            
            # Get status from provider
            status_response = await provider.get_payment_status(payment.provider_payment_id)
            
            # Update payment
            payment.status = status_response.get('status', payment.status)
            
            if 'transaction_id' in status_response:
                payment.provider_transaction_id = status_response['transaction_id']
            
            if 'payment_info' in status_response:
                payment.payment_info = status_response['payment_info']
            
            # Update timestamps
            now = datetime.now()
            if payment.status == 'completed' and not payment.completed_at:
                payment.completed_at = now
            elif payment.status == 'failed' and not payment.failed_at:
                payment.failed_at = now
            elif payment.status == 'cancelled' and not payment.cancelled_at:
                payment.cancelled_at = now
            
            db.commit()
            db.refresh(payment)
        
        except Exception as e:
            # Log error but don't fail
            pass
        
        return payment
    
    async def refund(
        self,
        db: Session,
        *,
        payment: Payment,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Payment:
        """
        Refund a payment
        
        Args:
            db: Database session
            payment: Payment object
            amount: Amount to refund (None for full refund)
            reason: Refund reason
        
        Returns:
            Updated Payment object
        
        Raises:
            ValueError: If payment cannot be refunded
            PaymentProviderError: If refund fails
        """
        
        # Validate payment can be refunded
        if payment.status != 'completed':
            raise ValueError("Only completed payments can be refunded")
        
        if payment.refunded_amount and payment.refunded_amount >= payment.amount:
            raise ValueError("Payment already fully refunded")
        
        # Default to full refund if amount not specified
        if amount is None:
            amount = float(payment.amount - (payment.refunded_amount or 0))
        
        try:
            # Get payment provider
            provider = PaymentFactory.create(payment.provider)
            
            # Process refund
            refund_response = await provider.refund_payment(
                provider_payment_id=payment.provider_payment_id,
                amount=amount,
                reason=reason
            )
            
            # Update payment
            payment.refunded_amount = (payment.refunded_amount or 0) + amount
            payment.refund_reason = reason
            payment.refund_transaction_id = refund_response.get('refund_id')
            payment.refunded_at = datetime.now()
            
            # Update status if fully refunded
            if payment.refunded_amount >= payment.amount:
                payment.status = 'refunded'
            
            db.commit()
            db.refresh(payment)
            
            return payment
        
        except Exception as e:
            raise PaymentProviderError(
                message=f"Refund failed: {str(e)}",
                provider=payment.provider
            )


# Create singleton instance
crud_payment = CRUDPayment()
