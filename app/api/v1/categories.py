from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.schemas.category import (
    CategoryCreate,
    CategoryCreateResponse,
    CategoryChildrenListResponse,
    CategoryChildResponse
)
from app.crud import category as crud_category
from app.core.security.api_key import verify_api_key

router = APIRouter()


@router.post(
    "/admin/categories",
    response_model=CategoryCreateResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new category (main or child)
    
    Requires X-API-Key in header
    
    - **name**: Required - Category name
    - **slug**: Optional - URL-friendly name (auto-generated from name if not provided)
    - **image**: Optional - Category image URL
    - **icon**: Optional - Category icon URL
    - **sort_order**: For ordering in menus (1, 2, 3...)
    - **is_active**: Prepare categories before showing them
    - **parent_id**: ID of parent category (null for main categories)
    """
    try:
        # Check if slug already exists
        if category.slug:
            existing = crud_category.get_category_by_slug(db, category.slug)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this slug already exists"
                )
        
        db_category = crud_category.create_category(db=db, category=category)
        return {"data": db_category}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/api/v1/categories/{category_id}/children",
    response_model=CategoryChildrenListResponse
)
async def get_category_children(
    category_id: int,
    lang: Optional[str] = Query(
        default="it",
        description="Language code: it, en, fr, de, ar"
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all children (subcategories) of a parent category
    
    Requires X-API-Key in header
    
    - **category_id**: ID of the parent category
    - **lang**: Language code (default: it) - Supported: it, en, fr, de, ar
    
    Returns:
    - List of child categories with localized names
    - Meta information about parent and language
    """
    # Check if parent category exists
    parent = crud_category.get_category(db, category_id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent category not found"
        )
    
    if not parent.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent category is not active"
        )
    
    # Validate language
    supported_langs = ["it", "en", "fr", "de", "ar"]
    if lang not in supported_langs:
        lang = "it"  # Default to Italian
    
    # Get children
    children = crud_category.get_category_children(db, category_id, lang)
    
    # Format response
    children_data = [
        CategoryChildResponse(
            id=child.id,
            name=child.name,
            slug=child.slug,
            image=child.image,
            icon=child.icon,
            sort_order=child.sort_order,
            is_active=child.is_active,
            parent_id=child.parent_id,
            has_children=child.has_children
        )
        for child in children
    ]
    
    return {
        "data": children_data,
        "meta": {
            "parent_id": category_id,
            "requested_lang": lang,
            "resolved_lang": lang
        }
    }
