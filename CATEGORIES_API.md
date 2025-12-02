# Categories API - دليل الاستخدام

## 📋 نظرة عامة

API لإدارة الفئات (Categories) مع دعم:
- فئات رئيسية (Main Categories)
- فئات فرعية (Child/Sub Categories)
- ترجمات متعددة اللغات (5 لغات: it, en, fr, de, ar)

---

## 🔐 المصادقة (Authentication)

**جميع الـ endpoints تحتاج إلى X-API-Key في الـ Header:**

```
X-API-Key: X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE
```

---

## 📍 Endpoints

### 1️⃣ إنشاء فئة جديدة (Create Category)

**POST** `/admin/categories`

#### Headers:
```
X-API-Key: X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE
Content-Type: application/json
```

#### Request Body (فئة رئيسية):
```json
{
  "name": "Elettrodomestici",
  "slug": "elettrodomestici",
  "image": "https://cdn.onebby.it/categories/elettrodomestici.jpg",
  "icon": "https://cdn.onebby.it/icons/elettrodomestici.svg",
  "sort_order": 1,
  "is_active": true,
  "parent_id": null
}
```

#### Request Body (فئة فرعية):
```json
{
  "name": "Da incasso",
  "slug": "da-incasso",
  "image": "https://cdn.onebby.it/categories/da-incasso.jpg",
  "icon": "https://cdn.onebby.it/icons/da-incasso.svg",
  "sort_order": 1,
  "is_active": true,
  "parent_id": 1
}
```

#### Response (201 Created):
```json
{
  "data": {
    "id": 11,
    "name": "Da incasso",
    "slug": "da-incasso",
    "image": "https://cdn.onebby.it/categories/da-incasso.jpg",
    "icon": "https://cdn.onebby.it/icons/da-incasso.svg",
    "sort_order": 1,
    "is_active": true,
    "parent_id": 1,
    "has_children": false,
    "translations": [
      { "lang": "it", "name": "Da incasso", "slug": "da-incasso" },
      { "lang": "en", "name": "Da incasso", "slug": "da-incasso" },
      { "lang": "fr", "name": "Da incasso", "slug": "da-incasso" },
      { "lang": "de", "name": "Da incasso", "slug": "da-incasso" },
      { "lang": "ar", "name": "Da incasso", "slug": "da-incasso" }
    ]
  }
}
```

#### ملاحظات:
- `name`: **مطلوب** - اسم الفئة
- `slug`: **اختياري** - يتم إنشاؤه تلقائياً من `name` إذا لم يتم توفيره
- `parent_id`: `null` للفئات الرئيسية، أو `id` الفئة الأم للفئات الفرعية
- `sort_order`: لترتيب الفئات في القوائم (1, 2, 3...)
- `is_active`: لإعداد الفئات قبل عرضها
- الترجمات يتم إنشاؤها تلقائياً (في الإنتاج يمكن استخدام خدمة ترجمة)

---

### 2️⃣ الحصول على الفئات الفرعية (Get Children Categories)

**GET** `/api/v1/categories/{category_id}/children?lang=it`

#### Headers:
```
X-API-Key: X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE
```

#### Parameters:
- `category_id` (path): **مطلوب** - ID الفئة الأم
- `lang` (query): **اختياري** - كود اللغة (افتراضياً: `it`)
  - الخيارات: `it`, `en`, `fr`, `de`, `ar`

#### مثال:
```
GET /api/v1/categories/1/children?lang=it
```

#### Response (200 OK):
```json
{
  "data": [
    {
      "id": 11,
      "name": "Da incasso",
      "slug": "da-incasso",
      "image": "https://cdn.onebby.it/categories/da-incasso.jpg",
      "icon": "https://cdn.onebby.it/icons/da-incasso.svg",
      "sort_order": 1,
      "is_active": true,
      "parent_id": 1,
      "has_children": false
    },
    {
      "id": 12,
      "name": "Libera installazione",
      "slug": "libera-installazione",
      "image": "https://cdn.onebby.it/categories/libera-installazione.jpg",
      "icon": "https://cdn.onebby.it/icons/libera-installazione.svg",
      "sort_order": 2,
      "is_active": true,
      "parent_id": 1,
      "has_children": false
    }
  ],
  "meta": {
    "parent_id": 1,
    "requested_lang": "it",
    "resolved_lang": "it"
  }
}
```

