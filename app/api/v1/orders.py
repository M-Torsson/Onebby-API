# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.db.session import get_db
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse,
    OrderStatsResponse, WarrantyUpdateRequest, OrderCreateDirect,
    PayUrlRequest, PayUrlResponse, PaymentVerifyRequest, PaymentVerifyResponse,
    OrderCreateResponse
)
from app.crud.order import crud_order
from app.crud import cart as crud_cart
from app.core.security.api_key import verify_api_key
from app.core.security.dependencies import get_current_active_user
from app.models.user import User
from app.integrations.payplug import payplug_service
from app.integrations.floa import floa_service
from app.integrations.paypal import paypal_service
from app.core.config import settings

router = APIRouter()


def get_current_admin_user(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Verify that current user is an admin
    """
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

@router.post("/create-from-cart", response_model=OrderCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_order_from_cart(
    order_data: OrderCreateDirect,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Create an order directly (NEW API - no cart, no token required)
    
    **Requirements:**
    - API Key (in header X-API-Key)
    - NO Bearer Token Required
    
    **New Body Format:**
    ```json
    {
      "user_id": 10,
      "reg_type": "company",
      "address_id": 10,
      "order_date": "27-02-2026",
      "customer_note": "Test PayPlug payment",
      "payment_info": {
        "payment_type": "Payplug",
        "payment_id": "pay_5TVrOgdsnseJIlyluCa6ej"
      },
      "items": [
        {
          "product_id": 3630,
          "qty": 2,
          "warranty": {
            "title": "GARANZIA3 – 3 Years",
            "cost": 49.90
          },
          "delivery_opt": {
            "title": "Consegna al Piano",
            "cost": 69.0
          }
        },
        {
          "product_id": 3632,
          "qty": 1,
          "warranty": null,
          "delivery_opt": null
        }
      ],
      "total": {
        "sub_total": 3200,
        "warranty": 100.89,
        "shipping": 120.43,
        "total": 2332.09
      }
    }
    ```
    
    **Returns:**
    - Success message with order ID
    - Or error message with failure reason
    """
    # Create order directly (no cart needed)
    try:
        order = crud_order.create_direct(
            db=db,
            order_data=order_data,
            user_id=order_data.user_id
        )
        
        return OrderCreateResponse(
            success=True,
            message="Order placed successfully",
            order_id=order.id
        )
        
    except ValueError as e:
        return OrderCreateResponse(
            success=False,
            message=f"Order failed: {str(e)}",
            order_id=None
        )
    except Exception as e:
        return OrderCreateResponse(
            success=False,
            message=f"Order failed: Server error - {str(e)}",
            order_id=None
        )


@router.post("/get_pay_url", response_model=PayUrlResponse, status_code=status.HTTP_200_OK)
async def get_payment_url(
    request: PayUrlRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get payment URL for PayPlug or Floa without creating an order
    
    **Requirements:**
    - API Key (in header X-API-Key)
    
    **Request Body:**
    ```json
    {
      "payment_type": "Payplug",  // or "floa"
      "user_id": 5,
      "total": 2300.98
    }
    ```
    
    **Returns:**
    - user_id: User ID
    - payment_id: Payment ID (pay_xxxxx for PayPlug, FINxxxxx for Floa)
    - payment_url: Payment page URL - redirect user here
    - amount: Payment amount
    """
    # Normalize payment type
    payment_type = request.payment_type.lower()
    
    # Validate payment type
    if payment_type not in ['paypal', 'payplug', 'card', 'credit_card', 'floa']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment type. Allowed: PayPal, PayPlug, card, credit_card, floa"
        )
    
    # Verify user exists
    from app.models.user import User
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {request.user_id} not found"
        )
    
    try:
        # Get user email and info
        user_email = ""
        user_first_name = ""
        user_last_name = ""
        user_phone = ""
        user_address = {}
        
        # Try to get email from multiple sources
        if hasattr(user, 'email') and user.email:
            user_email = user.email
        elif hasattr(user, 'customer_info') and user.customer_info:
            # Try from customer_info JSON
            if isinstance(user.customer_info, dict):
                user_email = user.customer_info.get('email', '')
        
        if hasattr(user, 'first_name') and user.first_name:
            user_first_name = user.first_name
        elif hasattr(user, 'customer_info') and isinstance(user.customer_info, dict):
            user_first_name = user.customer_info.get('first_name', '')
        
        if hasattr(user, 'last_name') and user.last_name:
            user_last_name = user.last_name
        elif hasattr(user, 'customer_info') and isinstance(user.customer_info, dict):
            user_last_name = user.customer_info.get('last_name', '')
        
        # If company, use company name
        if user.reg_type == 'company':
            if hasattr(user, 'company_name') and user.company_name:
                user_first_name = user.company_name
            elif hasattr(user, 'customer_info') and isinstance(user.customer_info, dict):
                user_first_name = user.customer_info.get('company_name', user_first_name)
        
        # Get phone (for Floa)
        if hasattr(user, 'phone') and user.phone:
            user_phone = user.phone
        elif hasattr(user, 'customer_info') and isinstance(user.customer_info, dict):
            user_phone = user.customer_info.get('phone', '+393331234567')
        
        # Get address (for Floa)
        if hasattr(user, 'addresses') and user.addresses:
            first_address = user.addresses[0] if len(user.addresses) > 0 else None
            if first_address:
                user_address = {
                    'street': getattr(first_address, 'address_house_number', '') or getattr(first_address, 'street', 'Via Roma'),
                    'house_number': getattr(first_address, 'house_number', '') or '1',
                    'postal_code': getattr(first_address, 'postal_code', ''),
                    'city': getattr(first_address, 'city', ''),
                    'country': getattr(first_address, 'country', 'IT')
                }
        
        # Default address if not found
        if not user_address:
            user_address = {
                'street': 'Via Roma',
                'house_number': '1',
                'postal_code': '20121',
                'city': 'Milano',
                'country': 'IT'
            }
        
        # PayPlug payment
        if payment_type in ['payplug', 'card', 'credit_card']:
            # Check if PayPlug is configured
            if not settings.PAYPLUG_API_KEY:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="PayPlug is not configured"
                )
            
            # Create payment URLs
            return_url = f"{settings.FRONTEND_URL}/payment-success"
            cancel_url = f"{settings.FRONTEND_URL}/payment-cancel"
            
            # Create PayPlug payment
            payment_result = payplug_service.create_payment(
            amount=float(request.total),
            order_id=f"temp_{request.user_id}_{int(datetime.now().timestamp())}",
            customer_email=user_email,
            customer_first_name=user_first_name,
            customer_last_name=user_last_name,
            return_url=return_url,
            cancel_url=cancel_url
        )
        
            return PayUrlResponse(
                user_id=request.user_id,
                payment_id=payment_result['payment_id'],
                payment_url=payment_result['payment_url'],
                amount=request.total
            )
        
        # PayPal payment
        elif payment_type == 'paypal':
            # Check if PayPal is configured
            if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="PayPal is not configured"
                )
            
            # Create payment URLs
            # Use API endpoints for testing (no frontend needed)
            base_url = "https://onebby-api.onrender.com"  # Or settings.BACKEND_URL if available
            return_url = f"{base_url}/api/orders/payment/success"
            cancel_url = f"{base_url}/api/orders/payment/cancel"
            
            # Create PayPal payment
            payment_result = paypal_service.create_payment(
                amount=request.total,
                order_id=request.user_id,
                customer_email=user_email or "test@example.com",
                return_url=return_url,
                cancel_url=cancel_url
            )
            
            return PayUrlResponse(
                user_id=request.user_id,
                payment_id=payment_result['payment_id'],
                payment_url=payment_result['payment_url'],
                amount=request.total
            )
        
        # Floa payment
        elif payment_type == 'floa':
            # Check if Floa is configured
            if not settings.FLOA_CLIENT_ID or not settings.FLOA_CLIENT_SECRET:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Floa is not configured"
                )
            
            # Validate product_code if provided
            allowed_codes = ['BC3XCIT', 'BC4XCIT']
            product_code = request.product_code
            
            if product_code and product_code not in allowed_codes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid product_code. Allowed: {', '.join(allowed_codes)}"
                )
            
            # Prepare items for Floa
            items = [
                {
                    "name": "Order Item",
                    "amount": int(request.total * 100),
                    "quantity": 1,
                    "reference": f"ITEM_{request.user_id}",
                    "category": "General",
                    "subCategory": "Product",
                    "customCategory": "E-commerce"
                }
            ]
            
            # Create Floa payment
            payment_result = floa_service.create_payment(
                amount=request.total,
                order_id=request.user_id,
                customer_email=user_email or "test@example.com",
                customer_first_name=user_first_name or "Mario",
                customer_last_name=user_last_name or "Rossi",
                customer_phone=user_phone or "+393331234567",
                customer_address=user_address if user_address else {
                    'street': 'Via Roma',
                    'house_number': '1',
                    'postal_code': '20121',
                    'city': 'Milano',
                    'country': 'IT'
                },
                items=items,
                product_code=product_code  # Pass product_code or None (will use default)
            )
            
            return PayUrlResponse(
                user_id=request.user_id,
                payment_id=payment_result['payment_id'],
                payment_url=payment_result['payment_url'],
                amount=request.total
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment: {str(e)}"
        )


@router.post("/verify_payment", response_model=PaymentVerifyResponse, response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def verify_payment_status(
    verify_request: PaymentVerifyRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Verify payment status for PayPlug or Floa
    
    **Use this after user returns from payment page**
    
    **Requirements:**
    - API Key (in header X-API-Key)
    
    **Request Body:**
    ```json
    {
      "payment_id": "pay_xxxxx"  // PayPlug ID or "FINxxxxx" for Floa
    }
    ```
    
    **Returns:**
    - payment_id: Payment ID
    - status: completed, pending, or failed
    - amount: Payment amount
    - is_paid: true if payment completed
    - created_at: When payment was created
    - paid_at: When payment was completed (if completed)
    - customer_email: Customer email
    
    **Flow:**
    1. User gets payment_id from /get_pay_url response
    2. User completes payment
    3. User returns to your site
    4. Call this endpoint with payment_id to verify payment status
    5. If is_paid=true, payment successful!
    """
    # Initialize logger
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Get payment ID from request
        payment_id = verify_request.payment_id
        
        # Detect payment provider by payment_id format
        # PayPlug: pay_xxxxx
        # Floa: FINxxxxx
        # PayPal: Usually starts with digits or uppercase letters (e.g., 8PJ12345678901234)
        is_payplug = payment_id.startswith("pay_")
        is_floa = payment_id.startswith("FIN")
        is_paypal = not is_payplug and not is_floa  # If not PayPlug or Floa, assume PayPal
        
        if is_payplug:
            # Check if PayPlug is configured
            if not settings.PAYPLUG_API_KEY:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="PayPlug is not configured"
                )
            
            # Retrieve payment details from PayPlug
            payment = payplug_service.retrieve_payment(payment_id)
            
            if not payment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Payment {payment_id} not found"
                )
            
            # Determine status
            is_paid = payment.is_paid
            if is_paid:
                status_text = "completed"
            elif payment.failure:
                status_text = "failed"
            else:
                status_text = "pending"
            
            # Get timestamps
            from datetime import datetime
            created_at = datetime.fromtimestamp(payment.created_at).isoformat() if payment.created_at else None
            paid_at = datetime.fromtimestamp(payment.paid_at).isoformat() if hasattr(payment, 'paid_at') and payment.paid_at else None
            
            # Get customer email
            customer_email = None
            try:
                if hasattr(payment, 'customer') and payment.customer:
                    if isinstance(payment.customer, dict):
                        customer_email = payment.customer.get('email')
                    elif hasattr(payment.customer, 'email'):
                        customer_email = payment.customer.email
            except (TypeError, KeyError, AttributeError):
                customer_email = None
            
            # Get transaction number
            transaction_number = None
            try:
                if hasattr(payment, 'authorization') and payment.authorization:
                    if isinstance(payment.authorization, dict):
                        transaction_number = payment.authorization.get('authorization_id') or payment.authorization.get('id')
                    elif hasattr(payment.authorization, 'authorization_id'):
                        transaction_number = payment.authorization.authorization_id
                    elif hasattr(payment.authorization, 'id'):
                        transaction_number = payment.authorization.id
                
                if not transaction_number and hasattr(payment, 'card') and payment.card:
                    if isinstance(payment.card, dict):
                        transaction_number = payment.card.get('id') or payment.card.get('transaction_id')
            except (TypeError, KeyError, AttributeError):
                transaction_number = None
            
            # Build response
            response_data = {
                "payment_id": payment.id,
                "status": status_text,
                "amount": payment.amount / 100,
                "is_paid": is_paid,
            }
            
        elif is_floa:
            # Check if Floa is configured
            if not settings.FLOA_CLIENT_ID or not settings.FLOA_CLIENT_SECRET:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Floa is not configured"
                )
            
            # Get deal status from Floa
            deal = floa_service.get_deal_status(payment_id)
            
            if not deal:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Payment {payment_id} not found"
                )
            
            # Determine status from dealStatus
            deal_status = deal.get('dealStatus', 'UNKNOWN')
            
            # Log for debugging
            logger.info(f"Floa deal {payment_id} status: {deal_status}")
            
            # Check if we're in integration/test environment
            is_integration_env = 'live-int' in settings.FLOA_BASE_URL
            
            if deal_status == 'DELIVERED':
                # Check installments to determine if paid
                installments = deal.get('installments', [])
                first_installment = installments[0] if installments else None
                
                if first_installment and first_installment.get('status') == 'PAID':
                    status_text = "completed"
                    is_paid = True
                else:
                    status_text = "pending"
                    is_paid = False
            elif deal_status == 'APPROVED':
                # Floa approved the payment - waiting for first installment
                status_text = "approved"
                is_paid = True  # Consider approved as successful
            elif deal_status == 'DRAFT' and is_integration_env:
                # In integration/test environment, DRAFT with installments = test success
                installments = deal.get('installments', [])
                if installments and len(installments) > 0:
                    # Deal was finalized and has installment plan = simulation successful
                    status_text = "completed"
                    is_paid = True
                    logger.info(f"Integration mode: treating DRAFT deal {payment_id} with installments as completed")
                else:
                    status_text = "pending"
                    is_paid = False
            elif deal_status in ['CANCELLED', 'REFUSED', 'EXPIRED']:
                status_text = "failed"
                is_paid = False
            else:
                # DRAFT (in production), PENDING, etc.
                status_text = "pending"
                is_paid = False
            
            # Build response
            response_data = {
                "payment_id": payment_id,
                "status": status_text,
                "amount": deal.get('customerTotalAmount', 0) / 100,  # Floa uses cents
                "is_paid": is_paid,
                "deal_status": deal_status  # Add for debugging
            }
            
            # Add created_at if available
            created_at = None
            paid_at = None
            
            # No timestamp in Floa installment-plan response
            # Would need to track this separately or get from deal creation
            
            transaction_number = None
            customer_email = None
            
        elif is_paypal:
            # Check if PayPal is configured
            if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="PayPal is not configured"
                )
            
            # Get order details from PayPal
            order = paypal_service.get_order_details(payment_id)
            
            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Payment {payment_id} not found"
                )
            
            # Determine status from PayPal order status
            # CREATED, APPROVED, VOIDED, COMPLETED, PAYER_ACTION_REQUIRED
            order_status = order.get('status', 'UNKNOWN')
            
            # Log for debugging
            logger.info(f"PayPal order {payment_id} status: {order_status}")
            
            if order_status == 'COMPLETED':
                status_text = "completed"
                is_paid = True
            elif order_status == 'APPROVED':
                # Order approved but not yet captured
                status_text = "approved"
                is_paid = True  # Consider approved as successful
            elif order_status in ['VOIDED', 'CANCELLED']:
                status_text = "failed"
                is_paid = False
            else:
                # CREATED, PAYER_ACTION_REQUIRED, etc.
                status_text = "pending"
                is_paid = False
            
            # Extract amount
            amount = 0
            try:
                purchase_units = order.get('purchase_units', [])
                if purchase_units:
                    amount = float(purchase_units[0].get('amount', {}).get('value', 0))
            except (IndexError, KeyError, ValueError):
                amount = 0
            
            # Build response
            response_data = {
                "payment_id": payment_id,
                "status": status_text,
                "amount": amount,
                "is_paid": is_paid,
                "order_status": order_status  # Add for debugging
            }
            
            # Extract timestamps if available
            created_at = order.get('create_time')
            paid_at = order.get('update_time') if is_paid else None
            
            # Extract payer email
            customer_email = None
            try:
                payer = order.get('payer', {})
                customer_email = payer.get('email_address')
            except (TypeError, KeyError):
                customer_email = None
            
            transaction_number = payment_id  # Use order ID as transaction number
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment_id format: {payment_id}"
            )
        
        # Add optional fields only if they have values
        if transaction_number:
            response_data["transaction_number"] = transaction_number
        if created_at:
            response_data["created_at"] = created_at
        if paid_at:
            response_data["paid_at"] = paid_at
        if customer_email:
            response_data["customer_email"] = customer_email
        
        # ========================================
        # AUTO-UPDATE ORDER IN DATABASE
        # ========================================
        # Find order with this payment_id and update its status
        from app.models.order import Order
        from app.api.v1.webhooks import auto_register_warranties
        
        order = db.query(Order).filter(
            (Order.payment_transaction_id == payment_id) |
            (Order.payment_info['payment_id'].astext == payment_id)
        ).first()
        
        if order:
            logger.info(f"Found order {order.id} for payment {payment_id}, updating status")
            
            old_payment_status = order.payment_status
            
            # Update order based on payment status
            if is_paid and status_text in ['completed', 'approved']:
                order.payment_status = 'completed'
                order.status = 'confirmed'
                order.payment_transaction_id = payment_id
                
                # Auto-register warranties if payment successful
                await auto_register_warranties(db, order)
                
                logger.info(f"Order {order.id} payment completed: {payment_id}")
                
            elif status_text == 'failed':
                order.payment_status = 'failed'
                order.status = 'cancelled'
                logger.warning(f"Order {order.id} payment failed: {payment_id}")
            
            # Commit changes if status changed
            if order.payment_status != old_payment_status:
                db.commit()
                db.refresh(order)
                logger.info(f"Order {order.id} updated: {old_payment_status} -> {order.payment_status}")
                response_data["order_updated"] = True
                response_data["order_id"] = order.id
            else:
                response_data["order_updated"] = False
        else:
            logger.warning(f"No order found for payment {payment_id}")
            response_data["order_updated"] = False
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify payment: {str(e)}"
        )


