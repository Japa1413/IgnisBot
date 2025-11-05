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
VOX_LINK_CHANNELS = [
    "Vox-link I",
    "Vox-link II",
    "Vox-link III",
    "Vox-link IV",
]


class VCLogCog(commands.Cog):
    """Voice channel logging system - restricted to Vox-link channels"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.audit_service = AuditService()
    
    def _is_vox_link_channel(self, channel: discord.VoiceChannel | discord.StageChannel) -> bool:
        """
        Check if channel is a valid Vox-link channel.
        
        Args:
            channel: Voice or Stage channel
        
        Returns:
            True if channel name matches Vox-link pattern
        """
        if not channel:
            return False
        
        # Check exact match
        if channel.name in VOX_LINK_CHANNELS:
            return True
        
        # Check pattern match (case-insensitive, handles variations)
        pattern = r'^vox-link\s+[ivx]+$'
        if re.match(pattern, channel.name, re.IGNORECASE):
            return True
        
        return False
    
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
        amount="How many points to add to each user",
        event="Event or reason for logging",
        evidence="Evidence (image/screenshot/file) for the summary (optional)",
        vc_name="Vox-link channel (optional, defaults to your current VC)"
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
        amount: app_commands.Range[int, 1, 100_000],
        event: str,
        evidence: Optional[discord.Attachment] = None,
        vc_name: Optional[app_commands.Choice[str]] = None,
    ):
        """
        Log points for all users in a Vox-link channel.
        
        Only Vox-link channels are allowed:
        - Vox-link I
        - Vox-link II
        - Vox-link III
        - Vox-link IV
        """
        await interaction.response.defer(thinking=True, ephemeral=False)
        
        if interaction.guild is None:
            await interaction.followup.send("❌ This command can only be used in a server.")
            return
        
        # 1) Resolve the voice channel
        channel: Optional[discord.VoiceChannel | discord.StageChannel] = None
        
        if vc_name is not None:
            # Use specified channel
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
        else:
            # Use user's current VC
            if not interaction.user.voice or not interaction.user.voice.channel:
                await interaction.followup.send(
                    "❌ You are not in a voice channel.\n"
                    "Please join a Vox-link channel or specify one using the `vc_name` parameter.",
                    ephemeral=True
                )
                return
            channel = interaction.user.voice.channel
        
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
                    reason=f"VC Log: {event}",
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
                
                # Create embed
                embed = discord.Embed(
                    title="✅ Points Added",
                    color=discord.Color.dark_green()
                )
                embed.add_field(name="**User:**", value=member.mention, inline=False)
                embed.add_field(
                    name="**Points:**",
                    value=f"{before_points} → {after_points}",
                    inline=False
                )
                embed.add_field(name="**Event:**", value=event or "—", inline=False)
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
                    # Create error embed
                    embed = discord.Embed(
                        title="❌ Consent Required",
                        description=(
                            f"{member.mention} has not given consent for data processing.\n"
                            f"Please ask them to use `/consent grant` first."
                        ),
                        color=discord.Color.orange()
                    )
                    return (embed, member.mention)
                # Re-raise other ValueErrors
                raise
                
            except Exception as ex:
                logger.error(f"Error updating user {member.id} in vc_log: {ex}", exc_info=True)
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"Could not update {member.mention}.\n{str(ex)[:200]}",
                    color=discord.Color.red()
                )
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
            summary = discord.Embed(
                title="📊 Event Summary",
                color=discord.Color.dark_green()
            )
            summary.add_field(name="**Host:**", value=interaction.user.mention, inline=False)
            summary.add_field(name="**Event:**", value=event, inline=False)
            summary.add_field(name="**Channel:**", value=channel.mention, inline=False)
            summary.add_field(
                name="**Attendees:**",
                value=", ".join(attendees) or "None",
                inline=False
            )
            
            if evidence:
                if evidence.content_type and str(evidence.content_type).startswith("image/"):
                    summary.set_image(url=evidence.url)
                else:
                    summary.add_field(name="**Evidence:**", value=evidence.url, inline=False)
            
            summary.timestamp = discord.utils.utcnow()
            footer_icon = getattr(interaction.user.display_avatar, "url", None)
            summary.set_footer(
                text=f"Logged by {interaction.user.display_name}",
                icon_url=footer_icon
            )
            
            try:
                await summary_channel.send(embed=summary)
            except Exception as e:
                logger.error(f"Error sending summary to channel: {e}", exc_info=True)
        
        # 8) Final confirmation
        await interaction.followup.send(
            f"✅ Points have been logged for **{len(attendees)}** members in **{channel.name}**."
        )
        
        # Log audit
        try:
            await self.audit_service.log_operation(
                user_id=0,  # Multiple users
                action_type="CREATE",
                data_type="vc_log_batch",
                performed_by=interaction.user.id,
                purpose=f"VC log event: {event}",
                details={
                    "channel": channel.name,
                    "channel_id": channel.id,
                    "amount": amount,
                    "event": event,
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
