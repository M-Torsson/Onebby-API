# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from decimal import Decimal
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.schemas.cart import CartItemAdd, CartItemUpdate


# ============= Cart CRUD Functions =============

def get_or_create_active_cart(
    db: Session,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None
) -> Cart:
    """Get active cart for user/session or create new one"""
    # Try to find active cart
    query = db.query(Cart).filter(Cart.status == "active")
    
    if user_id:
        query = query.filter(Cart.user_id == user_id)
    elif session_id:
        query = query.filter(Cart.session_id == session_id)
    else:
        return None
    
    cart = query.first()
    
    # Create new cart if not exists
    if not cart:
        cart = Cart(
            user_id=user_id,
            session_id=session_id,
            status="active"
        )
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    return cart


def get_cart_by_id(db: Session, cart_id: int) -> Optional[Cart]:
    """Get cart by ID with items"""
    return db.query(Cart).options(
        joinedload(Cart.items).joinedload(CartItem.product),
        joinedload(Cart.items).joinedload(CartItem.product_variant)
    ).filter(Cart.id == cart_id).first()


def get_active_cart(
    db: Session,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None
) -> Optional[Cart]:
    """Get active cart for user/session"""
    query = db.query(Cart).options(
        joinedload(Cart.items).joinedload(CartItem.product),
        joinedload(Cart.items).joinedload(CartItem.product_variant)
    ).filter(Cart.status == "active")
    
    if user_id:
        query = query.filter(Cart.user_id == user_id)
    elif session_id:
        query = query.filter(Cart.session_id == session_id)
    else:
        return None
    
    return query.first()


# ============= Cart Item CRUD Functions =============

