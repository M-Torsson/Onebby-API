"""
Check if processing completed
"""
import requests

BASE_URL = "https://onebby-api.onrender.com"

print("🔍 التحقق من عدد المنتجات...")

# Check products count
response = requests.get(
    f"{BASE_URL}/api/v1/products",
    params={"limit": 1},
    timeout=10
)

if response.status_code == 200:
    data = response.json()
    total = data['meta']['total']
    print(f"\n✅ إجمالي المنتجات حالياً: {total}")
    print(f"\n💡 المعالجة قد تكون مازالت تعمل في الخلفية")
    print(f"   انتظر 5-10 دقائق ثم تحقق مرة أخرى")
else:
    print(f"❌ خطأ: {response.status_code}")
