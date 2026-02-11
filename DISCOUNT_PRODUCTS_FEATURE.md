# ✅ إضافة ميزة عرض المنتجات المخصومة

## 📅 التاريخ: 10 فبراير 2026

---

## 🎯 الهدف

إضافة endpoint جديد يرجع **المنتجات التي عليها خصم** من حملة تخفيض معينة، مرتبة حسب نسبة الخصم (الأعلى أولاً).

### مثال:
```
حملة: خصم 30% على كاتيغوري "التلفونات"
API يرجع: كل المنتجات في هذا الكاتيغوري مع:
  - السعر الأصلي
  - نسبة الخصم
  - المبلغ المخصوم
  - السعر النهائي
  - مرتبة حسب نسبة الخصم
```

---

## ✨ التعديلات المنفذة

### 1️⃣ Schemas ([app/schemas/discount_campaign.py](app/schemas/discount_campaign.py))

✅ **إضافة Schema جديد: `DiscountedProductItem`**
```python
class DiscountedProductItem(BaseModel):
    id: int
    reference: str
    title: str
    
    price_list: float           # السعر الأصلي
    discount_percentage: float  # نسبة الخصم (للمقارنة)
    discount_amount: float      # المبلغ المخصوم
    final_price: float          # السعر النهائي
    
    stock_status: str
    stock_quantity: int
    categories: List[int]
```

✅ **إضافة Schema: `CampaignProductsResponse`**
```python
class CampaignProductsResponse(BaseModel):
    campaign_id: int
    campaign_name: str
    total_products: int
    products: List[DiscountedProductItem]
    meta: dict
```

---

### 2️⃣ CRUD ([app/crud/discount_campaign.py](app/crud/discount_campaign.py))

✅ **إضافة Function: `get_campaign_products()`**
```python
def get_campaign_products(
    db: Session,
    campaign_id: int,
    skip: int = 0,
    limit: int = 50,
    sort_by_discount: bool = True
) -> dict:
    """Get all products with discount from campaign, sorted by discount"""
```

**الميزات:**
- جلب المنتجات من `ProductDiscount` table
- حساب نسبة الخصم تلقائياً (حتى لو fixed_amount)
- حساب السعر النهائي
- ترتيب حسب نسبة الخصم (الأعلى أولاً)
- دعم Pagination
- معلومات كاملة عن المنتج

---

### 3️⃣ API Endpoint ([app/api/v1/discounts.py](app/api/v1/discounts.py))

✅ **إضافة Endpoint جديد:**
```
GET /v1/discounts/{campaign_id}/products
```

**Query Parameters:**
- `skip`: عدد المنتجات المراد تخطيها (default: 0)
- `limit`: الحد الأقصى للمنتجات (default: 50, max: 500)
- `sort_by_discount`: ترتيب حسب الخصم (default: true)

**Headers:**
- `X-API-Key`: API key للتوثيق

**Response:**
```json
{
  "campaign": {
    "id": 1,
    "name": "خصم 30% على التلفونات",
    "discount_type": "percentage",
    "discount_value": 30,
    "target_type": "category"
  },
  "data": [
    {
      "id": 35965,
      "title": "iPhone 15 Pro Max",
      "price_list": 1299.00,
      "discount_percentage": 30.0,
      "discount_amount": 389.70,
      "final_price": 909.30,
      ...
    }
  ],
  "meta": {
    "total": 125,
    "skip": 0,
    "limit": 50,
    "page": 1,
    "total_pages": 3
  }
}
```

---

## 🧪 الاختبار

### الطريقة 1: Python Script
```bash
python test_discount_products.py
```

### الطريقة 2: cURL
```bash
curl -X GET "http://localhost:8000/v1/discounts/1/products?limit=10" \
  -H "X-API-Key: your-api-key"
```

### الطريقة 3: Postman
```
GET http://localhost:8000/v1/discounts/1/products
Headers:
  X-API-Key: your-api-key
```

