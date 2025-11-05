"""
Audit Handler - Handles audit logging for events.
"""

from __future__ import annotations

import asyncio
from discord.ext import commands
from services.audit_service import AuditService
from events.event_types import PointsChangedEvent, UserCreatedEvent
from utils.logger import get_logger

logger = get_logger(__name__)


def setup_audit_handler(bot: commands.Bot) -> None:
    """Setup audit event handlers"""
    
    audit_service = AuditService()
    
    @bot.event
    async def on_points_changed(event: PointsChangedEvent):
        """Handle audit logging for points changes"""
        # Fire-and-forget to avoid blocking
        asyncio.create_task(
            audit_service.log_operation(
                user_id=event.user_id,
                action_type="UPDATE",
                data_type="points",
                performed_by=event.performed_by,
                purpose=f"Points {event.command or 'change'}: {event.reason}",
                details={
                    "before": event.before,
                    "after": event.after,
                    "delta": event.delta
                }
            )
        )
    
    @bot.event
    async def on_user_created(event: UserCreatedEvent):
        """Handle audit logging for user creation"""
        # Fire-and-forget
        asyncio.create_task(
            audit_service.log_operation(
                user_id=event.user_id,
                action_type="CREATE",
                data_type="user_data",
                purpose="New user record creation"
            )
        )

