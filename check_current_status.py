"""
Check current product and category status
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"

print("=" * 80)
print("🔍 فحص الوضع الحالي للمنتجات والفئات")
print("=" * 80)

# 1. Check categories
print("\n1️⃣ الفئات:")
response = requests.get(f"{BASE_URL}/api/v1/categories", params={"limit": 500}, timeout=30)
if response.status_code == 200:
    cats = response.json()['data']
    print(f"   ✅ عدد الفئات: {len(cats)}")
    
    parents = [c for c in cats if not c.get('parent_id')]
    children = [c for c in cats if c.get('parent_id') and c['id'] not in [gc.get('parent_id') for gc in cats if gc.get('parent_id')]]
    grandchildren = [c for c in cats if c.get('parent_id') and any(gc.get('parent_id') == c['id'] for gc in cats)]
    
    print(f"   📁 رئيسية: {len(parents)}")
    print(f"   📂 فرعية: {len([c for c in cats if c.get('parent_id') and c['id'] in [gc.get('parent_id') for gc in cats]])} ")
    print(f"   📄 أحفاد: {len([c for c in cats if c.get('parent_id') and c['id'] not in [gc.get('parent_id') for gc in cats if gc.get('parent_id')]])}")

# 2. Check products
print("\n2️⃣ المنتجات:")
response = requests.get(f"{BASE_URL}/api/v1/products", params={"limit": 10, "active_only": False}, timeout=30)
if response.status_code == 200:
    data = response.json()
    products = data['data']
    total = data['meta']['total']
    
    print(f"   ✅ إجمالي المنتجات: {total}")
    
    # Check first few products for category info
    print(f"\n   🔍 فحص أول 10 منتجات:")
    with_category = 0
    without_category = 0
    
    for p in products:
        if p.get('categories'):
            with_category += 1
        else:
            without_category += 1
    
    print(f"   ✅ منتجات لها فئة: {with_category}")
    print(f"   ❌ منتجات بدون فئة: {without_category}")
    
    # Show sample
    if products:
        print(f"\n   📦 مثال على منتج:")
        first = products[0]
        print(f"      ID: {first.get('id')}")
        print(f"      Reference: {first.get('reference')}")
        print(f"      Title: {first.get('title', 'N/A')[:50]}")
        print(f"      Categories: {first.get('categories', 'N/A')}")

print("\n" + "=" * 80)
print("✅ انتهى الفحص")
print("=" * 80)
