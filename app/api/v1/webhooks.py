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
from app.crud.warranty_registration import crud_warranty_registration
from app.schemas.payment import PaymentUpdate
from app.schemas.warranty_registration import WarrantyRegistrationCreate
from app.services.payment import PaymentFactory, PaymentProviderError
from app.services.garanzia3_service import garanzia3_service
from app.core.security.api_key import verify_api_key
from app.integrations.payplug import payplug_service
from loguru import logger

router = APIRouter()


async def auto_register_warranties(db: Session, order):
    """
    Automatically register warranties for order items after successful payment
    
    Args:
        db: Database session
        order: Order object
        
    This function:
    1. Checks order items for warranty products
    2. Extracts customer info from order
    3. Registers each warranty with Garanzia3
    4. Creates WarrantyRegistration records
    """
    
    # Check if order has items
    if not hasattr(order, 'items') or not order.items:
        return
    
    # Get customer address for contact info
    customer_address = order.billing_address
    if not customer_address:
        # No address, cannot register
        return
    
    # Extract customer info
    customer_name = customer_address.get('name') or customer_address.get('first_name') or "Customer"
    customer_lastname = customer_address.get('last_name') or "Customer"
    
    # Get email from customer_info (preserved at order time)
    customer_email = order.customer_info.get('email', '')
    customer_phone = customer_address.get('phone', '')
    
    # Process each order item
    for item in order.items:
        # Check if item has warranty option (stored as JSON)
        if not item.warranty_option or not isinstance(item.warranty_option, dict):
            continue
        
        # Extract warranty info from JSON
        warranty_id = item.warranty_option.get('id')
        if not warranty_id:
            continue
        
        # Get product for EAN13
        product = item.product
        if not product:
            continue
        
        # Get product EAN13 (required for Garanzia3)
        # Try multiple sources in order of preference:
        # 1. product_ean13 field from OrderItem
        # 2. product.ean13 from Product model
        # 3. product_sku from OrderItem (fallback - SKU is often the same as EAN13)
        product_ean13 = None
        
        if hasattr(item, 'product_ean13') and item.product_ean13:
            product_ean13 = item.product_ean13
        elif hasattr(product, 'ean13') and product.ean13:
            product_ean13 = product.ean13
        elif hasattr(item, 'product_sku') and item.product_sku:
            # Use SKU as fallback (often SKU = EAN13 in product databases)
            product_ean13 = item.product_sku
        
        # Skip if no EAN13 found from any source
        if not product_ean13:
            continue
        
        # Check if warranty already registered for this item
        existing = crud_warranty_registration.get_by_order(db, order_id=order.id)
        already_registered = any(
            reg.product_id == item.product_id and reg.warranty_id == warranty_id and reg.status == 'registered'
            for reg in existing
        )
        
        if already_registered:
            continue
        
        # Create warranty registration record
        registration_data = WarrantyRegistrationCreate(
            order_id=order.id,
            product_id=item.product_id,
            warranty_id=warranty_id,
            customer_name=customer_name,
            customer_lastname=customer_lastname,
            customer_email=customer_email,
            customer_phone=customer_phone,
            product_ean13=product_ean13,
            product_name=item.product_title  # Use product title from order item
        )
        
        registration = crud_warranty_registration.create(
            db,
            registration_in=registration_data,
            is_test=False  # Production registration
        )
        
        # Call Garanzia3 API
        try:
            result = await garanzia3_service.register_warranty(
                ean13=product_ean13,
                customer_name=customer_name,
                customer_lastname=customer_lastname,
                customer_email=customer_email,
                customer_phone=customer_phone
            )
            
            if result['success']:
                # Update registration with success
                crud_warranty_registration.update_status(
                    db,
                    id=registration.id,
                    status='registered',
                    g3_transaction_id=result['transaction'],
                    g3_pin=result['pin'],
                    g3_response=result.get('raw_response')
                )
            else:
                # Update registration with failure
                crud_warranty_registration.update_status(
                    db,
                    id=registration.id,
                    status='failed',
                    error_message=result['error'],
                    error_code='G3_API_ERROR'
                )
        
        except Exception as e:
            # Update registration with failure
            crud_warranty_registration.update_status(
                db,
                id=registration.id,
                status='failed',
                error_message=str(e),
                error_code='SYSTEM_ERROR'
            )


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
            order.status = 'completed'  # Changed from 'confirmed' to match warranty registration check
            order.payment_transaction_id = updated_payment.provider_transaction_id
            
            # Auto-register warranties if order has warranty products
            await auto_register_warranties(db, order)
            
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


