# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.session import get_db
from app.core.config import settings
from app.schemas.warranty import WarrantyCreate, WarrantyUpdate, WarrantyResponse
from app.crud import warranty as crud_warranty


router = APIRouter()


# ============= Helper Functions =============

def verify_api_key(x_api_key: str = Header(...)):
    """Verify API Key from header"""
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


# ============= Endpoints =============

@router.post("/admin/warranties", response_model=dict, status_code=201)
def create_warranty(
    warranty: WarrantyCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new warranty option
    
    Requires X-API-Key header for authentication
    """
    try:
        db_warranty = crud_warranty.create_warranty(db, warranty)
        
        return {
            "message": "Warranty created successfully",
            "data": {
                "id": db_warranty.id,
                "title": db_warranty.title,
                "subtitle": db_warranty.subtitle,
                "meta_description": db_warranty.meta_description,
                "price": db_warranty.price,
                "image": db_warranty.image,
                "is_active": db_warranty.is_active,
                "categories": [cat.id for cat in db_warranty.categories],
                "translations": [
                    {
                        "id": t.id,
                        "lang": t.lang,
                        "title": t.title,
                        "subtitle": t.subtitle,
                        "meta_description": t.meta_description
                    } for t in db_warranty.translations
                ],
                "features": [
                    {
                        "id": f.id,
                        "key": f.key,
                        "value": f.value,
                        "position": f.position
                    } for f in db_warranty.features
                ],
                "created_at": db_warranty.created_at,
                "updated_at": db_warranty.updated_at
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating warranty: {str(e)}")


@router.get("/admin/warranties", response_model=dict)
def get_warranties(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all warranty options with pagination
    
    Requires X-API-Key header for authentication
    """
    try:
        warranties = crud_warranty.get_warranties(db, skip=skip, limit=limit, active_only=active_only)
        total = crud_warranty.count_warranties(db, active_only=active_only)
        
        return {
            "data": [
                {
                    "id": w.id,
                    "title": w.title,
                    "subtitle": w.subtitle,
                    "meta_description": w.meta_description,
                    "price": w.price,
                    "image": w.image,
                    "is_active": w.is_active,
                    "categories": [cat.id for cat in w.categories],
                    "translations": [
                        {
                            "id": t.id,
                            "lang": t.lang,
                            "title": t.title,
                            "subtitle": t.subtitle,
                            "meta_description": t.meta_description
                        } for t in w.translations
                    ],
                    "features": [
                        {
                            "id": f.id,
                            "key": f.key,
                            "value": f.value,
                            "position": f.position
                        } for f in w.features
                    ],
                    "created_at": w.created_at,
                    "updated_at": w.updated_at
                } for w in warranties
            ],
            "meta": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "count": len(warranties)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching warranties: {str(e)}")


@router.get("/admin/warranties/{warranty_id}", response_model=dict)
def get_warranty(
    warranty_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get a specific warranty option by ID
    
    Requires X-API-Key header for authentication
    """
    warranty = crud_warranty.get_warranty(db, warranty_id)
    if not warranty:
        raise HTTPException(status_code=404, detail="Warranty not found")
    
    return {
        "data": {
            "id": warranty.id,
            "title": warranty.title,
            "subtitle": warranty.subtitle,
            "meta_description": warranty.meta_description,
            "price": warranty.price,
            "image": warranty.image,
            "is_active": warranty.is_active,
            "categories": [cat.id for cat in warranty.categories],
            "translations": [
                {
                    "id": t.id,
                    "lang": t.lang,
                    "title": t.title,
                    "subtitle": t.subtitle,
                    "meta_description": t.meta_description
                } for t in warranty.translations
            ],
            "features": [
                {
                    "id": f.id,
                    "key": f.key,
                    "value": f.value,
                    "position": f.position
                } for f in warranty.features
            ],
            "created_at": warranty.created_at,
            "updated_at": warranty.updated_at
        }
    }


@router.put("/admin/warranties/{warranty_id}", response_model=dict)
def update_warranty(
    warranty_id: int,
    warranty: WarrantyUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update a warranty option
    
    Requires X-API-Key header for authentication
    """
    try:
        db_warranty = crud_warranty.update_warranty(db, warranty_id, warranty)
        if not db_warranty:
            raise HTTPException(status_code=404, detail="Warranty not found")
        
        return {
            "message": "Warranty updated successfully",
            "data": {
                "id": db_warranty.id,
                "title": db_warranty.title,
                "subtitle": db_warranty.subtitle,
                "meta_description": db_warranty.meta_description,
                "price": db_warranty.price,
                "image": db_warranty.image,
                "is_active": db_warranty.is_active,
                "categories": [cat.id for cat in db_warranty.categories],
                "translations": [
                    {
                        "id": t.id,
                        "lang": t.lang,
                        "title": t.title,
                        "subtitle": t.subtitle,
                        "meta_description": t.meta_description
                    } for t in db_warranty.translations
                ],
                "features": [
                    {
                        "id": f.id,
                        "key": f.key,
                        "value": f.value,
                        "position": f.position
                    } for f in db_warranty.features
                ],
                "created_at": db_warranty.created_at,
                "updated_at": db_warranty.updated_at
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating warranty: {str(e)}")


@router.delete("/admin/warranties/{warranty_id}", response_model=dict)
def delete_warranty(
    warranty_id: int,
    soft_delete: bool = Query(False, description="Soft delete (deactivate) instead of permanent deletion"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete a warranty option (permanent deletion by default, set soft_delete=true to only deactivate)
    
    Requires X-API-Key header for authentication
    """
    try:
        if soft_delete:
            success = crud_warranty.soft_delete_warranty(db, warranty_id)
        else:
            success = crud_warranty.delete_warranty(db, warranty_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Warranty not found")
        
        return {
            "message": "Warranty deactivated successfully" if soft_delete else "Warranty deleted successfully",
            "deleted": not soft_delete
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting warranty: {str(e)}")
