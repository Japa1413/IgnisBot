# cogs/leaderboard.py
from __future__ import annotations

import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import aiomysql

from utils.database import get_pool

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Shows the top 10 users with more points")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        try:
            pool = get_pool()
        except RuntimeError:
            await interaction.followup.send("❌ Database not initialized.")
            return

        # Usar pool de conexões ao invés de criar conexão direta
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(
                    "SELECT user_id, points FROM users ORDER BY points DESC LIMIT 10"
                )
                leaderboard = await cursor.fetchall()

        if not leaderboard:
            await interaction.followup.send("The Leaderboard is empty at the moment")
            return

        # Criando um embed para a leaderboard
        embed = discord.Embed(
            title="🏆 Leaderboard - Top 10",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        # OPTIMIZAÇÃO: Buscar todos os usuários em paralelo (evita N+1 query problem)
        user_ids = [row["user_id"] for row in leaderboard]
        user_fetches = [self.bot.fetch_user(uid) for uid in user_ids]
        users_results = await asyncio.gather(*user_fetches, return_exceptions=True)

        for i, (row, user_result) in enumerate(zip(leaderboard, users_results), start=1):
            if isinstance(user_result, Exception) or user_result is None:
                name = "[Unknown User]"
            else:
                try:
                    name = user_result.name
                except Exception:
                    name = "[Unknown User]"

            embed.add_field(
                name=f"{i}. {name}",
                value=f"💠 {row['points']} points",
                inline=False
            )

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot))