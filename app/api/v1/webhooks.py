# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.db.session import get_db
from app.crud.payment import crud_payment
from app.crud.order import crud_order
from app.schemas.payment import PaymentUpdate
from app.services.payment import PaymentFactory, PaymentProviderError
from app.core.security.api_key import verify_api_key

router = APIRouter()


@router.post("/payment/{provider}")
async def payment_webhook(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
    x_signature: Optional[str] = Header(None),
    x_webhook_signature: Optional[str] = Header(None)
):
    """
    Payment webhook handler
    
    This endpoint receives webhook notifications from payment providers:
    - Payplug: Payment completed, failed, refunded
    - Floa: Installment updates, payment status
    - Findomestic: Application status, payment status
    - Mock: Test webhook simulations
    
    The webhook updates payment and order status automatically.
    
    **Note:** This endpoint does NOT require API key authentication
    as webhooks come from external providers.
    """
    
    # Validate provider
    if provider not in ['payplug', 'floa', 'findomestic', 'mock']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown payment provider: {provider}"
        )
    
    # Get raw body
    body = await request.body()
    
    # Get signature from headers
    signature = x_signature or x_webhook_signature
    
    if not signature and provider != 'mock':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing webhook signature"
        )
    
    try:
        # Parse body
        payload = json.loads(body.decode('utf-8'))
        
        # Get payment provider
        payment_provider = PaymentFactory.create(provider)
        
        # Verify webhook signature (except for mock in development)
        if provider != 'mock':
            headers = dict(request.headers)
            is_valid = await payment_provider.verify_webhook(body, signature, headers)
            
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid webhook signature"
                )
        
        # Parse webhook payload
        webhook_data = await payment_provider.parse_webhook(payload)
        
        # Get payment by provider payment ID
        provider_payment_id = webhook_data.get('provider_payment_id')
        if not provider_payment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing provider_payment_id in webhook"
            )
        
        payment = crud_payment.get_by_provider_id(db, provider_payment_id=provider_payment_id)
        if not payment:
            # Payment not found, but don't return error to provider
            # Log this for investigation
            return {"status": "accepted", "message": "Payment not found but webhook acknowledged"}
        
        # Update payment status
        payment_update = PaymentUpdate(
            status=webhook_data.get('status'),
            provider_transaction_id=webhook_data.get('transaction_id'),
            payment_info=webhook_data.get('metadata'),
            error_message=webhook_data.get('error', {}).get('message') if 'error' in webhook_data else None,
            error_code=webhook_data.get('error', {}).get('code') if 'error' in webhook_data else None
        )
        
        updated_payment = crud_payment.update(db, payment=payment, payment_in=payment_update)
        
        # Update order status based on payment status
        order = updated_payment.order
        
        if updated_payment.status == 'completed':
            # Payment successful
            order.payment_status = 'completed'
            order.status = 'confirmed'
            order.payment_transaction_id = updated_payment.provider_transaction_id
            
            # TODO: Trigger Garanzia3 registration if order has warranties
            # TODO: Send order confirmation email
            # TODO: Notify admin
        
        elif updated_payment.status == 'failed':
            # Payment failed
            order.payment_status = 'failed'
            # Don't cancel order automatically, customer might retry
            
            # TODO: Send payment failed email
        
        elif updated_payment.status == 'cancelled':
            # Payment cancelled by customer
            order.payment_status = 'cancelled'
            order.status = 'cancelled'
            
            # TODO: Send cancellation email
        
        elif updated_payment.status == 'refunded':
            # Payment refunded
            order.payment_status = 'refunded'
            # Keep order status as is (completed), but mark payment as refunded
            
            # TODO: Send refund confirmation email
        
        db.commit()
        
        return {
            "status": "success",
            "payment_id": updated_payment.id,
            "payment_status": updated_payment.status,
            "order_id": order.id,
            "order_status": order.status
        }
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    except PaymentProviderError as e:
        # Provider error, but acknowledge webhook so provider doesn't retry
        return {
            "status": "error",
            "message": str(e)
        }
    
    except Exception as e:
        # Unexpected error, log it but acknowledge webhook
        # In production, you'd log this to error tracking service
        return {
            "status": "error",
            "message": "Internal error processing webhook"
        }


@router.post("/test/payment-webhook-simulator")
async def test_payment_webhook(
    request: Request,
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Test endpoint to simulate payment webhooks (Development Only)
    
    This endpoint allows you to manually trigger webhook processing for testing.
    
    Body format:
    ```json
    {
        "provider": "mock",
        "payment_id": "mock_pay_123abc",
        "event_type": "payment.completed",
        "status": "completed",
        "transaction_id": "mock_txn_456def",
        "amount": 1059.90,
        "currency": "EUR"
    }
    ```
    
    **Only available in test/development environment!**
    """
    
    from app.core.config import settings
    
    if not settings.TESTING and settings.ENVIRONMENT == 'production':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test endpoints not available in production"
        )
    
    try:
        body = await request.body()
        payload = json.loads(body.decode('utf-8'))
        
        provider = payload.get('provider', 'mock')
        
        # Get payment provider
        payment_provider = PaymentFactory.create(provider)
        
        # Parse webhook
        webhook_data = await payment_provider.parse_webhook(payload)
        
        # Get payment
        provider_payment_id = webhook_data.get('provider_payment_id')
        payment = crud_payment.get_by_provider_id(db, provider_payment_id=provider_payment_id)
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment {provider_payment_id} not found"
            )
        
        # Update payment
        payment_update = PaymentUpdate(
            status=webhook_data.get('status'),
            provider_transaction_id=webhook_data.get('transaction_id'),
            payment_info=webhook_data.get('metadata')
        )
        
        updated_payment = crud_payment.update(db, payment=payment, payment_in=payment_update)
        
        # Update order
        order = updated_payment.order
        if updated_payment.status == 'completed':
            order.payment_status = 'completed'
            order.status = 'confirmed'
        elif updated_payment.status == 'failed':
            order.payment_status = 'failed'
        elif updated_payment.status == 'cancelled':
            order.payment_status = 'cancelled'
            order.status = 'cancelled'
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Test webhook processed",
            "payment_id": updated_payment.id,
            "payment_status": updated_payment.status,
            "order_id": order.id,
            "order_status": order.status
        }
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
