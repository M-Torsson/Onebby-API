# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Onebby API"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str
    
    # Database Pool Configuration
    DB_POOL_SIZE: int = 20  # Increased from default 5
    DB_MAX_OVERFLOW: int = 30  # Increased from default 10
    DB_POOL_TIMEOUT: int = 60  # Increased from default 30
    DB_POOL_RECYCLE: int = 300  # Recycle connections after 5 minutes (prevent SSL timeout)
    DB_POOL_PRE_PING: bool = True  # Test connections before using
    
    # Security Configuration
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Key for additional security (optional)
    API_KEY: str = "your-api-key-here-change-in-production"
    
    # Cloudinary Configuration (required for image uploads)
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
