# 🚀 Deployment Guide - Render

## 📋 Pre-Deployment Checklist

### ✅ **1. Verify All Changes Are Committed**

```bash
git status
git add .
git commit -m "feat: Add product import system with multi-source support

- Change ean13 to ean (flexible length)
- Add import endpoint with source-aware mapping
- Support for Effezzeta, Erregame, and Dixe files
- Implement upsert logic by EAN
- Add NULL support for optional fields (price, brand)
- Create migrations for schema changes
- Add comprehensive documentation"
```

### ✅ **2. Push to Repository**

```bash
git push origin main
```

---

## 🗄️ Database Migrations on Render

### **Option 1: Run Migrations via Render Shell (Recommended)**

1. **Go to Render Dashboard** → Your Web Service
2. Click **"Shell"** tab
3. Run migrations:

```bash
alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Running upgrade 993e7110da86 -> d7d76accf25b, change_ean13_to_ean
INFO  [alembic.runtime.migration] Running upgrade d7d76accf25b -> 66552411929d, allow_null_price
```

### **Option 2: Add Migration Command to Build Script**

Edit `render.yaml`:

```yaml
services:
  - type: web
    name: onebby-api
    env: python
    buildCommand: "pip install -r requirements.txt && alembic upgrade head"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

---

## 🔐 Environment Variables

Ensure these are set in Render Dashboard → Environment:

| Variable | Value | Required |
|----------|-------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ Yes |
| `API_KEY` | Your API key for imports | ✅ Yes |
| `SECRET_KEY` | JWT secret key | ✅ Yes |
| `ENVIRONMENT` | `production` | ✅ Yes |

---

## 📁 Excel Files on Render

### **Verify Files Are in Git**

```bash
git ls-files app/excel/
```

**Should show:**
```
app/excel/Dixe_organized.xlsx
app/excel/erregame_organized.xlsx
app/excel/Listino-prodotti.xlsx
```

### **If Files Not in Git:**

```bash
# Remove from .gitignore if needed
git add app/excel/*.xlsx
git commit -m "Add Excel files for import"
git push
```

---

## 🧪 Testing After Deployment

### **1. Health Check**

```bash
curl https://your-app.onrender.com/api/health
```

**Expected:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-08T13:30:00"
}
```

### **2. Test Import (Dry Run) - Smallest File**

```bash
curl -X POST "https://your-app.onrender.com/api/import/products?source=dixe&dry_run=true" \
  -H "X-API-KEY: your-actual-api-key"
```

**Expected Response:**
```json
{
  "source": "dixe",
  "total_rows": 1949,
  "created": 1949,
  "updated": 0,
  "skipped": 0,
  "errors": [],
  "duration_seconds": 15.5,
  "dry_run": true,
  "timestamp": "2026-01-08T13:30:00"
}
```

### **3. Actual Import (If Dry Run Successful)**

```bash
# Start with smallest file (Dixe)
curl -X POST "https://your-app.onrender.com/api/import/products?source=dixe" \
  -H "X-API-KEY: your-actual-api-key"
```

### **4. Verify Products Were Created**

```bash
curl "https://your-app.onrender.com/api/products?limit=10" \
  -H "X-API-KEY: your-actual-api-key"
```

---

## 📊 Full Import Sequence

Once testing is successful, run full import:

```bash
# 1. Effezzeta (largest - ~40-50 seconds)
curl -X POST "https://your-app.onrender.com/api/import/products?source=effezzeta" \
  -H "X-API-KEY: your-api-key" \
  -o effezzeta_report.json

# 2. Erregame (~10-15 seconds)
curl -X POST "https://your-app.onrender.com/api/import/products?source=erregame" \
  -H "X-API-KEY: your-api-key" \
  -o erregame_report.json

# 3. Dixe (~15-20 seconds)
curl -X POST "https://your-app.onrender.com/api/import/products?source=dixe" \
  -H "X-API-KEY: your-api-key" \
  -o dixe_report.json
```

---

## 🔍 Monitoring & Logs

### **View Logs in Real-Time**

1. **Render Dashboard** → Your Service → **"Logs"** tab
2. Watch for:
   - ✅ Migration success messages
   - ✅ Import progress logs
   - ❌ Any error messages

### **Check Import Reports**

```bash
# View saved reports
cat effezzeta_report.json | jq
cat erregame_report.json | jq
cat dixe_report.json | jq
```

---

## ⚠️ Common Issues & Solutions

### **Issue: Migration Fails**

**Error:**
```
alembic.util.exc.CommandError: Can't locate revision identified by 'd7d76accf25b'
```

**Solution:**
```bash
# Check current DB version
alembic current

# Check available migrations
alembic history

# Force upgrade
alembic upgrade head --sql  # Preview SQL first
alembic upgrade head
```

---

### **Issue: "File not found" Error**

**Error:**
```json
{
  "detail": "File not found: /opt/render/project/src/app/excel/Listino-prodotti.xlsx"
}
```

**Solution:**
```bash
# Verify files are deployed
# In Render Shell:
ls -la app/excel/

# If files missing, ensure they're in Git
git add -f app/excel/*.xlsx
git push
```

---

### **Issue: Import Times Out**

**Error:**
```
504 Gateway Timeout
```

**Solution:**
1. **Increase Render timeout** (if on paid plan)
2. **Split imports into smaller batches**:
   ```bash
   # Use dry_run to test without timeout
   curl -X POST ".../import/products?source=effezzeta&dry_run=true"
   ```
3. **Run imports during off-peak hours**

---

### **Issue: High Memory Usage**

**Symptom:** Service crashes during import

**Solution:**
1. **Reduce chunk size** in `product_import.py`:
   ```python
   CHUNK_SIZE = 200  # Reduce from 300
   ```
2. **Upgrade Render plan** for more memory
3. **Process one file at a time**

---

### **Issue: Database Connection Errors**

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
1. **Check DATABASE_URL** is correct in Render env vars
2. **Verify PostgreSQL instance** is running
3. **Check IP whitelist** (if applicable)

---

## 📈 Expected Results

After successful deployment and import:

| Metric | Expected Value |
|--------|----------------|
| **Total Products** | ~6,075 unique |
| **With Brands** | ~1,285 (from Erregame) |
| **With Prices** | ~4,887 (Effezzeta + Erregame) |
| **Categories Created** | ~50-100 |
| **Brands Created** | ~100-200 |
| **Total Import Time** | ~80-120 seconds |

---

## ✅ Post-Deployment Verification

### **1. Check Database Counts**

Via Render Shell:
```bash
python -c "
from app.db.session import SessionLocal
from app.models.product import Product
from app.models.brand import Brand
from app.models.category import Category

db = SessionLocal()
print(f'Products: {db.query(Product).count()}')
print(f'Brands: {db.query(Brand).count()}')
print(f'Categories: {db.query(Category).count()}')
print(f'Products with price: {db.query(Product).filter(Product.price_list != None).count()}')
print(f'Products without price: {db.query(Product).filter(Product.price_list == None).count()}')
"
```

### **2. Test API Endpoints**

```bash
# Get products
curl "https://your-app.onrender.com/api/products?limit=5"

# Get brands
curl "https://your-app.onrender.com/api/brands"

# Get categories
curl "https://your-app.onrender.com/api/categories"
```

### **3. Verify Data Quality**

```bash
# Check for products with NULL price (should be ~1,949 from Dixe)
curl "https://your-app.onrender.com/api/products" | jq '[.[] | select(.price == null)] | length'

# Check for products with brands
curl "https://your-app.onrender.com/api/products" | jq '[.[] | select(.brand != null)] | length'
```

---

## 🔄 Re-importing / Updating

To update products with new data:

```bash
# Re-run import (will UPDATE existing products by EAN)
curl -X POST "https://your-app.onrender.com/api/import/products?source=effezzeta" \
  -H "X-API-KEY: your-api-key"
```

**Note:** The system will:
- ✅ **Update** existing products (by EAN)
- ✅ **Create** new products (if EAN not found)
- ✅ Preserve existing data (only updates provided fields)

---

## 📞 Support

If you encounter issues:

1. **Check Render Logs** for detailed error messages
2. **Review import reports** (JSON responses)
3. **Test with `dry_run=true`** first
4. **Check database migrations** are applied
5. **Verify environment variables** are set correctly

---

## 🎉 Success Checklist

- ✅ Code pushed to repository
- ✅ Migrations applied successfully
- ✅ Environment variables configured
- ✅ Excel files available on server
- ✅ Health check endpoint working
- ✅ Dry run import successful
- ✅ Actual imports completed without errors
- ✅ Products visible via API
- ✅ Data quality verified

---

**🚀 You're ready for production!**
