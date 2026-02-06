# حل مشكلة حملات التخفيض - Discount Campaigns Fix

## المشكلة الأساسية

عند إنشاء حملة تخفيض على فئة "Telefonia mobile" بتخفيض 12%، كان يظهر التخفيض على منتج واحد فقط بدلاً من جميع المنتجات في الفئة.

### السبب

الكود السابق في `app/crud/discount_campaign.py` كان يبحث فقط عن المنتجات المرتبطة **مباشرة** بالفئة المحددة، ولا يشمل المنتجات في **الفئات الفرعية** (subcategories).

**مثال على البنية الهرمية:**
```
📁 Telefonia mobile (ID: 8154)
   ├─ 📱 Smartphones 
   │    ├─ iPhone
   │    └─ Samsung
   ├─ 📱 Feature Phones
   └─ 📱 Accessories
```

عندما تنشئ حملة على "Telefonia mobile"، الكود القديم كان يبحث فقط في المنتجات المربوطة مباشرة بـ "Telefonia mobile"، لكن معظم المنتجات مربوطة بالفئات الفرعية مثل "Smartphones".

## الحل

تم تعديل الكود ليبحث في:
1. الفئة الأساسية (Telefonia mobile)
2. **جميع الفئات الفرعية** بشكل تلقائي

### التعديلات المنفذة

#### ملف: `app/crud/discount_campaign.py`

**تم إضافة دالة مساعدة لجلب جميع الفئات الفرعية:**
```python
def get_all_subcategory_ids(cat_id, db_session):
    """Recursively get all subcategory IDs"""
    category_ids = [cat_id]
    children = db_session.query(Category).filter(Category.parent_id == cat_id).all()
    for child in children:
        category_ids.extend(get_all_subcategory_ids(child.id, db_session))
    return category_ids
```

**تم تعديل كود البحث:**
```python
# القديم (يبحث في فئة واحدة فقط):
products = db.query(Product).join(Product.categories).filter(
    Product.categories.any(id=category_id),
    Product.is_active == True
).all()

# الجديد (يبحث في الفئة + جميع الفئات الفرعية):
all_category_ids = get_all_subcategory_ids(category_id, db)
products = db.query(Product).join(Product.categories).filter(
    Product.categories.any(Category.id.in_(all_category_ids)),
    Product.is_active == True
).all()
```

## خطوات تطبيق الإصلاح

### 1. إعادة تشغيل الـ API

بعد التعديلات، يجب إعادة تشغيل الخادم:

```bash
# إذا كنت تستخدم uvicorn
uvicorn app.main:app --reload

# أو إذا كان الخادم يعمل على Render.com
# سيتم إعادة النشر تلقائياً عند push للـ repository
```

### 2. إعادة تطبيق الحملة

استخدم API endpoint لإعادة تطبيق الحملة على جميع المنتجات:

**Endpoint:**
```
POST /api/v1/discounts/{campaign_id}/apply
```

**Headers:**
```
X-API-Key: your-api-key
```

**مثال باستخدام cURL:**
```bash
curl -X POST "https://your-api-url/api/v1/discounts/1/apply" \
  -H "X-API-Key: your-api-key"
```

**مثال باستخدام JavaScript:**
```javascript
fetch('https://your-api-url/api/v1/discounts/1/apply', {
  method: 'POST',
  headers: {
    'X-API-Key': 'your-api-key'
  }
})
.then(response => response.json())
.then(data => console.log(data))
```

### 3. التحقق من النتائج

بعد إعادة تطبيق الحملة، تحقق من المنتجات:

```
GET /api/v1/products?category=8154
```

يفترض أن ترى جميع المنتجات في "Telefonia mobile" والفئات الفرعية عليها التخفيض 12%.

## فحص الحملات

يمكنك استخدام السكريبت المرفق للفحص:

```bash
python test_campaign_fix.py
```

هذا السكريبت سيعرض:
- بنية الفئات الهرمية
- عدد المنتجات في كل فئة
- إجمالي المنتجات التي ستحصل على التخفيض

## ملاحظات مهمة

1. **تطبيق تلقائي**: الإصلاح يطبق تلقائياً على جميع الحملات المستقبلية
2. **الحملات القديمة**: الحملات الموجودة تحتاج إعادة تطبيق (re-apply)
3. **الأداء**: البحث في الفئات الفرعية قد يستغرق وقتاً أطول قليلاً للفئات ذات التفرعات الكثيرة

## API Endpoints ذات العلاقة

| Method | Endpoint | الوصف |
|--------|----------|-------|
| POST | `/api/v1/discounts` | إنشاء حملة تخفيض جديدة |
| GET | `/api/v1/discounts` | عرض جميع الحملات |
| GET | `/api/v1/discounts/{id}` | عرض تفاصيل حملة |
| PUT | `/api/v1/discounts/{id}` | تحديث حملة |
| POST | `/api/v1/discounts/{id}/apply` | **تطبيق الحملة على المنتجات** |
| POST | `/api/v1/discounts/{id}/remove` | إزالة التخفيضات من المنتجات |
| DELETE | `/api/v1/discounts/{id}` | حذف الحملة |

## مثال كامل

### 1. إنشاء حملة جديدة
```json
POST /api/v1/discounts
{
  "name": "Mobile Discount",
  "description": "12% off on all mobile phones",
  "discount_type": "percentage",
  "discount_value": 12,
  "target_type": "category",
  "target_ids": [8154],
  "start_date": "2026-02-06T00:00:00",
  "end_date": "2026-03-06T23:59:59",
  "is_active": true
}
```

### 2. تطبيق الحملة
```
POST /api/v1/discounts/1/apply
```

**Response:**
```json
{
  "campaign_id": 1,
  "campaign_name": "Mobile Discount",
  "products_updated": 250,
  "target_type": "category",
  "message": "Successfully applied discount to 250 products"
}
```

الآن جميع المنتجات في "Telefonia mobile" والفئات الفرعية (250 منتج) ستحصل على التخفيض!

## الدعم الفني

إذا واجهت أي مشاكل:
1. تحقق من أن المنتجات مربوطة بالفئات الصحيحة
2. تأكد من أن المنتجات `is_active = true`
3. راجع logs الخادم لأي أخطاء
4. استخدم `test_campaign_fix.py` لفحص البنية

---
**آخر تحديث:** 6 فبراير 2026  
**الإصدار:** 1.0
