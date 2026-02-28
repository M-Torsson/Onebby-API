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
    PayUrlRequest, PayUrlResponse, PaymentVerifyRequest, PaymentVerifyResponse
)
from app.crud.order import crud_order
from app.crud import cart as crud_cart
from app.core.security.api_key import verify_api_key
from app.core.security.dependencies import get_current_active_user
from app.models.user import User
from app.integrations.payplug import payplug_service
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

@router.post("/create-from-cart", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
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
      "user_id": 5,
      "reg_type": "customer",
      "address_id": 6,
      "order_date": "22-2-2222",
      "customer_note": "Please ring the bell twice",
      "payment_info": {
        "payment_type": "PayPal",
        "payment_status": "successful",
        "invoice_num": 2234454,
        "payment_id": 3
      },
      "items": [
        {
          "product_id": 99898,
          "qty": 2,
          "warranty": {
            "title": "GARANZIA3 – 3 Years",
            "cost": 49.90
          },
          "delivery_opt": {
            "title": "Delivery to floor",
            "cost": 69.0
          }
        },
        {
          "product_id": 44333,
          "qty": 5,
          "warranty": null,
          "delivery_opt": null
        }
      ]
    }
    ```
    
    **Note:** Total is calculated automatically by the system
    
    **Returns:**
    - Order object with full details including calculated totals
    - Payment URL for completing payment (if PayPlug is enabled)
    - Stock is automatically reduced
    """
    # Create order directly (no cart needed)
    try:
        order = crud_order.create_direct(
            db=db,
            order_data=order_data,
            user_id=order_data.user_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Initialize payment_url as None
    payment_url = None
    payment_error = None
    
    # Create PayPlug payment if configured and payment type is PayPal/card/payplug
    if (settings.PAYPLUG_API_KEY and 
        order_data.payment_info.payment_type.lower() in ['paypal', 'card', 'credit_card', 'payplug']):
        try:
            # Get customer info
            customer_info = order.customer_info
            customer_email = customer_info.get('email', '')
            customer_first_name = customer_info.get('first_name', '') or customer_info.get('company_name' , '')
            customer_last_name = customer_info.get('last_name', '')
            
            # Create payment URLs
            return_url = f"{settings.FRONTEND_URL}/orders/{order.id}/payment-success"
            cancel_url = f"{settings.FRONTEND_URL}/orders/{order.id}/payment-cancel"
            
            # Create payment
            payment_result = payplug_service.create_payment(
                amount=order.total_amount,
                order_id=order.id,
                customer_email=customer_email,
                customer_first_name=customer_first_name,
                customer_last_name=customer_last_name,
                return_url=return_url,
                cancel_url=cancel_url
            )
            
            payment_url = payment_result['payment_url']
            
            # Update order with PayPlug payment ID
            order.payment_transaction_id = payment_result['payment_id']
            order.payment_status = 'pending'  # Will be updated by webhook
            db.commit()
            db.refresh(order)
            
        except Exception as e:
            # Log error but don't fail order creation
            payment_error = str(e)
            print(f"PayPlug payment creation failed: {payment_error}")
    
    # Convert order to response model
    order_response = OrderResponse.model_validate(order)
    
    # Add payment_url if available
    if payment_url:
        # Convert to dict, add payment_url, and return
        response_dict = order_response.model_dump()
        response_dict['payment_url'] = payment_url
        return response_dict
    
    return order_response


@router.post("/get_pay_url", response_model=PayUrlResponse, status_code=status.HTTP_200_OK)
async def get_payment_url(
    request: PayUrlRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get PayPlug payment URL without creating an order
    
    **Requirements:**
    - API Key (in header X-API-Key)
    
    **Request Body:**
    ```json
    {
      "payment_type": "PayPal",
      "user_id": 5,
      "total": 2300.98
    }
    ```
    
    **Returns:**
    - user_id: User ID who requested payment
    - payment_id: PayPlug payment ID (use this for verification!)
    - payment_url: PayPlug payment URL (redirect user here - contains payment_id)
    - amount: Payment amount
    """
    # Validate payment type
    if request.payment_type.lower() not in ['paypal', 'payplug', 'card', 'credit_card']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment type. Allowed: PayPal, PayPlug, card, credit_card"
        )
    
    # Verify user exists
    from app.models.user import User
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {request.user_id} not found"
        )
    
    # Check if PayPlug is configured
    if not settings.PAYPLUG_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PayPlug is not configured"
        )
    
    try:
        # Get user email and info
        user_email = ""
        user_first_name = ""
        user_last_name = ""
        
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
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment: {str(e)}"
        )


@router.post("/verify_payment", response_model=PaymentVerifyResponse, status_code=status.HTTP_200_OK)
async def verify_payment_status(
    verify_request: PaymentVerifyRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Verify PayPlug payment status
    
    **Use this after user returns from PayPlug payment page**
    
    **Requirements:**
    - API Key (in header X-API-Key)
    
    **Request Body:**
    ```json
    {
      "payment_id": "pay_xxxxx"
    }
    ```
    
    **Returns:**
    - payment_id: PayPlug payment ID
    - status: completed, pending, or failed
    - amount: Payment amount
    - is_paid: true if payment completed
    - created_at: When payment was created
    - paid_at: When payment was completed (if completed)
    - customer_email: Customer email
    
    **Flow:**
    1. User gets payment_id from /get_pay_url response
    2. User completes payment on PayPlug
    3. User returns to your site
    4. Call this endpoint with payment_id to verify payment status
    5. If is_paid=true, payment successful!
    """
    # Check if PayPlug is configured
    if not settings.PAYPLUG_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PayPlug is not configured"
        )
    
    try:
        # Get payment ID from request
        payment_id = verify_request.payment_id
        
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
        
        # Get customer email (try multiple ways)
        customer_email = None
        try:
            if hasattr(payment, 'customer') and payment.customer:
                # Try as dictionary
                if isinstance(payment.customer, dict):
                    customer_email = payment.customer.get('email')
                # Try as object attribute
                elif hasattr(payment.customer, 'email'):
                    customer_email = payment.customer.email
        except (TypeError, KeyError, AttributeError):
            customer_email = None
        
        # Get transaction number (search in multiple places)
        transaction_number = None
        try:
            # Try different sources for transaction number:
            
            # 1. Authorization ID (from bank)
            if hasattr(payment, 'authorization') and payment.authorization:
                if isinstance(payment.authorization, dict):
                    transaction_number = payment.authorization.get('authorization_id') or payment.authorization.get('id')
                elif hasattr(payment.authorization, 'authorization_id'):
                    transaction_number = payment.authorization.authorization_id
                elif hasattr(payment.authorization, 'id'):
                    transaction_number = payment.authorization.id
            
            # 2. Card transaction ID
            if not transaction_number and hasattr(payment, 'card') and payment.card:
                if isinstance(payment.card, dict):
                    transaction_number = payment.card.get('id') or payment.card.get('transaction_id')
                elif hasattr(payment.card, 'id'):
                    transaction_number = payment.card.id
                elif hasattr(payment.card, 'transaction_id'):
                    transaction_number = payment.card.transaction_id
            
            # 3. Check for id_transaction field
            if not transaction_number and hasattr(payment, 'id_transaction'):
                transaction_number = payment.id_transaction
            
            # 4. Check for transaction_id field
            if not transaction_number and hasattr(payment, 'transaction_id'):
                transaction_number = payment.transaction_id
            
            # 5. Last resort: return None to avoid duplicating payment_id
            if not transaction_number:
                transaction_number = None
                
        except (TypeError, KeyError, AttributeError):
            transaction_number = None
        
        # Build response (exclude None values)
        response_data = {
            "payment_id": payment.id,
            "status": status_text,
            "amount": payment.amount / 100,  # PayPlug uses cents
            "is_paid": is_paid,
        }
        
        # Add optional fields only if they have values
        if transaction_number:
            response_data["transaction_number"] = transaction_number
        if created_at:
            response_data["created_at"] = created_at
        if paid_at:
            response_data["paid_at"] = paid_at
        if customer_email:
            response_data["customer_email"] = customer_email
        
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
