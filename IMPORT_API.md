# Product Import API Documentation

## Overview
API endpoint for importing products from multiple sources (Excel files). Supports upsert operations based on EAN codes.

---

## Endpoint

```
POST /api/import/products
```

---

## Authentication
Requires API Key authentication.

```bash
Header: X-API-KEY: your-api-key
```

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source` | string | Yes | - | Source of the import: `effezzeta`, `erregame`, `dixe`, or `commerce_clarity` |
| `dry_run` | boolean | No | `false` | If `true`, validates data without saving to database |
| `file` | file | No | - | Excel file to import (optional - uses default file from `app/excel/` folder if not provided) |

---

## Response Schema

```json
{
  "source": "effezzeta",
  "total_rows": 3958,
  "created": 3450,
  "updated": 152,
  "skipped": 356,
  "errors": [
    {
      "row_number": 15,
      "reason": "missing_ean",
      "details": "Product has no EAN code"
    }
  ],
  "duration_seconds": 45.2,
  "dry_run": false,
  "timestamp": "2026-01-08T12:00:00"
}
```

---

## Source Mappings

### 1. Effezzeta (`Listino-prodotti.xlsx`)

| Excel Column | Product Field | Notes |
|--------------|---------------|-------|
| `Codice a barre EAN-13 o JAN` | `ean` | **Required** - Skip if missing |
| `Nome prodotto` | `title` | **Required** |
| `Listino - IVA Esclusa` | `price` | Tax excluded price |
| `Quantità` | `stock` | Stock quantity |
| `Categoria` | `category_path` | Single level category |
| `Descrizione` | `description` | HTML allowed |
| `URL di immagini prodotto` | `image_urls` | Comma-separated URLs (deferred to MVP phase 2) |

**Notes:**
- ❌ No brand field
- ✅ Has descriptions (HTML)
- ✅ Has multiple image URLs
- ⚠️ 356 products without EAN (will be skipped)

---

### 2. Erregame (`erregame_organized.xlsx`)

| Excel Column | Product Field | Notes |
|--------------|---------------|-------|
| `EAN` | `ean` | **Required** |
| `Title` | `title` | **Required** |
| `Price` | `price` | Final price |
| `Available` | `stock` | Stock quantity |
| `Brand` | `brand_name` | Auto-creates brand |
| `Category` | `category_path[0]` | Parent category |
| `Subcategory` | `category_path[1]` | Child category |
| `Description` | `description` | Plain text |
| `ImageLink` | `image_urls` | Single URL (deferred) |

**Notes:**
- ✅ Has brands
- ✅ Has category hierarchy (Parent → Child)
- ✅ All products have EAN
- ⚠️ 759 products overlap with Dixe

---

### 3. Dixe (`Dixe_organized.xlsx`)

| Excel Column | Product Field | Notes |
|--------------|---------------|-------|
| `COD/EAN` | `ean` | **Required** |
| `Titolo` | `title` | **Required** |
| `quantity` | `stock` | Stock quantity |
| `Categoria` | `category_path` | Format: "Parent > Child" |

**Notes:**
- ❌ No brand field
- ❌ No price field
- ❌ No images
- ✅ Category hierarchy auto-parsed from "Parent > Child" format
- ✅ All products have EAN
- ⚠️ 759 products overlap with Erregame

---

## Business Logic

### Upsert by EAN
- **If EAN exists**: Update existing product (only fields present in import)
- **If EAN doesn't exist**: Create new product
- **If EAN missing**: Skip row (added to errors with reason `missing_ean`)

### Reference Field
- `reference = ean` (EAN is used as the product reference)

### Brand Handling
- If `brand_name` provided → Get or create brand by name
- If brand not found → `brand_id = NULL`

### Category Handling
- Categories are created hierarchically (Parent → Child)
- Product is linked to the **leaf category** (last in path)
- Auto-creates categories if they don't exist

### Tax Class
- All products use default tax class: "Standard VAT (22%)"
- VAT from files is ignored in MVP

### Missing Fields
- Missing optional fields are set to `NULL` (no default values)
- Examples:
  - If `price` is missing → `price = NULL` (not 0.0)
  - If `brand` not found → `brand_id = NULL`
  - If `description` is empty → `description = NULL`

---

## Error Reasons

| Reason | Description |
|--------|-------------|
| `missing_ean` | Product has no EAN code |
| `missing_title` | Product has no title |
| `upsert_failed` | Failed to create/update product |
| `integrity_error` | Database constraint violation |
| `unexpected_error` | Unexpected exception |

---

## Examples

### Example 1: Import Effezzeta (default file)

```bash
curl -X POST "http://localhost:8000/api/import/products?source=effezzeta" \
  -H "X-API-KEY: your-api-key"
