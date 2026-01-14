"""
Re-categorize all electronics products with correct categories
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Category mapping from keywords to new category IDs
category_map = {
    8151: ["lavatrice", "asciugatrice", "lavasciuga", "washing machine", "dryer"],  # Grandi elettrodomestici
    8152: ["incasso", "built-in", "da incasso"],  # Elettrodomestici incasso
    8153: ["tv", "televisore", "soundbar", "cuffie", "audio", "video", "speaker"],  # Audio video
    8154: ["condizionatore", "climatizzatore", "ventilatore", "stufa", "air conditioning"],  # Clima
    8155: ["frigorifero", "congelatore", "forno", "microonde", "cucina", "lavastoviglie", "fridge", "freezer", "oven", "dishwasher"],  # Elettrodomestici cucina
    8156: ["asciugacapelli", "piastra capelli", "rasoio", "epilatore", "hair", "trimmer", "shaver"],  # Cura della persona
    8157: ["computer", "notebook", "laptop", "tablet", "monitor", "stampante", "scanner", "pc"],  # Informatica
    8158: ["smartphone", "cellulare", "telefono", "mobile", "phone"],  # Telefonia
    8238: ["smartphone", "cellulare", "telefono mobile", "mobile phone"],  # Telefonia mobile
    8242: ["gps", "navigatore", "ricetrasmittente", "navigation"]  # GPS
}

print("=" * 100)
print("🔄 إعادة تصنيف المنتجات")
print("=" * 100)

# Get all products
print("\n📦 جاري تحميل جميع المنتجات...")
all_products = []
skip = 0
limit = 100

while True:
    response = requests.get(
        f"{BASE_URL}/api/v1/products",
        params={"skip": skip, "limit": limit},
        timeout=60
    )
    
    if response.status_code != 200:
        print(f"❌ فشل تحميل المنتجات: {response.status_code}")
        break
    
    data = response.json()
    products = data['data']
    total = data['meta']['total']
    
    if not products:
        break
    
    all_products.extend(products)
    skip += limit
    
    print(f"   • تم تحميل {len(all_products)}/{total}...", end='\r')
    
    if len(all_products) >= total:
        break

print(f"\n✅ تم تحميل {len(all_products)} منتج")

# Categorize products
print(f"\n{'='*100}")
print("🏷️ جاري تصنيف المنتجات...")
print(f"{'='*100}\n")

updated = 0
skipped = 0
errors = 0

for idx, product in enumerate(all_products, 1):
    product_id = product['id']
    title = product.get('title', '').lower()
    reference = product.get('reference', '').lower()
    
    # Find matching category
    matched_categories = set()
    
    for cat_id, keywords in category_map.items():
        for keyword in keywords:
            if keyword in title or keyword in reference:
                matched_categories.add(cat_id)
                break
    
    if matched_categories:
        try:
            # Update product with new categories
            response = requests.put(
                f"{BASE_URL}/api/v1/products/{product_id}",
                headers=headers,
                json={"category_ids": list(matched_categories)},
                timeout=30
            )
            
            if response.status_code == 200:
                updated += 1
                print(f"✅ [{idx}/{len(all_products)}] محدّث: {product_id} - {title[:50]}... → {matched_categories}")
            else:
                errors += 1
                print(f"❌ [{idx}/{len(all_products)}] فشل {product_id}: {response.status_code}")
        
        except Exception as e:
            errors += 1
            print(f"❌ [{idx}/{len(all_products)}] خطأ {product_id}: {e}")
    else:
        skipped += 1
        if idx % 100 == 0:
            print(f"⏭️  [{idx}/{len(all_products)}] تم تخطي منتجات غير إلكترونية...")

print(f"\n{'='*100}")
print(f"📊 النتيجة النهائية:")
print(f"   • تم تحديثها: {updated}")
print(f"   • تم تخطيها: {skipped}")
print(f"   • أخطاء: {errors}")
print("=" * 100)
