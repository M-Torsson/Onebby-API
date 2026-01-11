"""
اختبار API على Render للتحقق من وجود category "Pellet"
"""
import requests
import json

# إعدادات Render
RENDER_URL = "https://onebby-api.onrender.com/api"
API_KEY = "your-api-key-here"  # ضع API key الخاص بك هنا

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_health():
    """التحقق من أن الـ API يعمل"""
    print("=" * 60)
    print("🔍 اختبار: Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False


def check_pellet_exists():
    """التحقق من وجود category "Pellet" """
    print("\n" + "=" * 60)
    print("🔍 اختبار: البحث عن Pellet Category")
    print("=" * 60)
    
    try:
        # جرب باللغة الإنجليزية
        response = requests.get(
            f"{RENDER_URL}/v1/categories",
            headers=headers,
            params={"lang": "en", "active_only": True},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total Categories: {data['meta']['total']}")
            print(f"Categories in response: {len(data['data'])}")
            
            # ابحث عن Pellet
            pellet_found = False
            for cat in data['data']:
                if 'pellet' in cat['name'].lower():
                    pellet_found = True
                    print(f"\n✅ وجدنا Pellet!")
                    print(f"   ID: {cat['id']}")
                    print(f"   Name: {cat['name']}")
                    print(f"   Slug: {cat['slug']}")
                    print(f"   Active: {cat['is_active']}")
                    print(f"   Has Children: {cat.get('has_children', False)}")
                    break
            
            if not pellet_found:
                print("\n❌ Pellet غير موجود في النتائج!")
                print("\nCategories الموجودة:")
                for cat in data['data'][:10]:  # أول 10 فقط
                    print(f"  - {cat['name']} (ID: {cat['id']})")
                
                if len(data['data']) > 10:
                    print(f"  ... و {len(data['data']) - 10} أخرى")
            
            return pellet_found
        else:
            print(f"❌ خطأ: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False


def create_pellet_on_render():
    """إنشاء category "Pellet" على Render"""
    print("\n" + "=" * 60)
    print("➕ إنشاء Pellet Category على Render")
    print("=" * 60)
    
    data = {
        "name": "Pellet",
        "slug": "pellet",
        "is_active": True,
        "sort_order": 1,
        "parent_id": None
    }
    
    try:
        response = requests.post(
            f"{RENDER_URL}/v1/categories",
            headers=headers,
            json=data,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ تم إنشاء Pellet بنجاح!")
            print(f"   ID: {result['data']['id']}")
            print(f"   Name: {result['data']['name']}")
            return True
        else:
            print(f"❌ فشل الإنشاء: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False


def check_render_deployment():
    """التحقق من إصدار الـ deployment على Render"""
    print("\n" + "=" * 60)
    print("📋 معلومات الـ Deployment")
    print("=" * 60)
    print("\nللتحقق من آخر deployment على Render:")
    print("1. اذهب إلى: https://dashboard.render.com/")
    print("2. افتح service 'onebby-api'")
    print("3. تحقق من:")
    print("   - Latest Commit: هل هو 78c607a؟")
    print("   - Status: هل هو Live (🟢)؟")
    print("   - Last Deploy: متى كان آخر deploy؟")
    print("\nإذا لم يكن آخر commit هو 78c607a:")
    print("   → اضغط 'Manual Deploy' → 'Deploy latest commit'")


def main():
    print("\n" + "🚀" * 30)
    print("اختبار onebby-api على Render")
    print("🚀" * 30)
    
    if API_KEY == "your-api-key-here":
        print("\n⚠️  تحذير: يرجى وضع API Key الصحيح في المتغير API_KEY")
        print("قم بتعديل الملف ووضع API key الخاص بك\n")
        return
    
    # 1. Health Check
    if not test_health():
        print("\n❌ الـ API لا يعمل على Render!")
        return
    
    # 2. تحقق من وجود Pellet
    pellet_exists = check_pellet_exists()
    
    # 3. إذا لم يكن موجوداً، اسأل المستخدم
    if not pellet_exists:
        print("\n" + "=" * 60)
        print("💡 الحلول المقترحة:")
        print("=" * 60)
        print("\n1. تأكد من أن آخر commit تم deploy على Render (78c607a)")
        print("2. إذا كان الـ deployment قديم، قم بـ Manual Deploy")
        print("3. بعد الـ deploy، أضف Pellet من Dashboard أو API")
        print("\nهل تريد إنشاء Pellet الآن؟ (y/n): ", end="")
        
        choice = input().strip().lower()
        if choice == 'y':
            create_pellet_on_render()
            print("\n🔄 جاري التحقق مرة أخرى...")
            check_pellet_exists()
    else:
        print("\n✅ كل شيء يعمل بشكل صحيح!")
    
    # 4. معلومات عن الـ deployment
    check_render_deployment()
    
    print("\n" + "✨" * 30)
    print("انتهى الاختبار")
    print("✨" * 30 + "\n")


if __name__ == "__main__":
    main()
