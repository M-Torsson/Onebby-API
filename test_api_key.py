"""
Test API Key from .env file
"""
import requests
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://onebby-api.onrender.com"

print("🔑 اختبار API Key")
print("=" * 80)
print(f"API Key من .env: {API_KEY[:20]}...{API_KEY[-10:]}")
print(f"Base URL: {BASE_URL}")
print("=" * 80)

# Test 1: Health endpoint (no API key needed)
print("\n1️⃣ اختبار Health Endpoint (بدون API Key)...")
try:
    response = requests.get(f"{BASE_URL}/api/health", timeout=10)
    if response.status_code == 200:
        print(f"✅ السيرفر يعمل: {response.json()['status']}")
    else:
        print(f"❌ فشل: {response.status_code}")
except Exception as e:
    print(f"❌ خطأ: {e}")

# Test 2: Categories endpoint with API key
print("\n2️⃣ اختبار Categories Endpoint (مع API Key)...")
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/categories",
        headers={"X-API-Key": API_KEY},
        params={"limit": 5},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        count = len(data.get('data', []))
        print(f"✅ API Key صحيح! تم جلب {count} فئات")
    elif response.status_code == 403:
        print(f"❌ API Key غير صحيح أو منتهي الصلاحية")
        print(f"الرسالة: {response.json().get('detail', 'Unknown error')}")
    else:
        print(f"⚠️  HTTP {response.status_code}: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ خطأ: {e}")

# Test 3: Try without API key
print("\n3️⃣ اختبار بدون API Key (يجب أن يفشل)...")
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/categories",
        params={"limit": 5},
        timeout=10
    )
    
    if response.status_code == 403:
        print(f"✅ الحماية تعمل بشكل صحيح (رفض الوصول بدون API Key)")
    elif response.status_code == 200:
        print(f"⚠️  تحذير: الـ endpoint يعمل بدون API Key!")
    else:
        print(f"⚠️  HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ خطأ: {e}")

print("\n" + "=" * 80)
print("✅ انتهى الاختبار")
print("=" * 80)
