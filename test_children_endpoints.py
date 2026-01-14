"""
Wait for deployment and test children endpoints
"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"

print("=" * 100)
print("الانتظار 2 دقيقة حتى يكتمل الـ deployment...")
print("=" * 100)

time.sleep(120)

print("\nاختبار endpoints...")

# Test cases
test_cases = [
    (8454, "Home Cinema"),
    (8368, "Televisori"),
    (8151, "Grandi elettrodomestici"),
    (8384, "Cottura cibi"),
    (8295, "Frigoriferi da incasso"),
]

for cat_id, name in test_cases:
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/categories/{cat_id}/children",
            timeout=10
        )
        
        if response.status_code == 200:
            children = response.json()['data']
            if len(children) > 0:
                print(f"\n✅ [{cat_id}] {name}: {len(children)} أطفال")
                for child in children[:3]:
                    print(f"   • {child['name']}")
                if len(children) > 3:
                    print(f"   ... و {len(children) - 3} أخرى")
            else:
                print(f"\n⚠️  [{cat_id}] {name}: فارغ")
        else:
            print(f"\n❌ [{cat_id}] {name}: {response.status_code}")
    except Exception as e:
        print(f"\n❌ [{cat_id}] {name}: {e}")

print("\n" + "=" * 100)
