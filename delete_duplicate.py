"""Delete duplicate Rete networking"""
import requests

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

# Delete the duplicate with wrong slug
print("🗑️  حذف النسخة المكررة من Rete networking...")
response = requests.delete(
    f"{BASE_URL}/api/v1/categories/8286",
    headers={"X-API-Key": API_KEY},
    timeout=30
)

if response.status_code == 200:
    print("✅ تم حذف النسخة المكررة بنجاح")
else:
    print(f"❌ فشل الحذف: {response.status_code}")
    print(response.text)
