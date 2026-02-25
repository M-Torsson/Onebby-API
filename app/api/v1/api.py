# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter
from app.api.v1 import health, users, addresses, carts, orders, payments, webhooks, categories, products, brands_taxes, upload, import_products, discounts, deliveries, warranties, dashboard

api_router = APIRouter()

# Include health check routes
api_router.include_router(health.router, tags=["health"])

# Include user routes
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Include addresses routes
api_router.include_router(addresses.router, prefix="/addresses", tags=["addresses"])

# Include cart routes
api_router.include_router(carts.router, prefix="/cart", tags=["cart"])

# Include orders routes
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])

# Include payments routes
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])

# Include webhooks routes (no authentication required)
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

# Include categories routes
api_router.include_router(categories.router, tags=["categories"])

# Include brands and tax classes routes
api_router.include_router(brands_taxes.router, tags=["brands-taxes"])

# Include products routes
api_router.include_router(products.router, tags=["products"])

# Include discounts routes
api_router.include_router(discounts.router, tags=["discounts"])

# Include deliveries routes
api_router.include_router(deliveries.router, tags=["deliveries"])

# Include warranties routes
api_router.include_router(warranties.router, tags=["warranties"])

# Include dashboard routes (admin only)
api_router.include_router(dashboard.router, tags=["dashboard"])

# Include upload routes
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])

# Include import routes
api_router.include_router(import_products.router, tags=["import"])
