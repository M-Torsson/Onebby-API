# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from app.db.session import get_db
from app.schemas.cart import (
    CartItemAdd, CartItemUpdate, CartItemResponse, CartResponse,
    CartValidationResponse, CartMergeRequest, CartTotals
)
from app.crud import cart as crud_cart
from app.core.security.api_key import verify_api_key

router = APIRouter()


def get_user_or_session(
    user_id: Optional[int] = None,
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """Helper to get user_id or session_id"""
    if not user_id and not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either user_id or X-Session-ID header is required"
        )
    return user_id, session_id


def calculate_cart_totals(cart) -> dict:
    """Calculate cart totals"""
    subtotal = Decimal(0)
    total_discount = Decimal(0)
    items_count = 0
    
    for item in cart.items:
        # Get current price
        if item.product_variant_id and item.product_variant:
            current_price = item.product_variant.price_list if hasattr(item.product_variant, 'price_list') else Decimal(0)
        else:
            current_price = item.product.price_list if hasattr(item.product, 'price_list') else Decimal(0)
        
        # Skip items with invalid prices
        if current_price <= 0:
            continue
        
        # Calculate item totals
        item_subtotal = current_price * item.quantity
        
        subtotal += item_subtotal
        items_count += item.quantity
    
    total = subtotal
    
    return {
        "subtotal": float(subtotal),
        "total_discount": 0.0,
        "total": float(total),
        "items_count": items_count
    }


def build_cart_response(cart, db: Session) -> dict:
    """Build cart response with all details"""
    items_response = []
    warnings = []
    
    for item in cart.items:
        product = item.product
        
        if not product:
            warnings.append({
                "item_id": item.id,
                "product_id": item.product_id,
                "message": "Product not found",
                "type": "product_not_found"
            })
            continue
        
        # Get variant details if applicable
        variant_name = None
        if item.product_variant_id and item.product_variant:
            variant = item.product_variant
            variant_name = variant.reference or f"Variant {variant.id}"
            current_price = variant.price_list if hasattr(variant, 'price_list') else None
            stock_available = variant.stock_quantity if hasattr(variant, 'stock_quantity') else 0
        else:
            current_price = product.price_list if hasattr(product, 'price_list') else None
            stock_available = product.stock_quantity if hasattr(product, 'stock_quantity') else 0
        
        # Check if price is valid
        if current_price is None or current_price <= 0:
            warnings.append({
                "item_id": item.id,
                "product_id": item.product_id,
                "message": "Product price is not set or invalid",
                "type": "invalid_price"
            })
            continue
        
        # Check for price changes
        price_changed = (current_price != item.price_at_add)
        if price_changed:
            price_diff = current_price - item.price_at_add
            if price_diff > 0:
                warnings.append({
                    "item_id": item.id,
                    "product_id": item.product_id,
                    "message": f"Price increased from {item.price_at_add} to {current_price}",
                    "type": "price_increased"
                })
            else:
                warnings.append({
                    "item_id": item.id,
                    "product_id": item.product_id,
                    "message": f"Price decreased from {item.price_at_add} to {current_price}",
                    "type": "price_decreased"
                })
        
        # Check stock availability
        is_available = stock_available >= item.quantity
        if not is_available:
            warnings.append({
                "item_id": item.id,
                "product_id": item.product_id,
                "message": f"Insufficient stock. Available: {stock_available}, In cart: {item.quantity}",
                "type": "insufficient_stock"
            })
        elif stock_available < 10:
            warnings.append({
                "item_id": item.id,
                "product_id": item.product_id,
                "message": f"Low stock: only {stock_available} items left",
                "type": "stock_low"
            })
        
        # Calculate item totals
        item_subtotal = current_price * item.quantity
        item_total = item_subtotal
        
        # Get product image (first image)
        product_image = None
        if product.images and len(product.images) > 0:
            product_image = product.images[0].url
        
        items_response.append({
            "id": item.id,
            "cart_id": item.cart_id,
            "product_id": item.product_id,
            "product_variant_id": item.product_variant_id,
            "quantity": item.quantity,
            "price_at_add": float(item.price_at_add),
            "discount_at_add": float(item.discount_at_add) if item.discount_at_add else 0,
            "current_price": float(current_price),
            "price_changed": price_changed,
            "item_subtotal": float(item_subtotal),
            "item_total": float(item_total),
            "stock_available": stock_available,
            "is_available": is_available,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "product_name": product.reference or f"Product {product.id}",
            "product_image": product_image,
            "product_reference": product.reference,
            "variant_name": variant_name
        })
    
    totals = calculate_cart_totals(cart)
    
    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "session_id": cart.session_id,
        "status": cart.status,
        "items": items_response,
        "totals": totals,
        "warnings": warnings,
        "created_at": cart.created_at,
        "updated_at": cart.updated_at,
        "expires_at": cart.expires_at
    }


