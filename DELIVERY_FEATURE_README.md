# Delivery Feature Implementation

## Overview
تم إضافة ميزة الدليفري (Delivery) إلى نظام المنتجات. الآن كل منتج يمكن أن يحتوي على `delivery_id` والذي يشير إلى خيار توصيل محدد.

## التغييرات المنفذة

### 1. Models
#### ✅ Delivery Model (`app/models/delivery.py`)
- جدول `deliveries` الجديد يحتوي على:
  - `days_from` & `days_to`: وقت التوصيل المتوقع
  - `note`: ملاحظة عامة
  - `option_note`: ملاحظة الخيار
  - `is_free_delivery`: هل التوصيل مجاني
  - `is_active`: حالة التفعيل
  - علاقة many-to-many مع الفئات (Categories)

#### ✅ DeliveryTranslation Model
- جدول `delivery_translations` لدعم متعدد اللغات
- يحتوي على ترجمات الـ `note` و `option_note`

#### ✅ Product Model Update
- إضافة `delivery_id` في جدول المنتجات
- علاقة Foreign Key مع جدول `deliveries`

### 2. Schemas
#### ✅ Delivery Schemas (`app/schemas/delivery.py`)
- `DeliveryCreate`: لإنشاء خيار دليفري جديد
- `DeliveryUpdate`: لتحديث خيار دليفري
- `DeliveryResponse`: لإرجاع بيانات الدليفري الكاملة
- `DeliverySimple`: بيانات مبسطة للدليفري (للاستخدام في response المنتجات)

#### ✅ Product Schemas Update
- إضافة `delivery_id: Optional[int]` في `ProductCreate`
- إضافة `delivery_id: Optional[int]` في `ProductUpdate`
- إضافة `delivery_id: Optional[int]` في `ProductResponseFull`

### 3. CRUD Operations
#### ✅ Product CRUD Update (`app/crud/product.py`)
- التحقق من صحة `delivery_id` عند إنشاء منتج جديد
- التحقق من صحة `delivery_id` عند تحديث منتج
- إضافة `delivery_id` في عملية الإنشاء والتحديث

### 4. API Endpoints
#### ✅ Products API Update (`app/api/v1/products.py`)
- تحديث `build_product_response()` لإرجاع `delivery_id` مع كل منتج
- الآن عند جلب أي منتج، سيتم إرجاع `delivery_id` إذا كان موجوداً

### 5. Database Migration
#### ✅ Migration Script (`alembic/versions/d7e8f9g0h1i2_add_delivery_tables_and_product_delivery_id.py`)
- إنشاء جدول `deliveries`
- إنشاء جدول `delivery_translations`
- إنشاء جدول `delivery_categories` (association table)
- إضافة عمود `delivery_id` في جدول `products`

## كيفية التطبيق

### 1. تشغيل Migration
```bash
cd c:\Users\hebas\Desktop\onebby-api
alembic upgrade head
```

### 2. استخدام الميزة

#### إنشاء منتج جديد مع Delivery:
```json
{
  "product_type": "simple",
  "reference": "PRODUCT-001",
  "delivery_id": 1,
  "brand_id": 5,
  "categories": [10, 20],
  "price": {
    "list": 99.99,
    "currency": "EUR"
  },
  "stock": {
    "status": "in_stock",
    "quantity": 100
  },
  "translations": [
    {
      "lang": "it",
      "title": "Product Title"
    }
  ]
}
```

#### تحديث Delivery لمنتج موجود:
```json
{
  "delivery_id": 2
}
```

#### Response المنتج:
```json
{
  "data": {
    "id": 123,
    "reference": "PRODUCT-001",
    "delivery_id": 1,
    "brand": {...},
    "price": {...},
    ...
  }
}
```

## Notes المهمة

1. **`delivery_id` اختياري**: يمكن أن يكون `null`، أي ليس كل منتج يجب أن يحتوي على delivery
2. **Validation**: يتم التحقق من وجود الـ delivery قبل ربطه بالمنتج
3. **Cascade Delete**: عند حذف delivery، يتم تعيين `delivery_id` في المنتجات المرتبطة إلى `NULL`
4. **Multi-language Support**: الدليفري يدعم متعدد اللغات عبر جدول `delivery_translations`

## الخطوات التالية (Next Steps)

لتفعيل الميزة بالكامل، قد تحتاج إلى:

1. **إنشاء Delivery API Endpoints** (إذا أردت إدارة الدليفري من الداشبورد):
   - `POST /admin/deliveries` - إنشاء خيار دليفري جديد
   - `GET /admin/deliveries` - قائمة كل خيارات الدليفري
   - `GET /admin/deliveries/{id}` - الحصول على دليفري محدد
   - `PUT /admin/deliveries/{id}` - تحديث دليفري
   - `DELETE /admin/deliveries/{id}` - حذف دليفري

2. **إنشاء Delivery CRUD Operations** في `app/crud/delivery.py`

هل تريد مني إنشاء هذه الـ API endpoints؟
