# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.session import get_db
from app.core.config import settings
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate, DeliveryResponse
from app.crud import delivery as crud_delivery


router = APIRouter()


# ============= Helper Functions =============

def verify_api_key(x_api_key: str = Header(...)):
    """Verify API Key from header"""
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


# ============= Endpoints =============

@router.post("/admin/deliveries", response_model=dict, status_code=201)
def create_delivery(
    delivery: DeliveryCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new delivery option
    
    Requires X-API-Key header for authentication
    """
    try:
        db_delivery = crud_delivery.create_delivery(db, delivery)
        
        return {
            "message": "Delivery created successfully",
            "data": {
                "id": db_delivery.id,
                "days_from": db_delivery.days_from,
                "days_to": db_delivery.days_to,
                "note": db_delivery.note,
                "option_note": db_delivery.option_note,
                "is_free_delivery": db_delivery.is_free_delivery,
                "is_active": db_delivery.is_active,
                "categories": [cat.id for cat in db_delivery.categories],
                "translations": [
                    {
                        "id": t.id,
                        "lang": t.lang,
                        "note": t.note,
                        "option_note": t.option_note
                    } for t in db_delivery.translations
                ],
                "options": [
                    {
                        "id": o.id,
                        "icon": o.icon,
                        "details": o.details,
                        "price": o.price,
                        "position": o.position
                    } for o in db_delivery.options
                ],
                "created_at": db_delivery.created_at,
                "updated_at": db_delivery.updated_at
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating delivery: {str(e)}")


@router.get("/admin/deliveries", response_model=dict)
def get_deliveries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all delivery options with pagination
    
    Requires X-API-Key header for authentication
    """
    try:
        deliveries = crud_delivery.get_deliveries(db, skip=skip, limit=limit, active_only=active_only)
        total = crud_delivery.count_deliveries(db, active_only=active_only)
        
        return {
            "data": [
                {
                    "id": d.id,
                    "days_from": d.days_from,
                    "days_to": d.days_to,
                    "note": d.note,
                    "option_note": d.option_note,
                    "is_free_delivery": d.is_free_delivery,
                    "is_active": d.is_active,
                    "categories": [cat.id for cat in d.categories],
                    "translations": [
                        {
                            "id": t.id,
                            "lang": t.lang,
                            "note": t.note,
                            "option_note": t.option_note
                        } for t in d.translations
                    ],
                    "options": [
                        {
                            "id": o.id,
                            "icon": o.icon,
                            "details": o.details,
                            "price": o.price,
                            "position": o.position
                        } for o in d.options
                    ],
                    "created_at": d.created_at,
                    "updated_at": d.updated_at
                } for d in deliveries
            ],
            "meta": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "count": len(deliveries)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching deliveries: {str(e)}")


@router.get("/admin/deliveries/{delivery_id}", response_model=dict)
def get_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get a specific delivery option by ID
    
    Requires X-API-Key header for authentication
    """
    delivery = crud_delivery.get_delivery(db, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    return {
        "data": {
            "id": delivery.id,
            "days_from": delivery.days_from,
            "days_to": delivery.days_to,
            "note": delivery.note,
            "option_note": delivery.option_note,
            "is_free_delivery": delivery.is_free_delivery,
            "is_active": delivery.is_active,
            "categories": [cat.id for cat in delivery.categories],
            "translations": [
                {
                    "id": t.id,
                    "lang": t.lang,
                    "note": t.note,
                    "option_note": t.option_note
                } for t in delivery.translations
            ],
            "options": [
                {
                    "id": o.id,
                    "icon": o.icon,
                    "details": o.details,
                    "price": o.price,
                    "position": o.position
                } for o in delivery.options
            ],
            "created_at": delivery.created_at,
            "updated_at": delivery.updated_at
        }
    }


@router.put("/admin/deliveries/{delivery_id}", response_model=dict)
def update_delivery(
    delivery_id: int,
    delivery: DeliveryUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update a delivery option
    
    Requires X-API-Key header for authentication
    """
    try:
        db_delivery = crud_delivery.update_delivery(db, delivery_id, delivery)
        if not db_delivery:
            raise HTTPException(status_code=404, detail="Delivery not found")
        
        return {
            "message": "Delivery updated successfully",
            "data": {
                "id": db_delivery.id,
                "days_from": db_delivery.days_from,
                "days_to": db_delivery.days_to,
                "note": db_delivery.note,
                "option_note": db_delivery.option_note,
                "is_free_delivery": db_delivery.is_free_delivery,
                "is_active": db_delivery.is_active,
                "categories": [cat.id for cat in db_delivery.categories],
                "translations": [
                    {
                        "id": t.id,
                        "lang": t.lang,
                        "note": t.note,
                        "option_note": t.option_note
                    } for t in db_delivery.translations
                ],
                "options": [
                    {
                        "id": o.id,
                        "icon": o.icon,
                        "details": o.details,
                        "price": o.price,
                        "position": o.position
                    } for o in db_delivery.options
                ],
                "created_at": db_delivery.created_at,
                "updated_at": db_delivery.updated_at
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating delivery: {str(e)}")


@router.delete("/admin/deliveries/{delivery_id}", response_model=dict)
def delete_delivery(
    delivery_id: int,
    soft_delete: bool = Query(False, description="Soft delete (deactivate) instead of permanent deletion"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete a delivery option (permanent deletion by default, set soft_delete=true to only deactivate)
    
    Requires X-API-Key header for authentication
    """
    try:
        if soft_delete:
            success = crud_delivery.soft_delete_delivery(db, delivery_id)
        else:
            success = crud_delivery.delete_delivery(db, delivery_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Delivery not found")
        
        return {
            "message": "Delivery deactivated successfully" if soft_delete else "Delivery deleted successfully",
            "deleted": not soft_delete
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting delivery: {str(e)}")
