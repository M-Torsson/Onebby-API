from typing import Optional, List, Tuple
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session, joinedload, aliased
from slugify import slugify
from deep_translator import GoogleTranslator
from app.models.category import Category, CategoryTranslation
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """Get category by ID with translations"""
    return db.query(Category).options(
        joinedload(Category.translations)
    ).filter(Category.id == category_id).first()


def get_category_by_slug(db: Session, slug: str) -> Optional[Category]:
    """Get category by slug"""
    return db.query(Category).filter(Category.slug == slug).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100, parent_id: Optional[int] = None) -> List[Category]:
    """Get all categories with optional parent filter"""
    query = db.query(Category)
    
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    
    return query.offset(skip).limit(limit).all()


def get_all_categories(
    db: Session, 
    lang: Optional[str] = None, 
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100
) -> List[Category]:
    """Get all categories (main and children) with optional translation and pagination"""
    # Allow max depth=3 (parent + child + grandson). No filtering by depth.
    query = (
        db.query(Category)
        .options(joinedload(Category.children))
    )
    
    if active_only:
        query = query.filter(Category.is_active == True)
    
    categories = query.order_by(
        Category.parent_id.nulls_first(), 
        Category.sort_order
    ).offset(skip).limit(limit).all()
    
    # If language is specified, load translated names
    if lang and categories:
        for category in categories:
            translation = db.query(CategoryTranslation).filter(
                CategoryTranslation.category_id == category.id,
                CategoryTranslation.lang == lang
            ).first()
            
            if translation:
                category.name = translation.name
                category.slug = translation.slug
    
    return categories


def search_categories(
    db: Session,
    q: str,
    lang: Optional[str] = None,
    active_only: bool = True,
    parent_only: bool = False,
    limit: int = 5000,
) -> Tuple[List[Category], int]:
    """Search categories by name/slug (and translation for requested lang).

    Returns (categories, total_matches). Uses an ID subquery to avoid duplicate rows
    when joining translations.
    """
    q = (q or "").strip()
    if not q:
        return ([], 0)

    like = f"%{q}%"

    # Allow max depth=3 (parent + child + grandson). No filtering by depth.
    # Build an ID query first (stable ordering, distinct IDs)
    join_cond = (CategoryTranslation.category_id == Category.id)
    if lang:
        join_cond = and_(join_cond, CategoryTranslation.lang == lang)

    ids_query = (
        db.query(Category.id, Category.parent_id, Category.sort_order)
        .outerjoin(CategoryTranslation, join_cond)
    )

    if active_only:
        ids_query = ids_query.filter(Category.is_active == True)

    if parent_only:
        ids_query = ids_query.filter(Category.parent_id == None)

    ids_query = ids_query.filter(
        or_(
            Category.name.ilike(like),
            Category.slug.ilike(like),
            CategoryTranslation.name.ilike(like),
            CategoryTranslation.slug.ilike(like),
        )
    )

    ids_query = ids_query.distinct().order_by(
        Category.parent_id.nulls_first(),
        Category.sort_order,
        Category.id,
    )

    total = ids_query.count()
    ids = [row[0] for row in ids_query.limit(limit).all()]

    if not ids:
        return ([], total)

    categories = db.query(Category).options(joinedload(Category.children)).filter(Category.id.in_(ids)).all()

    # Preserve ordering from ids_query
    order_index = {category_id: idx for idx, category_id in enumerate(ids)}
    categories.sort(key=lambda c: order_index.get(c.id, 10**9))

    # Apply translation override for response language
    if lang and categories:
        for category in categories:
            translation = db.query(CategoryTranslation).filter(
                CategoryTranslation.category_id == category.id,
                CategoryTranslation.lang == lang,
            ).first()
            if translation:
                category.name = translation.name
                category.slug = translation.slug

    return (categories, total)


def count_all_categories(db: Session, active_only: bool = True) -> int:
    """Count total categories (all levels, no depth restriction)"""
    query = db.query(Category)
    
    if active_only:
        query = query.filter(Category.is_active == True)
    
    return query.count()


