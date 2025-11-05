"""
User Service - Business logic for user operations.
"""

from __future__ import annotations

from typing import Optional
from repositories.user_repository import UserRepository
from services.cache_service import CacheService
from domain.protocols import UserRepositoryProtocol, CacheServiceProtocol
from utils.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for user-related business logic"""
    
    def __init__(
        self,
        user_repo: Optional[UserRepositoryProtocol] = None,
        cache_service: Optional[CacheServiceProtocol] = None
    ):
        """
        Initialize user service.
        
        Args:
            user_repo: User repository (injected, defaults to UserRepository)
            cache_service: Cache service (injected, defaults to CacheService)
        """
        # Dependency injection with defaults for backward compatibility
        self.user_repo = user_repo or UserRepository()
        self.cache_service = cache_service or CacheService()
    
    async def get_user(
        self,
        user_id: int,
        use_cache: bool = True
    ) -> Optional[dict]:
        """
        Get user data with caching.
        
        Args:
            user_id: User ID
            use_cache: Whether to use cache
        
        Returns:
            User data dict or None
        """
        return await self.user_repo.get(user_id, use_cache=use_cache)
    
    async def ensure_exists(self, user_id: int) -> dict:
        """
        Ensure user exists, creating if necessary.
        
        Args:
            user_id: User ID
        
        Returns:
            User data dict
        """
        return await self.user_repo.get_or_create(user_id)