@router.post("/payplug")
async def payplug_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    PayPlug Webhook Endpoint
    
    Receives payment notifications from PayPlug and updates order status.
    
    **No authentication required** - PayPlug sends notifications directly.
    
    **Note:** Verify the webhook signature in production for security.
    """
    try:
        # Get webhook data
        webhook_data = await request.json()
        
        logger.info(f"Received PayPlug webhook: {webhook_data}")
        
        # Extract resource ID (payment ID)
        resource_id = webhook_data.get('data', {}).get('id')
        
        if not resource_id:
            logger.error("No resource ID in webhook data")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook data: missing resource ID"
            )
        
        # Process webhook
        payment_info = payplug_service.process_webhook(resource_id)
        
        # Get order ID
        order_id = payment_info.get('order_id')
        if not order_id:
            logger.error(f"No order ID in payment metadata for payment {resource_id}")
            return {"status": "ok", "message": "No order ID found"}
        
        # Get order
        order = crud_order.get(db, id=int(order_id))
        if not order:
            logger.error(f"Order {order_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found"
            )
        
        # Update order based on payment status
        if payment_info['status'] == 'completed':
            # Payment successful
            order.payment_status = 'completed'
            order.status = 'confirmed'
            order.payment_transaction_id = payment_info['payment_id']
            
            logger.info(f"Order {order_id} payment completed successfully")
            
            # Auto-register warranties if payment successful
            await auto_register_warranties(db, order)
            
        elif payment_info['status'] == 'failed':
            # Payment failed
            order.payment_status = 'failed'
            order.admin_note = (
                f"Payment failed: {payment_info.get('failure_message', 'Unknown error')}"
            )
            
            logger.warning(
                f"Order {order_id} payment failed: {payment_info.get('failure_message')}"
            )
        
        else:
            # Payment still pending
            order.payment_status = 'pending'
            logger.info(f"Order {order_id} payment still pending")
        
        # Save changes
        db.commit()
        db.refresh(order)
        
        return {
            "status": "ok",
            "order_id": order_id,
            "payment_status": order.payment_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PayPlug webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )


@router.get("/payplug/test")
async def test_payplug_webhook():
    """Test endpoint to verify PayPlug webhook route is accessible"""
    return {
        "status": "ok",
        "message": "PayPlug webhook endpoint is ready",
        "endpoint": "/api/payments/payplug"
    }


@router.post("/floa")
async def floa_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Floa payment notification webhook
    
    Floa sends notifications to this endpoint when payment status changes.
    This is the primary way to track payment completion.
    
    **Request Body:** (sent by Floa)
    ```json
    {
      "dealReference": "FINxxxxx",
      "status": "APPROVED",  // or REFUSED, CANCELLED, EXPIRED
      "merchantReference": "ORDxxxxx",
      "customerTotalAmount": 50000,
      "dealStatus": "DELIVERED"
    }
    ```
    
    **Returns:**
    - 200 OK if processed successfully
    - Floa expects quick response (< 30s)
    """
    try:
        # Get raw body
        body = await request.json()
        
        logger.info(f"Floa webhook received: {json.dumps(body, indent=2)}")
        
        # Extract data from webhook
        deal_reference = body.get('dealReference')
        deal_status = body.get('dealStatus')
        merchant_reference = body.get('merchantReference')
        
        if not deal_reference or not merchant_reference:
            logger.error("Missing dealReference or merchantReference in Floa webhook")
            return {"status": "error", "message": "Missing required fields"}
        
        # Extract order ID from merchantReference
        # Format: ORD{order_id}_{timestamp}
        if merchant_reference.startswith("ORD"):
            try:
                order_id_str = merchant_reference[3:].split('_')[0]
                order_id = int(order_id_str)
            except (IndexError, ValueError):
                logger.error(f"Invalid merchantReference format: {merchant_reference}")
                return {"status": "error", "message": "Invalid merchantReference format"}
        else:
            logger.error(f"Unknown merchantReference format: {merchant_reference}")
            return {"status": "error", "message": "Unknown merchantReference format"}
        
        # Get order
        order = crud_order.get(db, id=order_id)
        if not order:
            logger.error(f"Order {order_id} not found for Floa deal {deal_reference}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found"
            )
        
        # Update order based on deal status
        if deal_status == 'DELIVERED':
            # Check if first installment is paid
            # We could call Floa API here to get detailed status, but for webhook we trust the status
            order.payment_status = 'completed'
            order.status = 'confirmed'
            order.payment_transaction_id = deal_reference
            
            logger.info(f"Order {order_id} Floa payment completed (deal: {deal_reference})")
            
            # Auto-register warranties if payment successful
            await auto_register_warranties(db, order)
            
        elif deal_status in ['CANCELLED', 'REFUSED', 'EXPIRED']:
            # Payment failed/cancelled
            order.payment_status = 'failed'
            order.admin_note = f"Floa payment {deal_status.lower()}: {deal_reference}"
            
            logger.warning(f"Order {order_id} Floa payment {deal_status} (deal: {deal_reference})")
        
        else:
            # Payment still pending (DRAFT, etc.)
            order.payment_status = 'pending'
            logger.info(f"Order {order_id} Floa payment pending (deal: {deal_reference})")
        
        # Save changes
        db.commit()
        db.refresh(order)
        
        return {
            "status": "ok",
            "dealReference": deal_reference,
            "order_id": order_id,
            "payment_status": order.payment_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Floa webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )


@router.get("/floa/test")
async def test_floa_webhook():
    """Test endpoint to verify Floa webhook route is accessible"""
    return {
        "status": "ok",
        "message": "Floa webhook endpoint is ready",
        "endpoint": "/api/payments/floa"
    }