def get_main_categories(
    db: Session, 
    lang: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Category]:
    """Get all main categories (parent_id = null) with optional translation and pagination"""
    categories = db.query(Category).options(
        joinedload(Category.children)
    ).filter(
        Category.parent_id == None,
        Category.is_active == True
    ).order_by(Category.sort_order).offset(skip).limit(limit).all()
    
    # If language is specified, load translated names
    if lang and categories:
        for category in categories:
            translation = db.query(CategoryTranslation).filter(
                CategoryTranslation.category_id == category.id,
                CategoryTranslation.lang == lang
            ).first()
            
            if translation:
                category.name = translation.name
                category.slug = translation.slug
    
    return categories


def count_main_categories(db: Session) -> int:
    """Count main categories (parent_id = null)"""
    return db.query(Category).filter(
        Category.parent_id == None,
        Category.is_active == True
    ).count()


def get_category_children(
    db: Session, 
    parent_id: int, 
    lang: Optional[str] = None
) -> List[Category]:
    """Get children categories of a parent category"""
    # Allow 3-level hierarchy as per prezzoforte_category_tree.xlsx:
    # Parent (level 1) → Child (level 2) → Grandson (level 3)
    # No depth limit enforced - let the tree structure be flexible
    
    children = db.query(Category).filter(
        Category.parent_id == parent_id,
        Category.is_active == True
    ).order_by(Category.sort_order).all()
    
    # If language is specified, load translated names
    if lang and children:
        for child in children:
            translation = db.query(CategoryTranslation).filter(
                CategoryTranslation.category_id == child.id,
                CategoryTranslation.lang == lang
            ).first()
            
            if translation:
                child.name = translation.name
                child.slug = translation.slug
    
    return children


def get_category_grandchildren(
    db: Session, 
    parent_id: int, 
    lang: Optional[str] = None
) -> List[Category]:
    """Get all subcategories (children) of a category - works for any level"""
    # Just return direct children - same as get_category_children
    children = db.query(Category).filter(
        Category.parent_id == parent_id,
        Category.is_active == True
    ).order_by(Category.sort_order).all()
    
    # If language is specified, load translated names
    if lang and children:
        for child in children:
            translation = db.query(CategoryTranslation).filter(
                CategoryTranslation.category_id == child.id,
                CategoryTranslation.lang == lang
            ).first()
            
            if translation:
                child.name = translation.name
                child.slug = translation.slug
    
    return children


