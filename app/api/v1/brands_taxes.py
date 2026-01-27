# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.config import settings
from app.schemas.brand_tax import (
    BrandCreate, BrandUpdate, BrandResponse,
    TaxClassCreate, TaxClassUpdate, TaxClassResponse
)
from app.crud import brand_tax as crud


router = APIRouter()


def verify_api_key(x_api_key: str = Header(...)):
    """Verify API Key from header"""
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


# ============= Public Endpoints (No API Key) =============

@router.get("/v1/brands")
def get_brands_public(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all brands with pagination - Public endpoint"""
    # Get total count
    total = crud.count_brands(db, active_only=active_only)
    
    # Get brands for current page
    brands = crud.get_brands(db, skip=skip, limit=limit, active_only=active_only)
    
    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return {
        "data": brands,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "page": current_page,
            "total_pages": total_pages,
            "has_next": skip + limit < total,
            "has_prev": skip > 0
        }
    }


@router.get("/v1/brands/{brand_id}", response_model=BrandResponse)
def get_brand_public(
    brand_id: int,
    db: Session = Depends(get_db)
):
    """Get brand by ID - Public endpoint"""
    brand = crud.get_brand(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.get("/v1/tax-classes")
def get_tax_classes_public(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all tax classes with pagination - Public endpoint"""
    # Get total count
    total = crud.count_tax_classes(db, active_only=active_only)
    
    # Get tax classes for current page
    tax_classes = crud.get_tax_classes(db, skip=skip, limit=limit, active_only=active_only)
    
    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return {
        "data": tax_classes,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "page": current_page,
            "total_pages": total_pages,
            "has_next": skip + limit < total,
            "has_prev": skip > 0
        }
    }


@router.get("/v1/tax-classes/{tax_class_id}", response_model=TaxClassResponse)
def get_tax_class_public(
    tax_class_id: int,
    db: Session = Depends(get_db)
):
    """Get tax class by ID - Public endpoint"""
    tax_class = crud.get_tax_class(db, tax_class_id)
    if not tax_class:
        raise HTTPException(status_code=404, detail="Tax class not found")
    return tax_class


# ============= Admin Endpoints (Require API Key) =============

@router.post("/admin/brands", response_model=BrandResponse, status_code=201)
def create_brand(
    brand: BrandCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new brand"""
    existing = crud.get_brand_by_slug(db, brand.slug or brand.name.lower().replace(" ", "-"))
    if existing:
        raise HTTPException(status_code=400, detail="Brand with this slug already exists")
    
    return crud.create_brand(db, brand)


@router.get("/admin/brands")
def get_brands(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all brands with pagination - Public access allowed"""
    # Get total count
    total = crud.count_brands(db, active_only=active_only)
    
    # Get brands for current page
    brands = crud.get_brands(db, skip=skip, limit=limit, active_only=active_only)
    
    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return {
        "data": brands,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "page": current_page,
            "total_pages": total_pages,
            "has_next": skip + limit < total,
            "has_prev": skip > 0
        }
    }


@router.get("/admin/brands/{brand_id}", response_model=BrandResponse)
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db)
):
    """Get brand by ID - Public access allowed"""
    brand = crud.get_brand(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.put("/admin/brands/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: int,
    brand: BrandUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update a brand"""
    updated_brand = crud.update_brand(db, brand_id, brand)
    if not updated_brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return updated_brand


@router.delete("/admin/brands/{brand_id}", status_code=204)
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete a brand"""
    success = crud.delete_brand(db, brand_id)
    if not success:
        raise HTTPException(status_code=404, detail="Brand not found")
    return None


@router.post("/admin/tax-classes", response_model=TaxClassResponse, status_code=201)
def create_tax_class(
    tax_class: TaxClassCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new tax class"""
    return crud.create_tax_class(db, tax_class)


@router.get("/admin/tax-classes")
def get_tax_classes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all tax classes with pagination - Public access allowed"""
    # Get total count
    total = crud.count_tax_classes(db, active_only=active_only)
    
    # Get tax classes for current page
    tax_classes = crud.get_tax_classes(db, skip=skip, limit=limit, active_only=active_only)
    
    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return {
        "data": tax_classes,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "page": current_page,
            "total_pages": total_pages,
            "has_next": skip + limit < total,
            "has_prev": skip > 0
        }
    }


@router.get("/admin/tax-classes/{tax_class_id}", response_model=TaxClassResponse)
def get_tax_class(
    tax_class_id: int,
    db: Session = Depends(get_db)
):
    """Get tax class by ID - Public access allowed"""
    tax_class = crud.get_tax_class(db, tax_class_id)
    if not tax_class:
        raise HTTPException(status_code=404, detail="Tax class not found")
    return tax_class


@router.put("/admin/tax-classes/{tax_class_id}", response_model=TaxClassResponse)
def update_tax_class(
    tax_class_id: int,
    tax_class: TaxClassUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update a tax class"""
    updated_tax_class = crud.update_tax_class(db, tax_class_id, tax_class)
    if not updated_tax_class:
        raise HTTPException(status_code=404, detail="Tax class not found")
    return updated_tax_class


@router.delete("/admin/tax-classes/{tax_class_id}", status_code=204)
def delete_tax_class(
    tax_class_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete a tax class"""
    success = crud.delete_tax_class(db, tax_class_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tax class not found")
    return None
