# 🚀 دليل الإصلاح السريع - Quick Fix Guide

## ⚡ الخطوات السريعة

### 1. إعادة تطبيق الحملة الحالية

**Option A: عبر cURL**
```bash
curl -X POST "https://your-api-url/api/v1/discounts/1/apply" \
  -H "X-API-Key: your-api-key"
```

**Option B: عبر Postman / Insomnia**
```
Method: POST
URL: https://your-api-url/api/v1/discounts/1/apply
Headers:
  X-API-Key: your-api-key
```

**Option C: عبر JavaScript (في Console المتصفح)**
```javascript
fetch('https://your-api-url/api/v1/discounts/1/apply', {
  method: 'POST',
  headers: {
    'X-API-Key': 'your-api-key'
  }
})
.then(r => r.json())
.then(data => console.log('✅ تم التطبيق:', data))
```

### 2. تحقق من النتيجة

```bash
# عرض المنتجات
GET https://your-api-url/api/v1/products

# يفترض أن ترى جميع المنتجات عليها "discounts": "12%"
```

---

## 📋 Checklist

- [ ] قرأت ملف [CAMPAIGN_FIX_SUMMARY_AR.md](CAMPAIGN_FIX_SUMMARY_AR.md)
- [ ] أعدت تشغيل الـ API (إذا كان محلي)
- [ ] طبقت الحملة عبر POST /apply
- [ ] تحققت من المنتجات
- [ ] جميع المنتجات عليها التخفيض الآن ✅

---

## 🆘 المشاكل الشائعة

### لا يزال منتج واحد فقط عليه التخفيض

**السبب:** الحملة لم تُطبق بعد  
**الحل:** استدعِ endpoint `/apply`

### Error 404 عند استدعاء /apply

**السبب:** campaign_id غير صحيح  
**الحل:** تحقق من ID الحملة:
```bash
GET /api/v1/discounts
# ابحث عن campaign ID الصحيح
```

### Error 403 Forbidden

**السبب:** API Key غير صحيح  
**الحل:** تأكد من Header:
```
X-API-Key: your-correct-api-key
```

---

## 🎯 النتيجة المتوقعة

**قبل:**
```json
{
  "name": "Mobile Discount",
  "targets": "1 items"  ❌
}
```

**بعد:**
```json
{
  "campaign_id": 1,
  "campaign_name": "Mobile Discount",
  "products_updated": 250,  ✅
  "message": "Successfully applied discount to 250 products"
}
```

---

## 📞 تواصل

إذا واجهت أي مشكلة بعد تطبيق الخطوات، تحقق من:
1. Logs الخادم
2. ملف [CAMPAIGN_FIX_SUMMARY_AR.md](CAMPAIGN_FIX_SUMMARY_AR.md) للتفاصيل
3. السكريبت `test_campaign_fix.py` للفحص

---

**آخر تحديث:** 6 فبراير 2026
