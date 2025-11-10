# cogs/vc_log.py
"""
VC Log Cog - Voice Channel Points Logging System

Restricted to Vox-link channels only.
All points are stored exclusively in the SQL database (no external integrations).
"""

from __future__ import annotations

import asyncio
import re
from typing import Optional, List

import discord
from discord.ext import commands
from discord import app_commands

from services.points_service import PointsService
from services.user_service import UserService
from services.audit_service import AuditService
from utils.checks import appcmd_channel_only
from utils.config import (
    STAFF_CMDS_CHANNEL_ID,
    SUMMARY_CHANNEL_FALLBACK_ID,
)
from utils.logger import get_logger

logger = get_logger(__name__)

# Vox-link channels that are allowed for logging
# Note: Using exact Unicode characters (Roman numerals) as they appear in Discord
VOX_LINK_CHANNELS = [
    "Vox-link Ⅰ",
    "Vox-link ⅠⅠ",
    "Vox-link ⅠⅠⅠ",
    "Vox-link Ⅳ",
]


class VCLogCog(commands.Cog):
    """Voice channel logging system - restricted to Vox-link channels"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.audit_service = AuditService()
    
    def _is_vox_link_channel(self, channel: discord.VoiceChannel | discord.StageChannel) -> bool:
        """
        Check if channel is a valid Vox-link channel.
        
        Uses exact Unicode character matching for Roman numerals.
        
        Args:
            channel: Voice or Stage channel
        
        Returns:
            True if channel name matches exactly one of the Vox-link channels
        """
        if not channel:
            return False
        
        # Check exact match (case-sensitive for Unicode characters)
        return channel.name in VOX_LINK_CHANNELS
    
    def _find_vox_link_channels(self, guild: discord.Guild) -> List[discord.VoiceChannel | discord.StageChannel]:
        """
        Find all Vox-link channels in the guild.
        
        Args:
            guild: Discord guild
        
        Returns:
            List of Vox-link channels
        """
        channels = []
        
        # Check voice channels
        for channel in guild.voice_channels:
            if self._is_vox_link_channel(channel):
                channels.append(channel)
        
        # Check stage channels
        for channel in guild.stage_channels:
            if self._is_vox_link_channel(channel):
                channels.append(channel)
        
        return channels
    
    @app_commands.command(
        name="vc_log",
        description="Add points to all non-bot users in a Vox-link voice channel."
    )
    @app_commands.describe(
        vc_name="Vox-link channel (required)",
        amount="How many points to add to each user",
        event_type="Event type or reason for logging"
    )
    @app_commands.choices(
        vc_name=[
            app_commands.Choice(name=vc, value=vc) for vc in VOX_LINK_CHANNELS
        ]
    )
    @appcmd_channel_only(STAFF_CMDS_CHANNEL_ID)
    async def vc_log(
        self,
        interaction: discord.Interaction,
        vc_name: app_commands.Choice[str],
        amount: app_commands.Range[int, 1, 100_000],
        event_type: str,
    ):
        """
        Log points for all users in a Vox-link channel.
        
        Only Vox-link channels are allowed:
        - Vox-link Ⅰ
        - Vox-link ⅠⅠ
        - Vox-link ⅠⅠⅠ
        - Vox-link Ⅳ
        """
        await interaction.response.defer(thinking=True, ephemeral=False)
        
        if interaction.guild is None:
            await interaction.followup.send("❌ This command can only be used in a server.")
            return
        
        # 1) Resolve the voice channel (vc_name is now required)
        channel_name = vc_name.value
        channel = discord.utils.get(
            interaction.guild.voice_channels, 
            name=channel_name
        ) or discord.utils.get(
            interaction.guild.stage_channels,
            name=channel_name
        )
        
        if channel is None:
            await interaction.followup.send(
                f"❌ Vox-link channel '{channel_name}' not found.",
                ephemeral=True
            )
            return
        
        # 2) Validate that it's a Vox-link channel
        if not self._is_vox_link_channel(channel):
            available_channels = ", ".join(f"**{vc}**" for vc in VOX_LINK_CHANNELS)
            await interaction.followup.send(
                f"❌ Channel **{channel.name}** is not a valid Vox-link channel.\n\n"
                f"**Allowed channels:**\n{available_channels}\n\n"
                f"Please use one of the Vox-link channels or specify a channel using the `vc_name` parameter.",
                ephemeral=True
            )
            return
        
        # 3) Gather members (ignore bots)
        members: List[discord.Member] = [m for m in channel.members if not m.bot]
        if not members:
            await interaction.followup.send(
                f"❌ No members found in **{channel.name}**.",
                ephemeral=True
            )
            return
        
        embeds: List[discord.Embed] = []
        attendees: List[str] = []
        
        # Use Service Layer (Ignis Architecture)
        points_service = PointsService(self.bot)
        user_service = UserService()
        
        # 5) Process members in parallel
        async def process_member(member: discord.Member) -> Optional[tuple]:
            """Process a member and return embed and mention"""
            try:
                # Ensure user exists in Ignis system
                user_data = await user_service.ensure_exists(member.id)
                before_points = int(user_data.get("points", 0))
                
                # Add points using Ignis service (consent validation included)
                transaction = await points_service.add_points(
                    user_id=member.id,
                    amount=amount,
                    reason=f"VC Log: {event_type}",
                    performed_by=interaction.user.id,
                    check_consent=True  # Validate consent (LGPD Art. 7º, I)
                )
                
                # Dispatch event for handlers (audit, cache)
                try:
                    from events.event_types import PointsChangedEvent
                    event_obj = PointsChangedEvent(
                        user_id=transaction.user_id,
                        before=transaction.before,
                        after=transaction.after,
                        delta=transaction.delta,
                        reason=transaction.reason,
                        performed_by=transaction.performed_by,
                        command="/vc_log"
                    )
                    await self.bot.dispatch('points_changed', event_obj)
                except Exception as event_error:
                    logger.warning(f"Error dispatching points_changed event: {event_error}", exc_info=True)
                
                after_points = transaction.after
                
                # Create clean, aesthetic embed without emojis
                embed = discord.Embed(
                    title="Points Added",
                    color=discord.Color.from_rgb(46, 125, 50)  # Dark green
                )
                
                # Add user avatar as thumbnail
                if member.avatar:
                    embed.set_thumbnail(url=member.avatar.url)
                
                # Add fields in a clean, organized way
                embed.add_field(
                    name="User",
                    value=member.mention,
                    inline=True
                )
                
                embed.add_field(
                    name="Points",
                    value=f"{before_points} → {after_points}",
                    inline=True
                )
                
                embed.add_field(
                    name="Event Type",
                    value=event_type or "—",
                    inline=True
                )
                
                embed.timestamp = discord.utils.utcnow()
                footer_icon = getattr(interaction.user.display_avatar, "url", None)
                embed.set_footer(
                    text=f"Logged by {interaction.user.display_name}",
                    icon_url=footer_icon
                )
                
                return (embed, member.mention)
                
            except ValueError as ex:
                # Handle consent validation errors
                error_msg = str(ex)
                if "consent" in error_msg.lower():
                    logger.warning(f"User {member.id} attempted VC log without consent")
                    # Create error embed (clean, no emojis)
                    embed = discord.Embed(
                        title="Consent Required",
                        description=(
                            f"{member.mention} has not given consent for data processing.\n"
                            f"Please ask them to use `/consent grant` first."
                        ),
                        color=discord.Color.from_rgb(255, 152, 0)  # Orange
                    )
                    
                    # Add user avatar
                    if member.avatar:
                        embed.set_thumbnail(url=member.avatar.url)
                    return (embed, member.mention)
                # Re-raise other ValueErrors
                raise
                
            except Exception as ex:
                logger.error(f"Error updating user {member.id} in vc_log: {ex}", exc_info=True)
                embed = discord.Embed(
                    title="Error",
                    description=f"Could not update {member.mention}.\n{str(ex)[:200]}",
                    color=discord.Color.from_rgb(211, 47, 47)  # Dark red
                )
                
                # Add user avatar
                if member.avatar:
                    embed.set_thumbnail(url=member.avatar.url)
                return (embed, member.mention)
        
        # Process all members in parallel
        tasks = [process_member(member) for member in members]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error processing member: {result}", exc_info=True)
                continue
            if result is None:
                continue
            embed, mention = result
            embeds.append(embed)
            if mention:
                attendees.append(mention)
        
        # 6) Send user embeds in batches
        BATCH_SIZE = 4
        for i in range(0, len(embeds), BATCH_SIZE):
            await interaction.followup.send(embeds=embeds[i:i+BATCH_SIZE])
        
        # 7) Send summary to log channel
        summary_channel = self.bot.get_channel(SUMMARY_CHANNEL_FALLBACK_ID)
        
        if isinstance(summary_channel, (discord.TextChannel, discord.Thread)):
            # Create clean summary embed (no emojis)
            summary = discord.Embed(
                title="Event Summary",
                color=discord.Color.from_rgb(46, 125, 50),  # Dark green
                timestamp=discord.utils.utcnow()
            )
            
            summary.add_field(
                name="Host",
                value=interaction.user.mention,
                inline=True
            )
            
            summary.add_field(
                name="Event Type",
                value=event_type,
                inline=True
            )
            
            summary.add_field(
                name="Channel",
                value=channel.mention,
                inline=True
            )
            
            summary.add_field(
                name="Attendees",
                value=", ".join(attendees) if attendees else "None",
                inline=False
            )
            
            summary.add_field(
                name="Points",
                value=str(amount),
                inline=True
            )
            
            footer_icon = getattr(interaction.user.display_avatar, "url", None)
            summary.set_footer(
                text=f"Logged by {interaction.user.display_name}",
                icon_url=footer_icon
            )
            
            try:
                await summary_channel.send(embed=summary)
            except Exception as e:
                logger.error(f"Error sending summary to channel: {e}", exc_info=True)
        
        # 8) Final confirmation (beautiful embed)
        response_embed = discord.Embed(
            title="Points Logged",
            description=f"Points have been logged for **{len(attendees)}** member(s) in {channel.mention}.",
            color=discord.Color.from_rgb(46, 125, 50),  # Dark green
            timestamp=discord.utils.utcnow()
        )
        
        # Add summary information
        response_embed.add_field(
            name="Channel",
            value=channel.mention,
            inline=True
        )
        
        response_embed.add_field(
            name="Members",
            value=str(len(attendees)),
            inline=True
        )
        
        response_embed.add_field(
            name="Points",
            value=str(amount),
            inline=True
        )
        
        # Set footer
        footer_icon = getattr(interaction.user.display_avatar, "url", None)
        response_embed.set_footer(
            text=f"Logged by {interaction.user.display_name}",
            icon_url=footer_icon
        )
        
        await interaction.followup.send(embed=response_embed)
        
        # Log audit
        try:
            await self.audit_service.log_operation(
                user_id=0,  # Multiple users
                action_type="CREATE",
                data_type="vc_log_batch",
                performed_by=interaction.user.id,
                purpose=f"VC log event: {event_type}",
                details={
                    "channel": channel.name,
                    "channel_id": channel.id,
                    "amount": amount,
                    "event_type": event_type,
                    "attendees_count": len(attendees),
                    "attendees": [int(m.id) for m in members]
                }
            )
        except Exception as e:
            logger.error(f"Error logging audit: {e}", exc_info=True)


async def setup(bot: commands.Bot):
    """Setup function to load the cog"""
    await bot.add_cog(VCLogCog(bot))
    logger.info("✅ VC Log cog loaded (Vox-link channels only)")