```

**Response:**
```json
{
  "source": "effezzeta",
  "total_rows": 3958,
  "created": 3450,
  "updated": 152,
  "skipped": 356,
  "errors": [
    {
      "row_number": 5,
      "reason": "missing_ean",
      "details": "Product has no EAN code"
    }
  ],
  "duration_seconds": 45.2,
  "dry_run": false,
  "timestamp": "2026-01-08T12:00:00"
}
```

---

### Example 2: Dry Run (Validate Only)

```bash
curl -X POST "http://localhost:8000/api/import/products?source=erregame&dry_run=true" \
  -H "X-API-KEY: your-api-key"
```

**Response:**
```json
{
  "source": "erregame",
  "total_rows": 1285,
  "created": 1285,
  "updated": 0,
  "skipped": 0,
  "errors": [],
  "duration_seconds": 12.5,
  "dry_run": true,
  "timestamp": "2026-01-08T12:00:00"
}
```

---

### Example 3: Import Custom File

```bash
curl -X POST "http://localhost:8000/api/import/products?source=dixe" \
  -H "X-API-KEY: your-api-key" \
  -F "file=@/path/to/custom_dixe_file.xlsx"
```

---

## Import Sequence (Recommended)

1. **First Import** - Effezzeta (largest dataset)
   ```bash
   POST /api/import/products?source=effezzeta
   ```

2. **Second Import** - Erregame (adds brands + updates overlaps)
   ```bash
   POST /api/import/products?source=erregame
   ```

3. **Third Import** - Dixe (updates stock for overlaps)
   ```bash
   POST /api/import/products?source=dixe
   ```

---

## Statistics

| Source | Total Rows | With EAN | Unique EANs | Overlaps |
|--------|-----------|----------|-------------|----------|
| Effezzeta | 3,958 | 3,602 | 3,601 | 1 with Dixe |
| Erregame | 1,285 | 1,285 | 1,285 | 759 with Dixe |
| Dixe | 1,949 | 1,949 | 1,949 | 759 with Erregame, 1 with Effezzeta |
| **Total Unique** | **6,836** | **6,836** | **6,075** | - |

---

## Performance

- **Chunk Size**: 300 rows per batch
- **Average Speed**: ~100-150 products/second
- **Expected Duration**:
  - Effezzeta: ~40-50 seconds
  - Erregame: ~10-15 seconds
  - Dixe: ~15-20 seconds

---

## Migrations Required

Before using this endpoint, run the migrations:

```bash
alembic upgrade head
```

This will apply the following migrations:

### 1. `change_ean13_to_ean`
- Renames column `ean13` → `ean`
- Changes type from `String(13)` → `String(255)`
- Updates indexes accordingly

### 2. `allow_null_price`
- Allows `NULL` values in `price_list` column
- Removes default value of `0.0`
- Enables proper handling of products without prices (e.g., Dixe)

---

## Notes

### MVP Limitations
- ❌ Images are **not imported** (deferred to phase 2)
- ❌ VAT from files is **ignored** (default 22% used)
- ❌ Discounts/Promos are **not imported**
- ❌ Product attributes/features are **not imported**
- ❌ Multi-language translations are **not created** (only Italian)

### Future Enhancements
- Support for custom tax rates per product
- Image import and processing
- Discount/promo handling
- Multi-language auto-translation
- Variant support for configurable products
- Batch import status tracking
- Import history and rollback

---

## Troubleshooting

### Issue: "File not found"
- Ensure the file exists in `app/excel/` folder
- Or provide custom file via `file` parameter

### Issue: "Unknown source"
- Valid sources: `effezzeta`, `erregame`, `dixe`, `commerce_clarity`

### Issue: Migration not applied
- Run `alembic upgrade head` before using the endpoint

### Issue: High number of errors
- Check `errors` array in response for specific row issues
- Use `dry_run=true` to validate without saving

### Issue: "integrity_error" - Duplicate reference
- This occurs when `reference` already exists in the database
- Since `reference = ean`, ensure no existing products use the same EAN as reference
- Check the `errors` array for specific row numbers and EAN values

### Issue: Products without price showing as 0.0
- After migration, products without price will show `NULL` instead of `0.0`
- This allows proper differentiation between "free" (0.0) and "no price set" (NULL)
