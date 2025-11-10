# cogs/remove.py
from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands

from utils.checks import appcmd_channel_only
from utils.config import STAFF_CMDS_CHANNEL_ID
from services.points_service import PointsService

class RemovePointsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="remove", description="Removes points from a user.")
    @app_commands.describe(
        member="Target member", 
        points="Points to remove", 
        reason="Reason for removing points (REQUIRED)"
    )
    @appcmd_channel_only(STAFF_CMDS_CHANNEL_ID)
    async def remove(self, interaction: discord.Interaction, member: discord.Member, points: int, reason: str):
        # Use safe interaction response helper for timeout protection
        from utils.interaction_helpers import safe_interaction_response
        
        async def defer_response():
            await interaction.response.defer(thinking=True, ephemeral=False)
        
        success = await safe_interaction_response(interaction, defer_response, timeout=3.0, retry_count=1)
        if not success:
            # If defer failed, try to send error message
            try:
                if not interaction.response.is_done():
                    error_embed = discord.Embed(
                        title="Command Failed",
                        description="Failed to process command. Please try again.",
                        color=discord.Color.from_rgb(211, 47, 47)  # Dark red
                    )
                    await interaction.response.send_message(embed=error_embed, ephemeral=True)
            except Exception:
                pass
            return
        
        try:
            # Use Service Layer
            service = PointsService(self.bot)
            transaction = await service.remove_points(
                user_id=member.id,
                amount=points,
                reason=reason,
                performed_by=interaction.user.id
            )
            
            # Dispatch event with command context (wrap in try-except to not break on event errors)
            try:
                from events.event_types import PointsChangedEvent
                event = PointsChangedEvent(
                    user_id=transaction.user_id,
                    before=transaction.before,
                    after=transaction.after,
                    delta=transaction.delta,
                    reason=transaction.reason,
                    performed_by=transaction.performed_by,
                    command="/remove"
                )
                await self.bot.dispatch('points_changed', event)
            except Exception as event_error:
                # Log event error but don't fail the command
                from utils.logger import get_logger
                logger = get_logger(__name__)
                logger.warning(f"Error dispatching points_changed event: {event_error}", exc_info=True)

            # Create clean, aesthetic embed without emojis
            embed = discord.Embed(
                title="Points Removed",
                color=discord.Color.from_rgb(211, 47, 47)  # Dark red
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
                value=f"{transaction.before} → {transaction.after}",
                inline=True
            )
            
            embed.add_field(
                name="Reason",
                value=reason,
                inline=True
            )
            
            embed.timestamp = discord.utils.utcnow()
            footer_icon = getattr(interaction.user.display_avatar, "url", None)
            embed.set_footer(
                text=f"Logged by {interaction.user.display_name}",
                icon_url=footer_icon
            )
            
            await interaction.followup.send(embed=embed)
        except ValueError as e:
            # Handle consent validation errors or user not found
            error_msg = str(e)
            if "consent" in error_msg.lower():
                # Create clean error embed (no emojis)
                error_embed = discord.Embed(
                    title="Consent Required",
                    description=(
                        f"{member.mention} has not given consent for data processing (LGPD Art. 7º, I).\n"
                        f"Please ask them to use `/consent grant` first."
                    ),
                    color=discord.Color.from_rgb(255, 152, 0)  # Orange
                )
                
                # Add user avatar
                if member.avatar:
                    error_embed.set_thumbnail(url=member.avatar.url)
                
                error_embed.timestamp = discord.utils.utcnow()
                footer_icon = getattr(interaction.user.display_avatar, "url", None)
                error_embed.set_footer(
                    text=f"Logged by {interaction.user.display_name}",
                    icon_url=footer_icon
                )
                
                await interaction.followup.send(embed=error_embed, ephemeral=True)
            elif "not found" in error_msg.lower():
                error_embed = discord.Embed(
                    title="User Not Found",
                    description=f"{member.mention} is not registered.",
                    color=discord.Color.from_rgb(211, 47, 47)  # Dark red
                )
                
                if member.avatar:
                    error_embed.set_thumbnail(url=member.avatar.url)
                
                error_embed.timestamp = discord.utils.utcnow()
                footer_icon = getattr(interaction.user.display_avatar, "url", None)
                error_embed.set_footer(
                    text=f"Logged by {interaction.user.display_name}",
                    icon_url=footer_icon
                )
                
                await interaction.followup.send(embed=error_embed)
            else:
                error_embed = discord.Embed(
                    title="Error",
                    description=error_msg,
                    color=discord.Color.from_rgb(211, 47, 47)  # Dark red
                )
                
                if member.avatar:
                    error_embed.set_thumbnail(url=member.avatar.url)
                
                error_embed.timestamp = discord.utils.utcnow()
                footer_icon = getattr(interaction.user.display_avatar, "url", None)
                error_embed.set_footer(
                    text=f"Logged by {interaction.user.display_name}",
                    icon_url=footer_icon
                )
                
                await interaction.followup.send(embed=error_embed)
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error removing points for user {member.id}: {e}", exc_info=True)
            error_embed = discord.Embed(
                title="Database Error",
                description="An error occurred while removing points from the database.",
                color=discord.Color.from_rgb(211, 47, 47)  # Dark red
            )
            
            if member.avatar:
                error_embed.set_thumbnail(url=member.avatar.url)
            
            error_embed.add_field(
                name="Error Details",
                value=str(e)[:200],
                inline=False
            )
            
            error_embed.timestamp = discord.utils.utcnow()
            footer_icon = getattr(interaction.user.display_avatar, "url", None)
            error_embed.set_footer(
                text=f"Logged by {interaction.user.display_name}",
                icon_url=footer_icon
            )
            
            await interaction.followup.send(embed=error_embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(RemovePointsCog(bot))
