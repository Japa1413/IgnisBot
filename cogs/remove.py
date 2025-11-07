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
                    await interaction.response.send_message(
                        "❌ Failed to process command. Please try again.",
                        ephemeral=True
                    )
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

            embed = discord.Embed(title="Points Revoked", color=discord.Color.red())
            embed.add_field(name="**User:**", value=f"{member.mention}", inline=True)
            embed.add_field(name="**Points:**", value=f"{transaction.before} -> {transaction.after}", inline=True)
            embed.add_field(name="**Reason:**", value=reason, inline=True)
            footer_icon = getattr(interaction.user.display_avatar, "url", None)
            embed.set_footer(text=f"{interaction.user.display_name}", icon_url=footer_icon)
            embed.timestamp = discord.utils.utcnow()
            
            await interaction.followup.send(embed=embed)
        except ValueError as e:
            # Handle consent validation errors or user not found
            error_msg = str(e)
            if "consent" in error_msg.lower():
                await interaction.followup.send(
                    f"❌ {member.mention} has not given consent for data processing (LGPD Art. 7º, I).\n"
                    f"Please ask them to use `/consent grant` first.",
                    ephemeral=True
                )
            elif "not found" in error_msg.lower():
                await interaction.followup.send(f"❌ {member.mention} is not registered.")
            else:
                await interaction.followup.send(f"❌ {error_msg}")
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error removing points for user {member.id}: {e}", exc_info=True)
            await interaction.followup.send("❌ DB error while removing points.")

async def setup(bot: commands.Bot):
    await bot.add_cog(RemovePointsCog(bot))
