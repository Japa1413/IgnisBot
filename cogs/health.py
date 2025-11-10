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
            
            # System Resources section
            system_resources = report.get("system_resources", {})
            if system_resources.get("status") != "error":
                resources_status = system_resources.get("status", "unknown")
                resources_emoji = "✅" if resources_status == "healthy" else "⚠️" if resources_status == "warning" else "❌"
                resources_info = f"{resources_emoji} **Status:** {resources_status.upper()}\n"
                
                # CPU
                cpu = system_resources.get("cpu", {})
                if cpu:
                    cpu_info = f"🔧 **CPU:** {cpu.get('process_percent', 0)}% (process) / {cpu.get('system_percent', 0)}% (system)\n"
                    cpu_info += f"   Cores: {cpu.get('cores', 'N/A')}"
                    if cpu.get('frequency_mhz'):
                        cpu_info += f" | {cpu.get('frequency_mhz')} MHz"
                    resources_info += cpu_info + "\n"
                
                # Memory
                memory = system_resources.get("memory", {})
                if memory:
                    mem_info = f"💾 **Memory:** {memory.get('process_mb', 0)} MB (process) / {memory.get('process_percent', 0)}% (process)\n"
                    mem_info += f"   System: {memory.get('system_used_gb', 0)} GB / {memory.get('system_total_gb', 0)} GB ({memory.get('system_percent', 0)}%)\n"
                    mem_info += f"   Available: {memory.get('system_available_gb', 0)} GB"
                    resources_info += mem_info + "\n"
                
                # Disk
                disk = system_resources.get("disk", {})
                if disk:
                    disk_info = f"💿 **Disk:** {disk.get('used_gb', 0)} GB / {disk.get('total_gb', 0)} GB ({disk.get('percent', 0)}%)\n"
                    disk_info += f"   Free: {disk.get('free_gb', 0)} GB"
                    resources_info += disk_info + "\n"
                
                # GPU
                gpu = system_resources.get("gpu", {})
                if gpu and gpu.get("available"):
                    gpu_info = f"🎮 **GPU:** {gpu.get('count', 0)} GPU(s) detected\n"
                    for idx, gpu_data in enumerate(gpu.get("gpus", []), 1):
                        gpu_info += f"   GPU {idx}: {gpu_data.get('name', 'Unknown')}\n"
                        gpu_info += f"      Memory: {gpu_data.get('memory_used_gb', 0)} GB / {gpu_data.get('memory_total_gb', 0)} GB ({gpu_data.get('memory_percent', 0)}%)\n"
                        gpu_info += f"      Utilization: {gpu_data.get('utilization_percent', 0)}%"
                        if idx < len(gpu.get("gpus", [])):
                            gpu_info += "\n"
                    resources_info += gpu_info
                elif gpu and not gpu.get("available"):
                    resources_info += f"🎮 **GPU:** {gpu.get('note', 'Not available')}\n"
                
                embed.add_field(name="🖥️ System Resources", value=resources_info, inline=False)
            else:
                error_msg = system_resources.get("error", "Unknown error")
                embed.add_field(
                    name="🖥️ System Resources",
                    value=f"❌ **Error:** {error_msg}",
                    inline=False
                )
            
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

