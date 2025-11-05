"""
User Repository - Data access for user operations.
"""

from __future__ import annotations

from typing import Optional
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)

# CacheService will be imported lazily to avoid circular imports


class UserRepository(BaseRepository):
    """Repository for user data access with integrated caching"""
    
    def __init__(self):
        super().__init__()
        # Cache service will be imported when needed to avoid circular imports
        self._cache_service = None
    
    def _get_cache(self):
        """Lazy load cache service (synchronous property)"""
        if self._cache_service is None:
            from services.cache_service import CacheService
            self._cache_service = CacheService()
        return self._cache_service
    
    async def get(
        self,
        user_id: int,
        use_cache: bool = True
    ) -> Optional[dict]:
        """
        Get user data with automatic cache integration.
        
        Args:
            user_id: User ID
            use_cache: Whether to use cache (default: True)
        
        Returns:
            User data dict or None if not found
        """
        # Try cache first if enabled
        if use_cache:
            cache = self._get_cache()
            cached = await cache.get_user(user_id)
            if cached is not None:
                logger.debug(f"Cache hit for user_id {user_id}")
                return cached
        
        # Cache miss - query database
        logger.debug(f"Cache miss for user_id {user_id}")
        result = await self.execute_query(
            "SELECT user_id, points, exp, `rank`, path FROM users WHERE user_id = %s",
            (user_id,),
            fetch_one=True,
            as_dict=True
        )
        
        if result:
            # Store in cache
            cache = self._get_cache()
            await cache.set_user(user_id, result)
            return result
        
        return None
    
    async def get_or_create(self, user_id: int) -> dict:
        """
        Get user or create if doesn't exist.
        
        Args:
            user_id: User ID
        
        Returns:
            User data dict
        """
        user = await self.get(user_id, use_cache=False)
        if user is None:
            await self.create(user_id)
            user = await self.get(user_id, use_cache=False)
        return user
    
    async def create(self, user_id: int) -> None:
        """
        Create a new user record.
        
        Args:
            user_id: User ID
        """
        await self.execute_query(
            "INSERT INTO users (user_id, points, exp, `rank`, path) VALUES (%s, 0, 0, 'Civitas Aspirant', 'pre_induction')",
            (user_id,)
        )
        
        # Invalidate cache
        cache = self._get_cache()
        await cache.invalidate_user(user_id)
    
    async def update_points(
        self,
        user_id: int,
        delta: int
    ) -> int:
        """
        Update user points and return new value (optimized).
        
        Args:
            user_id: User ID
            delta: Points to add/subtract
        
        Returns:
            New points value after update
        
        Raises:
            Exception: If database operation fails
        """
        # Invalidate cache before update
        cache = self._get_cache()
        await cache.invalidate_user(user_id)
        
        pool = self.pool
        try:
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # First, check if user exists and get current values
                    await cursor.execute(
                        "SELECT points, exp FROM users WHERE user_id = %s",
                        (user_id,)
                    )
                    existing = await cursor.fetchone()
                    
                    if existing is None:
                        # User doesn't exist, create them first
                        initial_points = max(0, delta)
                        await cursor.execute(
                            "INSERT INTO users (user_id, points, exp, `rank`, path) VALUES (%s, %s, %s, 'Civitas Aspirant', 'pre_induction')",
                            (user_id, initial_points, initial_points)
                        )
                        new_points = initial_points
                    else:
                        # Update points and exp (keep them in sync)
                        current_points = int(existing[0]) if existing[0] is not None else 0
                        current_exp = int(existing[1]) if existing[1] is not None else current_points
                        
                        # Calculate new values (ensure non-negative)
                        new_points = max(0, current_points + delta)
                        new_exp = max(0, current_exp + delta)
                        
                        await cursor.execute(
                            """
                            UPDATE users 
                            SET points = %s, 
                                exp = %s 
                            WHERE user_id = %s
                            """,
                            (new_points, new_exp, user_id)
                        )
                        
                        # Check if update was successful
                        if cursor.rowcount == 0:
                            logger.warning(f"Update affected 0 rows for user {user_id}. User may have been deleted.")
                            raise ValueError(f"User {user_id} not found or update failed")
                    
                    # Verify the update by fetching the new value
                    await cursor.execute(
                        "SELECT points FROM users WHERE user_id = %s",
                        (user_id,)
                    )
                    result = await cursor.fetchone()
                    if result is None:
                        raise ValueError(f"User {user_id} not found after update")
                    new_points = int(result[0]) if result[0] is not None else 0
                    
                    logger.debug(f"Updated points for user {user_id}: delta={delta}, new_points={new_points}")
                    
        except Exception as e:
            logger.error(f"Error updating points for user {user_id} with delta {delta}: {e}", exc_info=True)
            raise
        
        # Cache is already invalidated - next get will refresh
        return new_points
    
    async def exists(self, user_id: int) -> bool:
        """
        Check if user exists.
        
        Args:
            user_id: User ID
        
        Returns:
            True if user exists
        """
        result = await self.execute_query(
            "SELECT 1 FROM users WHERE user_id = %s LIMIT 1",
            (user_id,),
            fetch_one=True
        )
        return result is not None
