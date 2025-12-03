from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from typing import List, Optional
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


# ============= Brand Endpoints =============

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


@router.get("/admin/brands", response_model=List[BrandResponse])
def get_brands(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get all brands"""
    return crud.get_brands(db, skip=skip, limit=limit, active_only=active_only)


@router.get("/admin/brands/{brand_id}", response_model=BrandResponse)
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get brand by ID"""
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


# ============= Tax Class Endpoints =============

@router.post("/admin/tax-classes", response_model=TaxClassResponse, status_code=201)
def create_tax_class(
    tax_class: TaxClassCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new tax class"""
    return crud.create_tax_class(db, tax_class)


@router.get("/admin/tax-classes", response_model=List[TaxClassResponse])
def get_tax_classes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get all tax classes"""
    return crud.get_tax_classes(db, skip=skip, limit=limit, active_only=active_only)


@router.get("/admin/tax-classes/{tax_class_id}", response_model=TaxClassResponse)
def get_tax_class(
    tax_class_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get tax class by ID"""
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
