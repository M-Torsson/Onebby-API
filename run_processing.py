"""
Test the new processing endpoint after deployment
"""
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

print("=" * 80)
print("🚀 تشغيل معالجة المنتجات")
print("=" * 80)

# Wait for deployment
print("\n⏳ انتظار Render deployment (60 ثانية)...")
for i in range(60, 0, -10):
    print(f"   {i}...")
    time.sleep(10)

print("\n" + "=" * 80)
print("📡 تشغيل المعالجة...")
print("=" * 80)

try:
    print("\n⚠️  هذه العملية قد تستغرق عدة دقائق...")
    
    response = requests.post(
        f"{BASE_URL}/api/admin/products/process-duplicates-and-categorize",
        headers={"X-API-Key": API_KEY},
        timeout=600  # 10 minutes timeout
    )
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('success'):
            report = data.get('report', {})
            
            print("\n" + "=" * 80)
            print("✅ اكتمل بنجاح!")
            print("=" * 80)
            
            print(f"\n📦 المنتجات:")
            print(f"   • إجمالي المنتجات الأصلي: {report.get('total_products_initial', 0)}")
            print(f"   • مجموعات مكررة وجدت: {report.get('duplicates_found', 0)}")
            print(f"   • منتجات محذوفة: {report.get('duplicates_deleted', 0)}")
            print(f"   • المنتجات المتبقية: {report.get('total_products_final', 0)}")
            
            print(f"\n🔍 التصنيف:")
            print(f"   • منتجات إلكترونية: {report.get('electronics_count', 0)}")
            print(f"   • منتجات أثاث: {report.get('furniture_count', 0)}")
            
            print(f"\n✏️  التحديثات:")
            print(f"   • منتجات تم تحديثها: {report.get('electronics_updated', 0)}")
            
            errors = report.get('errors', [])
            if errors:
                print(f"\n❌ أخطاء ({len(errors)}):")
                for error in errors[:10]:
                    print(f"   • {error}")
            
            print("\n" + "=" * 80)
            print("🎉 تم بنجاح!")
            print("=" * 80)
        else:
            print(f"\n❌ فشل: {data.get('message')}")
            
    elif response.status_code == 404:
        print("\n❌ Endpoint غير موجود بعد - انتظر المزيد من الوقت للـ deployment")
    else:
        print(f"\n❌ خطأ {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("\n⏳ انتهت المهلة - العملية قد تكون مازالت تعمل في الخلفية")
    print("   تحقق من لوجات Render")
except Exception as e:
    print(f"\n❌ خطأ: {e}")

print("\n" + "=" * 80)
