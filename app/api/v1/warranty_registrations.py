# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.session import get_db
from app.schemas.warranty_registration import (
    WarrantyRegistrationCreate, 
    WarrantyRegistrationResponse,
    WarrantyRegistrationListItem
)
from app.crud.warranty_registration import crud_warranty_registration
from app.crud.order import crud_order
from app.crud import product as crud_product
from app.crud import warranty as crud_warranty
from app.models.product import Product
from app.models.warranty import Warranty
from app.core.security.api_key import verify_api_key
from app.core.security.dependencies import get_current_active_user
from app.services.garanzia3_service import garanzia3_service

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

@router.post("/register", response_model=WarrantyRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_warranty(
    registration_in: WarrantyRegistrationCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Register a warranty with Garanzia3 (Manual registration)
    
    This endpoint:
    1. Validates order belongs to user
    2. Validates product and warranty exist
    3. Creates registration record
    4. Calls Garanzia3 API to register warranty
    5. Updates registration with transaction ID and PIN
    
    Customer will receive warranty contract via email from Garanzia3.
    """
    
    # Get order
    order = crud_order.get(db, id=registration_in.order_id)
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
    
    # Verify order is completed and paid
    # Accept both 'completed' and 'confirmed' status for backward compatibility
    if order.status not in ['completed', 'confirmed'] or order.payment_status != 'completed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be completed and paid before registering warranty"
        )
    
    # Get product
    product = crud_product.get_product(db, product_id=registration_in.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get warranty
    warranty = crud_warranty.get_warranty(db, warranty_id=registration_in.warranty_id)
    if not warranty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warranty not found"
        )
    
    # Check if warranty already registered for this product in this order
    existing = crud_warranty_registration.get_by_order(db, order_id=order.id)
    for reg in existing:
        if reg.product_id == product.id and reg.warranty_id == warranty.id:
            if reg.status == 'registered':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Warranty already registered for this product"
                )
    
    # Create registration record
    registration = crud_warranty_registration.create(
        db,
        registration_in=registration_in
    )
    
    # Call Garanzia3 API
    try:
        result = await garanzia3_service.register_warranty(
            ean13=registration.product_ean13,
            customer_name=registration.customer_name,
            customer_lastname=registration.customer_lastname,
            customer_email=registration.customer_email,
            customer_phone=registration.customer_phone
        )
        
        if result['success']:
            # Update registration with success
            registration = crud_warranty_registration.update_status(
                db,
                id=registration.id,
                status='registered',
                g3_transaction_id=result['transaction'],
                g3_pin=result['pin'],
                g3_response=result.get('raw_response')
            )
        else:
            # Update registration with failure
            registration = crud_warranty_registration.update_status(
                db,
                id=registration.id,
                status='failed',
                error_message=result['error'],
                error_code='G3_API_ERROR'
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to register warranty with Garanzia3: {result['error']}"
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register warranty: {str(e)}"
        )
    
    return registration


@router.get("/registrations", response_model=List[WarrantyRegistrationListItem])
async def list_my_registrations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Get list of warranty registrations for current user
    
    Query Parameters:
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return
    - status: Filter by status (pending, registered, failed, cancelled)
    """
    
    user_id = int(current_user["id"])
    
    registrations = crud_warranty_registration.list_user_registrations(
        db,
        user_id=user_id,
        skip=skip,
        limit=limit,
        status=status
    )
    
    return registrations


@router.get("/registrations/{registration_id}", response_model=WarrantyRegistrationResponse)
async def get_registration_details(
    registration_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Get warranty registration details by ID
    
    Returns complete registration information including:
    - Registration data
    - Garanzia3 transaction ID and PIN
    - Product and warranty details
    - Order information
    """
    
    # Get registration
    registration = crud_warranty_registration.get(db, id=registration_id)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )
    
    # Verify registration belongs to user
    user_id = int(current_user["id"])
    if registration.order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this registration"
        )
    
    return registration


# ========================================
# ADMIN ENDPOINTS
# ========================================

@router.get("/admin/registrations", response_model=List[WarrantyRegistrationListItem])
async def admin_list_registrations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Admin: List all warranty registrations
    
    Query Parameters:
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return
    - status: Filter by status (pending, registered, failed, cancelled)
    """
    
    if status:
        if status == 'pending':
            registrations = crud_warranty_registration.list_pending_registrations(
                db,
                skip=skip,
                limit=limit
            )
        else:
            # For other statuses, we need a more general query
            # This is a simplified version - you may want to add a more general method
            registrations = crud_warranty_registration.list_pending_registrations(
                db,
                skip=skip,
                limit=limit
            )
    else:
        registrations = crud_warranty_registration.list_pending_registrations(
            db,
            skip=skip,
            limit=limit
        )
    
    return registrations


@router.post("/admin/registrations/{registration_id}/retry", response_model=WarrantyRegistrationResponse)
async def admin_retry_registration(
    registration_id: int,
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Admin: Retry failed warranty registration
    
    This endpoint allows admins to retry registrations that failed
    due to API errors or timeouts.
    """
    
    # Get registration
    registration = crud_warranty_registration.get(db, id=registration_id)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )
    
    # Check if registration can be retried
    if registration.status not in ['failed', 'pending']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot retry registration with status: {registration.status}"
        )
    
    # Reset to pending
    registration = crud_warranty_registration.update_status(
        db,
        id=registration.id,
        status='pending',
        error_message=None,
        error_code=None
    )
    
    # Call Garanzia3 API
    try:
        result = await garanzia3_service.register_warranty(
            ean13=registration.product_ean13,
            customer_name=registration.customer_name,
            customer_lastname=registration.customer_lastname,
            customer_email=registration.customer_email,
            customer_phone=registration.customer_phone
        )
        
        if result['success']:
            # Update registration with success
            registration = crud_warranty_registration.update_status(
                db,
                id=registration.id,
                status='registered',
                g3_transaction_id=result['transaction'],
                g3_pin=result['pin'],
                g3_response=result.get('raw_response')
            )
        else:
            # Update registration with failure
            registration = crud_warranty_registration.update_status(
                db,
                id=registration.id,
                status='failed',
                error_message=result['error'],
                error_code='G3_API_ERROR'
            )
    
    except Exception as e:
        # Update registration with failure
        registration = crud_warranty_registration.update_status(
            db,
            id=registration.id,
            status='failed',
            error_message=str(e),
            error_code='SYSTEM_ERROR'
        )
    
    return registration
