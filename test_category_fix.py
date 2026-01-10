"""
اختبار بسيط للتحقق من أن الـ categories تظهر بشكل صحيح في API
"""
import requests

# استبدل هذا بـ API key الخاص بك
API_KEY = "your-api-key-here"
BASE_URL = "http://localhost:8000"  # أو الـ URL الخاص بـ server

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_create_category():
    """اختبار إنشاء category جديد"""
    print("=== اختبار إنشاء Category ===")
    
    data = {
        "name": "Test Pellet",
        "slug": "test-pellet",
        "is_active": True,
        "sort_order": 1,
        "parent_id": None
    }
    
    response = requests.post(
        f"{BASE_URL}/admin/categories",
        json=data,
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        return response.json()["data"]["id"]
    return None


def test_get_all_categories():
    """اختبار جلب جميع الـ categories"""
    print("\n=== اختبار جلب جميع الـ Categories ===")
    
    response = requests.get(
        f"{BASE_URL}/v1/categories",
        headers=headers,
        params={"active_only": True, "lang": "it"}
    )
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Total Categories: {data['meta']['total']}")
    print(f"Categories Found: {len(data['data'])}")
    
    for cat in data['data']:
        print(f"  - ID: {cat['id']}, Name: {cat['name']}, Active: {cat['is_active']}")


def test_get_main_categories():
    """اختبار جلب الـ main categories فقط"""
    print("\n=== اختبار جلب Main Categories ===")
    
    response = requests.get(
        f"{BASE_URL}/admin/categories",
        headers=headers,
        params={"lang": "it"}
    )
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Main Categories Found: {len(data['data'])}")
    
    for cat in data['data']:
        print(f"  - ID: {cat['id']}, Name: {cat['name']}, Has Children: {cat.get('has_children', False)}")


if __name__ == "__main__":
    print("تأكد من تشغيل الـ server أولاً!")
    print("ضع API Key الصحيح في المتغير API_KEY\n")
    
    # قم بتشغيل الاختبارات
    # category_id = test_create_category()
    test_get_all_categories()
    test_get_main_categories()
