"""
Database session management with connection pooling.

Features:
- Connection pooling with configurable size
- Connection health checking
- Automatic connection recycling
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings

logger = logging.getLogger(__name__)

# Connection pool settings
POOL_SIZE = 5           # Number of connections to keep open
MAX_OVERFLOW = 10       # Max additional connections above pool_size
POOL_RECYCLE = 3600     # Recycle connections after 1 hour
POOL_PRE_PING = True    # Check connection health before use

# Async engine with pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=POOL_PRE_PING,
)

AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Sync engine for scripts (with similar pooling)
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=POOL_PRE_PING,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session with automatic cleanup.
    
    Usage:
        async with get_db() as db:
            result = await db.execute(query)
    
    Or as dependency:
        @app.get("/")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except Exception as e:
            logger.error(f"Database error: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()


def get_pool_status() -> dict:
    """Get current connection pool status for monitoring."""
    pool = engine.pool
    return {
        "pool_size": POOL_SIZE,
        "max_overflow": MAX_OVERFLOW,
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "connections": pool.size(),
    }
