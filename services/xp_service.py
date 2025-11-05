"""
XP Service - Business logic for XP operations.
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from datetime import date
from repositories.xp_repository import XPRepository
from domain.protocols import XPRepositoryProtocol
from utils.logger import get_logger

logger = get_logger(__name__)

# Daily XP limits per source
DAILY_XP_LIMITS: Dict[str, int] = {
    "voice": 500,  # Max 500 XP per day from voice channels
    "message": 50,  # Max 50 XP per day from messages
    "quest": 0,  # No limit
    "achievement": 0,  # No limit
    "event": 0,  # No limit
    "manual": 0,  # No limit (admin override)
}


class XPService:
    """Service for XP-related business logic"""
    
    def __init__(self, xp_repo: Optional[XPRepositoryProtocol] = None):
        """
        Initialize XP service.
        
        Args:
            xp_repo: XP repository (injected, defaults to XPRepository)
        """
        self.xp_repo = xp_repo or XPRepository()
    
    async def add_xp(
        self,
        user_id: int,
        xp_amount: int,
        source: str,
        details: Optional[Dict[str, Any]] = None,
        check_daily_limit: bool = True
    ) -> Dict[str, Any]:
        """
        Add XP to user with business logic.
        
        Args:
            user_id: User ID
            xp_amount: XP amount to add
            source: Source of XP (voice, message, quest, etc.)
            details: Additional context
            check_daily_limit: Whether to check daily limits (default: True)
        
        Returns:
            Dict with:
                - added: Actual XP added (may be less due to limits)
                - total: New total XP
                - daily_limit_reached: Whether daily limit was reached
        """
        # Check daily limit if required
        added_xp = xp_amount
        daily_limit_reached = False
        
        if check_daily_limit and source in DAILY_XP_LIMITS:
            daily_limit = DAILY_XP_LIMITS[source]
            if daily_limit > 0:
                current_daily = await self.xp_repo.get_daily_xp_limit(user_id, source)
                
                if current_daily >= daily_limit:
                    logger.debug(
                        f"User {user_id} reached daily limit for source '{source}': "
                        f"{current_daily}/{daily_limit}"
                    )
                    return {
                        "added": 0,
                        "total": await self.xp_repo.get_total_xp(user_id),
                        "daily_limit_reached": True
                    }
                
                # Cap XP to remaining limit
                remaining = daily_limit - current_daily
                if xp_amount > remaining:
                    added_xp = remaining
                    daily_limit_reached = True
                    logger.debug(
                        f"User {user_id} XP capped to {remaining} "
                        f"(limit: {daily_limit}, already: {current_daily})"
                    )
        
        # Add XP
        new_total = await self.xp_repo.add_xp(
            user_id=user_id,
            xp_amount=added_xp,
            source=source,
            details=details
        )
        
        # Update daily limit tracking
        if check_daily_limit and source in DAILY_XP_LIMITS:
            await self.xp_repo.update_daily_xp_limit(
                user_id=user_id,
                source=source,
                xp_amount=added_xp
            )
        
        return {
            "added": added_xp,
            "total": new_total,
            "daily_limit_reached": daily_limit_reached
        }
    
    async def get_total_xp(self, user_id: int) -> int:
        """
        Get total XP for user.
        
        Args:
            user_id: User ID
        
        Returns:
            Total XP
        """
        return await self.xp_repo.get_total_xp(user_id)
    
    async def get_xp_history(
        self,
        user_id: int,
        limit: int = 100
    ) -> list:
        """
        Get XP gain history.
        
        Args:
            user_id: User ID
            limit: Maximum records
        
        Returns:
            List of XP events
        """
        return await self.xp_repo.get_xp_history(user_id, limit)


# Add XPRepositoryProtocol to domain/protocols.py
# This will be done when integrating

