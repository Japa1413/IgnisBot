"""
Level Service - Business logic for level calculations and progression.
"""

from __future__ import annotations

from typing import Optional, Dict, Tuple
from repositories.progression_repository import ProgressionRepository
from domain.protocols import ProgressionRepositoryProtocol
from utils.logger import get_logger

logger = get_logger(__name__)

# Level formula: XP required = 100 * level^1.5
# This creates a smooth exponential curve
def xp_for_level(level: int) -> int:
    """
    Calculate XP required to reach a level.
    
    Args:
        level: Target level
    
    Returns:
        XP required to reach that level
    """
    return int(100 * (level ** 1.5))


def level_from_xp(total_xp: int) -> Tuple[int, int, int]:
    """
    Calculate level from total XP.
    
    Args:
        total_xp: Total XP accumulated
    
    Returns:
        Tuple of (current_level, xp_in_current_level, xp_for_next_level)
    """
    if total_xp < 0:
        return (1, 0, xp_for_level(2))
    
    level = 1
    xp_accumulated = 0
    
    # Calculate level by accumulating XP requirements
    while True:
        xp_for_next = xp_for_level(level + 1)
        if xp_accumulated + xp_for_next > total_xp:
            break
        xp_accumulated += xp_for_next
        level += 1
        if level >= 1000:  # Safety limit
            break
    
    xp_in_current = total_xp - xp_accumulated
    xp_needed_for_next = xp_for_level(level + 1)
    
    return (level, xp_in_current, xp_needed_for_next)


class LevelService:
    """Service for level-related business logic"""
    
    def __init__(self, progression_repo: Optional[ProgressionRepositoryProtocol] = None):
        """
        Initialize level service.
        
        Args:
            progression_repo: Progression repository (injected, defaults to ProgressionRepository)
        """
        self.progression_repo = progression_repo or ProgressionRepository()
    
    async def calculate_level(
        self,
        total_xp: int
    ) -> Tuple[int, int, int]:
        """
        Calculate level from total XP.
        
        Args:
            total_xp: Total XP
        
        Returns:
            Tuple of (level, xp_in_level, xp_for_next_level)
        """
        return level_from_xp(total_xp)
    
    async def update_level_if_needed(
        self,
        user_id: int,
        total_xp: int
    ) -> Dict[str, Any]:
        """
        Update user level if XP increased enough.
        
        Args:
            user_id: User ID
            total_xp: Current total XP
        
        Returns:
            Dict with:
                - level_changed: Whether level increased
                - old_level: Previous level
                - new_level: New level
                - level_ups: Number of levels gained (if multiple)
        """
        # Get current progression
        progression = await self.progression_repo.get_or_create_progression(user_id)
        current_level = progression.get("current_level", 1)
        
        # Calculate new level
        new_level, xp_in_level, xp_for_next = await self.calculate_level(total_xp)
        
        if new_level > current_level:
            # Level up detected!
            level_ups = new_level - current_level
            await self.progression_repo.update_level(user_id, new_level)
            
            logger.info(
                f"User {user_id} leveled up from {current_level} to {new_level} "
                f"({level_ups} levels gained)"
            )
            
            return {
                "level_changed": True,
                "old_level": current_level,
                "new_level": new_level,
                "level_ups": level_ups,
                "xp_in_level": xp_in_level,
                "xp_for_next": xp_for_next
            }
        
        return {
            "level_changed": False,
            "old_level": current_level,
            "new_level": current_level,
            "level_ups": 0,
            "xp_in_level": xp_in_level,
            "xp_for_next": xp_for_next
        }
    
    async def get_progression(
        self,
        user_id: int
    ) -> Dict:
        """
        Get full progression data with calculated values.
        
        Args:
            user_id: User ID
        
        Returns:
            Progression dict with calculated level info
        """
        progression = await self.progression_repo.get_or_create_progression(user_id)
        total_xp = progression.get("total_xp", 0)
        
        level, xp_in_level, xp_for_next = await self.calculate_level(total_xp)
        
        # Update stored level if different (sync)
        if level != progression.get("current_level", 1):
            await self.progression_repo.update_level(user_id, level)
            progression["current_level"] = level
        
        progression["calculated_level"] = level
        progression["xp_in_level"] = xp_in_level
        progression["xp_for_next"] = xp_for_next
        progression["xp_progress_pct"] = (
            (xp_in_level / xp_for_next * 100) if xp_for_next > 0 else 100.0
        )
        
        return progression
    
    async def get_level_rewards(
        self,
        level: int
    ) -> Optional[Dict]:
        """
        Get rewards for a specific level.
        
        Args:
            level: Level number
        
        Returns:
            Reward dict or None
        """
        return await self.progression_repo.execute_query(
            "SELECT * FROM level_rewards WHERE level = %s",
            (level,),
            fetch_one=True,
            as_dict=True
        )

