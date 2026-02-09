# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.models.delivery import Delivery, DeliveryTranslation
from app.models.category import Category
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate


# ============= Helper Functions =============

def create_delivery_translations(db: Session, delivery: Delivery, translations_data: List[dict]):
    """Create delivery translations"""
    for trans_data in translations_data:
        translation = DeliveryTranslation(
            delivery_id=delivery.id,
            lang=trans_data["lang"],
            note=trans_data.get("note"),
            option_note=trans_data.get("option_note")
        )
        db.add(translation)
    db.commit()


# ============= Main CRUD Functions =============

def get_delivery(db: Session, delivery_id: int) -> Optional[Delivery]:
    """Get delivery by ID with all relationships"""
    return db.query(Delivery).options(
        joinedload(Delivery.categories),
        joinedload(Delivery.translations)
    ).filter(Delivery.id == delivery_id).first()


def get_deliveries(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
) -> List[Delivery]:
    """Get all deliveries with filters"""
    query = db.query(Delivery).options(
        joinedload(Delivery.categories),
        joinedload(Delivery.translations)
    )
    
    if active_only:
        query = query.filter(Delivery.is_active == True)
    
    return query.offset(skip).limit(limit).all()


def count_deliveries(db: Session, active_only: bool = False) -> int:
    """Count total deliveries"""
    query = db.query(Delivery)
    
    if active_only:
        query = query.filter(Delivery.is_active == True)
    
    return query.count()


def create_delivery(db: Session, delivery_data: DeliveryCreate) -> Delivery:
    """Create a new delivery option"""
    
    # Validate categories if provided
    if delivery_data.categories:
        categories = db.query(Category).filter(Category.id.in_(delivery_data.categories)).all()
        if len(categories) != len(delivery_data.categories):
            raise ValueError("One or more categories not found")
    
    # Create delivery
    delivery = Delivery(
        days_from=delivery_data.days_from,
        days_to=delivery_data.days_to,
        note=delivery_data.note,
        option_note=delivery_data.option_note,
        is_free_delivery=delivery_data.is_free_delivery,
        is_active=delivery_data.is_active
    )
    
    db.add(delivery)
    db.flush()
    
    # Add categories
    if delivery_data.categories:
        delivery.categories.extend(categories)
    
    # Create translations
    if delivery_data.translations:
        create_delivery_translations(db, delivery, [t.dict() for t in delivery_data.translations])
    
    db.commit()
    db.refresh(delivery)
    
    return delivery


def update_delivery(db: Session, delivery_id: int, delivery_data: DeliveryUpdate) -> Optional[Delivery]:
    """Update a delivery option"""
    delivery = get_delivery(db, delivery_id)
    if not delivery:
        return None
    
    update_data = delivery_data.model_dump(exclude_unset=True)
    
    # Handle categories update
    if "categories" in update_data:
        category_ids = update_data.pop("categories")
        # Validate all categories exist
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        if len(categories) != len(category_ids):
            raise ValueError("One or more categories not found")
        # Clear existing categories and add new ones
        delivery.categories.clear()
        db.flush()  # Ensure the clear is committed
        delivery.categories.extend(categories)
    
    # Handle translations update (replace all)
    if "translations" in update_data:
        translations_data = update_data.pop("translations")
        # Delete existing translations
        db.query(DeliveryTranslation).filter(DeliveryTranslation.delivery_id == delivery_id).delete()
        # Create new translations
        create_delivery_translations(db, delivery, [t.dict() if hasattr(t, 'dict') else t for t in translations_data])
    
    # Update simple fields
    for field, value in update_data.items():
        setattr(delivery, field, value)
    
    delivery.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(delivery)
    return delivery


def delete_delivery(db: Session, delivery_id: int) -> bool:
    """Permanently delete a delivery option"""
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        return False
    
    # Hard delete - permanently remove from database
    db.delete(delivery)
    db.commit()
    return True


def soft_delete_delivery(db: Session, delivery_id: int) -> bool:
    """Soft delete a delivery option (set is_active to False)"""
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        return False
    
    # Soft delete - just mark as inactive
    delivery.is_active = False
    delivery.updated_at = datetime.utcnow()
    
    db.commit()
    return True
