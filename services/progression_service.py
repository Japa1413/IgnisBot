"""
Progression Service - Business logic for manual EXP and rank management.
"""

from __future__ import annotations

from typing import Optional, Dict, Tuple
from repositories.user_repository import UserRepository
from utils.rank_paths import (
    get_rank_progress,
    get_rank_from_exp,
    get_path_display_name,
    progress_bar,
    get_rank_limit,
    ALL_PATHS,
    DEFAULT_PATH
)
from utils.logger import get_logger

logger = get_logger(__name__)


class ProgressionService:
    """Service for manual progression management"""
    
    def __init__(self):
        """Initialize progression service"""
        self.user_repo = UserRepository()
    
    async def grant_exp(
        self,
        user_id: int,
        exp_amount: int,
        granted_by: int,
        reason: str
    ) -> Dict:
        """
        Grant EXP manually to a user.
        
        Args:
            user_id: User ID
            exp_amount: EXP amount to grant
            granted_by: ID of user granting EXP
            reason: Reason for granting EXP
        
        Returns:
            Dict with updated user data
        """
        # Get or create user
        user = await self.user_repo.get_or_create(user_id)
        current_exp = int(user.get("exp", 0) or user.get("points", 0))
        current_rank = user.get("rank", "Civitas Aspirant")
        current_path = user.get("path", DEFAULT_PATH)
        
        # Update EXP (stored in both exp and points for compatibility)
        new_exp = current_exp + exp_amount
        
        # Update in database
        pool = self.user_repo.pool
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    UPDATE users 
                    SET exp = %s, points = %s, updated_at = NOW()
                    WHERE user_id = %s
                    """,
                    (new_exp, new_exp, user_id)
                )
        
        # Calculate new rank (auto-detect based on EXP)
        new_rank = get_rank_from_exp(new_exp, current_path)
        
        # Update rank if changed
        if new_rank != current_rank and not self._is_handpicked_rank(new_rank, current_path):
            # Only auto-update if not handpicked
            await self._update_rank(user_id, new_rank)
        
        logger.info(
            f"User {user_id} granted {exp_amount} EXP by {granted_by}. "
            f"New total: {new_exp}, Rank: {new_rank}"
        )
        
        return {
            "user_id": user_id,
            "exp": new_exp,
            "points": new_exp,  # For compatibility
            "rank": new_rank,
            "path": current_path,
            "path_display": get_path_display_name(current_path),
            "granted": exp_amount
        }
    
    async def set_rank(
        self,
        user_id: int,
        rank: str,
        path: Optional[str] = None,
        set_by: int = 0
    ) -> Dict:
        """
        Manually set user rank (for handpicked promotions).
        
        Args:
            user_id: User ID
            rank: Rank name to set
            path: Path identifier (optional, uses current if not provided)
            set_by: ID of user setting rank
        
        Returns:
            Dict with updated user data
        """
        user = await self.user_repo.get_or_create(user_id)
        final_path = path or user.get("path", DEFAULT_PATH)
        
        # Update rank
        await self._update_rank(user_id, rank)
        
        # Update path if provided
        if path and path in ALL_PATHS:
            await self._update_path(user_id, path)
            final_path = path
        
        logger.info(f"User {user_id} rank set to '{rank}' by {set_by}")
        
        return {
            "user_id": user_id,
            "rank": rank,
            "path": final_path,
            "path_display": get_path_display_name(final_path)
        }
    
    async def get_user_info(
        self,
        user_id: int
    ) -> Dict:
        """
        Get complete user information for /userinfo command.
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with all user info including progress data
        """
        user = await self.user_repo.get_or_create(user_id)
        points = int(user.get("exp", 0) or user.get("points", 0))
        rank = user.get("rank", "Civitas Aspirant")
        path_name = user.get("path", DEFAULT_PATH)
        
        # Get rank limit (visual bar limit)
        rank_limit = get_rank_limit(rank, path_name)
        
        # Calculate progress towards next rank
        next_rank, exp_in_current, exp_needed, additional_req, is_handpicked = get_rank_progress(
            points, rank, path_name
        )
        
        # Generate progress bar with rank_limit logic
        # Sacred protocol: Bar fills completely when points >= rank_limit
        # But always displays actual points (even if exceeds limit)
        bar = progress_bar(points, rank_limit, width=12)  # Uniform width for terminal aesthetic
        
        # Calculate percentage for display
        visual_fill = min(points, rank_limit)
        progress_pct = (visual_fill / rank_limit * 100) if rank_limit > 0 else 100.0
        
        return {
            "user_id": user_id,
            "points": points,
            "exp": points,  # For compatibility
            "rank": rank,
            "rank_limit": rank_limit,
            "path": path_name,
            "path_display": get_path_display_name(path_name),
            "next_rank": next_rank,
            "exp_in_current": exp_in_current,
            "exp_needed": exp_needed,
            "progress_pct": progress_pct,
            "progress_bar": bar,
            "additional_requirement": additional_req,
            "is_handpicked": is_handpicked
        }
    
    async def _update_rank(self, user_id: int, rank: str) -> None:
        """Update user rank in database"""
        pool = self.user_repo.pool
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "UPDATE users SET `rank` = %s, updated_at = NOW() WHERE user_id = %s",
                    (rank, user_id)
                )
    
    async def _update_path(self, user_id: int, path: str) -> None:
        """Update user path in database"""
        pool = self.user_repo.pool
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "UPDATE users SET path = %s, updated_at = NOW() WHERE user_id = %s",
                    (path, user_id)
                )
    
    def _is_handpicked_rank(self, rank: str, path_name: str) -> bool:
        """Check if rank is handpicked"""
        if path_name not in ALL_PATHS:
            return False
        
        path = ALL_PATHS[path_name]
        for req in path.ranks:
            if req.next_rank == rank and req.is_handpicked:
                return True
        return False

