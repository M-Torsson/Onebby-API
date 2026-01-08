# Product Import - Quick Start Guide

## 📋 Prerequisites

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run migration:**
```bash
alembic upgrade head
```

This will change `ean13` → `ean` in the database.

---

## 🚀 Usage

### Method 1: Using Default Files (Recommended)

The API automatically uses files from `app/excel/` folder:

```bash
# Import Effezzeta
curl -X POST "http://localhost:8000/api/import/products?source=effezzeta" \
  -H "X-API-KEY: your-api-key"

# Import Erregame
curl -X POST "http://localhost:8000/api/import/products?source=erregame" \
  -H "X-API-KEY: your-api-key"

# Import Dixe
curl -X POST "http://localhost:8000/api/import/products?source=dixe" \
  -H "X-API-KEY: your-api-key"
```

### Method 2: Using Custom Files

```bash
curl -X POST "http://localhost:8000/api/import/products?source=effezzeta" \
  -H "X-API-KEY: your-api-key" \
  -F "file=@/path/to/your/file.xlsx"
```

### Method 3: Dry Run (Validation Only)

Test without saving to database:

```bash
curl -X POST "http://localhost:8000/api/import/products?source=effezzeta&dry_run=true" \
  -H "X-API-KEY: your-api-key"
```

---

## 📊 Expected Results

### Effezzeta (Listino-prodotti.xlsx)
- **Total Rows:** 3,958
- **With EAN:** 3,602
- **Skipped (no EAN):** 356
- **Duration:** ~40-50 seconds

### Erregame (erregame_organized.xlsx)
- **Total Rows:** 1,285
- **With EAN:** 1,285
- **Skipped:** 0
- **Duration:** ~10-15 seconds

### Dixe (Dixe_organized.xlsx)
- **Total Rows:** 1,949
- **With EAN:** 1,949
- **Skipped:** 0
- **Duration:** ~15-20 seconds

### Combined
- **Total Unique Products:** 6,075
- **Overlapping Products:** 760 (will be updated on subsequent imports)

---

## 📖 How It Works

### 1. **Upsert by EAN**
- If product with same EAN exists → **Update**
- If product doesn't exist → **Create**
- If EAN is missing → **Skip** (added to errors)

### 2. **Brand Handling**
- Automatically creates brands if they don't exist
- Uses brand name as identifier

### 3. **Category Handling**
- Creates parent → child hierarchy automatically
- Examples:
  - `"Videogiochi e Toys" → "Giochi"` (Erregame)
  - `"Climatizzazione e riscaldamento > Scaldasonno"` (Dixe - auto-parsed)

### 4. **Reference = EAN**
- Product reference is set to EAN value
- No prefixes or source identifiers

### 5. **Default Tax Class**
- All products use "Standard VAT (22%)"

---

## 🔄 Recommended Import Order

```bash
# 1. First: Effezzeta (creates most products)
POST /api/import/products?source=effezzeta

# 2. Second: Erregame (adds brands + updates overlaps)
POST /api/import/products?source=erregame

# 3. Third: Dixe (updates stock for overlaps)
POST /api/import/products?source=dixe
```

**Why this order?**
- Effezzeta has the largest dataset (3,602 unique products)
- Erregame adds brand information to 759 overlapping products with Dixe
- Dixe updates stock quantities for those overlapping products

---

## 📝 Response Example

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

## ⚠️ Important Notes

### MVP Limitations
- ❌ **Images are NOT imported** (coming in phase 2)
- ❌ **Only Italian translations** are created
- ❌ **VAT rates from files are ignored** (all use 22%)
- ❌ **Discounts/Promos are NOT imported**

### What IS Imported
- ✅ EAN (unique identifier)
- ✅ Title
- ✅ Price (when available)
- ✅ Stock quantity
- ✅ Brand (when available)
- ✅ Categories (with hierarchy)
- ✅ Description (when available, HTML preserved)

### Missing Fields
- Fields not present in source file are set to `NULL`
- No default values are used

---

## 🧪 Testing

Run the test script to validate import logic without database:

```bash
python test_import.py
```

This will show:
- Total rows read from each file
- Valid vs skipped rows
- Skip reasons
- Sample mapped data
- Chunk information

---

## 🐛 Troubleshooting

### "File not found"
Ensure files are in `app/excel/` folder:
- `Listino-prodotti.xlsx`
- `erregame_organized.xlsx`
- `Dixe_organized.xlsx`

### "Migration not applied"
Run: `alembic upgrade head`

### "openpyxl not found"
Run: `pip install -r requirements.txt`

### High number of errors
- Check the `errors` array in response
- Use `dry_run=true` to validate first

---

## 📚 Full Documentation

See [IMPORT_API.md](./IMPORT_API.md) for complete API documentation.

---

## 🎯 What's Next?

After successful import:

1. **Verify products:**
   ```bash
   GET /api/products
   ```

2. **Check brands:**
   ```bash
   GET /api/brands
   ```

3. **Check categories:**
   ```bash
   GET /api/categories
   ```

4. **Import images** (phase 2)
5. **Add multi-language translations** (phase 2)
6. **Import variants** (phase 2)