def create_category(db: Session, category: CategoryCreate) -> Category:
    """Create a new category"""
    # Generate slug if not provided
    if not category.slug:
        category.slug = slugify(category.name)
    
    # Check if parent exists and is active (if parent_id provided)
    if category.parent_id:
        parent = get_category(db, category.parent_id)
        if not parent or not parent.is_active:
            raise ValueError("Parent category not found or not active")
        # Allow max depth=3 (parent -> child -> grandson)
        # Removed restriction: now allows grandchildren
    
    db_category = Category(
        name=category.name,
        slug=category.slug,
        image=category.image,
        icon=category.icon,
        sort_order=category.sort_order,
        is_active=category.is_active,
        parent_id=category.parent_id
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    # Create default translations
    create_default_translations(db, db_category)
    
    return db_category


def create_default_translations(db: Session, category: Category):
    """Create automatic translations for a category using Google Translate"""
    # Language mappings
    languages = {
        "it": "it",  # Italian (source language)
        "en": "en",  # English
        "fr": "fr",  # French
        "de": "de",  # German
        "ar": "ar"   # Arabic
    }
    
    translations_created = []
    for lang_code, target_lang in languages.items():
        try:
            if lang_code == "it":
                # Italian is the source, use original name
                translated_name = category.name
                translated_slug = category.slug
                print(f"   → {lang_code}: {translated_name} (original)")
            else:
                # Translate to target language using GoogleTranslator
                try:
                    translated_name = GoogleTranslator(
                        source='it',
                        target=target_lang
                    ).translate(category.name)
                    print(f"   → {lang_code}: {translated_name} (translated)")
                except Exception as trans_error:
                    # If translation fails, use original name
                    print(f"   ⚠ {lang_code}: Translation failed, using original name - {trans_error}")
                    translated_name = category.name
                
                # For Arabic, keep the Arabic text in slug (don't transliterate)
                if lang_code == "ar":
                    translated_slug = translated_name.replace(" ", "-").lower()
                else:
                    translated_slug = slugify(translated_name)
            
            # Create translation record
            translation = CategoryTranslation(
                category_id=category.id,
                lang=lang_code,
                name=translated_name,
                slug=translated_slug,
                description=None  # Empty for now, can be updated later
            )
            db.add(translation)
            translations_created.append(lang_code)
        
        except Exception as e:
            # Fallback to original name if translation fails
            print(f"   ✗ {lang_code}: Error creating translation - {e}")
            translation = CategoryTranslation(
                category_id=category.id,
                lang=lang_code,
                name=category.name,
                slug=category.slug,
                description=None
            )
            db.add(translation)
            translations_created.append(f"{lang_code} (fallback)")
    
    db.commit()
    print(f"   ✓ Total translations created: {len(translations_created)} - {', '.join(translations_created)}")
    
    # Reload category with translations
    db.refresh(category)


def update_category(db: Session, category_id: int, category: CategoryUpdate) -> Optional[Category]:
    """Update a category"""
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    update_data = category.model_dump(exclude_unset=True)
    
    # If parent_id is being updated, verify parent exists and is active
    if "parent_id" in update_data:
        new_parent_id = update_data.get("parent_id")
        if new_parent_id is not None:
            if new_parent_id == category_id:
                raise ValueError("Invalid parent_id: category cannot be its own parent")
            parent = get_category(db, new_parent_id)
            if not parent or not parent.is_active:
                raise ValueError("Parent category not found or not active")
            # Allow max depth=3 (parent -> child -> grandson)
            # Removed restriction: now allows grandchildren
    
    # If name is updated and no slug provided, regenerate slug
    if "name" in update_data and "slug" not in update_data:
        update_data["slug"] = slugify(update_data["name"])
    
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int, force: bool = False) -> bool:
    """
    Delete a category safely
    
    Args:
        category_id: ID of category to delete
        force: If True, deletes children first using simple SQL
    """
    # Check if exists (simple check without loading object)
    exists = db.query(Category.id).filter(Category.id == category_id).scalar()
    if not exists:
        return False
    
    if force:
        # Get all descendants using simple iteration
        to_delete = [category_id]
        processed = []
        
        while to_delete:
            current_id = to_delete.pop(0)
            if current_id in processed:
                continue
            
            # Find children of current category
            children_ids = db.query(Category.id).filter(
                Category.parent_id == current_id
            ).all()
            
            # Add children to delete list
            for child_id_tuple in children_ids:
                if child_id_tuple[0] not in processed:
                    to_delete.append(child_id_tuple[0])
            
            processed.append(current_id)
        
        # Delete all in reverse order (children first)
        for cat_id in reversed(processed):
            # Delete translations
            db.query(CategoryTranslation).filter(
                CategoryTranslation.category_id == cat_id
            ).delete(synchronize_session=False)
            
            # Delete category
            db.query(Category).filter(Category.id == cat_id).delete(synchronize_session=False)
        
        db.commit()
        return True
    else:
        # Normal delete - check for children
        has_children = db.query(Category.id).filter(Category.parent_id == category_id).first()
        if has_children:
            raise ValueError("Cannot delete category with children")
        
        # Delete translations first
        db.query(CategoryTranslation).filter(
            CategoryTranslation.category_id == category_id
        ).delete(synchronize_session=False)
        
        # Delete category
        db.query(Category).filter(Category.id == category_id).delete(synchronize_session=False)
        
        db.commit()
        return True


def update_category_translation(
    db: Session,
    category_id: int,
    lang: str,
    name: str,
    slug: str
) -> Optional[CategoryTranslation]:
    """Update or create a category translation"""
    translation = db.query(CategoryTranslation).filter(
        CategoryTranslation.category_id == category_id,
        CategoryTranslation.lang == lang
    ).first()
    
    if translation:
        translation.name = name
        translation.slug = slug
    else:
        translation = CategoryTranslation(
            category_id=category_id,
            lang=lang,
            name=name,
            slug=slug
        )
        db.add(translation)
    
    db.commit()
    db.refresh(translation)
    return translation


def update_category_translations(
    db: Session,
    category_id: int,
    translations_data: List[dict]
) -> Category:
    """Update all translations for a category"""
    # Verify category exists
    category = get_category(db, category_id)
    if not category:
        raise ValueError("Category not found")
    
    # Update each translation
    for trans_data in translations_data:
        update_category_translation(
            db=db,
            category_id=category_id,
            lang=trans_data["lang"],
            name=trans_data["name"],
            slug=trans_data["slug"]
        )
    
    # Reload category with updated translations
    db.refresh(category)
    return category
