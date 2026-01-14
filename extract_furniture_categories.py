"""
Script to extract furniture category names from the database
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL)

# Furniture related keywords in Italian
FURNITURE_KEYWORDS = [
    'mobili',           # furniture
    'arredamento',      # furnishing
    'divani',           # sofas
    'letti',            # beds
    'armadi',           # wardrobes
    'tavoli',           # tables
    'sedie',            # chairs
    'scaffali',         # shelves
    'librerie',         # bookcases
    'cassettiere',      # chest of drawers
    'comodini',         # nightstands
    'credenze',         # sideboards
    'scrivania',        # desk
    'poltrone',         # armchairs
    'soggiorno',        # living room
    'camera da letto',  # bedroom
    'sala da pranzo',   # dining room
    'cucina mobile',    # kitchen furniture
    'bagno mobile',     # bathroom furniture
    'ingresso mobile',  # entrance furniture
    'ufficio mobile',   # office furniture
]

def extract_furniture_categories():
    """Extract all furniture categories from database"""
    
    print("🔍 Extracting furniture categories...")
    print("=" * 80)
    
    with engine.connect() as conn:
        # Get all categories
        query = text("""
            SELECT id, name, slug, parent_id, sort_order
            FROM categories
            ORDER BY parent_id NULLS FIRST, sort_order, name
        """)
        
        result = conn.execute(query)
        all_categories = result.fetchall()
        
        # Filter furniture categories
        furniture_categories = []
        
        for cat in all_categories:
            cat_id, name, slug, parent_id, sort_order = cat
            name_lower = name.lower()
            
            # Check if category name contains furniture keywords
            is_furniture = any(keyword in name_lower for keyword in FURNITURE_KEYWORDS)
            
            if is_furniture:
                furniture_categories.append({
                    'id': cat_id,
                    'name': name,
                    'slug': slug,
                    'parent_id': parent_id,
                    'sort_order': sort_order
                })
        
        # Display results
        print(f"\n📊 Found {len(furniture_categories)} furniture categories:\n")
        
        # Group by parent
        root_categories = [c for c in furniture_categories if c['parent_id'] is None]
        child_categories = [c for c in furniture_categories if c['parent_id'] is not None]
        
        print("🏠 ROOT FURNITURE CATEGORIES:")
        print("-" * 80)
        for cat in root_categories:
            print(f"ID: {cat['id']:5} | {cat['name']}")
        
        print(f"\n📦 CHILD FURNITURE CATEGORIES ({len(child_categories)}):")
        print("-" * 80)
        for cat in sorted(child_categories, key=lambda x: (x['parent_id'], x['sort_order'])):
            print(f"ID: {cat['id']:5} | Parent: {cat['parent_id']:5} | {cat['name']}")
        
        # Save to file
        output_file = "furniture_categories_list.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("FURNITURE CATEGORIES - EXTRACTED FROM DATABASE\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("ROOT CATEGORIES:\n")
            f.write("-" * 80 + "\n")
            for cat in root_categories:
                f.write(f"ID: {cat['id']:5} | {cat['name']}\n")
            
            f.write(f"\n\nCHILD CATEGORIES ({len(child_categories)}):\n")
            f.write("-" * 80 + "\n")
            for cat in sorted(child_categories, key=lambda x: (x['parent_id'], x['sort_order'])):
                f.write(f"ID: {cat['id']:5} | Parent: {cat['parent_id']:5} | {cat['name']}\n")
            
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("CATEGORY IDs ONLY:\n")
            f.write("-" * 80 + "\n")
            for cat in furniture_categories:
                f.write(f"{cat['id']}\n")
            
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("CATEGORY NAMES ONLY:\n")
            f.write("-" * 80 + "\n")
            for cat in furniture_categories:
                f.write(f"{cat['name']}\n")
        
        print(f"\n✅ Results saved to: {output_file}")
        print(f"\n📋 Summary:")
        print(f"   - Total furniture categories: {len(furniture_categories)}")
        print(f"   - Root categories: {len(root_categories)}")
        print(f"   - Child categories: {len(child_categories)}")

if __name__ == "__main__":
    extract_furniture_categories()
