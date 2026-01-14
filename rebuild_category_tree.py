"""
Re-import the complete electronics category tree
Based on standard electronics categories structure
"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Complete electronics category tree structure
# Parent ID: [children]
category_tree = {
    8151: {  # Grandi elettrodomestici
        "children": [
            {"name": "Lavatrici", "name_en": "Washing machines"},
            {"name": "Asciugatrici", "name_en": "Dryers"},
            {"name": "Lavasciuga", "name_en": "Washer dryers"},
            {"name": "Frigoriferi", "name_en": "Refrigerators"},
            {"name": "Congelatori orizzontali", "name_en": "Chest freezers"},
            {"name": "Congelatori verticali", "name_en": "Upright freezers"},
            {"name": "Cucine", "name_en": "Cookers"},
            {"name": "Lavastoviglie", "name_en": "Dishwashers"},
        ]
    },
    8152: {  # Elettrodomestici incasso
        "children": [
            {"name": "Frigoriferi da incasso", "name_en": "Built-in refrigerators"},
            {"name": "Congelatori da incasso", "name_en": "Built-in freezers"},
            {"name": "Lavastoviglie da incasso", "name_en": "Built-in dishwashers"},
            {"name": "Forni da incasso", "name_en": "Built-in ovens"},
            {"name": "Lavatrici da incasso", "name_en": "Built-in washing machines"},
            {"name": "Microonde da incasso", "name_en": "Built-in microwaves"},
            {"name": "Cappe cucina", "name_en": "Kitchen hoods"},
            {"name": "Piani cottura", "name_en": "Cooktops"},
            {"name": "Asciugatrici da incasso", "name_en": "Built-in dryers"},
            {"name": "Lavelli cucina", "name_en": "Kitchen sinks"},
            {"name": "Miscelatori cucina", "name_en": "Kitchen faucets"},
            {"name": "Accessori incasso", "name_en": "Built-in accessories"},
        ]
    },
    8153: {  # Audio video
        "children": [
            {"name": "TV", "name_en": "TVs"},
            {"name": "Soundbar", "name_en": "Soundbars"},
            {"name": "Cuffie", "name_en": "Headphones"},
            {"name": "Altoparlanti", "name_en": "Speakers"},
            {"name": "Home cinema", "name_en": "Home cinema"},
            {"name": "Lettori multimediali", "name_en": "Media players"},
            {"name": "Proiettori", "name_en": "Projectors"},
            {"name": "Accessori audio video", "name_en": "Audio video accessories"},
        ]
    },
    8154: {  # Clima
        "children": [
            {"name": "Condizionatori fissi", "name_en": "Fixed air conditioners"},
            {"name": "Condizionatori portatili", "name_en": "Portable air conditioners"},
            {"name": "Ventilatori", "name_en": "Fans"},
            {"name": "Stufe elettriche", "name_en": "Electric heaters"},
            {"name": "Termoventilatori", "name_en": "Fan heaters"},
            {"name": "Deumidificatori", "name_en": "Dehumidifiers"},
            {"name": "Umidificatori", "name_en": "Humidifiers"},
            {"name": "Accessori clima", "name_en": "Climate accessories"},
        ]
    },
    8155: {  # Elettrodomestici cucina
        "children": [
            {"name": "Forni microonde", "name_en": "Microwave ovens"},
            {"name": "Forni elettrici", "name_en": "Electric ovens"},
            {"name": "Macchine caffè", "name_en": "Coffee machines"},
            {"name": "Frullatori", "name_en": "Blenders"},
            {"name": "Robot da cucina", "name_en": "Food processors"},
            {"name": "Impastatrici", "name_en": "Stand mixers"},
            {"name": "Tostapane", "name_en": "Toasters"},
            {"name": "Bollitori elettrici", "name_en": "Electric kettles"},
            {"name": "Piastre elettriche", "name_en": "Electric hotplates"},
            {"name": "Friggitrici", "name_en": "Deep fryers"},
            {"name": "Affettatrici", "name_en": "Slicers"},
            {"name": "Macchine sottovuoto", "name_en": "Vacuum sealers"},
            {"name": "Caraffe filtranti", "name_en": "Filter jugs"},
            {"name": "Accessori cucina", "name_en": "Kitchen accessories"},
        ]
    },
    8156: {  # Cura della persona
        "children": [
            {"name": "Asciugacapelli", "name_en": "Hair dryers"},
            {"name": "Piastre per capelli", "name_en": "Hair straighteners"},
            {"name": "Tagliacapelli", "name_en": "Hair clippers"},
            {"name": "Rasoi elettrici", "name_en": "Electric shavers"},
            {"name": "Regolabarba", "name_en": "Beard trimmers"},
            {"name": "Epilatori", "name_en": "Epilators"},
            {"name": "Manicure e pedicure", "name_en": "Manicure and pedicure"},
            {"name": "Spazzolini elettrici", "name_en": "Electric toothbrushes"},
            {"name": "Bilance pesapersone", "name_en": "Bathroom scales"},
            {"name": "Massaggiatori", "name_en": "Massagers"},
            {"name": "Misuratori di pressione", "name_en": "Blood pressure monitors"},
            {"name": "Aerosol", "name_en": "Nebulizers"},
            {"name": "Termometri", "name_en": "Thermometers"},
            {"name": "Specchi luminosi", "name_en": "Lighted mirrors"},
            {"name": "Accessori cura persona", "name_en": "Personal care accessories"},
        ]
    },
    8157: {  # Informatica
        "children": [
            {"name": "Computer portatili", "name_en": "Laptops"},
            {"name": "Computer desktop", "name_en": "Desktop computers"},
            {"name": "Monitor", "name_en": "Monitors"},
            {"name": "Stampanti", "name_en": "Printers"},
            {"name": "Scanner", "name_en": "Scanners"},
            {"name": "Tablet", "name_en": "Tablets"},
            {"name": "Hard disk esterni", "name_en": "External hard drives"},
            {"name": "Chiavette USB", "name_en": "USB flash drives"},
            {"name": "Mouse e tastiere", "name_en": "Mice and keyboards"},
            {"name": "Webcam", "name_en": "Webcams"},
            {"name": "Router e networking", "name_en": "Routers and networking"},
            {"name": "Accessori informatica", "name_en": "Computer accessories"},
        ]
    }
}

print("=" * 100)
print("🌳 إعادة بناء شجرة الفئات الكاملة")
print("=" * 100)

total_to_create = sum(len(data["children"]) for data in category_tree.values())
print(f"\n📊 سيتم إنشاء {total_to_create} فئة فرعية\n")

created = 0
skipped = 0
errors = []

for parent_id, data in category_tree.items():
    print(f"\n📂 معالجة الفئة الأب: {parent_id}")
    
    for idx, child_data in enumerate(data["children"], 1):
        try:
            # Create child category
            payload = {
                "name": child_data["name"],
                "parent_id": parent_id,
                "is_active": True,
                "translations": {
                    "it": {"name": child_data["name"]},
                    "en": {"name": child_data["name_en"]}
                }
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/categories",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                created += 1
                result = response.json()['data']
                print(f"  ✅ [{idx}/{len(data['children'])}] {child_data['name']} (ID: {result['id']})")
            elif response.status_code == 409:
                skipped += 1
                print(f"  ⚠️  [{idx}/{len(data['children'])}] {child_data['name']} موجودة مسبقاً")
            else:
                errors.append((child_data['name'], response.status_code, response.text[:100]))
                print(f"  ❌ [{idx}/{len(data['children'])}] {child_data['name']}: {response.status_code}")
            
            time.sleep(0.1)
            
        except Exception as e:
            errors.append((child_data['name'], 'Exception', str(e)[:100]))
            print(f"  ❌ خطأ في {child_data['name']}: {e}")

print(f"\n{'='*100}")
print(f"📊 النتيجة النهائية:")
print(f"   • تم إنشاؤها: {created}")
print(f"   • موجودة مسبقاً: {skipped}")
print(f"   • أخطاء: {len(errors)}")

if errors:
    print(f"\n❌ الأخطاء:")
    for name, status, msg in errors[:10]:
        print(f"   • {name}: {status} - {msg}")

# Final check
print(f"\n{'='*100}")
print("🔍 التحقق النهائي...")
response = requests.get(f"{BASE_URL}/api/v1/categories", timeout=30)
if response.status_code == 200:
    total_cats = response.json()['meta']['total']
    print(f"✅ إجمالي الفئات الآن: {total_cats}")
else:
    print(f"❌ فشل التحقق: {response.status_code}")

print("=" * 100)
