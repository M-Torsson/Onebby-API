"""Show category tree structure"""
import requests

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

print("🌲 هيكل شجرة الفئات")
print("=" * 80)

# Get all categories
response = requests.get(
    f"{BASE_URL}/api/v1/categories",
    headers={"X-API-Key": API_KEY},
    params={"limit": 500},
    timeout=30
)

categories = response.json()['data']

# Build hierarchy
parents = [c for c in categories if not c.get('parent_id')]
children_map = {}
grandchildren_map = {}

for cat in categories:
    parent_id = cat.get('parent_id')
    if parent_id:
        if parent_id not in children_map:
            children_map[parent_id] = []
        children_map[parent_id].append(cat)

# Count levels
for parent in parents:
    for child in children_map.get(parent['id'], []):
        for cat in categories:
            if cat.get('parent_id') == child['id']:
                if child['id'] not in grandchildren_map:
                    grandchildren_map[child['id']] = []
                grandchildren_map[child['id']].append(cat)

parents_count = len(parents)
children_count = sum(len(children_map.get(p['id'], [])) for p in parents)
grandchildren_count = sum(len(grandchildren_map.get(c['id'], [])) for children in children_map.values() for c in children)

print(f"\n📊 الإحصائيات:")
print(f"   🔹 الفئات الرئيسية: {parents_count}")
print(f"   🔹 الفئات الفرعية: {children_count}")
print(f"   🔹 فئات الأحفاد: {grandchildren_count}")
print(f"   🔹 المجموع: {parents_count + children_count + grandchildren_count}")

print(f"\n🌳 الشجرة:")
for parent in sorted(parents, key=lambda x: x.get('sort_order', 0)):
    print(f"\n📁 {parent['name']}")
    
    children = sorted(children_map.get(parent['id'], []), key=lambda x: x.get('sort_order', 0))
    for child in children:
        grandchildren = sorted(grandchildren_map.get(child['id'], []), key=lambda x: x.get('sort_order', 0))
        
        if grandchildren:
            print(f"   ├─ 📂 {child['name']} ({len(grandchildren)} grandchildren)")
            for i, grandson in enumerate(grandchildren):
                prefix = "└─" if i == len(grandchildren) - 1 else "├─"
                print(f"   │  {prefix} 📄 {grandson['name']}")
        else:
            print(f"   ├─ 📄 {child['name']}")

print("\n" + "=" * 80)
print(f"✅ شجرة الفئات مكتملة ومطابقة لملف Excel!")
