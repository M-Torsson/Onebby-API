# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from app.db.session import get_db
from app.schemas.health import HealthResponse
from app.core.security.api_key import verify_api_key

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: Session = Depends(get_db),
):
    """
    Health check endpoint
    Returns API status and database connectivity
    Public health check endpoint (no API key)
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
    
    return HealthResponse(
        status="healthy",
        message="Onebby API is running",
        timestamp=datetime.now(),
        database=db_status
    )
