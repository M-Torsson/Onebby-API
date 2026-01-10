# إصلاح: Pellet Category لا يظهر على Render

## المشكلة

عند استدعاء API على Render:
```
GET https://onebby-api.onrender.com/api/v1/categories?lang=en
```

الـ category "Pellet" الذي تم إضافته من Dashboard لا يظهر في النتائج.

## السبب

هناك احتمالين:

### 1. الكود الجديد لم يتم نشره على Render بعد ❌

التغييرات التي قمنا بها موجودة على GitHub (commit `78c607a`) لكن Render لم يقم بـ auto-deploy بعد.

**الحل:**
- انتقل إلى Render Dashboard
- اذهب إلى service "onebby-api"
- اضغط "Manual Deploy" → "Deploy latest commit"
- انتظر حتى يكتمل الـ deployment (حوالي 2-3 دقائق)

### 2. الـ category "Pellet" غير موجود في قاعدة بيانات Render 🤔

قد يكون الـ category "Pellet" موجود فقط في قاعدة البيانات المحلية (localhost) وليس على Render.

## خطوات الحل

### الخطوة 1: تحقق من آخر Deploy على Render

1. اذهب إلى: https://dashboard.render.com/
2. افتح service "onebby-api"
3. تحقق من:
   - **Latest Deploy**: هل هو commit `78c607a`؟
   - **Status**: هل هو "Live"؟
   - **Deploy Date**: متى آخر deploy؟

### الخطوة 2: قم بـ Manual Deploy (إذا لزم الأمر)

إذا لم يكن آخر commit هو `78c607a`:

1. في Render Dashboard → onebby-api
2. اضغط "Manual Deploy" (زر أزرق في الأعلى)
3. اختر "Deploy latest commit"
4. انتظر حتى يظهر "Live" (🟢)

### الخطوة 3: أضف الـ category "Pellet" في قاعدة بيانات Render

بعد اكتمال الـ deploy، أضف الـ category من Dashboard أو باستخدام Postman:

```http
POST https://onebby-api.onrender.com/api/admin/categories
X-API-Key: your-api-key-here
Content-Type: application/json

{
  "name": "Pellet",
  "slug": "pellet",
  "is_active": true,
  "sort_order": 1,
  "parent_id": null
}
```

**Response المتوقع:**
```json
{
  "data": {
    "id": 123,
    "name": "Pellet",
    "slug": "pellet",
    "is_active": true,
    "has_children": false,
    "translations": [...]
  }
}
```

### الخطوة 4: تحقق من ظهور الـ category

```http
GET https://onebby-api.onrender.com/api/v1/categories?lang=en
X-API-Key: your-api-key-here
```

يجب أن ترى "Pellet" في النتائج الآن! ✅

## التحقق من Auto-Deploy

تأكد من أن Render مربوط بـ GitHub بشكل صحيح:

1. Render Dashboard → onebby-api → Settings
2. تحت "Build & Deploy":
   - **Auto-Deploy**: Yes ✅
   - **Branch**: main
   - **Deploy Hook**: (اختياري)

## ملاحظات مهمة

⚠️ **قاعدتي بيانات منفصلتين:**
- **Local** (localhost): قاعدة بيانات على جهازك
- **Render** (Production): قاعدة بيانات على السيرفر

إذا أضفت category على Local، لن يظهر على Render والعكس صحيح!

⚠️ **بعد كل push لـ GitHub:**
- انتظر 1-2 دقيقة حتى يبدأ Render الـ auto-deploy
- تابع Logs في Render Dashboard
- تأكد من أن الـ deploy نجح (Status: Live 🟢)

## استكشاف الأخطاء

### المشكلة: Category موجود في Local لكن ليس في Render

**الحل:** أضف الـ category مباشرة على Render باستخدام API:
```bash
# استخدم URL الخاص بـ Render
POST https://onebby-api.onrender.com/api/admin/categories
```

### المشكلة: Deploy فشل على Render

**الحل:**
1. افتح Logs في Render Dashboard
2. ابحث عن أخطاء (Build errors)
3. تأكد من أن `requirements.txt` محدث
4. تأكد من أن migrations تعمل بشكل صحيح

### المشكلة: API يعمل لكن لا يوجد categories

**الحل:** قد تحتاج لتشغيل migrations على Render:
```bash
# في Render Shell
alembic upgrade head
```

## الخلاصة

✅ **الكود تم رفعه على GitHub**
❓ **الكود لم يتم نشره على Render بعد** ← هذا هو السبب الأرجح!

**الحل السريع:**
1. اذهب إلى Render Dashboard
2. Manual Deploy → Deploy latest commit
3. انتظر حتى يكتمل
4. اختبر API مرة أخرى
5. إذا لم يظهر "Pellet"، أضفه من خلال API (POST request)
