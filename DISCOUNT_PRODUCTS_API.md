# 🎯 Discount Campaign Products API

## ✨ الميزة الجديدة

تم إضافة endpoint جديد يرجع **المنتجات التي عليها خصم** من حملة تخفيض معينة، مرتبة حسب نسبة الخصم (الأعلى أولاً).

---

## 📡 API Endpoint

```
GET /v1/discounts/{campaign_id}/products
```

### المعلمات (Query Parameters):

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | عدد المنتجات المراد تخطيها (pagination) |
| `limit` | int | 50 | الحد الأقصى للمنتجات في الصفحة (1-500) |
| `sort_by_discount` | bool | true | ترتيب حسب نسبة الخصم (الأعلى أولاً) |

### Headers:
```
X-API-Key: your-api-key
```

---

## 📊 Response Format

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
      "reference": "PHONE-001",
      "ean": "1234567890123",
      "title": "iPhone 15 Pro Max",
      "image": "https://example.com/iphone.jpg",
      
      "price_list": 1299.00,
      "currency": "EUR",
      
      "discount_type": "percentage",
      "discount_value": 30,
      "discount_percentage": 30.0,
      
      "discount_amount": 389.70,
      "final_price": 909.30,
      
      "is_active": true,
      "stock_status": "in_stock",
      "stock_quantity": 50,
      
      "categories": [8154, 8155]
    },
    {
      "id": 35966,
      "reference": "PHONE-002",
      "title": "Samsung Galaxy S24 Ultra",
      "price_list": 1199.00,
      "discount_percentage": 30.0,
      "discount_amount": 359.70,
      "final_price": 839.30,
      ...
    }
  ],
  "meta": {
    "total": 125,
    "skip": 0,
    "limit": 50,
    "page": 1,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## 🔍 شرح الحقول

### معلومات الحملة (campaign):
- `id` - رقم الحملة
- `name` - اسم الحملة
- `discount_type` - نوع الخصم (`percentage` أو `fixed_amount`)
- `discount_value` - قيمة الخصم (مثلاً 30 يعني 30%)
- `target_type` - نوع الهدف (`products`, `category`, `brand`, `all`)

### معلومات المنتج (data):
- `price_list` - السعر الأصلي
- `discount_percentage` - **نسبة الخصم بالمئة** (دائماً محسوبة للمقارنة)
- `discount_amount` - **المبلغ المخصوم** (كم توفر)
- `final_price` - **السعر النهائي** بعد الخصم

---

## 💡 أمثلة الاستخدام

### مثال 1: خصم 30% على كاتيغوري التلفونات

```bash
curl -X GET "http://localhost:8000/v1/discounts/1/products" \
  -H "X-API-Key: your-api-key"
```

**النتيجة:**
- يرجع كل المنتجات في كاتيغوري "التلفونات" التي عليها الخصم
- مرتبة حسب نسبة الخصم (الأعلى أولاً)
- مع السعر الأصلي والسعر بعد الخصم

---

### مثال 2: خصم ثابت 50€ على براند معين

```bash
curl -X GET "http://localhost:8000/v1/discounts/5/products?limit=20" \
  -H "X-API-Key: your-api-key"
```

**إذا كان الخصم `fixed_amount` = 50€:**
```json
{
  "data": [
    {
      "id": 100,
      "title": "Product A",
      "price_list": 200.00,
      "discount_type": "fixed_amount",
      "discount_value": 50,
      "discount_percentage": 25.0,  // محسوبة: 50/200 * 100
      "discount_amount": 50.00,
      "final_price": 150.00
    },
    {
      "id": 101,
      "title": "Product B",
      "price_list": 100.00,
      "discount_type": "fixed_amount",
      "discount_value": 50,
      "discount_percentage": 50.0,  // محسوبة: 50/100 * 100
      "discount_amount": 50.00,
      "final_price": 50.00
    }
  ]
}
```

**ملاحظة:** حتى لو كان الخصم ثابت (50€)، نسبة الخصم تختلف حسب سعر المنتج!
- منتج بـ 200€ → خصم 25%
- منتج بـ 100€ → خصم 50%

---

### مثال 3: Pagination (صفحات)

```bash
# الصفحة الأولى (50 منتج)
curl -X GET "http://localhost:8000/v1/discounts/1/products?skip=0&limit=50" \
  -H "X-API-Key: your-api-key"

# الصفحة الثانية (50 منتج التالية)
curl -X GET "http://localhost:8000/v1/discounts/1/products?skip=50&limit=50" \
  -H "X-API-Key: your-api-key"

# الصفحة الثالثة
curl -X GET "http://localhost:8000/v1/discounts/1/products?skip=100&limit=50" \
  -H "X-API-Key: your-api-key"
```

---

### مثال 4: بدون ترتيب حسب الخصم

```bash
curl -X GET "http://localhost:8000/v1/discounts/1/products?sort_by_discount=false" \
  -H "X-API-Key: your-api-key"
```

---

## 🎯 حالات الاستخدام

### 1️⃣ عرض "أعلى الخصومات" في الموقع
```javascript
// في الفرونت اند
const response = await fetch('/v1/discounts/1/products?limit=10', {
  headers: { 'X-API-Key': 'your-key' }
});

const data = await response.json();

// الآن عندك أول 10 منتجات بأعلى خصم!
data.data.forEach(product => {
  console.log(`${product.title}: خصم ${product.discount_percentage}%`);
  console.log(`السعر: ${product.final_price}€ بدلاً من ${product.price_list}€`);
});
```

### 2️⃣ إحصائيات الحملة
```javascript
const response = await fetch('/v1/discounts/1/products', {
  headers: { 'X-API-Key': 'your-key' }
});

const data = await response.json();

console.log(`الحملة: ${data.campaign.name}`);
console.log(`عدد المنتجات: ${data.meta.total}`);
console.log(`أعلى خصم: ${data.data[0].discount_percentage}%`);
```

### 3️⃣ فلترة المنتجات حسب الخصم
```javascript
// جلب المنتجات مع خصم أكثر من 40%
const response = await fetch('/v1/discounts/1/products?limit=500', {
  headers: { 'X-API-Key': 'your-key' }
});

const data = await response.json();

const highDiscounts = data.data.filter(
  product => product.discount_percentage > 40
);

console.log(`عدد المنتجات مع خصم فوق 40%: ${highDiscounts.length}`);
```

---

## 🔄 مقارنة مع Endpoints الموجودة

| Endpoint | الوظيفة |
|----------|---------|
| `POST /v1/discounts` | إنشاء حملة تخفيض جديدة |
| `GET /v1/discounts` | عرض جميع الحملات |
| `GET /v1/discounts/{id}` | عرض تفاصيل حملة واحدة |
| `PUT /v1/discounts/{id}` | تحديث حملة |
| `DELETE /v1/discounts/{id}` | حذف حملة |
| `POST /v1/discounts/{id}/apply` | **تطبيق** الخصم على المنتجات |
| `POST /v1/discounts/{id}/remove` | **إزالة** الخصم من المنتجات |
| `GET /v1/discounts/{id}/products` | ✨ **جديد**: عرض المنتجات المخصومة |

---

## 📝 ملاحظات مهمة

### ✅ الترتيب التلقائي
- افتراضياً، المنتجات مرتبة حسب **نسبة الخصم** (الأعلى أولاً)
- هذا يساعدك تعرف المنتجات الي عليها أعلى خصم بسرعة

### ✅ حساب النسبة المئوية
- حتى لو الخصم `fixed_amount`، يتم حساب النسبة المئوية تلقائياً
- هذا يسهل المقارنة بين المنتجات

### ✅ معلومات كاملة
- كل منتج يرجع مع:
  - السعر الأصلي
  - قيمة الخصم
  - السعر النهائي
  - حالة المخزون
  - الصورة
  - الكاتيغوريات

### ✅ Pagination
- استخدم `skip` و `limit` للتعامل مع حملات كبيرة
- الـ `meta` يرجع معلومات عن عدد الصفحات

---

## 🧪 اختبار الـ API

### Python:
```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "your-api-key"

# جلب المنتجات المخصومة
response = requests.get(
    f"{API_URL}/v1/discounts/1/products",
    headers={"X-API-Key": API_KEY},
    params={"limit": 20}
)

data = response.json()

print(f"Campaign: {data['campaign']['name']}")
print(f"Total Products: {data['meta']['total']}")
print("\nTop 5 Discounted Products:")

for product in data['data'][:5]:
    print(f"- {product['title']}")
    print(f"  Price: {product['price_list']}€ → {product['final_price']}€")
    print(f"  Discount: {product['discount_percentage']}%\n")
```

### Postman:
```
GET http://localhost:8000/v1/discounts/1/products?limit=20

Headers:
  X-API-Key: your-api-key
```

---

## ❓ أسئلة شائعة

**Q: هل يرجع المنتجات الغير نشطة؟**  
A: لا، يرجع فقط المنتجات `is_active = true`

**Q: هل يشمل الكاتيغوريات الفرعية؟**  
A: نعم، إذا كان الخصم على كاتيغوري، يشمل جميع الكاتيغوريات الفرعية

**Q: ماذا لو المنتج عليه أكثر من خصم؟**  
A: يرجع الخصم من هذه الحملة المحددة فقط

**Q: كيف أعرف إذا في صفحة ثانية؟**  
A: تحقق من `meta.has_next` في الـ response

---

## ✅ الخلاصة

| Feature | Status |
|---------|--------|
| **Endpoint** | ✅ `/v1/discounts/{campaign_id}/products` |
| **Sorting** | ✅ By discount percentage (highest first) |
| **Pagination** | ✅ skip & limit |
| **Discount Calculation** | ✅ Automatic |
| **Product Details** | ✅ Full info |
| **Active Products Only** | ✅ Yes |
| **Subcategories** | ✅ Included |

🎉 **الآن يمكنك بسهولة عرض المنتجات التي عليها أعلى خصم من أي حملة!**
