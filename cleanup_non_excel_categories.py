"""
Clean up categories not in Excel file
Keep only categories from prezzoforte_category_tree.xlsx
"""
import pandas as pd
import requests
import time

BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

headers = {"X-API-Key": API_KEY}

print("=" * 100)
print("🧹 تنظيف الفئات غير الموجودة في Excel")
print("=" * 100)

# Read Excel
df = pd.read_excel('app/excel/prezzoforte_category_tree.xlsx')

# Get all names from Excel
excel_names = set()
excel_names.update(df['Parent'].unique())
excel_names.update(df['Child'].dropna().unique())
excel_names.update(df['Grandson'].dropna().unique())

print(f"\n📋 أسماء في Excel: {len(excel_names)}")

# Get current categories from API
response = requests.get(f"{BASE_URL}/api/v1/categories", params={"limit": 200}, timeout=30)
current_cats = response.json()['data']

print(f"📋 فئات في API: {len(current_cats)}")

# Find categories not in Excel
to_delete = []
for cat in current_cats:
    cat_name = cat['name']
    if cat_name not in excel_names:
        to_delete.append(cat)

print(f"\n🗑️  فئات للحذف: {len(to_delete)}")

if to_delete:
    print(f"\n{'='*100}")
    print("قائمة الحذف:")
    print("=" * 100)
    for cat in to_delete[:20]:
        parent_info = f" (تحت: {cat.get('parent_id', 'N/A')})" if cat.get('parent_id') else " (رئيسية)"
        print(f"  • [{cat['id']}] {cat['name']}{parent_info}")
    
    if len(to_delete) > 20:
        print(f"  ... و {len(to_delete) - 20} أخرى")
    
    print(f"\n{'='*100}")
    confirm = input(f"هل تريد حذف {len(to_delete)} فئة؟ (yes/no): ")
    
    if confirm.lower() == 'yes':
        print(f"\n🗑️  جاري الحذف...")
        deleted = 0
        failed = 0
        
        # Sort by ID descending (delete children before parents)
        to_delete_sorted = sorted(to_delete, key=lambda x: x['id'], reverse=True)
        
        for cat in to_delete_sorted:
            try:
                response = requests.delete(
                    f"{BASE_URL}/api/v1/categories/{cat['id']}?force=true",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code in [200, 204]:
                    deleted += 1
                    print(f"  ✅ {cat['name']}")
                else:
                    failed += 1
                    print(f"  ❌ {cat['name']}: {response.status_code}")
                
                time.sleep(0.1)
                
            except Exception as e:
                failed += 1
                print(f"  ❌ {cat['name']}: {e}")
        
        print(f"\n{'='*100}")
        print(f"📊 نجح: {deleted}, فشل: {failed}")
    else:
        print("تم الإلغاء")
else:
    print("\n✅ لا توجد فئات للحذف - كل شيء متطابق!")

# Final count
response = requests.get(f"{BASE_URL}/api/v1/categories", timeout=30)
final_total = response.json()['meta']['total']

print(f"\n{'='*100}")
print(f"📊 النتيجة النهائية: {final_total} فئة")
print(f"📊 المطلوب: 134 فئة")
print("=" * 100)
