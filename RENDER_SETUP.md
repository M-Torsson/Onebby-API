# 📋 إعدادات Render - Environment Variables

## خطوات إنشاء قاعدة البيانات والإعدادات على Render:

### 1️⃣ إنشاء PostgreSQL Database:
1. اذهب إلى Render Dashboard
2. اضغط **"New +"** → **"PostgreSQL"**
3. املأ المعلومات:
   - **Name:** onebby-db
   - **Database:** onebby_db
   - **User:** onebby_user
   - **Region:** نفس region الـ Web Service
   - **Plan:** Free
4. اضغط **"Create Database"**
5. انسخ **"Internal Database URL"** (يبدأ بـ `postgresql://`)

### 2️⃣ إعدادات Web Service على Render:

بعد ربط GitHub repository، أضف هذه **Environment Variables**:

```bash
# Database (من PostgreSQL Internal URL)
DATABASE_URL=postgresql://onebby_user:xxxxx@dpg-xxxxx.frankfurt-postgres.render.com/onebby_db

# Security - Generate strong secret key
SECRET_KEY=your-super-secret-key-at-least-32-characters-long-random-string

# JWT Settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Environment
ENVIRONMENT=production
DEBUG=false

# Server (Render uses port 10000)
HOST=0.0.0.0
PORT=10000

# API
API_V1_STR=/api/v1
PROJECT_NAME=Onebby API
```

### 3️⃣ توليد SECRET_KEY قوي:

استخدم أحد هذه الطرق:

**Python:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**أو Online:**
https://generate-secret.vercel.app/32

### 4️⃣ بعد إنشاء Database و Web Service:

1. انتظر حتى ينتهي Deploy
2. شغل migrations تلقائياً (أو يدوياً من Shell):
   ```bash
   alembic upgrade head
   ```

### 5️⃣ رابط API الخاص بك سيكون:
```
https://onebby-api.onrender.com
```

### 📌 ملاحظات مهمة:
- ✅ استخدم **Internal Database URL** (أسرع وبدون رسوم)
- ✅ **لا تضع** SECRET_KEY في الكود أبداً
- ✅ DEBUG يجب أن يكون **false** في production
- ⚠️ Free tier ينام بعد 15 دقيقة من عدم الاستخدام
- ⚠️ أول طلب بعد النوم قد يأخذ 30-60 ثانية

### 🔧 للاختبار بعد Deploy:
```bash
# Health check
curl https://onebby-api.onrender.com/api/v1/health

# Docs
https://onebby-api.onrender.com/api/v1/docs
```
