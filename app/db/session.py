from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine with proper pool configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,  # Number of permanent connections
    max_overflow=settings.DB_MAX_OVERFLOW,  # Additional connections when pool is full
    pool_timeout=settings.DB_POOL_TIMEOUT,  # Seconds to wait for available connection
    pool_recycle=settings.DB_POOL_RECYCLE,  # Recycle connections after this time
    pool_pre_ping=settings.DB_POOL_PRE_PING,  # Test connections before use
    echo=settings.DEBUG
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
