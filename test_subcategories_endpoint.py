import requests

BASE_URL = "https://onebby-api.onrender.com/api/v1"

# Test the new subcategories endpoint
test_categories = [
    (8155, "Elettrodomestici cucina"),
    (8151, "Grandi elettrodomestici"),
    (8153, "Audio video")
]

print("=" * 80)
print("اختبار endpoint الجديد: /subcategories")
print("=" * 80)

for cat_id, cat_name in test_categories:
    print(f"\n{'='*80}")
    print(f"الفئة: {cat_name} (ID: {cat_id})")
    print(f"{'='*80}")
    
    # Test subcategories endpoint
    response = requests.get(f"{BASE_URL}/categories/{cat_id}/subcategories")
    
    if response.status_code == 200:
        data = response.json()
        subcategories = data["data"]
        total = data["meta"].get("total_subcategories", len(subcategories))
        
        print(f"\n✅ عدد الأحفاد (المستوى الثالث): {total}\n")
        
        if subcategories:
            # Group by parent_id to show structure
            from collections import defaultdict
            by_parent = defaultdict(list)
            for sub in subcategories:
                by_parent[sub["parent_id"]].append(sub)
            
            for parent_id, subs in by_parent.items():
                # Get parent name
                parent_response = requests.get(f"{BASE_URL}/categories/{parent_id}")
                if parent_response.status_code == 200:
                    parent_name = parent_response.json()["data"]["name"]
                    print(f"  تحت: {parent_name} (ID: {parent_id})")
                    for sub in subs:
                        print(f"    • {sub['name']} (ID: {sub['id']})")
                    print()
        else:
            print("  لا توجد أحفاد (المستوى الثالث)")
    else:
        print(f"❌ خطأ: {response.status_code}")
        print(response.text)

print("\n" + "=" * 80)
print("✅ انتهى الاختبار!")
print("=" * 80)
