import os
import asyncpg
from typing import Optional
import logging

logger=logging.getLogger(__name__)

# Global variable to hold the connection pool after startup
_pool: Optional[asyncpg.Pool]=None

# Read DB url from the env variable or use local db
POSTGRES_DSN= os.getenv(
    "POSTGRES_DSN",
    "postgresql://postgres:postgres@localhost:5432/xai_metrics",
)

# create the connection pool when application starts
async def connect_postgres():
    global _pool
    logger.info("Connecting to PostgreSQL pool")

    #creating a reusable bucket of db connections
    _pool = await asyncpg.create_pool(
        POSTGRES_DSN,
        min_size=2,
        max_size=10
    )

    logger.info("Connection pool initialized")

# closing all db connections when shutting down
async def disconnect_postgres():
    global _pool
    if _pool:
        await _pool.close()
        logger.info("Pool disconnected")
    
# giving pool access to the other parts of the app
def get_pool() -> asyncpg.Pool:
    # safety check sp routes dont use an uninitialized pool
    if _pool is None:
        raise RuntimeError(
            " CRITICAL: PostgreSQL pool is not initialized"
        )
    
    # returning the active connection pool
    return _pool

