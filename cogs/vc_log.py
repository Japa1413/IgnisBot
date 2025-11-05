# cogs/vc_log.py
from __future__ import annotations

import asyncio
from typing import Optional, List

import discord
from discord.ext import commands
from discord import app_commands

from services.points_service import PointsService
from services.user_service import UserService
from utils.checks import appcmd_channel_only
from utils.config import (
    STAFF_CMDS_CHANNEL_ID,
    SUMMARY_CHANNEL_FALLBACK_ID,
    ALLOWED_VC_IDS
)

class VCLogCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="vc_log",
        description="Add points to all non-bot users currently in a voice channel."
    )
    @app_commands.describe(
        amount="How many points to add to each user",
        event="Event or reason",
        evidence="Evidence (image/screenshot/file) for the summary (optional)",
        vc_channel="Voice channel (optional). Defaults to the one you are in."
    )
    @appcmd_channel_only(STAFF_CMDS_CHANNEL_ID)
    async def vc_log(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100_000],
        event: str,
        evidence: Optional[discord.Attachment] = None,
        vc_channel: Optional[discord.VoiceChannel] = None,
    ):
        await interaction.response.defer(thinking=True, ephemeral=False)

        if interaction.guild is None:
            await interaction.followup.send("This command can only be used in a server.")
            return

        # 1) Resolve the voice channel
        channel: Optional[discord.VoiceChannel]
        if vc_channel is not None:
            channel = vc_channel
        else:
            # Use the host's current VC
            if not interaction.user or not getattr(interaction.user, "voice", None) or not interaction.user.voice:
                await interaction.followup.send("You are not in a voice channel.")
                return
            channel = interaction.user.voice.channel  # type: ignore[assignment]

        # 2) Validate whitelist
        if channel.id not in ALLOWED_VC_IDS:
            await interaction.followup.send(
                f"❌ This voice channel is not allowed for logging.\n"
                f"Channel: {channel.mention} (`{channel.id}`)",
            )
            return

        # 3) Gather members (ignore bots)
        members: List[discord.Member] = [m for m in channel.members if not m.bot]
        if not members:
            await interaction.followup.send(f"No members found in **{channel.name}**.")
            return

        embeds: List[discord.Embed] = []
        attendees: List[str] = []

        # Use Service Layer (NEW - Architecture Phase 2)
        points_service = PointsService(self.bot)
        user_service = UserService()

        # OPTIMIZATION: Process members in parallel where possible
        async def process_member(member: discord.Member) -> Optional[tuple]:
            """Process a member and return embed and mention"""
            try:
                # Ensure user exists
                user_data = await user_service.ensure_exists(member.id)
                before = int(user_data.get("points", 0))
                
                # Add points using service (consent validation included)
                transaction = await points_service.add_points(
                    user_id=member.id,
                    amount=amount,
                    reason=f"VC Log: {event}",
                    performed_by=interaction.user.id,
                    check_consent=True  # Validate consent (LGPD Art. 7º, I)
                )
                
                # Dispatch event with command context for handlers (audit, cache)
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
                
                after = transaction.after

                e = discord.Embed(title="Points Added", color=discord.Color.dark_green())
                e.add_field(name="**User:**", value=member.mention, inline=False)
                e.add_field(name="**Points:**", value=f"{before} -> {after}", inline=False)
                e.add_field(name="**Reason:**", value=event or "—", inline=False)
                e.timestamp = discord.utils.utcnow()
                footer_icon = getattr(interaction.user.display_avatar, "url", None)
                e.set_footer(text=f"{interaction.user.display_name}", icon_url=footer_icon)
                
                return (e, member.mention)
            except ValueError as ex:
                # Handle consent validation errors
                error_msg = str(ex)
                if "consent" in error_msg.lower():
                    from utils.logger import get_logger
                    logger = get_logger(__name__)
                    logger.warning(f"User {member.id} attempted VC log without consent")
                    # Skip this user but continue with others - return None
                    return None
                # Re-raise other ValueErrors
                raise
            except Exception as ex:
                from utils.logger import get_logger
                logger = get_logger(__name__)
                logger.error(f"Error updating user {member.id} in vc_log: {ex}", exc_info=True)
                err = discord.Embed(
                    title="Error",
                    description=f"Could not update {member.mention}.",
                    color=discord.Color.red()
                )
                return (err, member.mention)

        # 4) Process all members in parallel
        tasks = [process_member(member) for member in members]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception) or result is None:
                continue
            embed, mention = result
            embeds.append(embed)
            attendees.append(mention)

        # 5) Send user embeds in batches
        BATCH = 4
        for i in range(0, len(embeds), BATCH):
            await interaction.followup.send(embeds=embeds[i:i+BATCH])

        # 6) Send summary to log channel (configured or fallback)
        summary_channel_id = getattr(self.bot, "log_channel_id", None) or SUMMARY_CHANNEL_FALLBACK_ID
        summary_channel = interaction.client.get_channel(summary_channel_id)

        if isinstance(summary_channel, (discord.TextChannel, discord.Thread)):
            summary = discord.Embed(title="Event Summary", color=discord.Color.dark_green())
            summary.add_field(name="Host", value=interaction.user.mention, inline=False)
            summary.add_field(name="Event", value=event, inline=False)
            summary.add_field(name="Channel", value=channel.mention, inline=False)
            summary.add_field(name="Attendees", value=", ".join(attendees) or "None", inline=False)

            if evidence:
                if evidence.content_type and str(evidence.content_type).startswith("image/"):
                    summary.set_image(url=evidence.url)
                else:
                    summary.add_field(name="Evidence", value=evidence.url, inline=False)

            summary.timestamp = discord.utils.utcnow()
            footer_icon = getattr(interaction.user.display_avatar, "url", None)
            summary.set_footer(text=f"{interaction.user.display_name}", icon_url=footer_icon)

            await summary_channel.send(embed=summary)

        await interaction.followup.send(
            f"✅ Points have been logged for members in **{channel.name}**."
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(VCLogCog(bot))
