import asyncio
import logging
from core.database.models import Base
from core.database.session import engine
from sqlalchemy import text

async def init_db():
    logging.basicConfig(level=logging.INFO)
    logging.info("Initializing database...")
    
    async with engine.begin() as conn:
        # Enable PostGIS extension if it doesn't exist
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Ensure columns exist for existing installations
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20)"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS pending_likes_count INTEGER DEFAULT 0"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_like_notification_id BIGINT"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS target_min_age INTEGER DEFAULT 14"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS target_max_age INTEGER DEFAULT 100"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_frozen BOOLEAN DEFAULT FALSE"))
        except Exception as e:
            logging.warning(f"Could not update schema: {e}")
        
    logging.info("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
