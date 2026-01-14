"""Check if new endpoint is deployed"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

print("🔍 التحقق من حالة الـ Deployment...")
print("=" * 80)

# Check health
try:
    response = requests.get(f"{BASE_URL}/api/health", timeout=10)
    print(f"✅ Health: {response.json()['status']}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

print("\n📡 التحقق من وجود endpoint الجديد...")

# Try the new endpoint
try:
    response = requests.post(
        f"{BASE_URL}/api/v1/categories/deactivate-all",
        headers={"X-API-Key": API_KEY},
        timeout=30
    )
    
    if response.status_code == 200:
        print("✅ Endpoint موجود! الـ deployment تم بنجاح")
        print(f"📊 النتيجة: {response.json()}")
    elif response.status_code == 404:
        print("⏳ Endpoint غير موجود بعد - Render مازال يعمل deploy...")
        print("   انتظر 2-3 دقائق ثم حاول مرة أخرى")
    else:
        print(f"⚠️  HTTP {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"❌ خطأ: {e}")

print("=" * 80)
