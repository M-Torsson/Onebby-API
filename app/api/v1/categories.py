from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryCreateResponse,
    CategoryChildrenListResponse,
    CategoryChildResponse,
    CategoryTranslationUpdate,
    CategoryListResponse,
    CategoryMainResponse
)
from app.crud import category as crud_category
from app.core.security.api_key import verify_api_key

router = APIRouter()


@router.get(
    "/v1/categories",
    response_model=CategoryListResponse
)
async def get_all_categories(
    lang: Optional[str] = Query(
        default="it",
        description="Language code: it, en, fr, de, ar"
    ),
    active_only: bool = Query(
        default=True,
        description="Show only active categories"
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all categories (main and children)
    
    Requires X-API-Key in header
    
    - **lang**: Language code (default: it) - Supported: it, en, fr, de, ar
    - **active_only**: Filter active categories only (default: true)
    
    Returns:
    - List of all categories with localized names
    - Main categories first (parent_id = null), then children ordered by sort_order
    - Meta information about language
    """
    # Validate language
    supported_langs = ["it", "en", "fr", "de", "ar"]
    if lang not in supported_langs:
        lang = "it"  # Default to Italian
    
    # Get all categories
    categories = crud_category.get_all_categories(db, lang, active_only)
    
    # Format response
    categories_data = [
        CategoryMainResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            sort_order=cat.sort_order,
            is_active=cat.is_active,
            parent_id=cat.parent_id,
            has_children=cat.has_children
        )
        for cat in categories
    ]
    
    return {
        "data": categories_data,
        "meta": {
            "requested_lang": lang,
            "resolved_lang": lang,
            "total": len(categories_data)
        }
    }


@router.get(
    "/admin/categories",
    response_model=CategoryListResponse
)
async def get_main_categories(
    lang: Optional[str] = Query(
        default="it",
        description="Language code: it, en, fr, de, ar"
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all main categories (parent_id = null)
    
    Requires X-API-Key in header
    
    - **lang**: Language code (default: it) - Supported: it, en, fr, de, ar
    
    Returns:
    - List of main categories with localized names
    - Meta information about language
    """
    # Validate language
    supported_langs = ["it", "en", "fr", "de", "ar"]
    if lang not in supported_langs:
        lang = "it"  # Default to Italian
    
    # Get main categories
    categories = crud_category.get_main_categories(db, lang)
    
    # Format response
    categories_data = [
        CategoryMainResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            sort_order=cat.sort_order,
            is_active=cat.is_active,
            parent_id=cat.parent_id,
            has_children=cat.has_children
        )
        for cat in categories
    ]
    
    return {
        "data": categories_data,
        "meta": {
            "requested_lang": lang,
            "resolved_lang": lang
        }
    }


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
    "/categories/{category_id}/children",
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


@router.put(
    "/admin/categories/{category_id}",
    response_model=CategoryCreateResponse
)
async def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update a category
    
    Requires X-API-Key in header
    
    - **category_id**: ID of the category to update
    - **name**: Category name (optional)
    - **slug**: URL-friendly name (optional, auto-generated if name provided)
    - **image**: Category image URL (optional)
    - **icon**: Category icon URL (optional)
    - **sort_order**: Display order (optional)
    - **is_active**: Active status (optional)
    - **parent_id**: Parent category ID (optional)
    
    Example request body:
    ```json
    {
      "image": "https://example.com/image.jpg",
      "icon": "https://example.com/icon.svg",
      "sort_order": 5,
      "is_active": true
    }
    ```
    """
    try:
        updated_category = crud_category.update_category(
            db=db,
            category_id=category_id,
            category=category
        )
        
        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return {"data": updated_category}
    
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


@router.delete(
    "/admin/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category(
    category_id: int,
    delete_children: bool = Query(
        default=False,
        description="Delete children (subcategories) too"
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete a category and optionally its children
    
    Requires X-API-Key in header
    
    - **category_id**: ID of the category to delete
    - **delete_children**: If true, deletes all children (subcategories) recursively (default: false)
    
    Examples:
    - DELETE /api/admin/categories/4 - Fails if has children
    - DELETE /api/admin/categories/4?delete_children=true - Deletes category and all its children
    """
    try:
        success = crud_category.delete_category(db, category_id, delete_children)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return None  # 204 No Content
    
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


@router.put(
    "/admin/categories/{category_id}/translations",
    response_model=CategoryCreateResponse
)
async def update_category_translations(
    category_id: int,
    translations: CategoryTranslationUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update translations for a category
    
    Requires X-API-Key in header
    
    - **category_id**: ID of the category to update
    - **translations**: Array of translations for all languages
    
    Example request body:
    ```json
    {
      "translations": [
        { "lang": "it", "name": "Da incasso", "slug": "da-incasso" },
        { "lang": "en", "name": "Built-in", "slug": "built-in" },
        { "lang": "fr", "name": "Intégré", "slug": "integre" },
        { "lang": "de", "name": "Eingebaut", "slug": "eingebaut" },
        { "lang": "ar", "name": "مدمج", "slug": "mdmj" }
      ]
    }
    ```
    """
    try:
        # Validate languages
        supported_langs = ["it", "en", "fr", "de", "ar"]
        provided_langs = [t.lang for t in translations.translations]
        
        for lang in provided_langs:
            if lang not in supported_langs:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported language: {lang}. Supported: {', '.join(supported_langs)}"
                )
        
        # Update translations
        translations_list = [
            {"lang": t.lang, "name": t.name, "slug": t.slug}
            for t in translations.translations
        ]
        
        updated_category = crud_category.update_category_translations(
            db=db,
            category_id=category_id,
            translations_data=translations_list
        )
        
        return {"data": updated_category}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
