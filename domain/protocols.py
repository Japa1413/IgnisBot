"""
Protocols for type hints and dependency injection.

These Protocols define contracts for repositories and services,
allowing better type safety and testability without the overhead
of full Hexagonal Architecture.

Benefits:
- Type safety with mypy/pyright
- Explicit interfaces for testing
- Zero runtime overhead (Protocols are structural typing)
- Backward compatible with existing code
"""

from __future__ import annotations

from typing import Protocol, Optional, Dict, Any, List
from datetime import date


# ============================================
# REPOSITORY PROTOCOLS
# ============================================

class UserRepositoryProtocol(Protocol):
    """Protocol for user repository operations"""
    
    async def get(self, user_id: int, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Get user data"""
        ...
    
    async def create(self, user_id: int) -> None:
        """Create new user"""
        ...
    
    async def get_or_create(self, user_id: int) -> Dict[str, Any]:
        """Get user or create if not exists"""
        ...
    
    async def update_points(self, user_id: int, points: int) -> int:
        """Update user points and return new value"""
        ...


class AuditRepositoryProtocol(Protocol):
    """Protocol for audit repository operations"""
    
    async def create(
        self,
        user_id: int,
        action_type: str,
        data_type: str,
        performed_by: Optional[int] = None,
        purpose: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create audit log entry"""
        ...


class ConsentRepositoryProtocol(Protocol):
    """Protocol for consent repository operations"""
    
    async def get(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get consent data"""
        ...
    
    async def create_or_update(
        self,
        user_id: int,
        base_legal: str = "consentimento",
        version: str = "1.0"
    ) -> bool:
        """Create or update consent"""
        ...
    
    async def revoke(self, user_id: int) -> bool:
        """Revoke consent"""
        ...


# ============================================
# SERVICE PROTOCOLS
# ============================================

class CacheServiceProtocol(Protocol):
    """Protocol for cache service operations"""
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user from cache"""
        ...
    
    async def set_user(self, user_id: int, data: Dict[str, Any]) -> None:
        """Set user in cache"""
        ...
    
    async def invalidate_user(self, user_id: int) -> None:
        """Invalidate user cache"""
        ...
    
    async def invalidate_user_cache(self, user_id: int) -> None:
        """Invalidate user cache (alias)"""
        ...
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        ...


class ConsentServiceProtocol(Protocol):
    """Protocol for consent service operations"""
    
    async def has_consent(self, user_id: int) -> bool:
        """Check if user has given consent"""
        ...
    
    async def grant_consent(
        self,
        user_id: int,
        base_legal: str = "consentimento",
        version: str = "1.0"
    ) -> bool:
        """Grant consent"""
        ...
    
    async def revoke_consent(self, user_id: int) -> bool:
        """Revoke consent"""
        ...


# ============================================
# EVENT PROTOCOLS
# ============================================

class EventDispatcherProtocol(Protocol):
    """Protocol for event dispatching"""
    
    async def dispatch(self, event_name: str, event_data: Any) -> None:
        """Dispatch an event"""
        ...


# ============================================
# GAMIFICATION PROTOCOLS
# ============================================

class XPRepositoryProtocol(Protocol):
    """Protocol for XP repository operations"""
    
    async def add_xp(
        self,
        user_id: int,
        xp_amount: int,
        source: str,
        details: Optional[Dict[str, Any]] = None
    ) -> int:
        """Add XP and return new total"""
        ...
    
    async def get_total_xp(self, user_id: int) -> int:
        """Get total XP"""
        ...
    
    async def get_daily_xp_limit(
        self,
        user_id: int,
        source: str,
        target_date: Optional[date] = None
    ) -> int:
        """Get daily XP limit for source"""
        ...


class ProgressionRepositoryProtocol(Protocol):
    """Protocol for progression repository operations"""
    
    async def get_progression(self, user_id: int) -> Optional[Dict]:
        """Get user progression"""
        ...
    
    async def get_or_create_progression(
        self,
        user_id: int,
        initial_xp: int = 0,
        initial_level: int = 1
    ) -> Dict:
        """Get or create progression"""
        ...
    
    async def update_level(self, user_id: int, new_level: int) -> None:
        """Update user level"""
        ...

