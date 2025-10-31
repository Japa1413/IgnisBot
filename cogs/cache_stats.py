# cogs/cache_stats.py
"""
Cache Statistics Cog

Provides commands to monitor cache performance and statistics.
"""

from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands

from utils.cache import get_cache_stats
from utils.logger import get_logger

logger = get_logger(__name__)


class CacheStatsCog(commands.Cog):
    """Cog for cache statistics and monitoring"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(
        name="cache_stats",
        description="Display cache performance statistics"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def cache_stats(self, interaction: discord.Interaction):
        """Display current cache statistics"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            stats = get_cache_stats()
            
            embed = discord.Embed(
                title="📊 Cache Statistics",
                description="Performance metrics for the caching system",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Hit Rate",
                value=f"**{stats['hit_rate']}**",
                inline=True
            )
            
            embed.add_field(
                name="Total Requests",
                value=f"**{stats['hits'] + stats['misses']}**",
                inline=True
            )
            
            embed.add_field(
                name="Cache Entries",
                value=f"**{stats['entries']}**",
                inline=True
            )
            
            embed.add_field(
                name="Cache Hits",
                value=f"**{stats['hits']}**",
                inline=True
            )
            
            embed.add_field(
                name="Cache Misses",
                value=f"**{stats['misses']}**",
                inline=True
            )
            
            # Performance indicator
            hit_rate_float = float(stats['hit_rate'].replace('%', ''))
            if hit_rate_float >= 60:
                status_emoji = "🟢"
                status_text = "Excellent"
            elif hit_rate_float >= 40:
                status_emoji = "🟡"
                status_text = "Good"
            else:
                status_emoji = "🔴"
                status_text = "Needs Improvement"
            
            embed.add_field(
                name="Status",
                value=f"{status_emoji} **{status_text}**",
                inline=False
            )
            
            embed.set_footer(text="Cache TTL: 30 seconds")
            embed.timestamp = discord.utils.utcnow()
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Cache stats retrieved by {interaction.user.id}")
            
        except Exception as e:
            logger.error(f"Error retrieving cache stats: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Error retrieving cache statistics.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(CacheStatsCog(bot))