def add_item_to_cart(
    db: Session,
    cart_id: int,
    item_data: CartItemAdd
) -> Tuple[CartItem, str]:
    """
    Add item to cart or update quantity if already exists
    Returns: (CartItem, action) where action is 'added' or 'updated'
    """
    # Get product to check availability and price
    product = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not product:
        raise ValueError("Product not found")
    
    if not product.is_active:
        raise ValueError("Product is not available")
    
    # Determine which price and stock to use
    if item_data.product_variant_id:
        variant = db.query(ProductVariant).filter(
            ProductVariant.id == item_data.product_variant_id,
            ProductVariant.product_id == item_data.product_id
        ).first()
        
        if not variant:
            raise ValueError("Product variant not found")
        
        current_price = variant.price or (product.price if hasattr(product, 'price') and product.price else None)
        current_stock = variant.stock
        current_discount = variant.discount_price if variant.discount_price else None
    else:
        # Check if product has price attribute
        if not hasattr(product, 'price') or product.price is None:
            raise ValueError(f"Product {product.id} does not have a valid price")
        
        current_price = product.price
        current_stock = product.stock if hasattr(product, 'stock') else 0
        current_discount = product.discount_price if hasattr(product, 'discount_price') else None
    
    # Validate price
    if current_price is None or current_price <= 0:
        raise ValueError(f"Product price is invalid or not set")
    
    # Check stock availability
    if current_stock < item_data.quantity:
        raise ValueError(f"Insufficient stock. Available: {current_stock}")
    
    # Check if item already exists in cart
    existing_item = db.query(CartItem).filter(
        and_(
            CartItem.cart_id == cart_id,
            CartItem.product_id == item_data.product_id,
            CartItem.product_variant_id == item_data.product_variant_id
        )
    ).first()
    
    if existing_item:
        # Update quantity
        new_quantity = existing_item.quantity + item_data.quantity
        
        # Check if new quantity exceeds stock
        if new_quantity > current_stock:
            raise ValueError(f"Cannot add {item_data.quantity} more. Maximum available: {current_stock}")
        
        existing_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item, "updated"
    else:
        # Create new cart item
        cart_item = CartItem(
            cart_id=cart_id,
            product_id=item_data.product_id,
            product_variant_id=item_data.product_variant_id,
            quantity=item_data.quantity,
            price_at_add=current_price,
            discount_at_add=current_discount or Decimal(0)
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return cart_item, "added"


def update_cart_item_quantity(
    db: Session,
    item_id: int,
    cart_id: int,
    quantity: int
) -> Optional[CartItem]:
    """Update cart item quantity"""
    cart_item = db.query(CartItem).filter(
        and_(
            CartItem.id == item_id,
            CartItem.cart_id == cart_id
        )
    ).first()
    
    if not cart_item:
        return None
    
    # Check stock availability
    product = cart_item.product
    if cart_item.product_variant_id:
        variant = cart_item.product_variant
        available_stock = variant.stock
    else:
        available_stock = product.stock
    
    if quantity > available_stock:
        raise ValueError(f"Insufficient stock. Available: {available_stock}")
    
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


def remove_cart_item(db: Session, item_id: int, cart_id: int) -> bool:
    """Remove item from cart"""
    cart_item = db.query(CartItem).filter(
        and_(
            CartItem.id == item_id,
            CartItem.cart_id == cart_id
        )
    ).first()
    
    if not cart_item:
        return False
    
    db.delete(cart_item)
    db.commit()
    return True


def clear_cart(db: Session, cart_id: int) -> bool:
    """Remove all items from cart"""
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        return False
    
    # Delete all cart items
    db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
    db.commit()
    return True


def delete_cart(db: Session, cart_id: int) -> bool:
    """Delete cart completely"""
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        return False
    
    db.delete(cart)
    db.commit()
    return True


# ============= Cart Validation Functions =============

def validate_cart_for_checkout(db: Session, cart_id: int) -> Tuple[bool, List[dict], List[dict]]:
    """
    Validate cart before checkout
    Returns: (is_valid, errors, warnings)
    """
    cart = get_cart_by_id(db, cart_id)
    if not cart:
        return False, [{"message": "Cart not found"}], []
    
    if not cart.items:
        return False, [{"message": "Cart is empty"}], []
    
    errors = []
    warnings = []
    
    for item in cart.items:
        product = item.product
        
        # Check if product still exists and is active
        if not product or not product.is_active:
            errors.append({
                "item_id": item.id,
                "product_id": item.product_id,
                "message": "Product is no longer available",
                "type": "product_unavailable"
            })
            continue
        
        # Determine current stock and price
        if item.product_variant_id:
            variant = item.product_variant
            if not variant:
                errors.append({
                    "item_id": item.id,
                    "product_id": item.product_id,
                    "message": "Product variant is no longer available",
                    "type": "variant_unavailable"
                })
                continue
            
            current_stock = variant.stock
            current_price = variant.price or (product.price if hasattr(product, 'price') else None)
        else:
            current_stock = product.stock if hasattr(product, 'stock') else 0
            current_price = product.price if hasattr(product, 'price') else None
        
        # Check if price is valid
        if current_price is None or current_price <= 0:
            errors.append({
                "item_id": item.id,
                "product_id": item.product_id,
                "message": "Product price is not set or invalid",
                "type": "invalid_price"
            })
            continue
        
        # Check stock availability
        if current_stock <= 0:
            errors.append({
                "item_id": item.id,
                "product_id": item.product_id,
                "message": "Product is out of stock",
                "type": "out_of_stock"
            })
        elif item.quantity > current_stock:
            errors.append({
                "item_id": item.id,
                "product_id": item.product_id,
                "message": f"Insufficient stock. Available: {current_stock}, Requested: {item.quantity}",
                "type": "insufficient_stock"
            })
        elif current_stock < 10:  # Low stock warning
            warnings.append({
                "item_id": item.id,
                "product_id": item.product_id,
                "message": f"Low stock: only {current_stock} items left",
                "type": "stock_low"
            })
        
        # Check price changes
        if current_price != item.price_at_add:
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
    
    is_valid = len(errors) == 0
    return is_valid, errors, warnings


# ============= Cart Merge Function =============

def merge_carts(db: Session, session_id: str, user_id: int) -> Cart:
    """Merge guest cart into user cart after login"""
    # Get guest cart
    guest_cart = db.query(Cart).filter(
        and_(
            Cart.session_id == session_id,
            Cart.status == "active"
        )
    ).first()
    
    if not guest_cart:
        # No guest cart to merge, just get or create user cart
        return get_or_create_active_cart(db, user_id=user_id)
    
    # Get or create user cart
    user_cart = get_or_create_active_cart(db, user_id=user_id)
    
    # Merge items from guest cart to user cart
    for guest_item in guest_cart.items:
        # Check if item already exists in user cart
        existing_item = db.query(CartItem).filter(
            and_(
                CartItem.cart_id == user_cart.id,
                CartItem.product_id == guest_item.product_id,
                CartItem.product_variant_id == guest_item.product_variant_id
            )
        ).first()
        
        if existing_item:
            # Update quantity (don't exceed stock)
            product = guest_item.product
            if guest_item.product_variant_id:
                available_stock = guest_item.product_variant.stock
            else:
                available_stock = product.stock
            
            new_quantity = min(existing_item.quantity + guest_item.quantity, available_stock)
            existing_item.quantity = new_quantity
        else:
            # Move item to user cart
            guest_item.cart_id = user_cart.id
    
    # Delete guest cart
    db.delete(guest_cart)
    db.commit()
    db.refresh(user_cart)
    
    return user_cart


# ============= Clean up old carts =============

def cleanup_abandoned_carts(db: Session, days_old: int = 30) -> int:
    """Delete carts that are older than specified days and not completed"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    old_carts = db.query(Cart).filter(
        and_(
            Cart.status == "active",
            Cart.created_at < cutoff_date
        )
    ).all()
    
    count = len(old_carts)
    
    for cart in old_carts:
        cart.status = "abandoned"
    
    db.commit()
    return count
