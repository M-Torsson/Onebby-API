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
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Key for additional security (optional)
    API_KEY: str
    
    # Payment Configuration
    PAYMENT_MODE: str = "test"  # test or production
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Payment Provider Credentials (Mock mode by default)
    PAYPLUG_API_KEY: Optional[str] = None
    PAYPLUG_SECRET_KEY: Optional[str] = None
    PAYPLUG_MODE: str = "test"  # test or live
    PAYPLUG_WEBHOOK_URL: Optional[str] = None  # Full webhook URL
    
    # Floa Payment Configuration
    FLOA_CLIENT_ID: Optional[str] = None
    FLOA_CLIENT_SECRET: Optional[str] = None
    FLOA_BASE_URL: str = "https://api.floapay.io/api-nx-live-int"
    FLOA_PRODUCT_CODE: str = "BC3XF"  # Default: 3 times payment (BC1XFD, BC3XF, BC4XF available)
    FLOA_CULTURE: str = "it-IT"  # Italy locale
    FLOA_WEBHOOK_URL: Optional[str] = None  # Webhook notification URL
    
    FLOA_API_KEY: Optional[str] = None
    FLOA_SECRET_KEY: Optional[str] = None
    
    FINDOMESTIC_API_KEY: Optional[str] = None
    FINDOMESTIC_SECRET_KEY: Optional[str] = None
    
    # Mock Payment Settings (for testing)
    MOCK_WEBHOOK_SECRET: str = "mock_webhook_secret_key"
    TESTING: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Garanzia3 Configuration (Warranty Registration)
    GARANZIA3_API_URL: Optional[str] = None  # Base URL for Garanzia3 API
    GARANZIA3_TOKEN: Optional[str] = None  # Authentication token
    GARANZIA3_MODE: str = "test"  # test or production
    GARANZIA3_TIMEOUT: int = 30  # API timeout in seconds
    
    # Cloudinary Configuration (required for image uploads)
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
