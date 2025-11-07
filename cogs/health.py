"""
Health Check Cog - Command to check bot health and system status.
"""

from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands
from utils.health_check import get_health_check
from utils.logger import get_logger

logger = get_logger(__name__)


class HealthCog(commands.Cog):
    """Cog for health check command"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.health_check = get_health_check()
    
    @app_commands.command(
        name="health",
        description="Check bot health and system status"
    )
    @app_commands.guild_only()
    async def health(self, interaction: discord.Interaction):
        """Check bot health and system status"""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        try:
            # Get health report
            report = await self.health_check.get_full_health_report()
            
            # Determine embed color based on status
            if report["status"] == "healthy":
                color = discord.Color.green()
                status_emoji = "✅"
            elif report["status"] == "degraded":
                color = discord.Color.orange()
                status_emoji = "⚠️"
            else:
                color = discord.Color.red()
                status_emoji = "❌"
            
            # Create embed
            embed = discord.Embed(
                title=f"{status_emoji} Bot Health Status",
                description=f"**Overall Status:** {report['status'].upper()}",
                color=color,
                timestamp=discord.utils.utcnow()
            )
            
            # Database section
            db = report.get("database", {})
            db_status = db.get("status", "unknown")
            db_emoji = "✅" if db_status == "healthy" else "❌"
            db_info = f"{db_emoji} **Status:** {db_status.upper()}\n"
            if "latency_ms" in db:
                db_info += f"⏱️ **Latency:** {db['latency_ms']}ms\n"
            if "pool_size" in db:
                db_info += f"🔌 **Pool Size:** {db['pool_size']}\n"
            if "pool_utilization" in db:
                db_info += f"📊 **Utilization:** {db['pool_utilization']}\n"
            if "error" in db:
                db_info += f"❌ **Error:** {db['error']}\n"
            embed.add_field(name="🗄️ Database", value=db_info, inline=False)
            
            # Cache section
            cache = report.get("cache", {})
            cache_status = cache.get("status", "unknown")
            cache_emoji = "✅" if cache_status == "healthy" else "❌"
            cache_info = f"{cache_emoji} **Status:** {cache_status.upper()}\n"
            if "hit_rate" in cache:
                cache_info += f"📈 **Hit Rate:** {cache['hit_rate']}\n"
            if "hits" in cache:
                cache_info += f"✅ **Hits:** {cache['hits']}\n"
            if "misses" in cache:
                cache_info += f"❌ **Misses:** {cache['misses']}\n"
            if "entries" in cache:
                cache_info += f"📦 **Entries:** {cache['entries']}\n"
            if "error" in cache:
                cache_info += f"❌ **Error:** {cache['error']}\n"
            embed.add_field(name="💾 Cache", value=cache_info, inline=False)
            
            # Integrations section
            integrations = report.get("integrations", {})
            integrations_info = ""
            
            # Bloxlink
            bloxlink = integrations.get("bloxlink", {})
            bloxlink_status = bloxlink.get("status", "unknown")
            bloxlink_emoji = "✅" if bloxlink_status == "healthy" else "❌"
            integrations_info += f"{bloxlink_emoji} **Bloxlink:** {bloxlink_status.upper()}"
            if "latency_ms" in bloxlink:
                integrations_info += f" ({bloxlink['latency_ms']}ms)"
            integrations_info += "\n"
            
            # Roblox API
            roblox = integrations.get("roblox_api", {})
            roblox_status = roblox.get("status", "unknown")
            roblox_emoji = "✅" if roblox_status == "healthy" else "❌"
            integrations_info += f"{roblox_emoji} **Roblox API:** {roblox_status.upper()}"
            if "latency_ms" in roblox:
                integrations_info += f" ({roblox['latency_ms']}ms)"
            integrations_info += "\n"
            
            embed.add_field(name="🔗 Integrations", value=integrations_info, inline=False)
            
            # Command latency section
            latency = report.get("command_latency", {})
            latency_status = latency.get("status", "unknown")
            latency_emoji = "✅" if latency_status == "healthy" else "⚠️"
            latency_info = f"{latency_emoji} **Status:** {latency_status.upper()}\n"
            if "average_latency_ms" in latency:
                latency_info += f"⏱️ **Average:** {latency['average_latency_ms']}ms\n"
            if "note" in latency:
                latency_info += f"ℹ️ {latency['note']}\n"
            embed.add_field(name="⚡ Command Latency", value=latency_info, inline=False)
            
            # Footer
            embed.set_footer(
                text=f"Check completed in {report.get('check_duration_ms', 0):.2f}ms",
                icon_url=self.bot.user.display_avatar.url if self.bot.user else None
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in health check command: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Error checking health status: {str(e)}",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(HealthCog(bot))

