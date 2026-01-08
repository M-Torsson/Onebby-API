"""
Test script for import functionality (dry run without database)
"""
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.product_import import ProductImportService


def test_import_service():
    """Test import service with all three files"""
    
    excel_dir = Path("f:/onebby-api/app/excel")
    
    sources = {
        "effezzeta": "Listino-prodotti.xlsx",
        "erregame": "erregame_organized.xlsx",
        "dixe": "Dixe_organized.xlsx"
    }
    
    print("=" * 80)
    print("TESTING PRODUCT IMPORT SERVICE")
    print("=" * 80)
    
    for source, filename in sources.items():
        print(f"\n{'=' * 80}")
        print(f"Source: {source.upper()}")
        print(f"File: {filename}")
        print('=' * 80)
        
        file_path = excel_dir / filename
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
        
        try:
            # Initialize service
            service = ProductImportService(source)
            
            # Read file
            print(f"\n📖 Reading file...")
            raw_rows = service.read_excel_file(file_path)
            print(f"✅ Total rows read: {len(raw_rows)}")
            
            # Map rows
            print(f"\n🔄 Mapping rows...")
            valid_rows, skipped_rows = service.map_rows(raw_rows)
            print(f"✅ Valid rows: {len(valid_rows)}")
            print(f"⚠️  Skipped rows: {len(skipped_rows)}")
            
            # Show skip reasons
            if skipped_rows:
                reasons = {}
                for skip in skipped_rows:
                    reason = skip["reason"]
                    reasons[reason] = reasons.get(reason, 0) + 1
                
                print(f"\n📊 Skip reasons:")
                for reason, count in reasons.items():
                    print(f"  - {reason}: {count} rows")
            
            # Show sample valid row
            if valid_rows:
                print(f"\n📝 Sample valid row:")
                sample = valid_rows[0]
                for key, value in sample.items():
                    if key == "image_urls":
                        print(f"  {key}: {len(value)} images")
                    elif isinstance(value, str) and len(value) > 50:
                        print(f"  {key}: {value[:50]}...")
                    else:
                        print(f"  {key}: {value}")
            
            # Chunk info
            chunks = service.chunk_rows(valid_rows)
            print(f"\n📦 Chunks: {len(chunks)} (chunk size: {service.CHUNK_SIZE})")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 80}")
    print("✅ TEST COMPLETED")
    print('=' * 80)


if __name__ == "__main__":
    test_import_service()
