"""Check single product with categories"""
import requests

BASE_URL = "https://onebby-api.onrender.com"

# Check the product you mentioned
response = requests.get(f"{BASE_URL}/api/v1/products/3622", timeout=30)

if response.status_code == 200:
    product = response.json()['data']
    
    print("=" * 80)
    print("📦 منتج 3622")
    print("=" * 80)
    print(f"\nTitle: {product.get('title')}")
    print(f"Reference: {product.get('reference')}")
    print(f"\nCategories: {product.get('categories')}")
    
    if product.get('categories'):
        for cat in product['categories']:
            print(f"\n✅ فئة قديمة موجودة:")
            print(f"   ID: {cat['id']}")
            print(f"   Name: {cat['name']}")
            print(f"   Slug: {cat['slug']}")
    else:
        print("\n❌ لا توجد فئات")
else:
    print(f"❌ Error: {response.status_code}")
