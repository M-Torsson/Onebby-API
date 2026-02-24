# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.session import get_db
from app.schemas.payment import (
    PaymentCreate, PaymentResponse, PaymentListItem,
    RefundCreate, RefundResponse, MockPaymentSimulation
)
from app.crud.payment import crud_payment
from app.crud.order import crud_order
from app.core.security.api_key import verify_api_key
from app.core.security.dependencies import get_current_active_user
from app.core.config import settings
from app.services.payment import PaymentProviderError

router = APIRouter()


def get_current_admin_user(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify that current user is an admin"""
    from app.models.user import User
    
    user_id = int(current_user["id"])
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.reg_type != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    
    return user


# ========================================
# CUSTOMER/USER ENDPOINTS
# ========================================

@router.post("/orders/{order_id}/payment", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_for_order(
    order_id: int,
    payment_in: PaymentCreate,
    request: Request,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Create payment for an order (Customer)
    
    This endpoint:
    1. Validates order belongs to user
    2. Creates payment record
    3. Initiates payment with provider
    4. Returns payment URL for redirect
    
    The customer will be redirected to payment_url to complete payment.
    After payment, provider will send webhook to update order status.
    """
    
    # Get order
    order = crud_order.get(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify order belongs to user
    user_id = int(current_user["id"])
    if order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order"
        )
    
    # Check if order already paid
    if order.payment_status == 'completed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already paid"
        )
    
    # Use order total if amount not provided
    payment_amount = payment_in.amount if payment_in.amount is not None else order.total_amount
    
    # Validate payment amount matches order total
    if float(payment_amount) != float(order.total_amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount {payment_amount} does not match order total {order.total_amount}"
        )
    
    # Update payment_in with amount if not provided
    if payment_in.amount is None:
        payment_in.amount = order.total_amount
    
    # Build URLs
    base_url = str(request.base_url).rstrip('/')
    frontend_url = settings.FRONTEND_URL
    
    return_url = f"{frontend_url}/checkout/success?order_id={order_id}"
    cancel_url = f"{frontend_url}/checkout/cancelled?order_id={order_id}"
    webhook_url = f"{base_url}/api/webhooks/payment/{payment_in.provider}"
    
    try:
        # Create and initiate payment
        payment = await crud_payment.initiate_payment(
            db,
            order_id=order_id,
            payment_in=payment_in,
            return_url=return_url,
            cancel_url=cancel_url,
            webhook_url=webhook_url
        )
        
        # Update order payment status
        order.payment_status = 'processing'
        db.commit()
        
        return payment
    
    except PaymentProviderError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Payment provider error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment: {str(e)}"
        )


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Get payment details (Customer)
    
    Returns payment information including current status.
    """
    
    payment = crud_payment.get(db, payment_id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Verify payment belongs to user's order
    user_id = int(current_user["id"])
    if payment.order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this payment"
        )
    
    return payment


@router.get("/orders/{order_id}/payments", response_model=List[PaymentListItem])
async def get_order_payments(
    order_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Get all payments for an order (Customer)
    
    Useful for viewing payment history or retrying failed payments.
    """
    
    # Get order
    order = crud_order.get(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify order belongs to user
    user_id = int(current_user["id"])
    if order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order"
        )
    
    payments = crud_payment.get_by_order(db, order_id=order_id)
    return payments


# ========================================
# ADMIN ENDPOINTS
# ========================================

@router.get("/admin/payments", response_model=List[PaymentListItem])
async def get_all_payments(
    skip: int = 0,
    limit: int = 100,
    provider: Optional[str] = None,
    status: Optional[str] = None,
    is_test: Optional[bool] = None,
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Get all payments (Admin)
    
    Supports filtering by provider, status, and test mode.
    """
    
    payments = crud_payment.get_multi(
        db,
        skip=skip,
        limit=limit,
        provider=provider,
        status=status,
        is_test=is_test
    )
    
    return payments


@router.get("/admin/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment_admin(
    payment_id: int,
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Get payment details (Admin)
    """
    
    payment = crud_payment.get(db, payment_id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


@router.post("/admin/payments/{payment_id}/check-status", response_model=PaymentResponse)
async def check_payment_status(
    payment_id: int,
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Manually check payment status with provider (Admin)
    
    Useful for debugging or resolving stuck payments.
    """
    
    payment = crud_payment.get(db, payment_id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    try:
        updated_payment = await crud_payment.check_status(db, payment=payment)
        return updated_payment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check status: {str(e)}"
        )


@router.post("/admin/payments/{payment_id}/refund", response_model=RefundResponse)
async def refund_payment(
    payment_id: int,
    refund_in: RefundCreate,
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Refund a payment (Admin)
    
    Supports full or partial refunds.
    """
    
    payment = crud_payment.get(db, payment_id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    try:
        refunded_payment = await crud_payment.refund(
            db,
            payment=payment,
            amount=float(refund_in.amount) if refund_in.amount else None,
            reason=refund_in.reason
        )
        
        # Update order payment status
        order = refunded_payment.order
        order.payment_status = 'refunded'
        db.commit()
        
        return RefundResponse(
            payment_id=refunded_payment.id,
            refunded_amount=refunded_payment.refunded_amount,
            refund_transaction_id=refunded_payment.refund_transaction_id,
            refund_reason=refunded_payment.refund_reason,
            refunded_at=refunded_payment.refunded_at
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PaymentProviderError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Refund failed: {e.message}"
        )


# ========================================
# TEST/MOCK ENDPOINTS
# ========================================

@router.post("/test/simulate-payment", response_model=PaymentResponse)
async def simulate_payment_completion(
    simulation: MockPaymentSimulation,
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Simulate payment completion for testing (Test Mode Only)
    
    This endpoint allows you to simulate webhook callbacks for testing:
    - scenario='success': Complete payment successfully
    - scenario='failure': Simulate payment failure
    - scenario='cancelled': Simulate user cancellation
    
    **Only available in test/development environment!**
    """
    
    # Check if test mode is enabled
    if not settings.TESTING and settings.ENVIRONMENT == 'production':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test endpoints not available in production"
        )
    
    payment = crud_payment.get(db, payment_id=simulation.payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Simulate webhook processing
    from app.schemas.payment import PaymentUpdate
    
    if simulation.scenario == 'success':
        update_data = PaymentUpdate(
            status='completed',
            provider_transaction_id=f"mock_txn_{payment.id}",
            payment_info={'test': True, 'scenario': 'success'}
        )
    elif simulation.scenario == 'failure':
        update_data = PaymentUpdate(
            status='failed',
            error_message=simulation.error_message or 'Mock payment failure',
            error_code='mock_error'
        )
    elif simulation.scenario == 'cancelled':
        update_data = PaymentUpdate(
            status='cancelled'
        )
    
    # Update payment
    updated_payment = crud_payment.update(db, payment=payment, payment_in=update_data)
    
    # Update order status
    order = updated_payment.order
    if simulation.scenario == 'success':
        order.payment_status = 'completed'
        order.status = 'confirmed'
    elif simulation.scenario == 'failure':
        order.payment_status = 'failed'
    elif simulation.scenario == 'cancelled':
        order.payment_status = 'cancelled'
        order.status = 'cancelled'
    
    db.commit()
    db.refresh(updated_payment)
    
    return updated_payment
