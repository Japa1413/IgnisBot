# cogs/leaderboard.py
from __future__ import annotations

import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import aiomysql

from utils.database import get_pool
from services.consent_service import ConsentService

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.consent_service = ConsentService()

    @app_commands.command(name="leaderboard", description="Shows the top 10 users with more points")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        try:
            pool = get_pool()
        except RuntimeError:
            await interaction.followup.send("❌ Database not initialized.")
            return

        # Use connection pool instead of creating direct connection
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Filter users with consent (LGPD Art. 7º, I - Base Legal: Consentimento)
                await cursor.execute(
                    """
                    SELECT u.user_id, u.points 
                    FROM users u
                    INNER JOIN user_consent uc ON u.user_id = uc.user_id
                    WHERE uc.consent_given = TRUE
                    ORDER BY u.points DESC 
                    LIMIT 10
                    """
                )
                leaderboard = await cursor.fetchall()

        if not leaderboard:
            await interaction.followup.send("The Leaderboard is empty at the moment")
            return

        # Creating an embed for the leaderboard
        embed = discord.Embed(
            title="🏆 Leaderboard - Top 10",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        # OPTIMIZATION: Fetch all users in parallel (avoids N+1 query problem)
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