# utils/database.py
from __future__ import annotations

import asyncio
import aiomysql
from typing import Optional
from utils.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT, DB_POOL_MIN, DB_POOL_MAX
from utils.logger import get_logger

logger = get_logger(__name__)

_POOL: Optional[aiomysql.Pool] = None

_CONN_KW = dict(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    db=DB_NAME,
    charset="utf8mb4",
    autocommit=True,
    connect_timeout=5,   # <-- supported
    # read_timeout / write_timeout are NOT supported by aiomysql
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
                    exp INT DEFAULT 0,
                    `rank` VARCHAR(50) DEFAULT 'Civitas Aspirant',
                    path VARCHAR(50) DEFAULT 'pre_induction',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_exp (exp DESC),
                    INDEX idx_rank (`rank`)
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
            
            # Gamification tables (Phase 1)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_progression (
                    user_id BIGINT PRIMARY KEY,
                    total_xp BIGINT DEFAULT 0,
                    current_level INT DEFAULT 1,
                    prestige_level INT DEFAULT 0,
                    last_xp_gain TIMESTAMP NULL,
                    last_level_up TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_level (current_level),
                    INDEX idx_total_xp (total_xp),
                    INDEX idx_prestige (prestige_level),
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS xp_events (
                    event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    xp_amount INT NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    details JSON NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_user_id (user_id),
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_source (source),
                    INDEX idx_user_timestamp (user_id, timestamp),
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_xp_limits (
                    user_id BIGINT NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    date DATE NOT NULL,
                    xp_gained INT DEFAULT 0,
                    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, source, date),
                    INDEX idx_date (date),
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS level_rewards (
                    level INT PRIMARY KEY,
                    xp_bonus INT DEFAULT 0,
                    points_bonus INT DEFAULT 0,
                    reward_type VARCHAR(50) NULL,
                    reward_value VARCHAR(255) NULL,
                    description TEXT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Insert default level rewards
            await cursor.execute("""
                INSERT INTO level_rewards (level, xp_bonus, points_bonus, description) VALUES
                (1, 0, 0, 'Starting level'),
                (5, 50, 25, 'First milestone'),
                (10, 100, 50, 'Double digits!'),
                (25, 250, 125, 'Quarter century'),
                (50, 500, 250, 'Half century milestone'),
                (100, 1000, 500, 'Century achievement')
                ON DUPLICATE KEY UPDATE description=VALUES(description)
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
    
    DEPRECATED: Use repositories.user_repository.UserRepository.get() instead.
    This function is kept for backward compatibility.
    
    This function will be removed on 2025-12-31. Please migrate to UserRepository.
    
    Args:
        user_id: User ID
        use_cache: If True, uses cache with TTL (default: True)
    
    Returns:
        Dict with user data or None if not found
    
    Raises:
        RuntimeError: If database pool is not initialized
    """
    # Use repository for new architecture
    try:
        from repositories.user_repository import UserRepository
        repo = UserRepository()
        return await repo.get(user_id, use_cache=use_cache)
    except ImportError:
        # Fallback to old implementation if repositories not available
        pass
    
    # OPTIMIZATION PHASE 2: Use cache if enabled (legacy fallback)
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
    """
    Create a new user.
    
    DEPRECATED: Use repositories.user_repository.UserRepository.create() instead.
    This function is kept for backward compatibility.
    
    This function will be removed on 2025-12-31. Please migrate to UserRepository.
    """
    # Use repository for new architecture
    try:
        from repositories.user_repository import UserRepository
        repo = UserRepository()
        await repo.create(user_id)
        
        # Legacy audit logging (will be replaced by events in Phase 3)
        try:
            from utils.audit_log import log_data_operation
            asyncio.create_task(log_data_operation(
                user_id=user_id,
                action_type="CREATE",
                data_type="user_data",
                purpose="New user record creation"
            ))
        except Exception:
            pass
        return
    except ImportError:
        # Fallback to old implementation if repositories not available
        pass
    
    # Legacy implementation (fallback)
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
    
    DEPRECATED: Use repositories.user_repository.UserRepository.update_points() instead.
    This function is kept for backward compatibility.
    
    This function will be removed on 2025-12-31. Please migrate to UserRepository.
    
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
    # Use repository for new architecture
    try:
        from repositories.user_repository import UserRepository
        repo = UserRepository()
        new_points = await repo.update_points(user_id, points)
        
        # Legacy audit logging (will be replaced by events in Phase 3)
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
            pass
        
        return new_points
    except ImportError:
        # Fallback to old implementation if repositories not available
        pass
    
    # Legacy implementation (fallback)
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