from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.models.category import Category
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
    skip: int = Query(0, ge=0, description="Number of categories to skip"),
    limit: int = Query(50, ge=1, le=500, description="Maximum categories to return"),
    q: Optional[str] = Query(
        default=None,
        description="Optional search text (name or slug). If provided, search runs across ALL categories (not just first page)."
    ),
    lang: Optional[str] = Query(
        default="it",
        description="Language code: it, en, fr, de, ar"
    ),
    active_only: bool = Query(
        default=True,
        description="Show only active categories"
    ),
    parent_only: bool = Query(
        default=False,
        description="Show only main categories (parent_id = null)"
    ),
    db: Session = Depends(get_db),
):
    """
    Get categories with pagination. If `q` is provided, performs a global search across all categories.
    
    - **skip**: Number of categories to skip (default: 0)
    - **limit**: Maximum categories per page (default: 50, max: 500)
    - **lang**: Language code (default: it) - Supported: it, en, fr, de, ar
    - **active_only**: Filter active categories only (default: true)
    - **parent_only**: Show only main categories without children (default: false)
    
    Returns:
    - List of categories with localized names
    - If parent_only=true: only main categories (parent_id = null)
    - If parent_only=false: all categories ordered by parent_id and sort_order
    - Pagination metadata (total, page, has_next, has_prev)
    """
    # Validate language
    supported_langs = ["it", "en", "fr", "de", "ar"]
    if lang not in supported_langs:
        lang = "it"  # Default to Italian

    # Global search mode (ignore pagination)
    if q and q.strip():
        categories, total = crud_category.search_categories(
            db=db,
            q=q,
            lang=lang,
            active_only=active_only,
            parent_only=parent_only,
            limit=5000,
        )

        categories_data = [
            CategoryMainResponse(
                id=cat.id,
                name=cat.name,
                slug=cat.slug,
                sort_order=cat.sort_order,
                is_active=cat.is_active,
                parent_id=cat.parent_id,
                has_children=cat.has_children,
            )
            for cat in categories
        ]

        return {
            "data": categories_data,
            "meta": {
                "total": total,
                "returned": len(categories_data),
                "skip": 0,
                "limit": len(categories_data),
                "page": 1,
                "total_pages": 1,
                "has_next": False,
                "has_prev": False,
                "requested_lang": lang,
                "resolved_lang": lang,
                "parent_only": parent_only,
                "q": q,
                "search_limit": 5000,
            },
        }
    
    # Get total count
    if parent_only:
        total = crud_category.count_main_categories(db)
        categories = crud_category.get_main_categories(db, lang, skip=skip, limit=limit)
    else:
        total = crud_category.count_all_categories(db, active_only=active_only)
        categories = crud_category.get_all_categories(db, lang, active_only=active_only, skip=skip, limit=limit)
    
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
    
    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return {
        "data": categories_data,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "page": current_page,
            "total_pages": total_pages,
            "has_next": skip + limit < total,
            "has_prev": skip > 0,
            "requested_lang": lang,
            "resolved_lang": lang,
            "parent_only": parent_only,
            "q": q
        }
    }


