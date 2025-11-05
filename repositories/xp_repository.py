"""
XP Repository - Data access for XP operations.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
from datetime import datetime, date
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class XPRepository(BaseRepository):
    """Repository for XP data access"""
    
    async def add_xp(
        self,
        user_id: int,
        xp_amount: int,
        source: str,
        details: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Add XP to user and log event.
        
        Args:
            user_id: User ID
            xp_amount: XP amount to add
            source: Source of XP (voice, message, quest, etc.)
            details: Additional context (optional)
        
        Returns:
            New total XP value
        """
        import json
        
        # 1. Insert XP event log
        details_json = json.dumps(details) if details else None
        await self.execute_query(
            """
            INSERT INTO xp_events (user_id, xp_amount, source, details)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, xp_amount, source, details_json)
        )
        
        # 2. Update user progression
        pool = self.pool
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Get or create progression entry
                await cursor.execute(
                    """
                    INSERT INTO user_progression (user_id, total_xp, last_xp_gain)
                    VALUES (%s, %s, NOW())
                    ON DUPLICATE KEY UPDATE
                        total_xp = total_xp + VALUES(total_xp),
                        last_xp_gain = NOW()
                    """,
                    (user_id, xp_amount)
                )
                
                # Get new total XP
                await cursor.execute(
                    "SELECT total_xp FROM user_progression WHERE user_id = %s",
                    (user_id,)
                )
                result = await cursor.fetchone()
                new_total_xp = int(result[0]) if result else xp_amount
        
        return new_total_xp
    
    async def get_daily_xp_limit(
        self,
        user_id: int,
        source: str,
        target_date: Optional[date] = None
    ) -> int:
        """
        Get daily XP limit for a user and source.
        
        Args:
            user_id: User ID
            source: XP source type
            target_date: Target date (defaults to today)
        
        Returns:
            XP already gained today for this source
        """
        if target_date is None:
            target_date = date.today()
        
        result = await self.execute_query(
            """
            SELECT xp_gained FROM daily_xp_limits
            WHERE user_id = %s AND source = %s AND date = %s
            """,
            (user_id, source, target_date),
            fetch_one=True
        )
        
        return int(result[0]) if result else 0
    
    async def update_daily_xp_limit(
        self,
        user_id: int,
        source: str,
        xp_amount: int,
        target_date: Optional[date] = None
    ) -> None:
        """
        Update daily XP limit tracking.
        
        Args:
            user_id: User ID
            source: XP source type
            xp_amount: XP amount to add
            target_date: Target date (defaults to today)
        """
        if target_date is None:
            target_date = date.today()
        
        await self.execute_query(
            """
            INSERT INTO daily_xp_limits (user_id, source, date, xp_gained)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                xp_gained = xp_gained + VALUES(xp_gained)
            """,
            (user_id, source, target_date, xp_amount)
        )
    
    async def get_xp_history(
        self,
        user_id: int,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get XP gain history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of records
        
        Returns:
            List of XP events
        """
        return await self.execute_query(
            """
            SELECT event_id, xp_amount, source, details, timestamp
            FROM xp_events
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (user_id, limit),
            fetch_all=True,
            as_dict=True
        ) or []
    
    async def get_total_xp(
        self,
        user_id: int
    ) -> int:
        """
        Get total XP for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Total XP (0 if no progression exists)
        """
        result = await self.execute_query(
            "SELECT total_xp FROM user_progression WHERE user_id = %s",
            (user_id,),
            fetch_one=True
        )
        
        return int(result[0]) if result else 0

