@echo off
REM 🚀 Deployment Script for Render (Windows)
REM Run this script to commit and push all changes

echo ==================================
echo 🚀 Onebby API - Deployment Script
echo ==================================
echo.

REM Step 1: Stage all changes
echo 📦 Step 1: Staging all changes...
git add .

REM Step 2: Show what will be committed
echo.
echo 📋 Step 2: Files to be committed:
git status --short

REM Step 3: Commit
echo.
echo 💾 Step 3: Committing changes...
git commit -m "feat: Add product import system with multi-source support" -m "✨ Features:" -m "- Change ean13 to ean (flexible length, String 255)" -m "- Add /api/import/products endpoint" -m "- Support for 3 sources: Effezzeta, Erregame, Dixe" -m "- Source-aware column mapping" -m "- Upsert logic by EAN" -m "- NULL support for optional fields (price, brand)" -m "- Chunk processing (300 rows/batch)" -m "- Dry run mode for validation" -m "- Comprehensive error reporting" -m "" -m "📦 New Files:" -m "- app/services/product_import.py (Import service + mappers)" -m "- app/crud/product_import.py (CRUD operations)" -m "- app/api/v1/import_products.py (API endpoint)" -m "- app/schemas/import_products.py (Request/response schemas)" -m "- alembic/versions/d7d76accf25b_change_ean13_to_ean.py" -m "- alembic/versions/66552411929d_allow_null_price.py" -m "" -m "📝 Documentation:" -m "- IMPORT_API.md (Complete API docs)" -m "- IMPORT_QUICKSTART.md (Quick start guide)" -m "- DEPLOYMENT_RENDER.md (Deployment guide)" -m "" -m "🔧 Modified:" -m "- app/models/product.py (ean13 → ean, price nullable)" -m "- app/models/product_variant.py (ean13 → ean)" -m "- app/schemas/product.py (ean validation)" -m "- app/core/security/api_key.py (X-API-KEY header)" -m "- requirements.txt (added openpyxl)" -m "" -m "📊 Statistics:" -m "- Total unique products: 6,075" -m "- Import capacity: ~6,800+ products" -m "- Expected import time: 80-120 seconds" -m "- Chunk size: 300 rows"

REM Step 4: Push to remote
echo.
echo 🌐 Step 4: Pushing to remote repository...
git push origin main

REM Step 5: Success
echo.
echo ==================================
echo ✅ Deployment Successful!
echo ==================================
echo.
echo 📋 Next Steps:
echo 1. Go to Render Dashboard
echo 2. Check deployment logs
echo 3. Run migrations: alembic upgrade head
echo 4. Test with: curl https://your-app.onrender.com/api/health
echo 5. Import products using DEPLOYMENT_RENDER.md guide
echo.
echo 📚 Documentation:
echo - IMPORT_API.md - Complete API documentation
echo - IMPORT_QUICKSTART.md - Quick start guide
echo - DEPLOYMENT_RENDER.md - Deployment instructions
echo.
echo 🎉 Happy importing!
pause
