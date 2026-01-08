from pydantic import BaseModel, Field
from typing import Optional, List, Literal
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
    reason: str
    details: Optional[str] = None


class ImportReport(BaseModel):
    """Import operation report"""
    source: str
    total_rows: int
    created: int
    updated: int
    skipped: int
    errors: List[ImportErrorDetail]
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
                "errors": [
                    {
                        "row_number": 15,
                        "reason": "missing_ean",
                        "details": "Product has no EAN code"
                    }
                ],
                "duration_seconds": 45.2,
                "dry_run": False,
                "timestamp": "2026-01-08T12:00:00"
            }
        }