@router.get(
    "/v1/categories/main",
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


@router.get(
    "/v1/categories/{category_id}"
)
async def get_category_by_id(
    category_id: int,
    lang: Optional[str] = Query(
        default="it",
        description="Language code: it, en, fr, de, ar"
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get single category by ID (works for both parent and sub-categories)
    
    Requires X-API-Key in header
    
    - **category_id**: Category ID to retrieve
    - **lang**: Language code (default: it) - Supported: it, en, fr, de, ar
    
    Returns:
    - Single category details with localized name
    """
    # Validate language
    supported_langs = ["it", "en", "fr", "de", "ar"]
    if lang not in supported_langs:
        lang = "it"
    
    # Get category from database
    category = crud_category.get_category(db, category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
    
    # Get translated name if available
    category_name = category.name
    category_slug = category.slug
    
    if category.translations:
        translation = next((t for t in category.translations if t.lang == lang), None)
        if not translation and lang != "it":
            # Fallback to Italian
            translation = next((t for t in category.translations if t.lang == "it"), None)
        
        if translation:
            category_name = translation.name
            category_slug = translation.slug
    
    return {
        "data": {
            "id": category.id,
            "name": category_name,
            "slug": category_slug,
            "image": category.image,
            "icon": category.icon,
            "parent_id": category.parent_id,
            "is_active": category.is_active,
            "sort_order": category.sort_order
        }
    }


@router.post(
    "/v1/categories",
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
    "/v1/categories/{category_id}/children",
    response_model=CategoryChildrenListResponse
)
async def get_category_children(
    category_id: int,
    lang: Optional[str] = Query(
        default="it",
        description="Language code: it, en, fr, de, ar"
    ),
    db: Session = Depends(get_db)
):
    """
    Get all children (subcategories) of a parent category
    
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

    # Enforce max depth=2: children of a child category are always empty
    if parent.parent_id is not None:
        return {
            "data": [],
            "meta": {
                "parent_id": category_id,
                "requested_lang": lang,
                "resolved_lang": lang,
                "note": "Max depth is 2 (no grandchildren)"
            }
        }
    
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
    "/v1/categories/{category_id}",
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
    "/v1/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category(
    category_id: int,
    force: bool = Query(
        default=False,
        description="Force delete with all children"
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete a category
    
    Requires X-API-Key in header
    
    - **category_id**: ID of category to delete
    - **force**: If true, deletes category with all children (default: false)
    
    Examples:
    - DELETE /api/v1/categories/4 - Fails if has children
    - DELETE /api/v1/categories/4?force=true - Deletes with all children
    """
    try:
        success = crud_category.delete_category(db, category_id, force)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return None
    
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
    "/v1/categories/{category_id}/translations",
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


@router.get(
    "/v1/categories/children/{category_id}/products",
    response_model=dict
)
async def get_category_products(
    category_id: int,
    lang: Optional[str] = Query(
        default="it",
        description="Language code: it, en, fr, de, ar"
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get simple products by child category ID
    
    Requires X-API-Key in header
    
    - **category_id**: Child category ID
    - **lang**: Language code (default: it) - Supported: it, en, fr, de, ar
    
    Returns:
    - List of simple products with details
    - Each product includes: id, child_category, slug, image, brand_id, condition,
      quantity, title, sub_title, simple_description, is_active, and price object
    """
    from app.crud import product as crud_product
    from app.schemas.product import CategoryProductsResponse, CategoryProductItem, ProductPriceSimple
    
    # Validate language
    supported_langs = ["it", "en", "fr", "de", "ar"]
    if lang not in supported_langs:
        lang = "it"
    
    # Get products by category
    products_data = crud_product.get_products_by_category(db, category_id, lang)
    
    if not products_data:
        return {
            "data": [],
            "meta": {
                "parent_id": None,
                "requested_lang": lang,
                "resolved_lang": lang
            }
        }
    
    # Format response
    parent_id = products_data[0].get("parent_id") if products_data else None
    
    formatted_products = []
    for prod in products_data:
        formatted_products.append(
            CategoryProductItem(
                id=prod["id"],
                child_category=prod["child_category"],
                slug=prod["slug"],
                image=prod["image"],
                brand_id=prod["brand_id"],
                condition=prod["condition"],
                quantity=prod["quantity"],
                title=prod["title"],
                sub_title=prod["sub_title"],
                simple_description=prod["simple_description"],
                is_active=prod["is_active"],
                price=ProductPriceSimple(**prod["price"])
            )
        )
    
    return {
        "data": [p.model_dump() for p in formatted_products],
        "meta": {
            "parent_id": parent_id,
            "requested_lang": lang,
            "resolved_lang": lang
        }
    }


@router.post(
    "/v1/categories/deactivate-all",
    dependencies=[Depends(verify_api_key)]
)
async def deactivate_all_categories(
    db: Session = Depends(get_db)
):
    """
    Deactivate all active categories by setting is_active=False and adding [OLD] prefix
    
    **Requires API Key authentication**
    
    This endpoint:
    - Sets is_active=False for all categories
    - Adds [OLD] prefix to category names
    - Adds old- prefix to slugs
    - Does NOT delete any data
    
    Use this before importing new category tree structure.
    """
    try:
        # Get all active categories
        active_categories = db.query(Category).filter(Category.is_active == True).all()
        count = len(active_categories)
        
        if count == 0:
            return {
                "success": True,
                "message": "No active categories to deactivate",
                "deactivated_count": 0
            }
        
        # Deactivate all
        for cat in active_categories:
            cat.is_active = False
            if not cat.name.startswith("[OLD] "):
                cat.name = f"[OLD] {cat.name}"
            if cat.slug and not cat.slug.startswith("old-"):
                cat.slug = f"old-{cat.slug}"
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Successfully deactivated {count} categories",
            "deactivated_count": count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate categories: {str(e)}"
        )
