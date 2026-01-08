from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime


# ============= Import Schemas =============

class ImportRequest(BaseModel):
    """Import request schema"""
    source: Literal["effezzeta", "erregame", "dixe", "commerce_clarity"] = Field(
        ...,
        description="Source of the import file"
    )
    dry_run: bool = Field(
        default=False,
        description="If True, validates data without saving to database"
    )


class ImportErrorDetail(BaseModel):
    """Single error detail"""
    row_number: int
    ean: Optional[str] = None
    reason: str
    details: Optional[str] = None


class ImportReport(BaseModel):
    """Import operation report"""
    source: str
    total_rows: int
    created: int
    updated: int
    skipped: int
    errors_summary: Dict[str, int] = Field(
        default_factory=dict,
        description="Summary of errors by reason"
    )
    errors: List[ImportErrorDetail] = Field(
        default_factory=list,
        description="Detailed error list (controlled by verbose_errors parameter)"
    )
    sample_imports: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Sample of first 5 imports with EAN and status"
    )
    duration_seconds: float
    dry_run: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "source": "effezzeta",
                "total_rows": 1000,
                "created": 850,
                "updated": 100,
                "skipped": 30,
                "errors_summary": {
                    "missing_ean": 356,
                    "missing_title": 12
                },
                "errors": [],
                "sample_imports": [
                    {"ean": "8001234567890", "existed_before": False, "action": "created"},
                    {"ean": "8001234567891", "existed_before": True, "action": "updated"}
                ],
                "duration_seconds": 45.2,
                "dry_run": False,
                "timestamp": "2026-01-08T12:00:00"
            }
        }


class ProductStatsResponse(BaseModel):
    """Product statistics response"""
    total_products: int
    unique_eans: int
    products_with_ean: int
    products_without_ean: int
    total_brands: int
    total_categories: int
    products_with_price: int
    products_without_price: int
    products_with_brand: int
    products_without_brand: int
    earliest_created_at: Optional[datetime] = None
    latest_created_at: Optional[datetime] = None
    earliest_updated_at: Optional[datetime] = None
    latest_updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_products": 6075,
                "unique_eans": 6075,
                "products_with_ean": 6075,
                "products_without_ean": 0,
                "total_brands": 245,
                "total_categories": 128,
                "products_with_price": 4126,
                "products_without_price": 1949,
                "products_with_brand": 4285,
                "products_without_brand": 1790,
                "earliest_created_at": "2026-01-08T10:00:00",
                "latest_created_at": "2026-01-08T12:00:00",
                "earliest_updated_at": "2026-01-08T10:00:00",
                "latest_updated_at": "2026-01-08T12:00:00"
                        "details": "Product has no EAN code"
                    }
                ],
                "duration_seconds": 45.2,
                "dry_run": False,
                "timestamp": "2026-01-08T12:00:00"
            }
        }
