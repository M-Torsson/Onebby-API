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
from app.schemas.import_products import ImportReport, ImportErrorDetail
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
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """
    Import products from Excel file
    
    - **source**: Source of the import (effezzeta, erregame, dixe, commerce_clarity)
    - **dry_run**: If True, validates data without saving to database
    - **file**: Excel file to import (optional - uses default file from excel/ folder if not provided)
    
    Returns import report with statistics and errors
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
        
        for chunk in chunks:
            stats = import_products_batch(db, chunk, dry_run)
            total_created += stats["created"]
            total_updated += stats["updated"]
            all_errors.extend(stats["errors"])
        
        # Add skipped rows to errors
        all_errors.extend([
            ImportErrorDetail(
                row_number=skip["row_number"],
                ean=skip.get("ean"),
                reason=skip["reason"],
                details=skip.get("details")
            )
            for skip in skipped_rows
        ])
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Build report
        report = ImportReport(
            source=source,
            total_rows=total_rows,
            created=total_created,
            updated=total_updated,
            skipped=len(skipped_rows),
            errors=all_errors,
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


@router.get("/import/stats", status_code=status.HTTP_200_OK)
async def get_import_stats(
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """
    Get database statistics for imported products
    
    Returns:
    - total_products: Total number of products
    - unique_eans: Number of unique EAN codes
    - total_brands: Total number of brands
    - total_categories: Total number of categories
    - products_with_price: Products that have a price
    - products_without_price: Products without a price
    - products_with_brand: Products that have a brand
    - products_without_brand: Products without a brand
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
