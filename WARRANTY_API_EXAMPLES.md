# Warranty API - Usage Examples

## Base URL
```
https://your-api-domain.com/api/v1
```

## Authentication
All endpoints require `X-API-Key` header:
```
X-API-Key: your-api-key-here
```

---

## 1. Create Warranty (POST)

### Endpoint
```
POST /admin/warranties
```

### Request Headers
```json
{
  "X-API-Key": "your-api-key-here",
  "Content-Type": "application/json"
}
```

### Request Body - Example 1 (Basic)
```json
{
  "title": "ضمان شامل لمدة سنتين",
  "subtitle": "تغطية شاملة ضد جميع الأعطال",
  "meta_description": "احمِ منتجك بضمان شامل لمدة سنتين يغطي جميع الأعطال والصيانة",
  "price": 49900,
  "image": "https://example.com/images/warranty-2years.jpg",
  "is_active": true,
  "categories": [8152, 8153, 8154],
  "translations": [
    {
      "lang": "en",
      "title": "2-Year Comprehensive Warranty",
      "subtitle": "Complete coverage against all defects",
      "meta_description": "Protect your product with a comprehensive 2-year warranty covering all defects and maintenance"
    },
    {
      "lang": "ar",
      "title": "ضمان شامل لمدة سنتين",
      "subtitle": "تغطية شاملة ضد جميع الأعطال",
      "meta_description": "احمِ منتجك بضمان شامل لمدة سنتين يغطي جميع الأعطال والصيانة"
    },
    {
      "lang": "it",
      "title": "Garanzia Completa di 2 Anni",
      "subtitle": "Copertura completa contro tutti i difetti",
      "meta_description": "Proteggi il tuo prodotto con una garanzia completa di 2 anni che copre tutti i difetti e la manutenzione"
    }
  ],
  "features": [
    {
      "key": "مدة الضمان",
      "value": "24 شهر"
    },
    {
      "key": "التغطية",
      "value": "جميع الأعطال الكهربائية والميكانيكية"
    },
    {
      "key": "الصيانة",
      "value": "صيانة مجانية في المنزل"
    },
    {
      "key": "قطع الغيار",
      "value": "قطع غيار أصلية مضمونة"
    },
    {
      "key": "خدمة العملاء",
      "value": "دعم فني على مدار 24/7"
    }
  ]
}
```

### Request Body - Example 2 (Premium Warranty)
```json
{
  "title": "ضمان بريميوم 5 سنوات",
  "subtitle": "أفضل حماية متاحة لمنتجاتك",
  "meta_description": "ضمان بريميوم حصري لمدة 5 سنوات مع خدمات إضافية وأولوية في الصيانة",
  "price": 129900,
  "image": "https://example.com/images/warranty-premium-5years.jpg",
  "is_active": true,
  "categories": [8151, 8152, 8368],
  "translations": [
    {
      "lang": "en",
      "title": "5-Year Premium Warranty",
      "subtitle": "Best protection available for your products",
      "meta_description": "Exclusive 5-year premium warranty with additional services and priority maintenance"
    },
    {
      "lang": "ar",
      "title": "ضمان بريميوم 5 سنوات",
      "subtitle": "أفضل حماية متاحة لمنتجاتك",
      "meta_description": "ضمان بريميوم حصري لمدة 5 سنوات مع خدمات إضافية وأولوية في الصيانة"
    }
  ],
  "features": [
    {
      "key": "مدة الضمان",
      "value": "60 شهر (5 سنوات)"
    },
    {
      "key": "التغطية",
      "value": "تغطية شاملة 100% لجميع الأعطال"
    },
    {
      "key": "الصيانة السريعة",
      "value": "خدمة صيانة في نفس اليوم"
    },
    {
      "key": "استبدال المنتج",
      "value": "استبدال فوري في حالة العطل الكبير"
    },
    {
      "key": "التنظيف الدوري",
      "value": "خدمة تنظيف وصيانة دورية مجانية"
    },
    {
      "key": "خدمة VIP",
      "value": "أولوية قصوى في جميع الخدمات"
    }
  ]
}
```

