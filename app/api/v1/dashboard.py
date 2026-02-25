# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
from typing import Optional, List
from decimal import Decimal

from app.db.session import get_db
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    DashboardProductsResponse,
    DashboardProductItem,
    DashboardPaymentsResponse,
    DashboardPaymentItem,
    DashboardCRMLiveResponse
)
from app.models.category import Category
from app.models.brand import Brand
from app.models.product import Product, ProductTranslation
from app.models.order import Order
from app.models.payment import Payment
from app.core.security.api_key import verify_api_key
from app.core.security.dependencies import get_current_active_user

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


def calculate_percentage_change(current: float, previous: float) -> float:
    """Calculate percentage change between two values"""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 2)


# ========================================
# DASHBOARD OVERVIEW ENDPOINT
# ========================================

@router.get("/admin/dashboard/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Get dashboard overview statistics
    
    Returns:
    - Total categories, brands, products
    - Total revenue
    - Orders, sales, and profit statistics with percentage changes
    """
    
    # Get current date and calculate time ranges
    now = datetime.utcnow()
    
    # Last week range
    last_week_start = now - timedelta(days=7)
    previous_week_start = now - timedelta(days=14)
    previous_week_end = last_week_start
    
    # Last year range
    last_year_start = now - timedelta(days=365)
    previous_year_start = now - timedelta(days=730)
    previous_year_end = last_year_start
    
    # ========== Main Statistics ==========
    
    # Count categories
    total_categories = db.query(func.count(Category.id)).filter(
        Category.is_active == True
    ).scalar() or 0
    
    # Count brands
    total_brands = db.query(func.count(Brand.id)).filter(
        Brand.is_active == True
    ).scalar() or 0
    
    # Count products
    total_products = db.query(func.count(Product.id)).filter(
        Product.is_active == True
    ).scalar() or 0
    
    # Calculate total revenue (all completed orders)
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.payment_status == 'completed'
    ).scalar() or 0.0
    total_revenue = float(total_revenue) if total_revenue else 0.0
    
    # ========== Orders Last Week ==========
    
    # Orders last week
    orders_last_week = db.query(func.sum(Order.total_amount)).filter(
        and_(
            Order.created_at >= last_week_start,
            Order.created_at <= now,
            Order.payment_status == 'completed'
        )
    ).scalar() or 0.0
    orders_last_week = float(orders_last_week) if orders_last_week else 0.0
    
    # Orders previous week (for comparison)
    orders_previous_week = db.query(func.sum(Order.total_amount)).filter(
        and_(
            Order.created_at >= previous_week_start,
            Order.created_at < previous_week_end,
            Order.payment_status == 'completed'
        )
    ).scalar() or 0.0
    orders_previous_week = float(orders_previous_week) if orders_previous_week else 0.0
    
    # Calculate percentage change
    orders_last_week_change_pct = calculate_percentage_change(
        orders_last_week, orders_previous_week
    )
    
    # ========== Sales Last Year ==========
    
    # Sales last year
    sales_last_year = db.query(func.sum(Order.total_amount)).filter(
        and_(
            Order.created_at >= last_year_start,
            Order.created_at <= now,
            Order.payment_status == 'completed'
        )
    ).scalar() or 0.0
    sales_last_year = float(sales_last_year) if sales_last_year else 0.0
    
    # Sales previous year (for comparison)
    sales_previous_year = db.query(func.sum(Order.total_amount)).filter(
        and_(
            Order.created_at >= previous_year_start,
            Order.created_at < previous_year_end,
            Order.payment_status == 'completed'
        )
    ).scalar() or 0.0
    sales_previous_year = float(sales_previous_year) if sales_previous_year else 0.0
    
    # Calculate percentage change
    sales_last_year_change_pct = calculate_percentage_change(
        sales_last_year, sales_previous_year
    )
    
    # ========== Profit Last Week ==========
    # Note: For profit calculation, we're using a simplified approach
    # In a real scenario, profit = revenue - costs
    # Here we'll use: profit = revenue * 0.15 (assuming 15% profit margin)
    
    profit_last_week = orders_last_week * 0.15
    profit_previous_week = orders_previous_week * 0.15
    
    profit_last_week_change_pct = calculate_percentage_change(
        profit_last_week, profit_previous_week
    )
    
    # ========== Sales Last Week ==========
    # Sales last week (same as orders for now, but kept separate for flexibility)
    sales_last_week = orders_last_week
    sales_previous_week = orders_previous_week
    
    sales_last_week_change_pct = calculate_percentage_change(
        sales_last_week, sales_previous_week
    )
    
    # Return response
    return DashboardOverviewResponse(
        categories=total_categories,
        brands=total_brands,
        products=total_products,
        revenue=total_revenue,
        orders_last_week=orders_last_week,
        orders_last_week_change_pct=orders_last_week_change_pct,
        sales_last_year=sales_last_year,
        sales_last_year_change_pct=sales_last_year_change_pct,
        profit_last_week=profit_last_week,
        profit_last_week_change_pct=profit_last_week_change_pct,
        sales_last_week=sales_last_week,
        sales_last_week_change_pct=sales_last_week_change_pct
    )


# ========================================
# LATEST PRODUCTS ENDPOINT
# ========================================

@router.get("/admin/dashboard/products/recent", response_model=DashboardProductsResponse)
async def get_latest_products(
    limit: int = Query(default=10, ge=1, le=50, description="Number of products to return"),
    lang: str = Query(default="en", description="Language code (en, it, ar, fr, de)"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Get latest products for dashboard
    
    Returns the most recently created products with their basic info
    """
    
    # Query latest products
    products = db.query(Product).filter(
        Product.is_active == True
    ).order_by(desc(Product.created_at)).limit(limit).all()
    
    # Build response items
    items = []
    for product in products:
        # Get translation for requested language
        title = None
        translation = None
        
        if product.translations:
            # Try requested language
            translation = next((t for t in product.translations if t.lang == lang), None)
            # Fallback to Italian
            if not translation:
                translation = next((t for t in product.translations if t.lang == "it"), None)
            # Last fallback
            if not translation and product.translations:
                translation = product.translations[0]
        
        if translation:
            title = translation.name
        else:
            title = f"Product {product.id}"
        
        # Get first image
        image_url = None
        if product.images and len(product.images) > 0:
            # Sort by position and get first
            sorted_images = sorted(product.images, key=lambda x: x.position or 999)
            image_url = sorted_images[0].url if sorted_images else None
        
        # Get price (use price_final if available, otherwise price_list)
        price = product.price_final if product.price_final else (product.price_list if product.price_list else 0.0)
        
        items.append(DashboardProductItem(
            id=product.id,
            title=title,
            sku=product.reference,
            price=float(price),
            currency="EUR",
            image=image_url,
            created_at=product.created_at
        ))
    
    return DashboardProductsResponse(
        items=items,
        meta={"total": len(items)}
    )


# ========================================
# LATEST PAYMENTS ENDPOINT
# ========================================

@router.get("/admin/dashboard/payments/recent", response_model=DashboardPaymentsResponse)
async def get_latest_payments(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=50, description="Number of payments to return"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Get latest payments for dashboard
    
    Returns the most recent payment transactions sorted by creation date (descending)
    """
    
    # Get total count
    total = db.query(func.count(Payment.id)).scalar() or 0
    
    # Query latest payments
    payments = db.query(Payment).order_by(
        desc(Payment.created_at)
    ).offset(skip).limit(limit).all()
    
    # Build response items
    payment_items = []
    for payment in payments:
        payment_items.append(DashboardPaymentItem(
            id=payment.id,
            amount=float(payment.amount),
            currency=payment.currency,
            status=payment.status,
            provider=payment.provider,
            payment_method=payment.payment_method,
            order_id=payment.order_id,
            created_at=payment.created_at
        ))
    
    return DashboardPaymentsResponse(
        payments=payment_items,
        total=total
    )


# ========================================
# COMBINED CRM LIVE ENDPOINT (OPTIMAL)
# ========================================

@router.get("/admin/dashboard/crm-live", response_model=DashboardCRMLiveResponse)
async def get_crm_live_data(
    lang: str = Query(default="ar", description="Language code for products"),
    limit_products: int = Query(default=10, ge=1, le=50, description="Number of products to return"),
    limit_payments: int = Query(default=10, ge=1, le=50, description="Number of payments to return"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Get all CRM dashboard data in a single request (optimal performance)
    
    Returns:
    - Overview statistics
    - Latest products
    - Latest payments
    
    This endpoint combines all three separate endpoints into one,
    reducing the number of HTTP requests and improving load time.
    """
    
    # Get overview data (reuse logic from overview endpoint)
    now = datetime.utcnow()
    last_week_start = now - timedelta(days=7)
    previous_week_start = now - timedelta(days=14)
    previous_week_end = last_week_start
    last_year_start = now - timedelta(days=365)
    previous_year_start = now - timedelta(days=730)
    previous_year_end = last_year_start
    
    # Main statistics
    total_categories = db.query(func.count(Category.id)).filter(Category.is_active == True).scalar() or 0
    total_brands = db.query(func.count(Brand.id)).filter(Brand.is_active == True).scalar() or 0
    total_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar() or 0
    total_revenue = float(db.query(func.sum(Order.total_amount)).filter(Order.payment_status == 'completed').scalar() or 0.0)
    
    # Orders last week
    orders_last_week = float(db.query(func.sum(Order.total_amount)).filter(
        and_(Order.created_at >= last_week_start, Order.created_at <= now, Order.payment_status == 'completed')
    ).scalar() or 0.0)
    orders_previous_week = float(db.query(func.sum(Order.total_amount)).filter(
        and_(Order.created_at >= previous_week_start, Order.created_at < previous_week_end, Order.payment_status == 'completed')
    ).scalar() or 0.0)
    orders_last_week_change_pct = calculate_percentage_change(orders_last_week, orders_previous_week)
    
    # Sales last year
    sales_last_year = float(db.query(func.sum(Order.total_amount)).filter(
        and_(Order.created_at >= last_year_start, Order.created_at <= now, Order.payment_status == 'completed')
    ).scalar() or 0.0)
    sales_previous_year = float(db.query(func.sum(Order.total_amount)).filter(
        and_(Order.created_at >= previous_year_start, Order.created_at < previous_year_end, Order.payment_status == 'completed')
    ).scalar() or 0.0)
    sales_last_year_change_pct = calculate_percentage_change(sales_last_year, sales_previous_year)
    
    # Profit last week
    profit_last_week = orders_last_week * 0.15
    profit_previous_week = orders_previous_week * 0.15
    profit_last_week_change_pct = calculate_percentage_change(profit_last_week, profit_previous_week)
    
    # Sales last week
    sales_last_week = orders_last_week
    sales_last_week_change_pct = orders_last_week_change_pct
    
    overview = DashboardOverviewResponse(
        categories=total_categories,
        brands=total_brands,
        products=total_products,
        revenue=total_revenue,
        orders_last_week=orders_last_week,
        orders_last_week_change_pct=orders_last_week_change_pct,
        sales_last_year=sales_last_year,
        sales_last_year_change_pct=sales_last_year_change_pct,
        profit_last_week=profit_last_week,
        profit_last_week_change_pct=profit_last_week_change_pct,
        sales_last_week=sales_last_week,
        sales_last_week_change_pct=sales_last_week_change_pct
    )
    
    # Get latest products
    products = db.query(Product).filter(Product.is_active == True).order_by(desc(Product.created_at)).limit(limit_products).all()
    product_items = []
    for product in products:
        title = None
        translation = next((t for t in product.translations if t.lang == lang), None) if product.translations else None
        if not translation and product.translations:
            translation = next((t for t in product.translations if t.lang == "it"), None)
        if not translation and product.translations:
            translation = product.translations[0]
        title = translation.name if translation else f"Product {product.id}"
        
        image_url = None
        if product.images:
            sorted_images = sorted(product.images, key=lambda x: x.position or 999)
            image_url = sorted_images[0].url if sorted_images else None
        
        price = product.price_final if product.price_final else (product.price_list if product.price_list else 0.0)
        
        product_items.append(DashboardProductItem(
            id=product.id,
            title=title,
            sku=product.reference,
            price=float(price),
            currency="EUR",
            image=image_url,
            created_at=product.created_at
        ))
    
    # Get latest payments
    payments = db.query(Payment).order_by(desc(Payment.created_at)).limit(limit_payments).all()
    payment_items = []
    for payment in payments:
        payment_items.append(DashboardPaymentItem(
            id=payment.id,
            amount=float(payment.amount),
            currency=payment.currency,
            status=payment.status,
            provider=payment.provider,
            payment_method=payment.payment_method,
            order_id=payment.order_id,
            created_at=payment.created_at
        ))
    
    return DashboardCRMLiveResponse(
        overview=overview,
        latest_products=product_items,
        latest_payments=payment_items
    )
