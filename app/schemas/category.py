from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Translation Schemas
class CategoryTranslationBase(BaseModel):
    """Base translation schema"""
    lang: str = Field(..., max_length=5, description="Language code: it, en, fr, de, ar")
    name: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class CategoryTranslationResponse(CategoryTranslationBase):
    """Translation response schema"""
    pass

    class Config:
        from_attributes = True


class CategoryTranslationUpdate(BaseModel):
    """Schema for updating translations"""
    translations: List[CategoryTranslationBase] = Field(
        ..., 
        description="List of translations for all languages"
    )


# Category Schemas
class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    image: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=500)
    sort_order: int = Field(default=0)
    is_active: bool = Field(default=True)
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    image: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=500)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    """Category response schema"""
    id: int
    has_children: bool
    translations: List[CategoryTranslationResponse] = []

    class Config:
        from_attributes = True


class CategoryChildResponse(BaseModel):
    """Child category response schema (without translations)"""
    id: int
    name: str
    slug: Optional[str]
    image: Optional[str]
    icon: Optional[str]
    sort_order: int
    is_active: bool
    parent_id: Optional[int]
    has_children: bool

    class Config:
        from_attributes = True


class CategoryChildrenListResponse(BaseModel):
    """Response schema for listing children categories"""
    data: List[CategoryChildResponse]
    meta: dict


class CategoryCreateResponse(BaseModel):
    """Response schema for creating category"""
    data: CategoryResponse


class CategoryMainResponse(BaseModel):
    """Main category response schema"""
    id: int
    name: str
    slug: Optional[str]
    image: Optional[str]
    icon: Optional[str]
    sort_order: int
    is_active: bool
    parent_id: Optional[int]
    has_children: bool

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Response schema for listing main categories"""
    data: List[CategoryMainResponse]
    meta: dict