### Request Body - Example 3 (Electronics Warranty)
```json
{
  "title": "ضمان الأجهزة الإلكترونية",
  "subtitle": "حماية متخصصة للإلكترونيات",
  "meta_description": "ضمان مخصص للأجهزة الإلكترونية يغطي الأعطال التقنية والبرمجية",
  "price": 79900,
  "image": "https://example.com/images/warranty-electronics.jpg",
  "is_active": true,
  "categories": [8295, 8302, 8303],
  "translations": [
    {
      "lang": "en",
      "title": "Electronics Warranty",
      "subtitle": "Specialized protection for electronics",
      "meta_description": "Specialized warranty for electronic devices covering technical and software failures"
    }
  ],
  "features": [
    {
      "key": "المدة",
      "value": "3 سنوات"
    },
    {
      "key": "تغطية البرمجيات",
      "value": "إصلاح جميع المشاكل البرمجية"
    },
    {
      "key": "تغطية الهاردوير",
      "value": "استبدال القطع التالفة"
    },
    {
      "key": "حماية من السوائل",
      "value": "تغطية الأضرار الناتجة عن السوائل"
    }
  ]
}
```

### Response (Success - 201)
```json
{
  "message": "Warranty created successfully",
  "data": {
    "id": 1,
    "title": "ضمان شامل لمدة سنتين",
    "subtitle": "تغطية شاملة ضد جميع الأعطال",
    "meta_description": "احمِ منتجك بضمان شامل لمدة سنتين يغطي جميع الأعطال والصيانة",
    "price": 49900,
    "image": "https://example.com/images/warranty-2years.jpg",
    "is_active": true,
    "categories": [8152, 8153, 8154],
    "translations": [
      {
        "id": 1,
        "lang": "en",
        "title": "2-Year Comprehensive Warranty",
        "subtitle": "Complete coverage against all defects",
        "meta_description": "Protect your product..."
      },
      {
        "id": 2,
        "lang": "ar",
        "title": "ضمان شامل لمدة سنتين",
        "subtitle": "تغطية شاملة ضد جميع الأعطال",
        "meta_description": "احمِ منتجك..."
      }
    ],
    "features": [
      {
        "id": 1,
        "key": "مدة الضمان",
        "value": "24 شهر",
        "position": 1
      },
      {
        "id": 2,
        "key": "التغطية",
        "value": "جميع الأعطال الكهربائية والميكانيكية",
        "position": 2
      },
      {
        "id": 3,
        "key": "الصيانة",
        "value": "صيانة مجانية في المنزل",
        "position": 3
      }
    ],
    "created_at": "2026-02-09T10:30:00.000000Z",
    "updated_at": null
  }
}
```

---

## 2. Get All Warranties (GET)

### Endpoint
```
GET /admin/warranties?skip=0&limit=10&active_only=false
```

### Response
```json
{
  "data": [
    {
      "id": 1,
      "title": "ضمان شامل لمدة سنتين",
      "subtitle": "تغطية شاملة ضد جميع الأعطال",
      "meta_description": "احمِ منتجك بضمان شامل...",
      "price": 49900,
      "image": "https://example.com/images/warranty-2years.jpg",
      "is_active": true,
      "categories": [8152, 8153, 8154],
      "translations": [...],
      "features": [...],
      "created_at": "2026-02-09T10:30:00.000000Z",
      "updated_at": null
    }
  ],
  "meta": {
    "total": 5,
    "skip": 0,
    "limit": 10,
    "count": 5
  }
}
```

---

## 3. Get Single Warranty (GET)

### Endpoint
```
GET /admin/warranties/1
```

