from fastapi import APIRouter
from app.api.v1 import health, users

api_router = APIRouter()

# Include health check routes
api_router.include_router(health.router, tags=["health"])

# Include user routes
api_router.include_router(users.router, prefix="/users", tags=["users"])
