"""
Gamification Event Handlers - Automatic XP gain from user activities.
"""

from __future__ import annotations

from typing import Optional
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from services.xp_service import XPService
from services.level_service import LevelService
from services.consent_service import ConsentService
from utils.logger import get_logger

logger = get_logger(__name__)

# XP rates per source
XP_RATES = {
    "voice_per_minute": 10,  # +10 XP per minute in voice
    "message": 1,  # +1 XP per message
    "reaction": 0.5,  # +0.5 XP per reaction (rounded down)
}

# Tracking voice channel time
_voice_join_times: dict[int, datetime] = {}  # user_id -> join_time


class GamificationHandlers(commands.Cog):
    """Event handlers for automatic gamification"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.xp_service = XPService()
        self.level_service = LevelService()
        self.consent_service = ConsentService()
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Award XP for messages (with daily limit).
        
        Filters:
        - Ignore bots
        - Ignore DMs (only server messages)
        - Ignore commands
        """
        # Ignore bots
        if message.author.bot:
            return
        
        # Ignore DMs
        if message.guild is None:
            return
        
        # Ignore commands (both prefix and slash)
        if message.content.startswith(self.bot.command_prefix) or message.content.startswith('/'):
            return
        
        # Check consent (LGPD compliance)
        try:
            has_consent = await self.consent_service.has_consent(message.author.id)
            if not has_consent:
                return  # Silently skip if no consent
        except Exception as e:
            logger.warning(f"Error checking consent for user {message.author.id}: {e}")
            return  # Fail silently to not break message handling
        
        # Award XP (with daily limit checking)
        try:
            result = await self.xp_service.add_xp(
                user_id=message.author.id,
                xp_amount=XP_RATES["message"],
                source="message",
                details={
                    "channel_id": message.channel.id,
                    "channel_name": message.channel.name,
                    "guild_id": message.guild.id,
                    "message_length": len(message.content)
                }
            )
            
            # Check if level up
            if result["added"] > 0:
                level_result = await self.level_service.update_level_if_needed(
                    message.author.id,
                    result["total"]
                )
                
                if level_result["level_changed"]:
                    logger.info(
                        f"User {message.author.id} leveled up from "
                        f"{level_result['old_level']} to {level_result['new_level']} "
                        f"via message XP"
                    )
                    # Dispatch level up event (for future notifications)
                    await self.bot.dispatch(
                        'level_up',
                        {
                            "user_id": message.author.id,
                            "old_level": level_result["old_level"],
                            "new_level": level_result["new_level"],
                            "source": "message"
                        }
                    )
        
        except Exception as e:
            logger.error(f"Error awarding message XP to {message.author.id}: {e}", exc_info=True)
            # Fail silently to not break message handling
    
    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        """
        Track voice channel time and award XP.
        
        Awards XP when user leaves voice channel based on time spent.
        """
        # Ignore bots
        if member.bot:
            return
        
        # User joined a voice channel
        if before.channel is None and after.channel is not None:
            _voice_join_times[member.id] = datetime.utcnow()
            logger.debug(f"User {member.id} joined voice channel {after.channel.id}")
        
        # User left a voice channel
        elif before.channel is not None and after.channel is None:
            if member.id in _voice_join_times:
                join_time = _voice_join_times.pop(member.id)
                time_spent = datetime.utcnow() - join_time
                minutes_spent = int(time_spent.total_seconds() / 60)
                
                if minutes_spent > 0:
                    # Check consent
                    try:
                        has_consent = await self.consent_service.has_consent(member.id)
                        if not has_consent:
                            return  # Silently skip
                    except Exception as e:
                        logger.warning(f"Error checking consent for user {member.id}: {e}")
                        return
                    
                    # Award XP (with daily limit)
                    xp_to_award = minutes_spent * XP_RATES["voice_per_minute"]
                    
                    try:
                        result = await self.xp_service.add_xp(
                            user_id=member.id,
                            xp_amount=xp_to_award,
                            source="voice",
                            details={
                                "channel_id": before.channel.id if before.channel else None,
                                "channel_name": before.channel.name if before.channel else None,
                                "minutes_spent": minutes_spent,
                                "guild_id": member.guild.id if member.guild else None
                            }
                        )
                        
                        logger.debug(
                            f"User {member.id} gained {result['added']} XP "
                            f"({minutes_spent} min in VC)"
                        )
                        
                        # Check if level up
                        if result["added"] > 0:
                            level_result = await self.level_service.update_level_if_needed(
                                member.id,
                                result["total"]
                            )
                            
                            if level_result["level_changed"]:
                                logger.info(
                                    f"User {member.id} leveled up from "
                                    f"{level_result['old_level']} to {level_result['new_level']} "
                                    f"via voice XP"
                                )
                                await self.bot.dispatch(
                                    'level_up',
                                    {
                                        "user_id": member.id,
                                        "old_level": level_result["old_level"],
                                        "new_level": level_result["new_level"],
                                        "source": "voice"
                                    }
                                )
                    
                    except Exception as e:
                        logger.error(f"Error awarding voice XP to {member.id}: {e}", exc_info=True)
        
        # User switched voice channels
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            # Calculate XP for time in old channel
            if member.id in _voice_join_times:
                join_time = _voice_join_times.pop(member.id)
                time_spent = datetime.utcnow() - join_time
                minutes_spent = int(time_spent.total_seconds() / 60)
                
                if minutes_spent > 0:
                    # Award XP for old channel
                    try:
                        has_consent = await self.consent_service.has_consent(member.id)
                        if not has_consent:
                            return
                    except Exception:
                        return
                    
                    xp_to_award = minutes_spent * XP_RATES["voice_per_minute"]
                    
                    try:
                        result = await self.xp_service.add_xp(
                            user_id=member.id,
                            xp_amount=xp_to_award,
                            source="voice",
                            details={
                                "channel_id": before.channel.id,
                                "channel_name": before.channel.name,
                                "minutes_spent": minutes_spent,
                                "guild_id": member.guild.id if member.guild else None
                            }
                        )
                        
                        if result["added"] > 0:
                            await self.level_service.update_level_if_needed(
                                member.id,
                                result["total"]
                            )
                    except Exception as e:
                        logger.error(f"Error awarding voice XP on switch: {e}")
            
            # Start tracking new channel
            _voice_join_times[member.id] = datetime.utcnow()
            logger.debug(f"User {member.id} switched to voice channel {after.channel.id}")


async def setup(bot: commands.Bot):
    """Load the gamification handlers cog"""
    # Remove existing on_voice_state_update handler if it conflicts
    # Our handler will work alongside the existing voice_logs handler
    await bot.add_cog(GamificationHandlers(bot))
    logger.info("✅ Gamification handlers loaded (XP system active)")

