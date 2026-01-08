# 📋 API Changelog - Onebby API

## 🔄 Latest Updates (January 8, 2026)

### **Breaking Changes** ⚠️

#### 1. **EAN Field Change**
- **OLD:** `ean13` (String 13, NOT NULL)
- **NEW:** `ean` (String 255, nullable)
- **Impact:** All API responses now return `ean` instead of `ean13`
- **Migration:** Database migration applied on production

#### 2. **Reference Field**
- **Current Behavior:** `reference = ean` (automatically set to same value)
- **Reason:** Simplified data model - EAN serves as both identifier and reference
- **Recommendation:** Remove `Reference` field from frontend form (auto-populated by backend)

#### 3. **Nullable Fields**
- **price_list:** Now nullable (some products don't have prices)
- **brand_id:** Now nullable (some products don't have brands)
- **Response Change:** Frontend should handle `null` values gracefully

---

## 📊 Current API Endpoints

### **Products**
```
GET    /api/v1/products              - List all products
GET    /api/v1/products/{id}         - Get product by ID
POST   /api/v1/products              - Create product
PUT    /api/v1/products/{id}         - Update product
DELETE /api/v1/products/{id}         - Delete product
```

**Response Schema Changes:**
```javascript
// OLD
{
  "ean13": "8001234567890",  // ❌ Removed
  "reference": "PROD-001",
  "price_list": 0.0,          // ❌ Was required (default 0.0)
  "brand_id": 1               // ❌ Was required
}

// NEW
{
  "ean": "8001234567890",     // ✅ Replaces ean13
  "reference": "8001234567890", // ✅ Same as ean (auto-set)
  "price_list": null,         // ✅ Can be null
  "brand_id": null            // ✅ Can be null
}
```

### **Categories**
```
GET    /api/v1/categories?lang=it    - List categories with translations
GET    /api/v1/categories/{id}       - Get category by ID
POST   /api/v1/categories            - Create category
PUT    /api/v1/categories/{id}       - Update category
DELETE /api/v1/categories/{id}       - Delete category
```

**Known Issue:** Category endpoint may return 500 error if:
- Circular parent-child relationships exist
- Translation is missing for requested language
- Slug conflicts in database

**Current Status:** ✅ Fixed in latest deployment (slug conflicts resolved)

### **Import (New)**
```
POST   /api/import/products          - Import products from Excel
  Query Params:
    - source: effezzeta|erregame|dixe
    - dry_run: true|false (default: false)
    - verbose_errors: true|false (default: false)

GET    /api/admin/stats/products     - Get product statistics
GET    /api/import/stats            - [DEPRECATED] Use /admin/stats/products
```

### **Brands & Tax Classes**
```
GET    /api/v1/brands                - List brands
GET    /api/v1/tax-classes           - List tax classes
```

### **Health Check**
```
GET    /api/health                   - API health status
```

---

## 🔐 Authentication

**Method:** API Key (Header-based)
```
Header: X-API-KEY
Value: [Your API Key]
```

**Note:** Header name changed from `X-API-Key` to `X-API-KEY` (uppercase KEY)

---

## 🌐 CORS Settings

**Current Configuration:**
```python
allow_origins = ["*"]  # All origins allowed
allow_methods = ["*"]  # All methods allowed
allow_headers = ["*"]  # All headers allowed
```

**Status:** ✅ No CORS restrictions currently

---

## 🚨 Known Issues & Solutions

### **Issue 1: Categories 500 Error**
**Symptoms:** `GET /api/v1/categories?lang=en` returns 500
**Cause:** Slug conflicts in database (fixed in latest deployment)
**Status:** ✅ Fixed (January 8, 2026)
**Solution:** Category slugs now use parent-child hierarchy

### **Issue 2: Product Response Validation**
**Symptoms:** `Network error: NetworkError when attempting to fetch resource`
**Cause:** Frontend expects `ean13` but backend returns `ean`
**Status:** ⚠️ Requires frontend update
**Solution:** Update frontend to use `ean` instead of `ean13`

### **Issue 3: Price Null Values**
**Symptoms:** Products without prices fail validation
**Cause:** Frontend validation expects price_list to be number
**Status:** ⚠️ Requires frontend update
**Solution:** Update frontend to accept `null` for price_list

---

## 📝 Required Frontend Changes

### **1. Update Product Schema**

```typescript
// OLD
interface Product {
  ean13: string;           // ❌ Remove
  reference: string;       // Keep but don't show in form
  price_list: number;      // ❌ Change to nullable
  brand_id: number;        // ❌ Change to nullable
}

// NEW
interface Product {
  ean: string;             // ✅ Add (replaces ean13)
  reference: string;       // ✅ Auto-populated (read-only)
  price_list: number | null; // ✅ Allow null
  brand_id: number | null;   // ✅ Allow null
}
```

### **2. Update Product Form**

```jsx
// Remove Reference field (auto-populated by backend)
<FormField name="reference" /> // ❌ Remove

// Update EAN field
<FormField 
  name="ean"              // ✅ Changed from ean13
  label="EAN"
  maxLength={255}         // ✅ Changed from 13
  placeholder="8001234567890"
/>

// Update Price field
<FormField 
  name="price_list"
  type="number"
  nullable={true}         // ✅ Add nullable support
  placeholder="Leave empty if no price"
/>

// Update Brand field
<SelectField 
  name="brand_id"
  nullable={true}         // ✅ Add nullable support
  placeholder="No brand"
/>
```

### **3. Handle Null Values**

```javascript
// Display price
const displayPrice = (product) => {
  return product.price_list !== null 
    ? `€${product.price_list.toFixed(2)}` 
    : 'Price not available';
}

// Display brand
const displayBrand = (product) => {
  return product.brand?.name || 'No brand';
}
```

---

## 📊 API Rate Limiting

**Current Status:** ❌ No rate limiting configured
**Recommendation:** Consider adding rate limiting in future

---

## 🔍 Monitoring & Logs

**Render Dashboard:** https://dashboard.render.com
**Logs Access:**
1. Go to Render Dashboard
2. Select `onebby-api` service
3. Click "Logs" tab
4. View real-time logs

**API Health Check:**
```bash
curl https://onebby-api.onrender.com/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-08T12:00:00"
}
```

---

## 📚 Documentation

### **Swagger/OpenAPI**
**URL:** https://onebby-api.onrender.com/docs
**Status:** ✅ Available (auto-updated with code changes)

**Features:**
- Interactive API testing
- Request/response schemas
- Authentication testing
- Try out endpoints directly

### **ReDoc (Alternative)**
**URL:** https://onebby-api.onrender.com/redoc
**Status:** ✅ Available

---

## 🔄 Deployment Status

**Platform:** Render.com
**Status:** ✅ Stable
**Last Deployment:** January 8, 2026
**Auto-Deploy:** ✅ Enabled (on git push to main)

**Deployment Process:**
1. Push to GitHub `main` branch
2. Render auto-detects changes
3. Runs migrations: `alembic upgrade head`
4. Starts application: `uvicorn main:app`
5. Health check verification

**Deployment Time:** ~2-3 minutes

---

## 📋 Migration Summary

### **Applied Migrations:**
1. `d7d76accf25b` - Change ean13 to ean (String 255)
2. `66552411929d` - Allow NULL price_list
3. Category slug conflict fixes

### **Database Changes:**
```sql
-- 1. Rename ean13 to ean
ALTER TABLE products DROP INDEX ix_products_ean13;
ALTER TABLE products CHANGE COLUMN ean13 ean VARCHAR(255);
ALTER TABLE products ADD UNIQUE INDEX ix_products_ean (ean);

-- 2. Allow NULL price
ALTER TABLE products MODIFY COLUMN price_list FLOAT NULL;

-- 3. Category slugs (auto-handled by application)
-- No schema change, logic updated in code
```

---

## 🐛 Troubleshooting Guide

### **Error: "Network error: NetworkError"**
**Solution:**
1. Check API is running: `curl https://onebby-api.onrender.com/api/health`
2. Verify API Key header: `X-API-KEY` (uppercase)
3. Update frontend to use `ean` instead of `ean13`

### **Error: "500 Internal Server Error on Categories"**
**Solution:**
1. Check Render logs for specific error
2. Verify latest deployment is active
3. Test endpoint: `curl https://onebby-api.onrender.com/api/v1/categories?lang=it`

### **Error: "Product validation failed"**
**Solution:**
1. Allow `null` for `price_list` and `brand_id`
2. Use `ean` field instead of `ean13`
3. Don't send `reference` field (auto-populated)

---

## 📞 Communication Protocol

### **Before Breaking Changes:**
- ✅ Update this changelog
- ✅ Notify frontend team via message
- ✅ Provide migration guide
- ✅ Test in staging before production

### **Emergency Fixes:**
- ⚡ Deploy immediately
- 📢 Notify team after deployment
- 📝 Update changelog within 24h

---

## 📦 Postman Collection

**Download:** [Coming Soon]

**Quick Setup:**
1. Import collection from GitHub
2. Set environment variable: `API_KEY`
3. Test all endpoints

---

## 🎯 Upcoming Changes (Planned)

- [ ] Add pagination to products list
- [ ] Add product search by EAN
- [ ] Add bulk product update endpoint
- [ ] Add product image upload endpoint
- [ ] Add rate limiting
- [ ] Add request ID tracking

---

## 📧 Contact

**Issues:** Create issue on GitHub
**Questions:** [Your contact method]
**Urgent:** [Your urgent contact]

---

**Last Updated:** January 8, 2026
**Version:** 2.0.0
**API Base URL:** https://onebby-api.onrender.com