# ============= Cart Endpoints =============

@router.post("/items", status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    item_data: CartItemAdd,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Add item to cart
    
    For logged-in users: provide user_id as query parameter
    For guests: provide X-Session-ID in header
    
    Request Body Example:
    ```json
    {
        "product_id": 123,
        "product_variant_id": 456,
        "quantity": 2
    }
    ```
    """
    # Get or create cart
    try:
        cart = crud_cart.get_or_create_active_cart(
            db=db,
            user_id=user_id,
            session_id=session_id
        )
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either user_id or X-Session-ID is required"
            )
        
        # Add item to cart
        cart_item, action = crud_cart.add_item_to_cart(
            db=db,
            cart_id=cart.id,
            item_data=item_data
        )
        
        # Get updated cart
        cart = crud_cart.get_cart_by_id(db, cart.id)
        response = build_cart_response(cart, db)
        
        return {
            "message": f"Item {action} successfully",
            "cart": response
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=CartResponse)
async def get_cart(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Get active cart
    
    For logged-in users: provide user_id as query parameter
    For guests: provide X-Session-ID in header
    """
    cart = crud_cart.get_active_cart(
        db=db,
        user_id=user_id,
        session_id=session_id
    )
    
    if not cart:
        # Return empty cart
        return {
            "id": 0,
            "user_id": user_id,
            "session_id": session_id,
            "status": "active",
            "items": [],
            "totals": {
                "subtotal": 0,
                "total_discount": 0,
                "total": 0,
                "items_count": 0
            },
            "warnings": [],
            "created_at": None,
            "updated_at": None,
            "expires_at": None
        }
    
    response = build_cart_response(cart, db)
    return response


@router.put("/items/{item_id}")
async def update_cart_item(
    item_id: int,
    update_data: CartItemUpdate,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Update cart item quantity
    
    Request Body Example:
    ```json
    {
        "quantity": 5
    }
    ```
    """
    # Get cart
    cart = crud_cart.get_active_cart(
        db=db,
        user_id=user_id,
        session_id=session_id
    )
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    try:
        # Update item
        updated_item = crud_cart.update_cart_item_quantity(
            db=db,
            item_id=item_id,
            cart_id=cart.id,
            quantity=update_data.quantity
        )
        
        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        
        # Get updated cart
        cart = crud_cart.get_cart_by_id(db, cart.id)
        response = build_cart_response(cart, db)
        
        return {
            "message": "Item updated successfully",
            "cart": response
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
async def remove_cart_item(
    item_id: int,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """Remove item from cart"""
    # Get cart
    cart = crud_cart.get_active_cart(
        db=db,
        user_id=user_id,
        session_id=session_id
    )
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    # Remove item
    success = crud_cart.remove_cart_item(
        db=db,
        item_id=item_id,
        cart_id=cart.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Get updated cart
    cart = crud_cart.get_cart_by_id(db, cart.id)
    response = build_cart_response(cart, db)
    
    return {
        "message": "Item removed successfully",
        "cart": response
    }


@router.delete("", status_code=status.HTTP_200_OK)
async def clear_cart(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """Clear all items from cart"""
    # Get cart
    cart = crud_cart.get_active_cart(
        db=db,
        user_id=user_id,
        session_id=session_id
    )
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    # Clear cart
    success = crud_cart.clear_cart(db=db, cart_id=cart.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    return {
        "message": "Cart cleared successfully"
    }


@router.post("/validate", response_model=CartValidationResponse)
async def validate_cart(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
    session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Validate cart before checkout
    
    Checks:
    - Product availability
    - Stock availability
    - Price changes
    """
    # Get cart
    cart = crud_cart.get_active_cart(
        db=db,
        user_id=user_id,
        session_id=session_id
    )
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    # Validate cart
    is_valid, errors, warnings = crud_cart.validate_cart_for_checkout(
        db=db,
        cart_id=cart.id
    )
    
    totals = calculate_cart_totals(cart)
    
    return {
        "is_valid": is_valid,
        "cart_id": cart.id,
        "items_count": len(cart.items),
        "errors": errors,
        "warnings": warnings,
        "totals": totals
    }


@router.post("/merge")
async def merge_carts(
    merge_data: CartMergeRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Merge guest cart with user cart after login
    
    Request Body Example:
    ```json
    {
        "session_id": "guest-session-id-12345",
        "user_id": 123
    }
    ```
    """
    try:
        merged_cart = crud_cart.merge_carts(
            db=db,
            session_id=merge_data.session_id,
            user_id=merge_data.user_id
        )
        
        response = build_cart_response(merged_cart, db)
        
        return {
            "message": "Carts merged successfully",
            "cart": response
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
