"""
Product Import API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
import time
import tempfile
import shutil
from typing import Literal

from app.db.session import get_db
from app.schemas.import_products import ImportReport, ImportErrorDetail, ProductStatsResponse
from app.services.product_import import ProductImportService
from app.crud.product_import import import_products_batch
from app.core.security.api_key import verify_api_key


router = APIRouter()


# Get excel directory: go up to app/ then add excel/
EXCEL_DIR = Path(__file__).parent.parent.parent / "excel"


@router.post("/import/products", response_model=ImportReport, status_code=status.HTTP_200_OK)
async def import_products(
    source: Literal["effezzeta", "erregame", "dixe", "commerce_clarity"],
    dry_run: bool = False,
    verbose_errors: bool = False,
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """
    Import products from Excel file
    
    - **source**: Source of the import (effezzeta, erregame, dixe, commerce_clarity)
    - **dry_run**: If True, validates data without saving to database
    - **verbose_errors**: If True, returns detailed error list (default: False, summary only)
    - **file**: Excel file to import (optional - uses default file from excel/ folder if not provided)
    
    Returns import report with statistics, error summary, and sample imports
    """
    start_time = time.time()
    
    # Determine file path
    if file:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            file_path = Path(tmp_file.name)
    else:
        # Use default file from excel/ folder
        file_mapping = {
            "effezzeta": "Listino-prodotti.xlsx",
            "erregame": "erregame_organized.xlsx",
            "dixe": "Dixe_organized.xlsx",
        }
        
        filename = file_mapping.get(source)
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No default file configured for source: {source}"
            )
        
        file_path = EXCEL_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_path}"
            )
    
    try:
        # Initialize import service
        import_service = ProductImportService(source)
        
        # Read Excel file
        raw_rows = import_service.read_excel_file(file_path)
        total_rows = len(raw_rows)
        
        # Map rows to standard format
        valid_rows, skipped_rows = import_service.map_rows(raw_rows)
        
        # Split into chunks
        chunks = import_service.chunk_rows(valid_rows)
        
        # Process chunks
        total_created = 0
        total_updated = 0
        all_errors = []
        all_samples = []
        
        for idx, chunk in enumerate(chunks):
            stats = import_products_batch(db, chunk, dry_run, batch_index=idx)
            total_created += stats["created"]
            total_updated += stats["updated"]
            all_errors.extend(stats["errors"])
            all_samples.extend(stats["samples"])
        
        # Add skipped rows to errors
        skipped_errors = [
            {
                "row_number": skip["row_number"],
                "ean": skip.get("ean"),
                "reason": skip["reason"],
                "details": skip.get("details")
            }
            for skip in skipped_rows
        ]
        all_errors.extend(skipped_errors)
        
        # Build errors summary
        errors_summary = {}
        for error in all_errors:
            reason = error.get("reason", "unknown")
            errors_summary[reason] = errors_summary.get(reason, 0) + 1
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Build report
        report = ImportReport(
            source=source,
            total_rows=total_rows,
            created=total_created,
            updated=total_updated,
            skipped=len(skipped_rows),
            errors_summary=errors_summary,
            errors=[ImportErrorDetail(**e) for e in all_errors] if verbose_errors else [],
            sample_imports=all_samples[:5],  # First 5 only
            duration_seconds=round(duration, 2),
            dry_run=dry_run
        )
        
        return report
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )
    
    finally:
        # Clean up temporary file if uploaded
        if file and file_path.exists():
            try:
                file_path.unlink()
            except:
                pass


@router.get("/admin/stats/products", response_model=ProductStatsResponse, status_code=status.HTTP_200_OK)
async def get_product_stats(
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """
    Get comprehensive product statistics
    
    Returns:
    - Total products count
    - Unique EANs count  
    - Products with/without EAN
    - Total brands and categories
    - Products with/without price
    - Products with/without brand
    - Earliest/latest created and updated timestamps
    """
    from sqlalchemy import func
    from app.models.product import Product
    from app.models.brand import Brand
    from app.models.category import Category
    
    # Total products
    total_products = db.query(func.count(Product.id)).scalar()
    
    # Unique EANs
    unique_eans = db.query(func.count(func.distinct(Product.ean))).filter(
        Product.ean.isnot(None),
        Product.ean != ''
    ).scalar()
    
    # Products with EAN
    products_with_ean = db.query(func.count(Product.id)).filter(
        Product.ean.isnot(None),
        Product.ean != ''
    ).scalar()
    
    products_without_ean = total_products - products_with_ean
    
    # Brands and categories
    total_brands = db.query(func.count(Brand.id)).scalar()
    total_categories = db.query(func.count(Category.id)).scalar()
    
    # Products with/without price
    products_with_price = db.query(func.count(Product.id)).filter(
        Product.price_list.isnot(None)
    ).scalar()
    products_without_price = total_products - products_with_price
    
    # Products with/without brand
    products_with_brand = db.query(func.count(Product.id)).filter(
        Product.brand_id.isnot(None)
    ).scalar()
    products_without_brand = total_products - products_with_brand
    
    # Timestamps
    earliest_created = db.query(func.min(Product.date_add)).scalar()
    latest_created = db.query(func.max(Product.date_add)).scalar()
    earliest_updated = db.query(func.min(Product.date_update)).scalar()
    latest_updated = db.query(func.max(Product.date_update)).scalar()
    
    return ProductStatsResponse(
        total_products=total_products or 0,
        unique_eans=unique_eans or 0,
        products_with_ean=products_with_ean or 0,
        products_without_ean=products_without_ean or 0,
        total_brands=total_brands or 0,
        total_categories=total_categories or 0,
        products_with_price=products_with_price or 0,
        products_without_price=products_without_price or 0,
        products_with_brand=products_with_brand or 0,
        products_without_brand=products_without_brand or 0,
        earliest_created_at=earliest_created,
        latest_created_at=latest_created,
        earliest_updated_at=earliest_updated,
        latest_updated_at=latest_updated
    )


@router.get("/import/stats", status_code=status.HTTP_200_OK)
async def get_import_stats_deprecated(
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """
    [DEPRECATED] Use /admin/stats/products instead
    
    Get database statistics for imported products
    """
    from sqlalchemy import func, distinct
    from app.models.product import Product
    from app.models.brand import Brand
    from app.models.category import Category
    
    # Count total products
    total_products = db.query(func.count(Product.id)).scalar()
    
    # Count unique EANs
    unique_eans = db.query(func.count(distinct(Product.ean))).filter(Product.ean.isnot(None)).scalar()
    
    # Count total brands
    total_brands = db.query(func.count(Brand.id)).scalar()
    
    # Count total categories
    total_categories = db.query(func.count(Category.id)).scalar()
    
    # Count products with/without price
    products_with_price = db.query(func.count(Product.id)).filter(Product.price_list.isnot(None)).scalar()
    products_without_price = db.query(func.count(Product.id)).filter(Product.price_list.is_(None)).scalar()
    
    # Count products with/without brand
    products_with_brand = db.query(func.count(Product.id)).filter(Product.brand_id.isnot(None)).scalar()
    products_without_brand = db.query(func.count(Product.id)).filter(Product.brand_id.is_(None)).scalar()
    
    return {
        "total_products": total_products,
        "unique_eans": unique_eans,
        "total_brands": total_brands,
        "total_categories": total_categories,
        "products_with_price": products_with_price,
        "products_without_price": products_without_price,
        "products_with_brand": products_with_brand,
        "products_without_brand": products_without_brand
    }
