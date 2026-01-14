"""
Test admin brands endpoint after removing API Key
"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"

print("=" * 80)
print("🧪 اختبار Admin Brands بدون API Key")
print("=" * 80)

# Wait for deployment
print("\n⏳ انتظار deployment (30 ثانية)...")
for i in range(30, 0, -5):
    print(f"   {i}...")
    time.sleep(5)

print("\n" + "=" * 80)
print("📡 اختبار GET /api/admin/brands")
print("=" * 80)

try:
    response = requests.get(
        f"{BASE_URL}/api/admin/brands",
        params={"skip": 0, "limit": 10},
        timeout=30
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        brands = data.get('data', [])
        total = data.get('meta', {}).get('total', 0)
        
        print(f"✅ نجح!")
        print(f"📊 عدد البراندات: {len(brands)}")
        print(f"📊 إجمالي: {total}")
        
        if brands:
            print(f"\n🏷️  أول 3 براندات:")
            for i, brand in enumerate(brands[:3], 1):
                print(f"   {i}. {brand.get('name')} (ID: {brand.get('id')})")
        
        print("\n✅ Frontend سيعمل الآن!")
        
    elif response.status_code == 403:
        print("❌ مازال يطلب API Key")
        print("   انتظر دقيقة إضافية لـ deployment")
    else:
        print(f"⚠️  {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ خطأ: {e}")

print("\n" + "=" * 80)