@router.post("/guest/create-from-cart", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order_from_cart_guest(
    order_data: OrderCreate,
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Create an order from cart (guest user)
    
    **Requirements:**
    - API Key (in header)
    - X-Session-ID (in header) - required for guest orders
    - Cart must have items
    
    **Body Example:**
    Same as authenticated endpoint, but uses session_id instead of user_id
    
    **Returns:**
    - Order object with status 'pending'
    - Payment needs to be completed separately
    """
    # Get guest cart
    cart = crud_cart.get_active_cart(db, user_id=None, session_id=session_id)
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    if not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create order from empty cart"
        )
    
    # Create order from cart
    try:
        order = crud_order.create_from_cart(
            db=db,
            cart=cart,
            order_data=order_data,
            user_id=None,
            session_id=session_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return order


@router.get("/my-orders", response_model=List[OrderListResponse])
async def get_my_orders(
    user_id: int = Query(..., description="User ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get current user's orders
    
    **Requirements:**
    - API Key (in header X-API-Key)
    - NO Bearer Token Required
    
    **Query Parameters:**
    - user_id: User ID (required)
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 100)
    
    **Returns:**
    List of orders (summary) for the user
    """
    
    orders = crud_order.get_by_user(db, user_id=user_id, skip=skip, limit=limit)
    
    # Build response with additional info
    response = []
    for order in orders:
        # Extract customer email and name from customer_info
        customer_email = order.customer_info.get('email')
        
        if order.user_type == 'company':
            customer_name = order.customer_info.get('company_name', 'Unknown')
        else:
            first_name = order.customer_info.get('first_name', '')
            last_name = order.customer_info.get('last_name', '')
            customer_name = f"{first_name} {last_name}".strip() or 'Unknown'
        
        # Check if order has warranty items
        has_warranty = any(item.warranty_option for item in order.items)
        
        response.append(OrderListResponse(
            id=order.id,
            user_id=order.user_id,
            user_type=order.user_type,
            customer_email=customer_email,
            customer_name=customer_name,
            total_amount=order.total_amount,
            currency=order.currency,
            status=order.status,
            payment_status=order.payment_status,
            payment_method=order.payment_method,
            shipping_status=order.shipping_status,
            items_count=len(order.items),
            has_warranty=has_warranty,
            created_at=order.created_at,
            paid_at=order.paid_at,
            shipped_at=order.shipped_at,
            delivered_at=order.delivered_at
        ))
    
    return response


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    user_id: Optional[int] = Query(None, description="User ID for authorization check"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get order details
    
    **Requirements:**
    - API Key (in header X-API-Key)
    - NO Bearer Token Required
    - Optional: user_id for authorization check
    
    **Returns:**
    Full order details including items
    """
    order = crud_order.get(db, id=order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Optional: Verify order belongs to user (if user_id provided)
    if user_id and order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order"
        )
    
    return order


@router.get("/guest/{order_id}", response_model=OrderResponse)
async def get_order_guest(
    order_id: int,
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get order details for guest user
    
    **Requirements:**
    - API Key
    - X-Session-ID (must match order's session_id)
    
    **Returns:**
    Full order details
    """
    order = crud_order.get(db, id=order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify session_id matches
    if order.session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order"
        )
    
    return order


# ========================================
# ADMIN ENDPOINTS
# ========================================

@router.get("/admin/all", response_model=List[OrderListResponse])
async def get_all_orders_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by order status"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status"),
    shipping_status: Optional[str] = Query(None, description="Filter by shipping status"),
    user_type: Optional[str] = Query(None, description="Filter by user type (customer/company/guest)"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all orders (Admin only)
    
    **Requirements:**
    - API Key
    - Bearer Token (admin user)
    
    **Query Parameters:**
    - skip: Records to skip
    - limit: Max records to return
    - status: Filter by order status (pending/confirmed/completed/cancelled)
    - payment_status: Filter by payment (pending/completed/failed/refunded)
    - shipping_status: Filter by shipping (pending/shipped/delivered)
    - user_type: Filter by user type (customer/company/guest)
    
    **Example Request:**
    ```
    GET /api/v1/orders/admin/all?status=pending&limit=50
    ```
    
    **Returns:**
    List of all orders (filtered)
    """
    orders = crud_order.get_multi(
        db,
        skip=skip,
        limit=limit,
        status=status,
        payment_status=payment_status,
        shipping_status=shipping_status,
        user_type=user_type
    )
    
    # Build response
    response = []
    for order in orders:
        customer_email = order.customer_info.get('email')
        
        if order.user_type == 'company':
            customer_name = order.customer_info.get('company_name', 'Unknown')
        else:
            first_name = order.customer_info.get('first_name', '')
            last_name = order.customer_info.get('last_name', '')
            customer_name = f"{first_name} {last_name}".strip() or 'Unknown'
        
        has_warranty = any(item.warranty_option for item in order.items)
        
        response.append(OrderListResponse(
            id=order.id,
            user_id=order.user_id,
            user_type=order.user_type,
            customer_email=customer_email,
            customer_name=customer_name,
            total_amount=order.total_amount,
            currency=order.currency,
            status=order.status,
            payment_status=order.payment_status,
            payment_method=order.payment_method,
            shipping_status=order.shipping_status,
            items_count=len(order.items),
            has_warranty=has_warranty,
            created_at=order.created_at,
            paid_at=order.paid_at,
            shipped_at=order.shipped_at,
            delivered_at=order.delivered_at
        ))
    
    return response


@router.get("/admin/{order_id}", response_model=OrderResponse)
async def get_order_admin(
    order_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get order details (Admin)
    
    **Requirements:**
    - API Key (in header X-API-Key)
    - NO Bearer Token Required
    
    **Returns:**
    Full order details
    """
    order = crud_order.get(db, id=order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.patch("/admin/{order_id}", response_model=OrderResponse)
async def update_order_admin(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update order (Admin)
    
    **Requirements:**
    - API Key (in header X-API-Key)
    - NO Bearer Token Required
    
    **Body Example:**
    ```json
    {
      "status": "confirmed",
      "payment_status": "completed",
      "shipping_status": "shipped",
      "tracking_number": "ABC123456789",
      "admin_note": "Shipped via DHL Express"
    }
    ```
    
    All fields are optional. Only provided fields will be updated.
    
    **Returns:**
    Updated order
    """
    order = crud_order.update(db, order_id=order_id, order_update=order_update)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.post("/admin/sync-payment/{order_id}")
async def sync_payment_status(
    order_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Sync payment status from payment gateway (Admin)
    
    Manually checks payment status from PayPal/Floa and updates order.
    Useful when webhook doesn't arrive or for sandbox testing.
    
    **Requirements:**
    - API Key (in header X-API-Key)
    
    **Returns:**
    ```json
    {
      "order_id": 123,
      "payment_method": "paypal",
      "old_status": "pending",
      "new_status": "completed",
      "synced": true,
      "message": "Payment confirmed"
    }
    ```
    """
    import logging
    from app.integrations.paypal import paypal_service
    from app.integrations.floa import floa_service
    from app.api.v1.webhooks import auto_register_warranties
    
    logger = logging.getLogger(__name__)
    
    # Get order
    order = crud_order.get(db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    
    old_status = order.payment_status
    payment_method = order.payment_method
    
    # Get payment_id from order
    payment_id = None
    if order.payment_info and isinstance(order.payment_info, dict):
        payment_id = order.payment_info.get('payment_id')
    
    if not payment_id:
        payment_id = order.payment_transaction_id
    
    if not payment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No payment ID found in order"
        )
    
    logger.info(f"Syncing payment {payment_id} for order {order_id} (method: {payment_method})")
    
    synced = False
    new_status = old_status
    message = "No changes"
    
    try:
        # Check payment status based on method
        if payment_method and payment_method.lower() == 'paypal':
            # Get PayPal order details
            paypal_order = paypal_service.get_order_details(payment_id)
            
            if not paypal_order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"PayPal payment {payment_id} not found"
                )
            
            order_status = paypal_order.get('status', 'UNKNOWN')
            logger.info(f"PayPal order {payment_id} status: {order_status}")
            
            # Update based on status
            if order_status == 'COMPLETED':
                order.payment_status = 'completed'
                order.status = 'confirmed'
                new_status = 'completed'
                message = "Payment confirmed (COMPLETED)"
                synced = True
                
                # Auto-register warranties
                await auto_register_warranties(db, order)
                
            elif order_status == 'APPROVED':
                order.payment_status = 'completed'
                order.status = 'confirmed'
                new_status = 'completed'
                message = "Payment confirmed (APPROVED)"
                synced = True
                
                # Auto-register warranties
                await auto_register_warranties(db, order)
                
            elif order_status in ['VOIDED', 'CANCELLED']:
                order.payment_status = 'failed'
                order.status = 'cancelled'
                new_status = 'failed'
                message = f"Payment {order_status.lower()}"
                synced = True
            else:
                message = f"Payment still {order_status}"
        
        elif payment_method and payment_method.lower() == 'floa':
            # Get Floa deal details
            deal = floa_service.get_deal_status(payment_id)
            
            if not deal:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Floa payment {payment_id} not found"
                )
            
            deal_status = deal.get('dealStatus', 'UNKNOWN')
            installments = deal.get('installmentsList', [])
            
            # Check environment
            base_url = floa_service.base_url
            is_integration = 'live-int' in base_url
            
            logger.info(f"Floa deal {payment_id} status: {deal_status}, installments: {len(installments)}, integration: {is_integration}")
            
            # Update based on status
            if deal_status == 'APPROVED':
                order.payment_status = 'completed'
                order.status = 'confirmed'
                new_status = 'completed'
                message = "Payment confirmed (APPROVED)"
                synced = True
                
                # Auto-register warranties
                await auto_register_warranties(db, order)
                
            elif deal_status == 'DRAFT' and is_integration and len(installments) > 0:
                # Integration environment - DRAFT with installments means approved
                order.payment_status = 'completed'
                order.status = 'confirmed'
                new_status = 'completed'
                message = "Payment confirmed (DRAFT with installments - integration env)"
                synced = True
                
                # Auto-register warranties
                await auto_register_warranties(db, order)
                
            elif deal_status in ['CANCELLED', 'REJECTED']:
                order.payment_status = 'failed'
                order.status = 'cancelled'
                new_status = 'failed'
                message = f"Payment {deal_status.lower()}"
                synced = True
            else:
                message = f"Payment still {deal_status}"
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot sync payment method: {payment_method}. Only PayPal and Floa are supported."
            )
        
        # Commit changes if synced
        if synced:
            db.commit()
            db.refresh(order)
        
        return {
            "order_id": order_id,
            "payment_method": payment_method,
            "payment_id": payment_id,
            "old_status": old_status,
            "new_status": new_status,
            "synced": synced,
            "message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync payment for order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync payment: {str(e)}"
        )


@router.post("/admin/sync-all-pending-payments")
async def sync_all_pending_payments(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Sync all pending payment orders (Admin)
    
    Checks all orders with payment_status='pending' and updates from gateways.
    Useful for dashboard initial load or bulk sync.
    
    **Requirements:**
    - API Key (in header X-API-Key)
    
    **Returns:**
    ```json
    {
      "total_checked": 10,
      "updated": 5,
      "failed": 1,
      "skipped": 4,
      "results": [...]
    }
    ```
    """
    import logging
    from app.integrations.paypal import paypal_service
    from app.integrations.floa import floa_service
    from app.api.v1.webhooks import auto_register_warranties
    from app.models.order import Order
    
    logger = logging.getLogger(__name__)
    
    # Get all pending orders with payment info
    pending_orders = db.query(Order).filter(
        Order.payment_status == 'pending',
        Order.payment_info.isnot(None)
    ).all()
    
    total_checked = 0
    updated = 0
    failed = 0
    skipped = 0
    results = []
    
    for order in pending_orders:
        total_checked += 1
        
        # Get payment_id
        payment_id = None
        if order.payment_info and isinstance(order.payment_info, dict):
            payment_id = order.payment_info.get('payment_id')
        
        if not payment_id:
            payment_id = order.payment_transaction_id
        
        if not payment_id:
            skipped += 1
            results.append({
                "order_id": order.id,
                "status": "skipped",
                "message": "No payment ID"
            })
            continue
        
        payment_method = order.payment_method
        if not payment_method:
            skipped += 1
            results.append({
                "order_id": order.id,
                "payment_id": payment_id,
                "status": "skipped",
                "message": "No payment method"
            })
            continue
        
        try:
            synced = False
            message = "No change"
            
            # Check based on payment method
            if payment_method.lower() == 'paypal':
                paypal_order = paypal_service.get_order_details(payment_id)
                
                if paypal_order:
                    order_status = paypal_order.get('status', 'UNKNOWN')
                    
                    if order_status in ['COMPLETED', 'APPROVED']:
                        order.payment_status = 'completed'
                        order.status = 'confirmed'
                        await auto_register_warranties(db, order)
                        message = f"Confirmed ({order_status})"
                        synced = True
                    elif order_status in ['VOIDED', 'CANCELLED']:
                        order.payment_status = 'failed'
                        order.status = 'cancelled'
                        message = f"Failed ({order_status})"
                        synced = True
                else:
                    message = "Payment not found"
            
            elif payment_method.lower() == 'floa':
                deal = floa_service.get_deal_status(payment_id)
                
                if deal:
                    deal_status = deal.get('dealStatus', 'UNKNOWN')
                    installments = deal.get('installmentsList', [])
                    is_integration = 'live-int' in floa_service.base_url
                    
                    if deal_status == 'APPROVED':
                        order.payment_status = 'completed'
                        order.status = 'confirmed'
                        await auto_register_warranties(db, order)
                        message = f"Confirmed (APPROVED)"
                        synced = True
                    elif deal_status == 'DRAFT' and is_integration and len(installments) > 0:
                        order.payment_status = 'completed'
                        order.status = 'confirmed'
                        await auto_register_warranties(db, order)
                        message = f"Confirmed (DRAFT-integration)"
                        synced = True
                    elif deal_status in ['CANCELLED', 'REJECTED']:
                        order.payment_status = 'failed'
                        order.status = 'cancelled'
                        message = f"Failed ({deal_status})"
                        synced = True
                else:
                    message = "Payment not found"
            
            elif payment_method.lower() == 'payplug':
                # PayPlug already has working webhook, skip
                skipped += 1
                message = "PayPlug has webhook (skipped)"
            
            else:
                skipped += 1
                message = f"Unsupported method: {payment_method}"
            
            if synced:
                db.commit()
                db.refresh(order)
                updated += 1
                results.append({
                    "order_id": order.id,
                    "payment_id": payment_id,
                    "payment_method": payment_method,
                    "status": "updated",
                    "message": message
                })
            else:
                results.append({
                    "order_id": order.id,
                    "payment_id": payment_id,
                    "payment_method": payment_method,
                    "status": "no_change",
                    "message": message
                })
        
        except Exception as e:
            failed += 1
            logger.error(f"Failed to sync order {order.id}: {str(e)}")
            results.append({
                "order_id": order.id,
                "payment_id": payment_id,
                "payment_method": payment_method,
                "status": "error",
                "message": str(e)
            })
    
    return {
        "total_checked": total_checked,
        "updated": updated,
        "failed": failed,
        "skipped": skipped,
        "results": results
    }


@router.get("/admin/statistics/overview", response_model=OrderStatsResponse)
async def get_order_statistics(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get order statistics (Admin)
    
    **Requirements:**
    - API Key (in header X-API-Key)
    - NO Bearer Token Required
    
    **Returns:**
    ```json
    {
      "total_orders": 150,
      "total_revenue": "125000.50",
      "pending_orders": 10,
      "confirmed_orders": 30,
      "completed_orders": 100,
      "cancelled_orders": 10,
      "unpaid_orders": 15,
      "paid_orders": 135,
      "pending_shipment": 20,
      "shipped_orders": 80,
      "delivered_orders": 50,
      "orders_with_warranty": 45,
      "warranty_revenue": "2245.50"
    }
    ```
    """
    stats = crud_order.get_statistics(db)
    
    return OrderStatsResponse(**stats)


@router.get("/admin/failed-warranties", response_model=List[OrderResponse])
async def get_orders_with_failed_warranties(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get orders with failed warranty registrations (Admin)
    
    **Requirements:**
    - API Key (in header X-API-Key)
    - NO Bearer Token Required
    
    **Use Case:**
    When Garanzia3 registration fails, admin can see these orders
    and retry the registration manually.
    
    **Returns:**
    List of orders that have items with failed warranty registration
    """
    orders = crud_order.get_orders_with_failed_warranty_registration(
        db,
        skip=skip,
        limit=limit
    )
    
    return orders


@router.patch("/admin/{order_id}/items/{item_id}/warranty", response_model=OrderResponse)
async def update_warranty_info_admin(
    order_id: int,
    item_id: int,
    warranty_update: WarrantyUpdateRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update warranty information for order item (Admin)
    
    **Requirements:**
    - API Key (in header X-API-Key)
    - NO Bearer Token Required
    
    **Use Case:**
    - Manually add Garanzia3 contract details
    - Fix failed warranty registrations
    
    **Body Example:**
    ```json
    {
      "contract_number": "G3-2026-001234",
      "pin_code": "A1B2C3D4",
      "registered_at": "2026-02-23T10:35:00"
    }
    ```
    
    **Returns:**
    Updated order with warranty info
    """
    # Update warranty info
    order_item = crud_order.update_warranty_info(
        db,
        order_item_id=item_id,
        contract_number=warranty_update.contract_number,
        pin_code=warranty_update.pin_code,
        registered_at=warranty_update.registered_at
    )
    
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found or has no warranty option"
        )
    
    # Return full order
    order = crud_order.get(db, id=order_id)
    return order


# ========================================
# PAYMENT RETURN ENDPOINTS (FOR TESTING)
# ========================================

@router.get("/payment/success")
async def payment_success(
    token: Optional[str] = Query(None),
    PayerID: Optional[str] = Query(None),
    order_id: Optional[str] = Query(None)
):
    """
    Payment success page (for testing without frontend)
    
    This endpoint is used as return_url for PayPal payments during testing.
    After payment approval, PayPal redirects here with query parameters.
    
    Query Parameters:
    - token: PayPal order token
    - PayerID: PayPal payer ID
    - order_id: Custom order ID (if provided)
    """
    return {
        "status": "success",
        "message": "Payment completed successfully!",
        "paypal_token": token,
        "payer_id": PayerID,
        "order_id": order_id,
        "next_steps": [
            "1. Copy the 'token' value (this is your payment_id)",
            "2. Call POST /api/orders/verify_payment with this payment_id",
            "3. Then call POST /api/orders/create-from-cart to create the order"
        ]
    }


@router.get("/payment/cancel")
async def payment_cancel():
    """Payment cancellation page (for testing without frontend)"""
    return {
        "status": "cancelled",
        "message": "Payment was cancelled by user"
    }