---

## 📖 التوثيق

راجع ملف [DISCOUNT_PRODUCTS_API.md](DISCOUNT_PRODUCTS_API.md) للتوثيق الكامل مع أمثلة.

---

## 💡 مميزات خاصة

### ✅ حساب تلقائي لنسبة الخصم
حتى لو الخصم `fixed_amount`، يتم حساب النسبة المئوية تلقائياً:

**مثال:**
```
خصم ثابت: 50€

منتج A: سعره 200€
  → discount_percentage = 25%
  → discount_amount = 50€
  → final_price = 150€

منتج B: سعره 100€
  → discount_percentage = 50%
  → discount_amount = 50€
  → final_price = 50€
```

هذا يسهل **المقارنة** بين المنتجات!

---

### ✅ ترتيب ذكي
افتراضياً، المنتجات مرتبة حسب **نسبة الخصم** (الأعلى أولاً).

**فائدة:** يمكنك عرض "أعلى الخصومات" مباشرة في الموقع!

---

### ✅ دعم الكاتيغوريات الفرعية
إذا كان الخصم على كاتيغوري، يشمل **جميع الكاتيغوريات الفرعية** تلقائياً.

**مثال:**
```
الخصم على: "الإلكترونيات" (ID: 8151)
المنتجات من:
  - الإلكترونيات
  - التلفونات (child)
  - الأكسسوارات (grandchild)
```

---

## 🔗 الـ Endpoints الكاملة

| Method | Endpoint | الوظيفة |
|--------|----------|---------|
| POST | `/v1/discounts` | إنشاء حملة |
| GET | `/v1/discounts` | عرض جميع الحملات |
| GET | `/v1/discounts/{id}` | عرض حملة واحدة |
| PUT | `/v1/discounts/{id}` | تحديث حملة |
| DELETE | `/v1/discounts/{id}` | حذف حملة |
| POST | `/v1/discounts/{id}/apply` | تطبيق الخصم |
| POST | `/v1/discounts/{id}/remove` | إزالة الخصم |
| GET | `/v1/discounts/{id}/products` | ✨ **عرض المنتجات المخصومة** |

---

## 🎯 حالات الاستخدام

### 1. عرض "أعلى الخصومات" في الموقع
```javascript
const response = await fetch('/v1/discounts/1/products?limit=10');
// يرجع أول 10 منتجات بأعلى خصم
```

### 2. إحصائيات الحملة
```javascript
const response = await fetch('/v1/discounts/1/products');
console.log(`Total Products: ${data.meta.total}`);
console.log(`Highest Discount: ${data.data[0].discount_percentage}%`);
```

### 3. فلترة حسب نسبة الخصم
```javascript
const highDiscounts = products.filter(p => p.discount_percentage > 40);
```

---

## ✅ الخلاصة

| Item | Status |
|------|--------|
| **Schema** | ✅ `DiscountedProductItem`, `CampaignProductsResponse` |
| **CRUD** | ✅ `get_campaign_products()` |
| **API** | ✅ `GET /v1/discounts/{id}/products` |
| **Sorting** | ✅ By discount percentage (highest first) |
| **Pagination** | ✅ skip & limit |
| **Auto Calculate** | ✅ Percentage always calculated |
| **Documentation** | ✅ DISCOUNT_PRODUCTS_API.md |
| **Test Script** | ✅ test_discount_products.py |

---

## 📝 ملاحظات

- الـ endpoint يرجع فقط المنتجات **النشطة** (`is_active = true`)
- يشمل المنتجات من **الكاتيغوريات الفرعية** إذا كان الخصم على كاتيغوري
- نسبة الخصم محسوبة تلقائياً للمقارنة (حتى لو fixed_amount)
- الترتيب الافتراضي: الأعلى خصماً أولاً

🎉 **جاهز للاستخدام!**
