from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from slugify import slugify
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


def get_category_children(
    db: Session, 
    parent_id: int, 
    lang: Optional[str] = None
) -> List[Category]:
    """Get children categories of a parent category"""
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
    """Create default translations for a category"""
    # Translation mappings (basic examples - in production, use a translation service)
    default_translations = {
        "it": {"name": category.name, "slug": category.slug},
        "en": {"name": category.name, "slug": category.slug},
        "fr": {"name": category.name, "slug": category.slug},
        "de": {"name": category.name, "slug": category.slug},
        "ar": {"name": category.name, "slug": category.slug}
    }
    
    for lang, trans_data in default_translations.items():
        translation = CategoryTranslation(
            category_id=category.id,
            lang=lang,
            name=trans_data["name"],
            slug=trans_data["slug"]
        )
        db.add(translation)
    
    db.commit()
    
    # Reload category with translations
    db.refresh(category)


def update_category(db: Session, category_id: int, category: CategoryUpdate) -> Optional[Category]:
    """Update a category"""
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    update_data = category.dict(exclude_unset=True)
    
    # If parent_id is being updated, verify parent exists and is active
    if "parent_id" in update_data and update_data["parent_id"]:
        parent = get_category(db, update_data["parent_id"])
        if not parent or not parent.is_active:
            raise ValueError("Parent category not found or not active")
    
    # If name is updated and no slug provided, regenerate slug
    if "name" in update_data and "slug" not in update_data:
        update_data["slug"] = slugify(update_data["name"])
    
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category"""
    db_category = get_category(db, category_id)
    if not db_category:
        return False
    
    # Check if category has children
    if db_category.has_children:
        raise ValueError("Cannot delete category with children")
    
    db.delete(db_category)
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
