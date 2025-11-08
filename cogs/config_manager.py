"""
Configuration Manager Cog - Admin commands to manage role-to-rank mappings.
"""

from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands

from services.config_service import get_config_service
from utils.checks import appcmd_channel_only
from utils.config import STAFF_CMDS_CHANNEL_ID
from utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManagerCog(commands.Cog):
    """Cog for managing role-to-rank configuration"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_service = get_config_service()
    
    @app_commands.command(name="config", description="Manage role-to-rank configuration")
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    async def config(self, interaction: discord.Interaction):
        """Main config command - shows subcommands"""
        await interaction.response.send_message(
            "Use `/config_role_add`, `/config_role_remove`, or `/config_role_list` to manage role mappings.",
            ephemeral=True
        )
    
    @app_commands.command(name="config_role_add", description="Add or update a role-to-rank mapping")
    @app_commands.describe(
        discord_role="Discord role name",
        system_rank="System rank name",
        category="Category (optional, default: Custom)"
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    async def config_role_add(
        self,
        interaction: discord.Interaction,
        discord_role: str,
        system_rank: str,
        category: str = "Custom"
    ):
        """Add or update a role-to-rank mapping"""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        try:
            success = self.config_service.add_role_mapping(discord_role, system_rank, category)
            
            if success:
                # Reload config in role sync handler if it exists
                await self._reload_role_sync_handler()
                
                await interaction.followup.send(
                    f"[OK] Role mapping added/updated:\n"
                    f"**Discord Role:** `{discord_role}`\n"
                    f"**System Rank:** `{system_rank}`\n"
                    f"**Category:** `{category}`",
                    ephemeral=True
                )
                logger.info(f"Role mapping added by {interaction.user.id}: {discord_role} -> {system_rank}")
            else:
                await interaction.followup.send(
                    "[ERRO] Failed to save role mapping. Check logs for details.",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error adding role mapping: {e}", exc_info=True)
            await interaction.followup.send(
                f"[ERRO] Error: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="config_role_remove", description="Remove a role-to-rank mapping")
    @app_commands.describe(discord_role="Discord role name to remove")
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    async def config_role_remove(self, interaction: discord.Interaction, discord_role: str):
        """Remove a role-to-rank mapping"""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        try:
            success = self.config_service.remove_role_mapping(discord_role)
            
            if success:
                # Reload config in role sync handler if it exists
                await self._reload_role_sync_handler()
                
                await interaction.followup.send(
                    f"[OK] Role mapping removed: `{discord_role}`",
                    ephemeral=True
                )
                logger.info(f"Role mapping removed by {interaction.user.id}: {discord_role}")
            else:
                await interaction.followup.send(
                    f"[ERRO] Role mapping `{discord_role}` not found.",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error removing role mapping: {e}", exc_info=True)
            await interaction.followup.send(
                f"[ERRO] Error: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="config_role_list", description="List all role-to-rank mappings")
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    async def config_role_list(self, interaction: discord.Interaction):
        """List all role-to-rank mappings"""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        try:
            mappings = self.config_service.list_all_mappings()
            
            if not mappings:
                await interaction.followup.send(
                    "No role mappings configured.",
                    ephemeral=True
                )
                return
            
            # Build embed
            embed = discord.Embed(
                title="Role-to-Rank Mappings",
                description="All configured Discord role to system rank mappings",
                color=discord.Color.blue()
            )
            
            for category, roles in mappings.items():
                if isinstance(roles, dict) and roles:
                    role_list = "\n".join([f"`{role}` → `{rank}`" for role, rank in roles.items()])
                    # Discord embed field value limit is 1024 characters
                    if len(role_list) > 1024:
                        role_list = role_list[:1021] + "..."
                    embed.add_field(
                        name=category,
                        value=role_list or "None",
                        inline=False
                    )
            
            embed.set_footer(text=f"Total categories: {len(mappings)}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error listing role mappings: {e}", exc_info=True)
            await interaction.followup.send(
                f"[ERRO] Error: {str(e)}",
                ephemeral=True
            )
    
    async def _reload_role_sync_handler(self):
        """Reload role sync handler configuration"""
        try:
            # Try to get role sync handler cog and reload its config
            from events.role_sync_handler import RoleSyncHandler
            for cog in self.bot.cogs.values():
                if isinstance(cog, RoleSyncHandler):
                    # Reload config in handler
                    cog.role_to_rank_map = self.config_service.get_role_to_rank_map()
                    cog.tracked_roles = set(cog.role_to_rank_map.keys())
                    logger.info("Role sync handler configuration reloaded")
                    break
        except Exception as e:
            logger.warning(f"Could not reload role sync handler: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(ConfigManagerCog(bot))
    logger.info("Config Manager cog loaded")

