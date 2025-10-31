# utils/database.py
from __future__ import annotations

import asyncio
import aiomysql
from typing import Optional
from utils.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_POOL_MIN, DB_POOL_MAX
from utils.logger import get_logger

logger = get_logger(__name__)

_POOL: Optional[aiomysql.Pool] = None

_CONN_KW = dict(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    db=DB_NAME,
    charset="utf8mb4",
    autocommit=True,
    connect_timeout=5,   # <-- suportado
    # read_timeout / write_timeout NÃO são suportados pelo aiomysql
)

async def initialize_db():
    """Create a global connection pool and ensure tables exist."""
    global _POOL
    if _POOL is None:
        # OPTIMIZATION PHASE 2: Pool configurable via environment
        _POOL = await aiomysql.create_pool(
            minsize=DB_POOL_MIN,
            maxsize=DB_POOL_MAX,
            **_CONN_KW
        )
        logger.info(f"Database pool initialized: {DB_POOL_MIN}-{DB_POOL_MAX} connections")

    async with _POOL.acquire() as conn:
        async with conn.cursor() as cursor:
            # Main users table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    points INT DEFAULT 0,
                    `rank` VARCHAR(50) DEFAULT 'Civitas aspirant',
                    progress INT DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # LGPD consent table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_consent (
                    user_id BIGINT PRIMARY KEY,
                    consent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    consent_version VARCHAR(20) DEFAULT '1.0',
                    base_legal VARCHAR(50) DEFAULT 'consentimento',
                    consent_given BOOLEAN DEFAULT FALSE,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Personal data audit table (LGPD Art. 10)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_audit_log (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    action_type VARCHAR(50) NOT NULL,
                    data_type VARCHAR(100) NOT NULL,
                    performed_by BIGINT,
                    purpose TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    details JSON,
                    INDEX idx_user_id (user_id),
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_action_type (action_type)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Index to optimize leaderboard queries (ORDER BY points DESC)
            # Check if index already exists before creating (IF NOT EXISTS doesn't work in all MySQL versions)
            try:
                await cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM information_schema.statistics 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'users' 
                    AND index_name = 'idx_points'
                """)
                result = await cursor.fetchone()
                index_exists = result[0] > 0 if result else False
                
                if not index_exists:
                    await cursor.execute("""
                        CREATE INDEX idx_points 
                        ON users(points DESC)
                    """)
                    logger.info("Index idx_points created successfully")
                else:
                    logger.debug("Index idx_points already exists")
            except Exception as e:
                # If error occurs while checking/creating index, just log and continue
                logger.warning(f"Error creating index idx_points: {e}. Continuing without index.")

async def get_user(user_id: int, use_cache: bool = True):
    """
    Get user data.
    
    Args:
        user_id: User ID
        use_cache: If True, uses cache with TTL (default: True)
    
    Returns:
        Dict with user data or None if not found
    
    Raises:
        RuntimeError: If database pool is not initialized
    """
    # OPTIMIZATION PHASE 2: Use cache if enabled
    if use_cache:
        try:
            from utils.cache import get_user_cached
            return await get_user_cached(user_id)
        except ImportError:
            # Cache not available, continue without cache
            pass
        except Exception as e:
            # In case of cache error, perform direct query
            logger = get_logger(__name__) if 'logger' not in dir() else None
            if logger:
                logger.warning(f"Cache error, performing direct query: {e}")
    
    # Direct query to database
    if _POOL is None:
        raise RuntimeError("DB pool not initialized. Call initialize_db() first.")
    async with _POOL.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT user_id, points, `rank`, progress FROM users WHERE user_id = %s",
                (user_id,)
            )
            return await cursor.fetchone()

async def create_user(user_id: int):
    if _POOL is None:
        raise RuntimeError("DB pool not initialized. Call initialize_db() first.")
    async with _POOL.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO users (user_id, points, `rank`) VALUES (%s, 0, 'Civitas aspirant')",
                (user_id,)
            )
    
    # OPTIMIZATION PHASE 2: Invalidate cache (user was created)
    try:
        from utils.cache import invalidate_user_cache
        invalidate_user_cache(user_id)
    except Exception:
        pass
    
    # OPTIMIZATION: Asynchronous audit (does not block response)
    try:
        from utils.audit_log import log_data_operation
        asyncio.create_task(log_data_operation(
            user_id=user_id,
            action_type="CREATE",
            data_type="user_data",
            purpose="New user record creation"
        ))
    except Exception:
        pass  # Don't fail if audit is not available

async def update_points(user_id: int, points: int, performed_by: int = None, purpose: str = None) -> int:
    """
    Update user points and return the new value.
    
    Args:
        user_id: User ID
        points: Amount of points to add/subtract
        performed_by: ID of who performed the action (optional)
        purpose: Purpose of the update (optional)
    
    Returns:
        New points value after update
    
    Raises:
        RuntimeError: If pool was not initialized
    """
    if _POOL is None:
        raise RuntimeError("DB pool not initialized. Call initialize_db() first.")
    
    # OPTIMIZATION PHASE 2: Invalidate cache before updating
    try:
        from utils.cache import invalidate_user_cache
        invalidate_user_cache(user_id)
    except Exception:
        pass
    
    async with _POOL.acquire() as conn:
        async with conn.cursor() as cursor:
            # Update points
            await cursor.execute(
                "UPDATE users SET points = points + %s WHERE user_id = %s",
                (points, user_id)
            )
            
            # Fetch new value in same connection (optimized)
            await cursor.execute(
                "SELECT points FROM users WHERE user_id = %s",
                (user_id,)
            )
            result = await cursor.fetchone()
            new_points = int(result[0]) if result else 0
    
    # OPTIMIZATION: Asynchronous audit (does not block response)
    try:
        from utils.audit_log import log_data_operation
        asyncio.create_task(log_data_operation(
            user_id=user_id,
            action_type="UPDATE",
            data_type="points",
            performed_by=performed_by,
            purpose=purpose or f"Points update: {'+' if points > 0 else ''}{points}"
        ))
    except Exception:
        pass  # Don't fail if audit is not available
    
    return new_points

async def ensure_user_exists(user_id: int):
    """Ensures user exists in database, creating if necessary"""
    # Use cache=false to ensure accurate verification
    if not await get_user(user_id, use_cache=False):
        await create_user(user_id)

def get_pool():
    """
    Get the database connection pool.
    
    Returns:
        aiomysql.Pool or None if not initialized
    
    Raises:
        RuntimeError: If pool was not initialized
    """
    if _POOL is None:
        raise RuntimeError("DB pool not initialized. Call initialize_db() first.")
    return _POOL