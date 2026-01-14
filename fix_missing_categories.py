"""Fix the 2 failed categories"""
import requests
from slugify import slugify

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

def get_categories():
    """Get all categories"""
    response = requests.get(
        f"{BASE_URL}/api/v1/categories",
        headers={"X-API-Key": API_KEY},
        params={"limit": 500},
        timeout=30
    )
    return response.json()['data']

def find_category_id(categories, name):
    """Find category ID by name"""
    for cat in categories:
        if cat['name'] == name:
            return cat['id']
    return None

def create_category(name, parent_id, sort_order):
    """Create category with unique slug"""
    # Try original slug first
    slug = slugify(name)
    
    payload = {
        "name": name,
        "slug": slug,
        "parent_id": parent_id,
        "sort_order": sort_order,
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/categories",
        json=payload,
        headers={"X-API-Key": API_KEY},
        timeout=60
    )
    
    if response.status_code in [200, 201]:
        return {'success': True, 'id': response.json().get('data', {}).get('id')}
    elif 'slug already exists' in response.text:
        # Try with parent name prefix
        slug = slugify(f"{name}-cura-persona")
        payload['slug'] = slug
        response = requests.post(
            f"{BASE_URL}/api/v1/categories",
            json=payload,
            headers={"X-API-Key": API_KEY},
            timeout=60
        )
        if response.status_code in [200, 201]:
            return {'success': True, 'id': response.json().get('data', {}).get('id')}
    
    return {'success': False, 'error': response.text}

print("🔧 إصلاح الفئات المفقودة...")
print("=" * 80)

# Get all categories
categories = get_categories()

# 1. Accessori e varie (under Cura della persona)
print("\n1️⃣ إضافة: Accessori e varie (تحت Cura della persona)")
cura_id = find_category_id(categories, "Cura della persona")
if cura_id:
    result = create_category("Accessori e varie", cura_id, 61)
    if result['success']:
        print(f"   ✅ تم إنشاء الفئة بنجاح")
    else:
        print(f"   ❌ فشل: {result['error']}")
else:
    print("   ❌ لم يتم العثور على الفئة الأب")

# 2. Rete networking (under Informatica)
print("\n2️⃣ إضافة: Rete networking (تحت Informatica)")
info_id = find_category_id(categories, "Informatica")
if info_id:
    result = create_category("Rete networking", info_id, 71)
    if result['success']:
        print(f"   ✅ تم إنشاء الفئة بنجاح")
    else:
        print(f"   ❌ فشل: {result['error']}")
else:
    print("   ❌ لم يتم العثور على الفئة الأب")

print("\n" + "=" * 80)
print("✅ تم الانتهاء!")
