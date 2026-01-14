"""
Check electronics products and their categories
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"

electronics_keywords = [
    'lavatrice', 'frigorifero', 'forno', 'microonde', 'lavastoviglie',
    'tv', 'televisore', 'computer', 'notebook', 'laptop', 'tablet', 
    'smartphone', 'cellulare', 'telefono', 'condizionatore', 'climatizzatore',
    'aspirapolvere', 'robot', 'frullatore', 'mixer', 'tostapane',
    'macchina caffè', 'bollitore', 'ferro da stiro', 'asciugacapelli',
    'monitor', 'stampante', 'scanner', 'cuffie', 'speaker', 'soundbar'
]

print("=" * 100)
print("🔍 فحص عينة من المنتجات الإلكترونية")
print("=" * 100)

# Get products
response = requests.get(
    f"{BASE_URL}/api/v1/products",
    timeout=60
)

print(f"Response status: {response.status_code}")
if response.status_code != 200:
    print(f"Response: {response.text}")
    print(f"❌ خطأ: {response.status_code}")
    exit(1)

products = response.json()['data']
print(f"\n📦 جاري فحص {len(products)} منتج...\n")

electronics_found = []

for product in products:
    title = product.get('title', '').lower()
    reference = product.get('reference', '').lower()
    
    # Check if it's electronics
    is_electronics = any(kw in title or kw in reference for kw in electronics_keywords)
    
    if is_electronics and len(electronics_found) < 15:  # Get 15 electronics samples
        # Get full details
        detail_response = requests.get(
            f"{BASE_URL}/api/v1/products/{product['id']}",
            timeout=10
        )
        
        if detail_response.status_code == 200:
            detailed = detail_response.json()['data']
            electronics_found.append(detailed)
            
            if len(electronics_found) >= 15:
                break

if not electronics_found:
    print("❌ لم يتم العثور على منتجات إلكترونية!")
    exit(1)

print(f"✅ تم العثور على {len(electronics_found)} منتج إلكتروني\n")
print("=" * 100)

for idx, product in enumerate(electronics_found, 1):
    print(f"\n{'='*100}")
    print(f"📦 منتج {idx}: {product.get('title', 'N/A')[:60]}...")
    print(f"   🔢 Reference: {product.get('reference', 'N/A')}")
    print(f"   📊 EAN: {product.get('ean', 'N/A')}")
    
    categories = product.get('categories', [])
    if categories:
        print(f"   ✅ الفئات ({len(categories)}):")
        for cat in categories:
            parent_info = ""
            if cat.get('parent'):
                parent = cat['parent']
                if parent.get('parent'):
                    grandparent = parent['parent']
                    parent_info = f" ← {parent.get('name', 'N/A')} ← {grandparent.get('name', 'N/A')}"
                else:
                    parent_info = f" ← {parent.get('name', 'N/A')}"
            
            print(f"      • {cat.get('name', 'N/A')}{parent_info}")
    else:
        print(f"   ❌ بدون فئات!")

print("\n" + "=" * 100)
print("📊 ملخص:")
print(f"   • منتجات بفئات: {sum(1 for p in electronics_found if p.get('categories'))}")
print(f"   • منتجات بدون فئات: {sum(1 for p in electronics_found if not p.get('categories'))}")

# Collect all unique categories
all_categories = set()
for product in electronics_found:
    for cat in product.get('categories', []):
        cat_name = cat.get('name', '')
        if cat_name:
            all_categories.add(cat_name)
        if cat.get('parent'):
            parent_name = cat['parent'].get('name', '')
            if parent_name:
                all_categories.add(parent_name)
            if cat['parent'].get('parent'):
                grandparent_name = cat['parent']['parent'].get('name', '')
                if grandparent_name:
                    all_categories.add(grandparent_name)

print(f"\n🏷️ الفئات المستخدمة ({len(all_categories)}):")
for cat_name in sorted(all_categories):
    print(f"   • {cat_name}")

print("=" * 100)
