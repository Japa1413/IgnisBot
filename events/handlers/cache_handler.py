"""
Cache Handler - Handles cache invalidation for events.
"""

from __future__ import annotations

from discord.ext import commands
from services.cache_service import CacheService
from events.event_types import PointsChangedEvent, UserCreatedEvent
from utils.logger import get_logger

logger = get_logger(__name__)


def setup_cache_handler(bot: commands.Bot) -> None:
    """Setup cache event handlers"""
    
    cache_service = CacheService()
    
    @bot.event
    async def on_points_changed(event: PointsChangedEvent):
        """Handle cache invalidation for points changes"""
        await cache_service.invalidate_user(event.user_id)
        logger.debug(f"Cache invalidated for user_id {event.user_id} (points changed)")
    
    @bot.event
    async def on_user_created(event: UserCreatedEvent):
        """Handle cache invalidation for user creation"""
        await cache_service.invalidate_user(event.user_id)
        logger.debug(f"Cache invalidated for user_id {event.user_id} (user created)")

