import pandas as pd
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

# Read the Excel file
excel_file = r"F:\onebby-api\app\excel\commerceclarity.xlsx"
print(f"📖 Reading Excel file: {excel_file}")
print("=" * 80)

try:
    # Try to read the file - check all sheets
    xls = pd.ExcelFile(excel_file)
    print(f"📋 Sheets found in file: {xls.sheet_names}\n")
    
    # Read all sheets
    all_products = []
    for sheet_name in xls.sheet_names:
        print(f"\n{'='*80}")
        print(f"📄 Processing sheet: {sheet_name}")
        print(f"{'='*80}")
        
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        print(f"Total rows in sheet: {len(df)}")
        print(f"Columns: {list(df.columns)}\n")
        
        # Show first few rows
        print("First 5 rows:")
        print(df.head())
        
        # Try to identify SKU/product identifier column
        possible_sku_columns = ['SKU', 'sku', 'Codice', 'codice', 'Code', 'code', 
                               'Product Code', 'product_code', 'EAN', 'ean',
                               'Codice Prodotto', 'codice_prodotto']
        
        sku_column = None
        for col in df.columns:
            if col in possible_sku_columns or 'sku' in col.lower() or 'codice' in col.lower() or 'code' in col.lower():
                sku_column = col
                break
        
        if sku_column:
            print(f"\n✅ Found SKU column: {sku_column}")
            skus = df[sku_column].dropna().tolist()
            print(f"Total SKUs in this sheet: {len(skus)}")
            
            # Add to all products list
            for sku in skus:
                all_products.append({
                    'sheet': sheet_name,
                    'sku': str(sku).strip()
                })
        else:
            print(f"\n⚠️  Could not identify SKU column in sheet: {sheet_name}")
            print("Please check the column names above.")
    
    if not all_products:
        print("\n❌ No products found in any sheet!")
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"📊 TOTAL PRODUCTS TO CHECK: {len(all_products)}")
    print(f"{'='*80}\n")
    
    # Check each product in database
    found_count = 0
    not_found_count = 0
    not_found_products = []
    
    with engine.connect() as conn:
        for idx, product in enumerate(all_products, 1):
            sku = product['sku']
            sheet = product['sheet']
            
            # Check in database by reference or ean
            result = conn.execute(
                text("SELECT id, reference, ean FROM products WHERE reference = :sku OR ean = :sku"),
                {"sku": sku}
            ).fetchone()
            
            if result:
                found_count += 1
                if idx <= 10:  # Show first 10 found
                    print(f"✅ [{idx}/{len(all_products)}] Found: SKU={sku} | ID={result[0]} | Reference={result[1]} | EAN={result[2]}")
            else:
                not_found_count += 1
                not_found_products.append(product)
                print(f"❌ [{idx}/{len(all_products)}] NOT FOUND: SKU={sku} (from sheet: {sheet})")
    
    # Final summary
    print(f"\n{'='*80}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*80}")
    print(f"✅ Products FOUND in database: {found_count}")
    print(f"❌ Products NOT FOUND in database: {not_found_count}")
    print(f"📈 Total products checked: {len(all_products)}")
    print(f"📊 Success rate: {(found_count/len(all_products)*100):.2f}%")
    
    if not_found_products:
        print(f"\n{'='*80}")
        print(f"⚠️  LIST OF MISSING PRODUCTS ({len(not_found_products)} items):")
        print(f"{'='*80}")
        
        # Group by sheet
        by_sheet = {}
        for product in not_found_products:
            sheet = product['sheet']
            if sheet not in by_sheet:
                by_sheet[sheet] = []
            by_sheet[sheet].append(product['sku'])
        
        for sheet, skus in by_sheet.items():
            print(f"\n📄 Sheet: {sheet} ({len(skus)} missing)")
            for sku in skus[:20]:  # Show first 20 per sheet
                print(f"   - {sku}")
            if len(skus) > 20:
                print(f"   ... and {len(skus)-20} more")
    
    print(f"\n{'='*80}")
    if not_found_count == 0:
        print("✅✅✅ جميع المنتجات موجودة في قاعدة البيانات! ✅✅✅")
    else:
        print(f"⚠️⚠️⚠️ يوجد {not_found_count} منتج غير موجود في قاعدة البيانات! ⚠️⚠️⚠️")
    print(f"{'='*80}")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