#### ملاحظات:
- يرجع فقط الفئات النشطة (`is_active = true`)
- مرتبة حسب `sort_order`
- الأسماء مترجمة حسب اللغة المطلوبة
- `has_children`: يوضح إذا كانت الفئة الفرعية لها فئات فرعية أخرى

---

## 🧪 اختبار الـ API

### خطوة 1: إنشاء فئة رئيسية

**POST** `https://onebby-api.onrender.com/admin/categories`

```json
{
  "name": "Elettrodomestici",
  "slug": "elettrodomestici",
  "image": "https://cdn.onebby.it/categories/elettrodomestici.jpg",
  "icon": "https://cdn.onebby.it/icons/elettrodomestici.svg",
  "sort_order": 1,
  "is_active": true,
  "parent_id": null
}
```

سيرجع `id: 1`

### خطوة 2: إنشاء فئات فرعية

**POST** `https://onebby-api.onrender.com/admin/categories`

```json
{
  "name": "Da incasso",
  "slug": "da-incasso",
  "image": "https://cdn.onebby.it/categories/da-incasso.jpg",
  "icon": "https://cdn.onebby.it/icons/da-incasso.svg",
  "sort_order": 1,
  "is_active": true,
  "parent_id": 1
}
```

```json
{
  "name": "Libera installazione",
  "slug": "libera-installazione",
  "image": "https://cdn.onebby.it/categories/libera-installazione.jpg",
  "icon": "https://cdn.onebby.it/icons/libera-installazione.svg",
  "sort_order": 2,
  "is_active": true,
  "parent_id": 1
}
```

### خطوة 3: الحصول على الفئات الفرعية

**GET** `https://onebby-api.onrender.com/api/v1/categories/1/children?lang=it`

---

## ❌ رسائل الأخطاء (Error Responses)

### 400 Bad Request - Slug موجود مسبقاً:
```json
{
  "detail": "Category with this slug already exists"
}
```

### 400 Bad Request - Parent غير موجود أو غير نشط:
```json
{
  "detail": "Parent category not found or not active"
}
```

### 401 Unauthorized - API Key مفقود أو خاطئ:
```json
{
  "detail": "Missing API Key"
}
```
أو
```json
{
  "detail": "Invalid API Key"
}
```

### 404 Not Found - Parent Category غير موجود:
```json
{
  "detail": "Parent category not found"
}
```

---

## 📁 هيكل الملفات (File Structure)

```
app/
├── models/
│   └── category.py                    # Category & CategoryTranslation models
├── schemas/
│   └── category.py                    # Pydantic schemas
├── crud/
│   └── category.py                    # CRUD operations
└── api/
    └── v1/
        └── categories.py              # API endpoints

alembic/
└── versions/
    └── 42615b91b703_create_categories_and_translations_.py  # Migration
```

---

## 🔄 التحديثات القادمة (Future Updates)

- [ ] Update category endpoint
- [ ] Delete category endpoint
- [ ] Get all categories (with pagination)
- [ ] Update translations endpoint
- [ ] Search categories
- [ ] Bulk operations

---

## 📝 ملاحظات مهمة

1. **كل endpoint يحتاج X-API-Key** للأمان
2. **Slug يجب أن يكون فريد** لكل فئة
3. **Parent category يجب أن تكون نشطة** (`is_active = true`)
4. **الترجمات تُنشأ تلقائياً** عند إنشاء فئة جديدة
5. **اللغات المدعومة**: `it`, `en`, `fr`, `de`, `ar`
6. **لا يمكن حذف فئة** إذا كان لها فئات فرعية

---

## ✅ تم التنفيذ بنجاح

جميع الـ endpoints جاهزة للاستخدام على:
- **Local**: `http://localhost:8000`
- **Production**: `https://onebby-api.onrender.com`
- **Documentation**: `/docs`
