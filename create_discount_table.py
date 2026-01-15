"""
Script to create discount_campaigns table directly in database
"""
import asyncio
from sqlalchemy import create_engine, text
from app.core.config import settings

# Database URL
DATABASE_URL = settings.DATABASE_URL

def create_discount_campaigns_table():
    """Create discount_campaigns table"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Create enums first
        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE discounttypeenum AS ENUM ('PERCENTAGE', 'FIXED_AMOUNT');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE targettypeenum AS ENUM ('PRODUCTS', 'CATEGORY', 'BRAND', 'ALL');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        # Create table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS discount_campaigns (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description VARCHAR(1000),
                discount_type discounttypeenum NOT NULL,
                discount_value FLOAT NOT NULL,
                target_type targettypeenum NOT NULL,
                target_ids JSONB,
                start_date TIMESTAMP WITH TIME ZONE,
                end_date TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE,
                created_by INTEGER
            );
        """))
        
        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_discount_campaigns_id ON discount_campaigns(id);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_discount_campaigns_name ON discount_campaigns(name);
        """))
        
        conn.commit()
        print("✅ discount_campaigns table created successfully!")

if __name__ == "__main__":
    create_discount_campaigns_table()
