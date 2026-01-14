"""
Check specific failed categories with their children
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"

failed_ids = [8159, 8167, 8179, 8180, 8192, 8193, 8195, 8197, 8198]

print("=" * 100)
print("🔍 فحص تفاصيل الفئات الفاشلة")
print("=" * 100)

all_children = []

for cat_id in failed_ids:
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/categories/{cat_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()['data']
            print(f"\n📂 [{cat_id}] {data.get('name')}")
            
            children = data.get('children', [])
            if children:
                print(f"   👶 أطفال ({len(children)}):")
                for child in children:
                    all_children.append(child['id'])
                    print(f"      • [{child['id']}] {child.get('name')}")
            else:
                print(f"   ⚠️ لا يوجد أطفال في الـ response!")
                
        elif response.status_code == 404:
            print(f"\n⚠️ [{cat_id}] غير موجودة")
        else:
            print(f"\n❌ [{cat_id}] خطأ: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ [{cat_id}] خطأ: {e}")

print(f"\n{'='*100}")
print(f"📋 إجمالي الأطفال المكتشفة: {len(all_children)}")
if all_children:
    print(f"IDs: {all_children}")
print("=" * 100)

# Save children IDs
if all_children:
    with open('children_to_delete.txt', 'w') as f:
        for child_id in all_children:
            f.write(f"{child_id}\n")
    print(f"✅ تم حفظ IDs في children_to_delete.txt")
