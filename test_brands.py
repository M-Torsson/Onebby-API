"""
Test brands endpoint
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"

print("=" * 80)
print("🔍 اختبار Brands API")
print("=" * 80)

# Test brands endpoint
print("\n📡 GET /api/v1/brands")
try:
    response = requests.get(
        f"{BASE_URL}/api/v1/brands",
        params={"limit": 10, "active_only": True},
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        brands = data.get('data', [])
        total = data.get('meta', {}).get('total', 0)
        
        print(f"✅ نجح!")
        print(f"📊 عدد البراندات: {len(brands)}")
        print(f"📊 إجمالي: {total}")
        
        if brands:
            print(f"\n🏷️  أول 5 براندات:")
            for i, brand in enumerate(brands[:5], 1):
                print(f"   {i}. {brand.get('name')} (ID: {brand.get('id')})")
        else:
            print("\n⚠️  لا توجد براندات في قاعدة البيانات")
    else:
        print(f"❌ فشل: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ خطأ: {e}")

print("\n" + "=" * 80)
