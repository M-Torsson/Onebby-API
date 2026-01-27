# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from typing import Optional, List
from sqlalchemy.orm import Session
from slugify import slugify
from app.models.brand import Brand
from app.models.tax_class import TaxClass
from app.schemas.brand_tax import BrandCreate, BrandUpdate, TaxClassCreate, TaxClassUpdate


# ============= Brand CRUD =============

def get_brand(db: Session, brand_id: int) -> Optional[Brand]:
    """Get brand by ID"""
    return db.query(Brand).filter(Brand.id == brand_id).first()


def get_brand_by_slug(db: Session, slug: str) -> Optional[Brand]:
    """Get brand by slug"""
    return db.query(Brand).filter(Brand.slug == slug).first()


def count_brands(db: Session, active_only: bool = False) -> int:
    """Count total brands"""
    query = db.query(Brand)
    
    if active_only:
        query = query.filter(Brand.is_active == True)
    
    return query.count()


def get_brands(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Brand]:
    """Get all brands"""
    query = db.query(Brand)
    
    if active_only:
        query = query.filter(Brand.is_active == True)
    
    return query.order_by(Brand.sort_order).offset(skip).limit(limit).all()


def create_brand(db: Session, brand: BrandCreate) -> Brand:
    """Create a new brand"""
    # Generate slug if not provided
    if not brand.slug:
        brand.slug = slugify(brand.name)
    
    db_brand = Brand(
        name=brand.name,
        slug=brand.slug,
        image=brand.image,
        is_active=brand.is_active,
        sort_order=brand.sort_order
    )
    
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    
    return db_brand


def update_brand(db: Session, brand_id: int, brand: BrandUpdate) -> Optional[Brand]:
    """Update a brand"""
    db_brand = get_brand(db, brand_id)
    if not db_brand:
        return None
    
    update_data = brand.model_dump(exclude_unset=True)
    
    # If name is updated and no slug provided, regenerate slug
    if "name" in update_data and "slug" not in update_data:
        update_data["slug"] = slugify(update_data["name"])
    
    for field, value in update_data.items():
        setattr(db_brand, field, value)
    
    db.commit()
    db.refresh(db_brand)
    return db_brand


def delete_brand(db: Session, brand_id: int) -> bool:
    """Delete a brand"""
    db_brand = get_brand(db, brand_id)
    if not db_brand:
        return False
    
    db.delete(db_brand)
    db.commit()
    return True


# ============= Tax Class CRUD =============

def get_tax_class(db: Session, tax_class_id: int) -> Optional[TaxClass]:
    """Get tax class by ID"""
    return db.query(TaxClass).filter(TaxClass.id == tax_class_id).first()


def count_tax_classes(db: Session, active_only: bool = False) -> int:
    """Count total tax classes"""
    query = db.query(TaxClass)
    
    if active_only:
        query = query.filter(TaxClass.is_active == True)
    
    return query.count()


def get_tax_classes(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[TaxClass]:
    """Get all tax classes"""
    query = db.query(TaxClass)
    
    if active_only:
        query = query.filter(TaxClass.is_active == True)
    
    return query.offset(skip).limit(limit).all()


def create_tax_class(db: Session, tax_class: TaxClassCreate) -> TaxClass:
    """Create a new tax class"""
    db_tax_class = TaxClass(
        name=tax_class.name,
        rate=tax_class.rate,
        is_active=tax_class.is_active
    )
    
    db.add(db_tax_class)
    db.commit()
    db.refresh(db_tax_class)
    
    return db_tax_class


def update_tax_class(db: Session, tax_class_id: int, tax_class: TaxClassUpdate) -> Optional[TaxClass]:
    """Update a tax class"""
    db_tax_class = get_tax_class(db, tax_class_id)
    if not db_tax_class:
        return None
    
    update_data = tax_class.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_tax_class, field, value)
    
    db.commit()
    db.refresh(db_tax_class)
    return db_tax_class


def delete_tax_class(db: Session, tax_class_id: int) -> bool:
    """Delete a tax class"""
    db_tax_class = get_tax_class(db, tax_class_id)
    if not db_tax_class:
        return False
    
    db.delete(db_tax_class)
    db.commit()
    return True
