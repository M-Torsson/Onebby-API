"""
Check for duplicate categories via API
"""
import requests
from collections import Counter

# API Configuration
BASE_URL = "https://onebby-api.onrender.com"
API_KEY = "your-api-key-here"  # Add your API key

def check_duplicates_via_api():
    """Check for duplicates by fetching all categories from API"""
    print("=" * 80)
    print("🔍 فحص التكرارات في الكاتيجوري عبر API")
    print("=" * 80)
    
    # Fetch all categories
    print("\n📥 جاري جلب جميع الفئات من API...")
    
    try:
        # Get all categories with max limit (500 per request)
        all_categories = []
        skip = 0
        limit = 500
        
        while True:
            response = requests.get(
                f"{BASE_URL}/api/v1/categories",
                params={
                    "skip": skip,
                    "limit": limit,
                    "lang": "it",
                    "active_only": False
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ خطأ: {response.status_code}")
                print(response.text)
                return
            
            data = response.json()
            categories = data.get("data", [])
            meta = data.get("meta", {})
            total = meta.get("total", 0)
            
            all_categories.extend(categories)
            
            print(f"   📦 تم جلب {len(categories)} فئة... (المجموع: {len(all_categories)}/{total})")
            
            # Check if we have all categories
            if not meta.get("has_next", False) or len(categories) == 0:
                break
            
            skip += limit
        
        categories = all_categories
        
        print(f"✅ تم جلب {len(categories)} فئة بنجاح!")
        print("-" * 80)
        
        # Check duplicates by name
        print("\n1️⃣ التكرار بناءً على الاسم (name):")
        print("-" * 80)
        names = [cat["name"] for cat in categories if cat.get("name")]
        name_counter = Counter(names)
        duplicates_by_name = {name: count for name, count in name_counter.items() if count > 1}
        
        if duplicates_by_name:
            print(f"⚠️  وجدنا {len(duplicates_by_name)} أسماء مكررة:")
            for name, count in sorted(duplicates_by_name.items(), key=lambda x: x[1], reverse=True)[:20]:
                print(f"   • '{name}' مكرر {count} مرات")
                # Show IDs
                cats = [cat for cat in categories if cat.get("name") == name]
                ids = [cat["id"] for cat in cats]
                parent_ids = [cat.get("parent_id") for cat in cats]
                print(f"     IDs: {ids}")
                print(f"     Parent IDs: {parent_ids}")
        else:
            print("✅ لا يوجد تكرار في الأسماء")
        
        # Check duplicates by slug
        print("\n2️⃣ التكرار بناءً على الـ slug:")
        print("-" * 80)
        slugs = [cat["slug"] for cat in categories if cat.get("slug")]
        slug_counter = Counter(slugs)
        duplicates_by_slug = {slug: count for slug, count in slug_counter.items() if count > 1}
        
        if duplicates_by_slug:
            print(f"⚠️  وجدنا {len(duplicates_by_slug)} slugs مكررة:")
            for slug, count in sorted(duplicates_by_slug.items(), key=lambda x: x[1], reverse=True)[:20]:
                print(f"   • '{slug}' مكرر {count} مرات")
                # Show IDs
                cats = [cat for cat in categories if cat.get("slug") == slug]
                ids = [cat["id"] for cat in cats]
                names = [cat["name"] for cat in cats]
                print(f"     IDs: {ids}")
                print(f"     Names: {names}")
        else:
            print("✅ لا يوجد تكرار في الـ slugs")
        
        # Check duplicates by name + parent_id
        print("\n3️⃣ التكرار بناءً على (الاسم + الأب):")
        print("-" * 80)
        name_parent_pairs = [(cat["name"], cat.get("parent_id")) for cat in categories]
        pair_counter = Counter(name_parent_pairs)
        duplicates_by_pair = {pair: count for pair, count in pair_counter.items() if count > 1}
        
        if duplicates_by_pair:
            print(f"⚠️  وجدنا {len(duplicates_by_pair)} فئات بنفس الاسم تحت نفس الأب:")
            for (name, parent_id), count in sorted(duplicates_by_pair.items(), key=lambda x: x[1], reverse=True)[:20]:
                parent_text = f"Parent ID: {parent_id}" if parent_id else "بدون أب (فئة رئيسية)"
                print(f"   • '{name}' ({parent_text}) - {count} مرات")
                # Show IDs
                cats = [cat for cat in categories if cat["name"] == name and cat.get("parent_id") == parent_id]
                ids = [cat["id"] for cat in cats]
                print(f"     IDs: {ids}")
        else:
            print("✅ لا يوجد تكرار في (الاسم + الأب)")
        
        # Check main categories only
        print("\n4️⃣ الفئات الرئيسية (بدون أب):")
        print("-" * 80)
        main_categories = [cat for cat in categories if not cat.get("parent_id")]
        print(f"📊 عدد الفئات الرئيسية: {len(main_categories)}")
        
        main_names = [cat["name"] for cat in main_categories]
        main_name_counter = Counter(main_names)
        main_duplicates = {name: count for name, count in main_name_counter.items() if count > 1}
        
        if main_duplicates:
            print(f"⚠️  وجدنا {len(main_duplicates)} أسماء مكررة في الفئات الرئيسية:")
            for name, count in sorted(main_duplicates.items(), key=lambda x: x[1], reverse=True):
                print(f"   • '{name}' مكرر {count} مرات")
                cats = [cat for cat in main_categories if cat["name"] == name]
                ids = [cat["id"] for cat in cats]
                print(f"     IDs: {ids}")
        else:
            print("✅ لا يوجد تكرار في الفئات الرئيسية")
        
        # Check child categories
        print("\n5️⃣ الفئات الفرعية (لها أب):")
        print("-" * 80)
        child_categories = [cat for cat in categories if cat.get("parent_id")]
        print(f"📊 عدد الفئات الفرعية: {len(child_categories)}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 الملخص:")
        print("=" * 80)
        print(f"✓ إجمالي الفئات: {len(categories)}")
        print(f"✓ الفئات الرئيسية: {len(main_categories)}")
        print(f"✓ الفئات الفرعية: {len(child_categories)}")
        print(f"✓ أسماء مكررة: {len(duplicates_by_name)}")
        print(f"✓ Slugs مكررة: {len(duplicates_by_slug)}")
        print(f"✓ فئات مكررة (اسم + أب): {len(duplicates_by_pair)}")
        print(f"✓ فئات رئيسية مكررة: {len(main_duplicates)}")
        print("=" * 80)
        
        # Save to JSON file
        import json
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"categories_backup_from_api_{timestamp}.json"
        
        backup_data = {
            "backup_date": datetime.now().isoformat(),
            "total_categories": len(categories),
            "categories": categories,
            "meta": {
                "main_categories": len(main_categories),
                "child_categories": len(child_categories),
                "duplicates_by_name": len(duplicates_by_name),
                "duplicates_by_slug": len(duplicates_by_slug)
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ النسخة الاحتياطية في: {filename}")
        
        return categories
        
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        return []
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_duplicates_via_api()
