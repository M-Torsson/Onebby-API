#!/bin/bash

# 🚀 Deployment Script for Render
# Run this script to commit and push all changes

echo "=================================="
echo "🚀 Onebby API - Deployment Script"
echo "=================================="
echo ""

# Step 1: Stage all changes
echo "📦 Step 1: Staging all changes..."
git add .

# Step 2: Show what will be committed
echo ""
echo "📋 Step 2: Files to be committed:"
git status --short

# Step 3: Commit
echo ""
echo "💾 Step 3: Committing changes..."
git commit -m "feat: Add product import system with multi-source support

✨ Features:
- Change ean13 to ean (flexible length, String 255)
- Add /api/import/products endpoint
- Support for 3 sources: Effezzeta, Erregame, Dixe
- Source-aware column mapping
- Upsert logic by EAN
- NULL support for optional fields (price, brand)
- Chunk processing (300 rows/batch)
- Dry run mode for validation
- Comprehensive error reporting

📦 New Files:
- app/services/product_import.py (Import service + mappers)
- app/crud/product_import.py (CRUD operations)
- app/api/v1/import_products.py (API endpoint)
- app/schemas/import_products.py (Request/response schemas)
- alembic/versions/d7d76accf25b_change_ean13_to_ean.py
- alembic/versions/66552411929d_allow_null_price.py

📝 Documentation:
- IMPORT_API.md (Complete API docs)
- IMPORT_QUICKSTART.md (Quick start guide)
- DEPLOYMENT_RENDER.md (Deployment guide)

🔧 Modified:
- app/models/product.py (ean13 → ean, price nullable)
- app/models/product_variant.py (ean13 → ean)
- app/schemas/product.py (ean validation)
- app/core/security/api_key.py (X-API-KEY header)
- requirements.txt (added openpyxl)

📊 Statistics:
- Total unique products: 6,075
- Import capacity: ~6,800+ products
- Expected import time: 80-120 seconds
- Chunk size: 300 rows
"

# Step 4: Push to remote
echo ""
echo "🌐 Step 4: Pushing to remote repository..."
git push origin main

# Step 5: Success
echo ""
echo "=================================="
echo "✅ Deployment Successful!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo "1. Go to Render Dashboard"
echo "2. Check deployment logs"
echo "3. Run migrations: alembic upgrade head"
echo "4. Test with: curl https://your-app.onrender.com/api/health"
echo "5. Import products using DEPLOYMENT_RENDER.md guide"
echo ""
echo "📚 Documentation:"
echo "- IMPORT_API.md - Complete API documentation"
echo "- IMPORT_QUICKSTART.md - Quick start guide"
echo "- DEPLOYMENT_RENDER.md - Deployment instructions"
echo ""
echo "🎉 Happy importing!"
