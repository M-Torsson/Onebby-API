"""
Product Import API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
import time
import tempfile
import shutil
from typing import Literal, Optional

from app.db.session import get_db
from app.schemas.import_products import (
    ImportReport,
    ImportErrorDetail,
    ProductStatsResponse,
    EnrichmentReport,
)
from app.services.product_import import ProductImportService, normalize_ean, is_valid_ean13
from app.services.product_enrichment import EnrichmentReader
from app.crud.product_import import import_products_batch, enrich_products_batch
from app.core.security.api_key import verify_api_key


router = APIRouter()


# Get excel directory: go up to app/ then add excel/
EXCEL_DIR = Path(__file__).parent.parent.parent / "excel"

# Default enrichment file mapping (eds group lists)
ENRICHMENT_DEFAULTS = {
    "telefonia": "Listino Telefonia web.xlsx",
    "informatica": "Listino INFORMATICA web.xlsx",
    "giochi": "Listino GIOCHI.xlsx",
    "cartoleria": "Listino Cartoleria.xlsx",
    "accessori": "Listino ACCESSORI telefonia.xlsx",
}

COMMERCE_ALLOWED_FILES = set(ENRICHMENT_DEFAULTS.values())


@router.post("/import/products", response_model=ImportReport, status_code=status.HTTP_200_OK)
async def import_products(
    source: Literal["effezzeta", "erregame", "dixe", "commerce_clarity"],
    filename: Optional[str] = None,
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

    # Special path: commerce_clarity uses the five fixed EDS files only
    if source == "commerce_clarity":
        if file:
            original_name = Path(file.filename or "").name
            if original_name not in COMMERCE_ALLOWED_FILES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File '{original_name}' is not allowed. Use one of: {sorted(COMMERCE_ALLOWED_FILES)}"
                )
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)
                file_path = Path(tmp_file.name)
        else:
            if not filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="filename is required for commerce_clarity when no file is uploaded"
                )
            if filename not in COMMERCE_ALLOWED_FILES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File '{filename}' is not allowed. Use one of: {sorted(COMMERCE_ALLOWED_FILES)}"
                )
            file_path = EXCEL_DIR / filename
            if not file_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"File not found: {file_path}"
                )

        try:
            reader = EnrichmentReader(file_path)
            raw_rows = reader.read()
            total_rows = len(raw_rows)

            valid_rows = []
            skipped_rows = []
            for row in raw_rows:
                row_number = row.get("row_number", 0)
                raw_ean = row.get("ean")
                if not raw_ean:
                    skipped_rows.append({
                        "row_number": row_number,
                        "ean": None,
                        "reason": "missing_ean",
                        "details": "Product has no EAN code"
                    })
                    continue

                ean = normalize_ean(raw_ean)
                if not is_valid_ean13(ean):
                    skipped_rows.append({
                        "row_number": row_number,
                        "ean": raw_ean,
                        "reason": "invalid_ean13",
                        "details": "EAN must be exactly 13 digits"
                    })
                    continue

                title = row.get("title")
                if not title:
                    skipped_rows.append({
                        "row_number": row_number,
                        "ean": ean,
                        "reason": "missing_title",
                        "details": "Product has no title"
                    })
                    continue

                valid_rows.append({
                    "ean": ean,
                    "title": title,
                    "price": row.get("price"),
                    "stock": 0,
                    "brand_name": row.get("brand_name"),
                    "category_path": [],
                    "description": row.get("description"),
                    "image_urls": row.get("image_urls") or [],
                    "row_number": row_number,
                })

            chunk_size = ProductImportService.CHUNK_SIZE
            chunks = [valid_rows[i:i + chunk_size] for i in range(0, len(valid_rows), chunk_size)]

            total_created = 0
            total_updated = 0
            total_skipped_dupe = 0
            total_skipped_manual = 0
            all_errors = []
            all_samples = []

            for idx, chunk in enumerate(chunks):
                stats = import_products_batch(db, chunk, dry_run, batch_index=idx)
                total_created += stats["created"]
                total_updated += stats["updated"]
                total_skipped_dupe += stats.get("skipped_duplicate", 0)
                total_skipped_manual += stats.get("skipped_manual", 0)
                all_errors.extend(stats["errors"])
                all_samples.extend(stats["samples"])

            skipped_errors = [
                {
                    "row_number": skip["row_number"],
                    "ean": skip.get("ean"),
                    "reason": skip["reason"],
                    "details": skip.get("details"),
                }
                for skip in skipped_rows
            ]
            all_errors.extend(skipped_errors)

            errors_summary: dict[str, int] = {}
            for error in all_errors:
                reason = error.get("reason", "unknown")
                errors_summary[reason] = errors_summary.get(reason, 0) + 1

            duration = time.time() - start_time

            invalid_count = errors_summary.get("invalid_ean13", 0)
            duplicate_count = errors_summary.get("duplicate_ean_in_batch", 0) + errors_summary.get("duplicate_ean_db", 0)
            manual_count = errors_summary.get("manual_blocked", 0)

            total_skipped = len(skipped_rows) + duplicate_count + manual_count

            report = ImportReport(
                source=source,
                total_rows=total_rows,
                created=total_created,
                updated=total_updated,
                skipped=total_skipped,
                skipped_invalid_ean13=invalid_count,
                skipped_duplicate=duplicate_count,
                skipped_manual=manual_count,
                errors_summary=errors_summary,
                errors=[ImportErrorDetail(**e) for e in all_errors] if verbose_errors else [],
                errors_sample=[ImportErrorDetail(**e) for e in all_errors[:20]],
                sample_imports=all_samples[:5],
                duration_seconds=round(duration, 2),
                dry_run=dry_run,
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
            if file and file_path.exists():
                try:
                    file_path.unlink()
                except:
                    pass

    # Determine file path for the legacy sources
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

        resolved_name = file_mapping.get(source)
        if not resolved_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No default file configured for source: {source}"
            )

        file_path = EXCEL_DIR / resolved_name

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
        total_skipped_invalid = 0
        total_skipped_dupe = 0
        total_skipped_manual = 0
        
        for idx, chunk in enumerate(chunks):
            stats = import_products_batch(db, chunk, dry_run, batch_index=idx)
            total_created += stats["created"]
            total_updated += stats["updated"]
            total_skipped_invalid += stats.get("skipped_invalid_ean13", 0)
            total_skipped_dupe += stats.get("skipped_duplicate", 0)
            total_skipped_manual += stats.get("skipped_manual", 0)
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

        invalid_count = errors_summary.get("invalid_ean13", 0)
        duplicate_count = errors_summary.get("duplicate_ean_in_batch", 0) + errors_summary.get("duplicate_ean_db", 0)
        manual_count = errors_summary.get("manual_blocked", 0)
        total_skipped = len(skipped_rows) + duplicate_count + manual_count
        
        # Build report
        report = ImportReport(
            source=source,
            total_rows=total_rows,
            created=total_created,
            updated=total_updated,
            skipped=total_skipped,
            skipped_invalid_ean13=invalid_count,
            skipped_duplicate=duplicate_count,
            skipped_manual=manual_count,
            errors_summary=errors_summary,
            errors=[ImportErrorDetail(**e) for e in all_errors] if verbose_errors else [],
            errors_sample=[ImportErrorDetail(**e) for e in all_errors[:20]],  # First 20 errors
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


@router.post("/import/products/enrich", response_model=EnrichmentReport, status_code=status.HTTP_200_OK)
async def enrich_products(
    filename: Optional[str] = None,
    dry_run: bool = False,
    verbose_errors: bool = False,
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """
    Enrich existing products using EAN as the only key.

    Rules:
    - Skip rows where EAN is missing or not found in DB.
    - Only fill missing fields (title/description/brand/images/price-if-empty).
    - Never touch stock or categories.
    """
    start_time = time.time()

    # Determine file path
    if file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            file_path = Path(tmp_file.name)
    else:
        # Pick default file
        chosen = filename
        if not chosen:
            # default to telefonia if not specified
            chosen = ENRICHMENT_DEFAULTS.get("telefonia")
        elif chosen in ENRICHMENT_DEFAULTS:
            chosen = ENRICHMENT_DEFAULTS[chosen]

        file_path = EXCEL_DIR / chosen
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_path}"
            )

    try:
        reader = EnrichmentReader(file_path)
        rows = reader.read()
        total_rows = len(rows)

        stats = enrich_products_batch(db, rows, dry_run=dry_run, batch_index=0)

        errors_summary: dict[str, int] = {}
        for err in stats["errors"]:
            reason = err.get("reason", "unknown")
            errors_summary[reason] = errors_summary.get(reason, 0) + 1

        duration = time.time() - start_time

        return EnrichmentReport(
            total_rows=total_rows,
            matched=stats["matched"],
            skipped=stats["skipped"],
            errors=len(stats["errors"]),
            errors_summary=errors_summary,
            matched_samples=stats.get("matched_samples", [])[:5],
            skipped_samples=stats.get("skipped_samples", [])[:5],
            errors_sample=[ImportErrorDetail(**e) for e in stats["errors"][:20]] if verbose_errors else [],
            duration_seconds=round(duration, 2),
            dry_run=dry_run,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Enrichment failed: {str(e)}")
    finally:
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
    
    Optimized with single query for better performance
    """
    from sqlalchemy import func, case
    from app.models.product import Product
    from app.models.brand import Brand
    from app.models.category import Category
    
    # Single optimized query for all product stats
    product_stats = db.query(
        func.count(Product.id).label('total_products'),
        func.count(func.distinct(Product.ean)).label('unique_eans'),
        func.sum(case((Product.ean.isnot(None) & (Product.ean != ''), 1), else_=0)).label('products_with_ean'),
        func.sum(case((Product.price_list.isnot(None), 1), else_=0)).label('products_with_price'),
        func.sum(case((Product.brand_id.isnot(None), 1), else_=0)).label('products_with_brand'),
        func.min(Product.date_add).label('earliest_created'),
        func.max(Product.date_add).label('latest_created'),
        func.min(Product.date_update).label('earliest_updated'),
        func.max(Product.date_update).label('latest_updated')
    ).first()
    
    # Separate simple queries for brands and categories
    total_brands = db.query(func.count(Brand.id)).scalar()
    total_categories = db.query(func.count(Category.id)).scalar()
    
    # Calculate derived values
    total_products = product_stats.total_products or 0
    products_with_ean = product_stats.products_with_ean or 0
    products_with_price = product_stats.products_with_price or 0
    products_with_brand = product_stats.products_with_brand or 0
    
    return ProductStatsResponse(
        total_products=total_products,
        unique_eans=product_stats.unique_eans or 0,
        products_with_ean=products_with_ean,
        products_without_ean=total_products - products_with_ean,
        total_brands=total_brands or 0,
        total_categories=total_categories or 0,
        products_with_price=products_with_price,
        products_without_price=total_products - products_with_price,
        products_with_brand=products_with_brand,
        products_without_brand=total_products - products_with_brand,
        earliest_created_at=product_stats.earliest_created,
        latest_created_at=product_stats.latest_created,
        earliest_updated_at=product_stats.earliest_updated,
        latest_updated_at=product_stats.latest_updated
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
