"""
Test all public API endpoints
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"

def test_endpoint(name, url, params=None):
    """Test a single endpoint"""
    print(f"\n{'='*80}")
    print(f"🧪 {name}")
    print(f"{'='*80}")
    print(f"URL: {url}")
    if params:
        print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check different response formats
            if 'data' in data:
                items = data['data']
                if isinstance(items, list):
                    print(f"✅ نجح! عدد العناصر: {len(items)}")
                    if 'meta' in data:
                        print(f"📊 إجمالي: {data['meta'].get('total', 'N/A')}")
                else:
                    print(f"✅ نجح! تم جلب عنصر واحد")
            else:
                print(f"✅ نجح! Response: {str(data)[:200]}")
                
            return True
        elif response.status_code == 403:
            print(f"❌ 403 Forbidden - يحتاج API Key")
            return False
        elif response.status_code == 404:
            print(f"⚠️  404 Not Found")
            return False
        else:
            print(f"❌ {response.status_code}")
            print(f"Response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False


print("\n" + "="*80)
print("🚀 اختبار جميع الـ Public Endpoints")
print("="*80)

results = {}

# 1. Health Check
results['health'] = test_endpoint(
    "Health Check",
    f"{BASE_URL}/api/health"
)

# 2. Categories
results['categories'] = test_endpoint(
    "Categories",
    f"{BASE_URL}/api/v1/categories",
    params={"limit": 5}
)

# 3. Brands
results['brands'] = test_endpoint(
    "Brands",
    f"{BASE_URL}/api/v1/brands",
    params={"limit": 5}
)

# 4. Tax Classes
results['tax_classes'] = test_endpoint(
    "Tax Classes",
    f"{BASE_URL}/api/v1/tax-classes",
    params={"limit": 5}
)

# 5. Products
results['products'] = test_endpoint(
    "Products",
    f"{BASE_URL}/api/v1/products",
    params={"limit": 5, "active_only": False}
)

# Summary
print("\n" + "="*80)
print("📊 ملخص النتائج")
print("="*80)

for endpoint, success in results.items():
    status = "✅ يعمل" if success else "❌ لا يعمل"
    print(f"{status}  {endpoint}")

all_working = all(results.values())
if all_working:
    print("\n🎉 جميع الـ Endpoints تعمل بشكل صحيح!")
else:
    print("\n⚠️  بعض الـ Endpoints لا تعمل - راجع التفاصيل أعلاه")

print("\n" + "="*80)
print("💡 تحقق من:")
print(f"   1. Console في المتصفح (F12) لرؤية الأخطاء")
print(f"   2. Network tab لرؤية الطلبات الفعلية")
print(f"   3. CORS Headers إذا كان الطلب من domain مختلف")
print("="*80)
