# cogs/remove.py
from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands

from utils.database import get_user, update_points
from utils.checks import appcmd_channel_only
from utils.config import STAFF_CMDS_CHANNEL_ID
from utils.audit_log import log_data_operation

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
        await interaction.response.defer(thinking=True, ephemeral=False)

        user = await get_user(member.id)
        if user is None:
            await interaction.followup.send(f"❌ {member.mention} is not registered.")
            return

        before = int(user["points"])
        # OPTIMIZAÇÃO: update_points agora retorna o novo valor diretamente
        after = await update_points(
            member.id,
            -abs(points),
            performed_by=interaction.user.id,
            purpose=f"Remoção de pontos via /remove: {reason}"
        )

        embed = discord.Embed(title="Points Revoked", color=discord.Color.red())
        embed.add_field(name="**User:**", value=f"{member.mention}", inline=True)
        embed.add_field(name="**Points:**", value=f"{before} -> {after}", inline=True)
        embed.add_field(name="**Reason:**", value=reason, inline=True)
        footer_icon = getattr(interaction.user.display_avatar, "url", None)
        embed.set_footer(text=f"{interaction.user.display_name}", icon_url=footer_icon)
        embed.timestamp = discord.utils.utcnow()
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(RemovePointsCog(bot))