### Response
```json
{
  "data": {
    "id": 1,
    "title": "ضمان شامل لمدة سنتين",
    "subtitle": "تغطية شاملة ضد جميع الأعطال",
    "meta_description": "احمِ منتجك بضمان شامل لمدة سنتين يغطي جميع الأعطال والصيانة",
    "price": 49900,
    "image": "https://example.com/images/warranty-2years.jpg",
    "is_active": true,
    "categories": [8152, 8153, 8154],
    "translations": [
      {
        "id": 1,
        "lang": "en",
        "title": "2-Year Comprehensive Warranty",
        "subtitle": "Complete coverage against all defects",
        "meta_description": "Protect your product..."
      }
    ],
    "features": [
      {
        "id": 1,
        "key": "مدة الضمان",
        "value": "24 شهر",
        "position": 1
      },
      {
        "id": 2,
        "key": "التغطية",
        "value": "جميع الأعطال الكهربائية والميكانيكية",
        "position": 2
      }
    ],
    "created_at": "2026-02-09T10:30:00.000000Z",
    "updated_at": null
  }
}
```

---

## 4. Update Warranty (PUT)

### Endpoint
```
PUT /admin/warranties/1
```

### Request Body (Update Price and Features)
```json
{
  "price": 59900,
  "features": [
    {
      "key": "مدة الضمان",
      "value": "36 شهر (3 سنوات)"
    },
    {
      "key": "التغطية",
      "value": "تغطية موسعة لجميع الأعطال"
    },
    {
      "key": "خدمة إضافية",
      "value": "صيانة وقائية مجانية كل 6 أشهر"
    }
  ]
}
```

### Request Body (Update Categories Only)
```json
{
  "categories": [8151, 8152, 8153, 8154, 8155]
}
```

### Request Body (Deactivate)
```json
{
  "is_active": false
}
```

---

## 5. Delete Warranty (DELETE)

### Endpoint (Soft Delete - Deactivate)
```
DELETE /admin/warranties/1?soft_delete=true
```

### Endpoint (Permanent Delete)
```
DELETE /admin/warranties/1?soft_delete=false
```

### Response
```json
{
  "message": "Warranty deactivated successfully",
  "deleted": false
}
```

---

## Important Notes

### 1. **Price Format**
- السعر يُحفظ كـ Integer (بالسنت أو الفلس)
- مثال: 49900 = 499.00 EUR
- 129900 = 1299.00 EUR

### 2. **Categories**
- كل فئة يمكن أن تُربط بضمان واحد فقط
- إذا حاولت ربط فئة مستخدمة، ستحصل على خطأ 400

### 3. **Features Order**
- الـ Features تُرتب حسب ترتيب إدخالها (position auto-generated)
- يمكنك إضافة ميزات غير محدودة

### 4. **Translations**
- اللغات المدعومة: it, en, fr, de, ar
- الترجمات اختيارية لكن موصى بها

### 5. **Image**
- URL واحد فقط للصورة
- يجب أن يكون URL صالح

---

## Error Responses

### 400 - Bad Request
```json
{
  "detail": "The following categories are already assigned to another warranty: Category A, Category B"
}
```

### 404 - Not Found
```json
{
  "detail": "Warranty not found"
}
```

### 403 - Forbidden
```json
{
  "detail": "Invalid API Key"
}
```

---

## cURL Examples

### Create Warranty
```bash
curl -X POST "https://your-api-domain.com/api/v1/admin/warranties" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "ضمان شامل لمدة سنتين",
    "subtitle": "تغطية شاملة ضد جميع الأعطال",
    "price": 49900,
    "categories": [8152, 8153],
    "features": [
      {"key": "مدة الضمان", "value": "24 شهر"},
      {"key": "التغطية", "value": "جميع الأعطال"}
    ]
  }'
```

### Get All Warranties
```bash
curl -X GET "https://your-api-domain.com/api/v1/admin/warranties?skip=0&limit=10" \
  -H "X-API-Key: your-api-key-here"
```

### Update Warranty
```bash
curl -X PUT "https://your-api-domain.com/api/v1/admin/warranties/1" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 59900,
    "is_active": true
  }'
```

### Delete Warranty (Soft Delete)
```bash
curl -X DELETE "https://your-api-domain.com/api/v1/admin/warranties/1?soft_delete=true" \
  -H "X-API-Key: your-api-key-here"
```
