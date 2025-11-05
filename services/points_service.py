"""
Points Service - Business logic for points operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import discord
from discord.ext import commands
from repositories.user_repository import UserRepository
from services.consent_service import ConsentService
from domain.protocols import UserRepositoryProtocol, ConsentServiceProtocol
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PointsTransaction:
    """Result of a points operation"""
    user_id: int
    before: int
    after: int
    delta: int
    reason: str
    performed_by: int
    timestamp: datetime


class PointsService:
    """Service for points-related business logic"""
    
    def __init__(
        self,
        bot: commands.Bot,
        user_repo: Optional[UserRepositoryProtocol] = None,
        consent_service: Optional[ConsentServiceProtocol] = None
    ):
        """
        Initialize points service.
        
        Args:
            bot: Discord bot instance
            user_repo: User repository (injected, defaults to UserRepository)
            consent_service: Consent service (injected, defaults to ConsentService)
        """
        self.bot = bot
        # Dependency injection with defaults for backward compatibility
        self.user_repo = user_repo or UserRepository()
        self.consent_service = consent_service or ConsentService()
    
    async def add_points(
        self,
        user_id: int,
        amount: int,
        reason: str,
        performed_by: int,
        check_consent: bool = True
    ) -> PointsTransaction:
        """
        Add points to a user with full business logic.
        
        Args:
            user_id: User ID
            amount: Points to add (positive)
            reason: Reason for adding points
            performed_by: ID of user performing the action
            check_consent: Whether to verify consent before processing (default: True)
        
        Returns:
            PointsTransaction with operation details
        
        Raises:
            ValueError: If consent is required but not given (LGPD Art. 7º, I)
        """
        # 0. Validate consent if required (LGPD Art. 7º, I)
        if check_consent:
            has_consent = await self.consent_service.has_consent(user_id)
            if not has_consent:
                logger.warning(f"Attempt to add points to user {user_id} without consent")
                raise ValueError(
                    "User has not given consent for data processing (LGPD Art. 7º, I). "
                    "Please use /consent grant first."
                )
        
        # 1. Get or create user
        try:
            user = await self.user_repo.get_or_create(user_id)
            before = int(user.get("points", 0) or user.get("exp", 0))
        except Exception as e:
            logger.error(f"Error getting/creating user {user_id} in add_points: {e}", exc_info=True)
            raise ValueError(f"Failed to get user data: {str(e)}")
        
        # 2. Update points (and exp to keep in sync)
        try:
            after = await self.user_repo.update_points(user_id, amount)
            logger.info(f"Added {amount} points to user {user_id}: {before} -> {after}")
        except ValueError as ve:
            # Re-raise ValueError as-is (already has user-friendly message)
            raise
        except Exception as e:
            logger.error(f"Database error in add_points for user {user_id}: {e}", exc_info=True)
            raise ValueError(f"Failed to add points: {str(e)}")
        
        # 3. Create transaction result
        transaction = PointsTransaction(
            user_id=user_id,
            before=before,
            after=after,
            delta=amount,
            reason=reason,
            performed_by=performed_by,
            timestamp=datetime.utcnow()
        )
        
        # 4. Event will be dispatched by the calling COG with command context
        # This allows the COG to set the command attribute
        
        return transaction
    
    async def remove_points(
        self,
        user_id: int,
        amount: int,
        reason: str,
        performed_by: int,
        check_consent: bool = True
    ) -> PointsTransaction:
        """
        Remove points from a user with full business logic.
        
        Args:
            user_id: User ID
            amount: Points to remove (positive, will be negated)
            reason: Reason for removing points
            performed_by: ID of user performing the action
            check_consent: Whether to verify consent before processing (default: True)
        
        Returns:
            PointsTransaction with operation details
        
        Raises:
            ValueError: If user not found or consent is required but not given
        """
        # 0. Validate consent if required (LGPD Art. 7º, I)
        if check_consent:
            has_consent = await self.consent_service.has_consent(user_id)
            if not has_consent:
                logger.warning(f"Attempt to remove points from user {user_id} without consent")
                raise ValueError(
                    "User has not given consent for data processing (LGPD Art. 7º, I). "
                    "Please use /consent grant first."
                )
        
        # Get or create user (ensure exists)
        try:
            user = await self.user_repo.get_or_create(user_id)
            before = int(user.get("points", 0) or user.get("exp", 0))
        except Exception as e:
            logger.error(f"Error getting/creating user {user_id} in remove_points: {e}", exc_info=True)
            raise ValueError(f"Failed to get user data: {str(e)}")
        
        # Remove points (negative delta)
        try:
            after = await self.user_repo.update_points(user_id, -abs(amount))
            logger.info(f"Removed {amount} points from user {user_id}: {before} -> {after}")
        except ValueError as ve:
            # Re-raise ValueError as-is (already has user-friendly message)
            raise
        except Exception as e:
            logger.error(f"Database error in remove_points for user {user_id}: {e}", exc_info=True)
            raise ValueError(f"Failed to remove points: {str(e)}")
        
        # Create transaction result
        transaction = PointsTransaction(
            user_id=user_id,
            before=before,
            after=after,
            delta=-abs(amount),
            reason=reason,
            performed_by=performed_by,
            timestamp=datetime.utcnow()
        )
        
        # Event will be dispatched by the calling COG with command context
        # This allows the COG to set the command attribute
        
        return transaction

