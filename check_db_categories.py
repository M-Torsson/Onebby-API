"""
Check categories with children from database directly
"""
from app.db.session import SessionLocal
from app.models.category import Category
from sqlalchemy import select

db = SessionLocal()

failed_ids = [8159, 8167, 8179, 8180, 8192, 8193, 8195, 8197, 8198]

print("=" * 100)
print("🔍 فحص الفئات من قاعدة البيانات")
print("=" * 100)

all_children_ids = []

for cat_id in failed_ids:
    category = db.query(Category).filter(Category.id == cat_id).first()
    
    if category:
        print(f"\n📂 [{cat_id}] {category.name}")
        
        # Get children
        children = db.query(Category).filter(Category.parent_id == cat_id).all()
        
        if children:
            print(f"   👶 أطفال ({len(children)}):")
            for child in children:
                all_children_ids.append(child.id)
                print(f"      • [{child.id}] {child.name}")
                
                # Check if child also has children (grandchildren)
                grandchildren = db.query(Category).filter(Category.parent_id == child.id).all()
                if grandchildren:
                    print(f"         👶👶 أحفاد ({len(grandchildren)}):")
                    for grandchild in grandchildren:
                        all_children_ids.append(grandchild.id)
                        print(f"            • [{grandchild.id}] {grandchild.name}")
        else:
            print(f"   ⚠️ لا يوجد أطفال!")
    else:
        print(f"\n❌ [{cat_id}] غير موجودة في قاعدة البيانات")

db.close()

print(f"\n{'='*100}")
print(f"📋 إجمالي الأطفال والأحفاد: {len(all_children_ids)}")
print(f"IDs: {sorted(set(all_children_ids))}")
print("=" * 100)

# Save to file
if all_children_ids:
    with open('all_children_to_delete.txt', 'w') as f:
        for child_id in sorted(set(all_children_ids)):
            f.write(f"{child_id}\n")
    print(f"✅ تم حفظ {len(set(all_children_ids))} ID في all_children_to_delete.txt")
