"""
Progression Repository - Data access for user progression (levels, prestige).
"""

from __future__ import annotations

from typing import Optional, Dict
from datetime import datetime
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class ProgressionRepository(BaseRepository):
    """Repository for user progression data access"""
    
    async def get_progression(
        self,
        user_id: int
    ) -> Optional[Dict]:
        """
        Get user progression data.
        
        Args:
            user_id: User ID
        
        Returns:
            Progression dict or None if not found
        """
        return await self.execute_query(
            """
            SELECT 
                user_id,
                total_xp,
                current_level,
                prestige_level,
                last_xp_gain,
                last_level_up,
                created_at,
                updated_at
            FROM user_progression
            WHERE user_id = %s
            """,
            (user_id,),
            fetch_one=True,
            as_dict=True
        )
    
    async def create_progression(
        self,
        user_id: int,
        initial_xp: int = 0,
        initial_level: int = 1
    ) -> None:
        """
        Create progression entry for new user.
        
        Args:
            user_id: User ID
            initial_xp: Initial XP (default: 0)
            initial_level: Initial level (default: 1)
        """
        await self.execute_query(
            """
            INSERT INTO user_progression (user_id, total_xp, current_level)
            VALUES (%s, %s, %s)
            """,
            (user_id, initial_xp, initial_level)
        )
    
    async def update_level(
        self,
        user_id: int,
        new_level: int
    ) -> None:
        """
        Update user level.
        
        Args:
            user_id: User ID
            new_level: New level value
        """
        await self.execute_query(
            """
            UPDATE user_progression
            SET current_level = %s, last_level_up = NOW()
            WHERE user_id = %s
            """,
            (new_level, user_id)
        )
    
    async def update_prestige(
        self,
        user_id: int,
        new_prestige: int
    ) -> None:
        """
        Update prestige level.
        
        Args:
            user_id: User ID
            new_prestige: New prestige level
        """
        await self.execute_query(
            """
            UPDATE user_progression
            SET prestige_level = %s
            WHERE user_id = %s
            """,
            (new_prestige, user_id)
        )
    
    async def get_or_create_progression(
        self,
        user_id: int,
        initial_xp: int = 0,
        initial_level: int = 1
    ) -> Dict:
        """
        Get progression or create if not exists.
        
        Args:
            user_id: User ID
            initial_xp: Initial XP if creating
            initial_level: Initial level if creating
        
        Returns:
            Progression dict
        """
        progression = await self.get_progression(user_id)
        
        if progression is None:
            await self.create_progression(user_id, initial_xp, initial_level)
            progression = await self.get_progression(user_id)
        
        return progression or {
            "user_id": user_id,
            "total_xp": initial_xp,
            "current_level": initial_level,
            "prestige_level": 0
        }

