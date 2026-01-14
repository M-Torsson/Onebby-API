"""
Monitor product count to detect if processing is running
"""
import requests
import time
from datetime import datetime

BASE_URL = "https://onebby-api.onrender.com"

def get_product_count():
    """Get current product count"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/products",
            params={"limit": 1},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()['meta']['total']
    except:
        pass
    return None

print("=" * 80)
print("📊 مراقبة المعالجة - كل دقيقة")
print("=" * 80)
print("💡 إذا تغير العدد = المعالجة تعمل")
print("⏹️  اضغط Ctrl+C للإيقاف")
print("=" * 80)

previous_count = get_product_count()
if previous_count:
    print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - البداية: {previous_count} منتج")
else:
    print("\n❌ فشل الاتصال بـ API")
    exit(1)

changes_detected = 0
no_change_count = 0

try:
    for i in range(15):  # Monitor for 15 minutes
        time.sleep(60)  # Wait 1 minute
        
        current_count = get_product_count()
        
        if current_count is None:
            print(f"⚠️  فشل الاتصال - المحاولة {i+1}/15")
            continue
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        change = current_count - previous_count
        
        if change != 0:
            changes_detected += 1
            no_change_count = 0
            if change < 0:
                print(f"✅ {timestamp} - {current_count} منتج (حُذف {abs(change)} منتج) 🔥")
            else:
                print(f"⚠️  {timestamp} - {current_count} منتج (زاد {change} منتج)")
        else:
            no_change_count += 1
            print(f"⏸️  {timestamp} - {current_count} منتج (بدون تغيير {no_change_count}/3)")
        
        previous_count = current_count
        
        # If no change for 3 checks, probably finished
        if no_change_count >= 3:
            print("\n" + "=" * 80)
            print("🎯 يبدو أن المعالجة انتهت!")
            print("=" * 80)
            print(f"✅ التغييرات المكتشفة: {changes_detected}")
            print(f"📊 العدد النهائي: {current_count} منتج")
            break

except KeyboardInterrupt:
    print("\n\n⏹️  تم الإيقاف من قبل المستخدم")
    print(f"📊 آخر عدد: {previous_count} منتج")
    print(f"✅ تغييرات مكتشفة: {changes_detected}")

print("\n" + "=" * 80)
print("💡 للحصول على التقرير الكامل، استخدم:")
print("   python check_final_status.py")
print("=" * 80)
