from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security.auth import decode_access_token
from app.db.session import get_db

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user
    Validates JWT token and returns user info
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Here you would fetch user from database
    # For now, return the payload
    return {"id": user_id, **payload}


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current active user
    Add additional checks here (e.g., is_active, is_verified)
    """
    # if not current_user.get("is_active"):
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
