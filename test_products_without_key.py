"""
Test products endpoint after removing API Key requirement
"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"

print("=" * 80)
print("🧪 اختبار Products API بدون API Key")
print("=" * 80)

# Wait for deployment
print("\n⏳ انتظار Render للـ deployment (30 ثانية)...")
for i in range(30, 0, -5):
    print(f"   {i} ثانية متبقية...")
    time.sleep(5)

print("\n" + "=" * 80)
print("📡 اختبار GET /v1/products (بدون API Key)")
print("=" * 80)

try:
    response = requests.get(
        f"{BASE_URL}/api/v1/products",
        params={
            "skip": 0,
            "limit": 10,
            "active_only": False,
            "lang": "it"
        },
        timeout=30
    )
    
    print(f"\n📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        products = data.get('data', [])
        total = data.get('total', 0)
        
        print(f"✅ نجح! تم جلب البيانات")
        print(f"📦 عدد المنتجات: {len(products)}")
        print(f"📊 إجمالي المنتجات في قاعدة البيانات: {total}")
        
        if products:
            print(f"\n🔍 أول منتج:")
            first = products[0]
            print(f"   ID: {first.get('id')}")
            print(f"   Reference: {first.get('reference')}")
            print(f"   Title: {first.get('title', 'N/A')[:50]}")
            print(f"   Type: {first.get('product_type')}")
        else:
            print("\n⚠️  لا توجد منتجات في قاعدة البيانات")
            
    elif response.status_code == 403:
        print("❌ مازال يطلب API Key - Render لم يعمل deployment بعد")
        print("   انتظر دقيقة أخرى وحاول مرة أخرى")
    else:
        print(f"⚠️  غير متوقع: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ خطأ: {e}")

print("\n" + "=" * 80)
print("✅ انتهى الاختبار")
print("=" * 80)
print("\n💡 الآن يمكنك فتح المتصفح واختبار:")
print(f"   {BASE_URL}/api/v1/products?limit=10&active_only=false")
