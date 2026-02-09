# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.models.warranty import Warranty, WarrantyTranslation, WarrantyFeature, warranty_categories
from app.models.category import Category
from app.schemas.warranty import WarrantyCreate, WarrantyUpdate


# ============= Helper Functions =============

def check_categories_in_use(db: Session, category_ids: List[int], exclude_warranty_id: Optional[int] = None) -> Optional[str]:
    """
    Check if any of the given categories are already assigned to another warranty.
    Returns error message in English if categories are in use, None otherwise.
    """
    if not category_ids:
        return None
    
    # Query for categories that are already in use
    query = db.query(warranty_categories.c.category_id, Warranty.id).join(
        Warranty, warranty_categories.c.warranty_id == Warranty.id
    ).filter(warranty_categories.c.category_id.in_(category_ids))
    
    # Exclude current warranty if updating
    if exclude_warranty_id:
        query = query.filter(Warranty.id != exclude_warranty_id)
    
    used_categories = query.all()
    
    if used_categories:
        # Get category names for error message
        used_cat_ids = [cat_id for cat_id, _ in used_categories]
        categories = db.query(Category).filter(Category.id.in_(used_cat_ids)).all()
        cat_names = [cat.name for cat in categories]
        
        return f"The following categories are already assigned to another warranty: {', '.join(cat_names)}"
    
    return None


def create_warranty_translations(db: Session, warranty: Warranty, translations_data: List[dict]):
    """Create warranty translations"""
    for trans_data in translations_data:
        translation = WarrantyTranslation(
            warranty_id=warranty.id,
            lang=trans_data["lang"],
            title=trans_data.get("title"),
            subtitle=trans_data.get("subtitle"),
            meta_description=trans_data.get("meta_description")
        )
        db.add(translation)
    db.commit()


def create_warranty_features(db: Session, warranty: Warranty, features_data: List[dict]):
    """Create warranty features"""
    for idx, feature_data in enumerate(features_data):
        feature = WarrantyFeature(
            warranty_id=warranty.id,
            key=feature_data.get("key"),
            value=feature_data.get("value"),
            position=idx + 1
        )
        db.add(feature)
    db.commit()


# ============= Main CRUD Functions =============

def get_warranty(db: Session, warranty_id: int) -> Optional[Warranty]:
    """Get warranty by ID with all relationships"""
    return db.query(Warranty).options(
        joinedload(Warranty.categories),
        joinedload(Warranty.translations),
        joinedload(Warranty.features)
    ).filter(Warranty.id == warranty_id).first()


def get_warranties(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
) -> List[Warranty]:
    """Get all warranties with filters"""
    query = db.query(Warranty).options(
        joinedload(Warranty.categories),
        joinedload(Warranty.translations),
        joinedload(Warranty.features)
    )
    
    if active_only:
        query = query.filter(Warranty.is_active == True)
    
    return query.offset(skip).limit(limit).all()


def count_warranties(db: Session, active_only: bool = False) -> int:
    """Count total warranties"""
    query = db.query(Warranty)
    
    if active_only:
        query = query.filter(Warranty.is_active == True)
    
    return query.count()


def create_warranty(db: Session, warranty_data: WarrantyCreate) -> Warranty:
    """Create a new warranty option"""
    
    # Validate categories if provided
    if warranty_data.categories:
        # Check if categories exist
        categories = db.query(Category).filter(Category.id.in_(warranty_data.categories)).all()
        if len(categories) != len(warranty_data.categories):
            raise ValueError("One or more categories not found")
        
        # Check if categories are already in use by another warranty
        error_msg = check_categories_in_use(db, warranty_data.categories)
        if error_msg:
            raise ValueError(error_msg)
    
    # Create warranty
    warranty = Warranty(
        title=warranty_data.title,
        subtitle=warranty_data.subtitle,
        meta_description=warranty_data.meta_description,
        price=warranty_data.price,
        image=warranty_data.image,
        is_active=warranty_data.is_active
    )
    
    db.add(warranty)
    db.flush()
    
    # Add categories
    if warranty_data.categories:
        warranty.categories.extend(categories)
    
    # Create translations
    if warranty_data.translations:
        create_warranty_translations(db, warranty, [t.dict() for t in warranty_data.translations])
    
    # Create features
    if warranty_data.features:
        create_warranty_features(db, warranty, [f.dict() for f in warranty_data.features])
    
    db.commit()
    db.refresh(warranty)
    
    return warranty


def update_warranty(db: Session, warranty_id: int, warranty_data: WarrantyUpdate) -> Optional[Warranty]:
    """Update a warranty option"""
    warranty = get_warranty(db, warranty_id)
    if not warranty:
        return None
    
    update_data = warranty_data.model_dump(exclude_unset=True)
    
    # Handle categories update - MUST CLEAR FIRST
    if "categories" in update_data:
        category_ids = update_data.pop("categories")
        
        # Validate and check if categories are in use by another warranty
        if category_ids:
            # Check if categories exist
            categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
            if len(categories) != len(category_ids):
                raise ValueError("One or more categories not found")
            
            # Check if categories are already in use by another warranty (exclude current warranty)
            error_msg = check_categories_in_use(db, category_ids, exclude_warranty_id=warranty_id)
            if error_msg:
                raise ValueError(error_msg)
        
        # Delete existing category associations directly from the association table
        db.execute(
            warranty_categories.delete().where(
                warranty_categories.c.warranty_id == warranty_id
            )
        )
        db.flush()
        
        # Insert new associations directly
        if category_ids:
            for cat_id in category_ids:
                db.execute(
                    warranty_categories.insert().values(
                        warranty_id=warranty_id,
                        category_id=cat_id
                    )
                )
    
    # Handle translations update (replace all)
    if "translations" in update_data:
        translations_data = update_data.pop("translations")
        # Delete existing translations
        db.query(WarrantyTranslation).filter(WarrantyTranslation.warranty_id == warranty_id).delete()
        # Create new translations
        create_warranty_translations(db, warranty, [t.dict() if hasattr(t, 'dict') else t for t in translations_data])
    
    # Handle features update (replace all)
    if "features" in update_data:
        features_data = update_data.pop("features")
        # Delete existing features
        db.query(WarrantyFeature).filter(WarrantyFeature.warranty_id == warranty_id).delete()
        # Create new features
        create_warranty_features(db, warranty, [f.dict() if hasattr(f, 'dict') else f for f in features_data])
    
    # Update simple fields
    for field, value in update_data.items():
        setattr(warranty, field, value)
    
    warranty.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(warranty)
    return warranty


def delete_warranty(db: Session, warranty_id: int) -> bool:
    """Permanently delete a warranty option"""
    warranty = db.query(Warranty).filter(Warranty.id == warranty_id).first()
    if not warranty:
        return False
    
    # Hard delete - permanently remove from database
    db.delete(warranty)
    db.commit()
    return True


def soft_delete_warranty(db: Session, warranty_id: int) -> bool:
    """Soft delete a warranty option (set is_active to False)"""
    warranty = db.query(Warranty).filter(Warranty.id == warranty_id).first()
    if not warranty:
        return False
    
    # Soft delete - just mark as inactive
    warranty.is_active = False
    warranty.updated_at = datetime.utcnow()
    
    db.commit()
    return True
