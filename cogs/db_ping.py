# cogs/db_ping.py
from __future__ import annotations

import time
import discord
from discord.ext import commands
from discord import app_commands
from utils.database import get_user

class DBPingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="dbping", description="Quick DB connectivity check.")
    async def dbping(self, interaction: discord.Interaction, user: discord.Member | None = None):
        await interaction.response.defer(ephemeral=True, thinking=True)
        target = user or interaction.user
        try:
            t0 = time.perf_counter()
            _ = await get_user(target.id)   # simple roundtrip
            dt = (time.perf_counter() - t0) * 1000.0
            await interaction.followup.send(f"✅ DB OK in **{dt:.1f}ms**", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ DB error: `{e}`", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(DBPingCog(bot))
