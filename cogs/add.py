# cogs/add.py
from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands

from utils.database import get_user, create_user, update_points
from utils.checks import cmd_channel_only, appcmd_channel_only
from utils.config import STAFF_CMDS_CHANNEL_ID
from utils.audit_log import log_data_operation

class AddPointsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="add", description="Adds points to a user.")
    @app_commands.describe(
        member="Target member",
        points="Points to add (positive)",
        reason="Reason for adding points (REQUIRED)"
    )
    @appcmd_channel_only(STAFF_CMDS_CHANNEL_ID)  # slash guard
    async def add(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        points: app_commands.Range[int, 1, 100_000],
        reason: str
    ):
        await interaction.response.defer(thinking=True, ephemeral=False)
        try:
            user = await get_user(member.id)
            if user is None:
                await create_user(member.id)
                user = await get_user(member.id)

            before = int(user["points"])
            # OPTIMIZATION: update_points now returns new value directly
            after = await update_points(
                member.id,
                points,
                performed_by=interaction.user.id,
                purpose=f"Points addition via /add: {reason}"
            )

            embed = discord.Embed(title="Points Added", color=discord.Color.green())
            embed.add_field(name="**User:**", value=f"{member.mention}", inline=True)
            embed.add_field(name="**Points:**", value=f"{before} -> {after}", inline=True)
            embed.add_field(name="**Reason:**", value=reason, inline=True)
            footer_icon = getattr(interaction.user.display_avatar, "url", None)
            embed.set_footer(text=f"{interaction.user.display_name}", icon_url=footer_icon)
            embed.timestamp = discord.utils.utcnow()
            await interaction.followup.send(embed=embed)
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error adding points for user {member.id}: {e}", exc_info=True)
            await interaction.followup.send("❌ DB error while adding points.")

async def setup(bot: commands.Bot):
    await bot.add_cog(AddPointsCog(bot))
