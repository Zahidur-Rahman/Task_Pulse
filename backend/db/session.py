import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Convert PostgreSQL URL to async
def get_async_database_url() -> str:
    """Convert synchronous PostgreSQL URL to async."""
    sync_url = settings.DATABASE_URL
    if sync_url.startswith("postgresql://"):
        return sync_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return sync_url

# Async database engine configuration
engine = create_async_engine(
    get_async_database_url(),
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    pool_size=10,        # Connection pool size
    max_overflow=20,     # Maximum overflow connections
    echo=False,          # Set to True for SQL query logging in development
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency to get database session.
    Ensures proper cleanup of database connections.
    """
    async with AsyncSessionLocal() as session:
        try:
            logger.debug("Async database session created")
            yield session
        except SQLAlchemyError as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error in database session: {e}")
            await session.rollback()
            raise


async def init_db() -> None:
    """
    Initialize database tables asynchronously.
    Should be called during application startup.
    """
    try:
        from db.base_class import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise


async def check_db_connection() -> bool:
    """
    Check if database connection is working asynchronously.
    Returns True if connection is successful, False otherwise.
    """
    try:
        from sqlalchemy import text
        async with engine.begin() as connection:
            await connection.execute(text("SELECT 1"))
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def close_db_connection() -> None:
    """Close database engine connections."""
    try:
        await engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
        raise    


