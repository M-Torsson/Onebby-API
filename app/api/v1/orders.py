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
    OrderStatsResponse, WarrantyUpdateRequest
)
from app.crud.order import crud_order
from app.crud import cart as crud_cart
from app.core.security.api_key import verify_api_key
from app.core.security.dependencies import get_current_active_user
from app.models.user import User

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
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_active_user),
    session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Create an order from cart (authenticated user)
    
    **Requirements:**
    - API Key (in header)
    - Bearer Token (authenticated user)
    - Cart must have items
    
    **Body Example (Customer):**
    ```json
    {
      "payment_method": "paypal",
      "customer_info": {
        "reg_type": "user",
        "title": "Sig.",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
      },
      "billing_address": {
        "address_type": "customer",
        "name": "John",
        "last_name": "Doe",
        "address_house_number": "Via Roma 123",
        "house_number": "123",
        "city": "Milan",
        "postal_code": "20100",
        "country": "Italy",
        "phone": "+39 1234567890"
      },
      "shipping_address": {
        "address_type": "customer",
        "name": "John",
        "last_name": "Doe",
        "address_house_number": "Via Roma 123",
        "house_number": "123",
        "city": "Milan",
        "postal_code": "20100",
        "country": "Italy",
        "phone": "+39 1234567890"
      },
      "shipping_method": "standard",
      "customer_note": "Please ring the bell twice"
    }
    ```
    
    **Body Example (Company):**
    ```json
    {
      "payment_method": "scalapay",
      "customer_info": {
        "reg_type": "company",
        "company_name": "ABC SRL",
        "email": "company@example.com",
        "vat_number": "IT12345678901",
        "tax_code": "12345678901",
        "sdi_code": "ABCDEFG",
        "pec": "company@pec.it"
      },
      "billing_address": {
        "address_type": "company",
        "company_name": "ABC SRL",
        "address_house_number": "Via Milano 456",
        "house_number": "456",
        "city": "Rome",
        "postal_code": "00100",
        "country": "Italy",
        "phone": "+39 0612345678"
      },
      "shipping_address": {
        "address_type": "company",
        "company_name": "ABC SRL",
        "address_house_number": "Via Milano 456",
        "house_number": "456",
        "city": "Rome",
        "postal_code": "00100",
        "country": "Italy",
        "phone": "+39 0612345678"
      },
      "shipping_method": "express"
    }
    ```
    
    **Returns:**
    - Order object with status 'pending'
    - Payment needs to be completed separately
    """
    user_id = int(current_user["id"])
    
    # Get user's cart
    cart = crud_cart.get_active_cart(db, user_id=user_id, session_id=session_id)
    
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
            user_id=user_id,
            session_id=session_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return order


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
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get current user's orders
    
    **Requirements:**
    - API Key
    - Bearer Token (authenticated user)
    
    **Query Parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 100)
    
    **Returns:**
    List of orders (summary) for the authenticated user
    """
    user_id = int(current_user["id"])
    
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
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get order details
    
    **Requirements:**
    - API Key
    - Bearer Token (authenticated user)
    - User must own the order
    
    **Returns:**
    Full order details including items
    """
    user_id = int(current_user["id"])
    
    order = crud_order.get(db, id=order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify order belongs to user
    if order.user_id != user_id:
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
    current_admin: User = Depends(get_current_admin_user),
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
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get order details (Admin only)
    
    **Requirements:**
    - API Key
    - Bearer Token (admin user)
    
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
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update order (Admin only)
    
    **Requirements:**
    - API Key
    - Bearer Token (admin user)
    
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
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get order statistics (Admin only)
    
    **Requirements:**
    - API Key
    - Bearer Token (admin user)
    
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
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get orders with failed warranty registrations (Admin only)
    
    **Requirements:**
    - API Key
    - Bearer Token (admin user)
    
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
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update warranty information for order item (Admin only)
    
    **Requirements:**
    - API Key
    - Bearer Token (admin user)
    
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
