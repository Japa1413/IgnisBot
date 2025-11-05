"""
Induction Cog - Induction process for new members.

Manages the induction process with Bloxlink integration,
displaying Roblox information and starting the process.
"""

from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands

from services.bloxlink_service import BloxlinkService
from services.audit_service import AuditService
from utils.checks import cmd_channel_only, appcmd_channel_only, appcmd_moderator_or_owner
from utils.config import GUILD_ID
from utils.logger import get_logger

logger = get_logger(__name__)

# Specific channel for induction and promotion commands
INDUCTION_CHANNEL_ID = 1375941286267326532


class InductionCog(commands.Cog):
    """Cog to manage induction process"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bloxlink_service = BloxlinkService()
        self.audit_service = AuditService()
    
    @app_commands.command(name="induction", description="Start induction process for a player")
    @app_commands.describe(
        roblox_username="Player's Roblox nickname",
        instructions="Additional instructions (optional)"
    )
    @appcmd_channel_only(INDUCTION_CHANNEL_ID)
    @appcmd_moderator_or_owner()
    async def induction(
        self,
        interaction: discord.Interaction,
        roblox_username: str,
        instructions: str = ""
    ):
        """
        Start induction process for a player by Roblox nickname.
        
        Requirements:
        - Valid Roblox nickname
        - User must be moderator or server owner
        - Command must be used in specific channel
        """
        await interaction.response.defer(thinking=True, ephemeral=False)
        
        try:
            # Fetch Roblox information by username
            searched_username = roblox_username.strip()
            
            if not searched_username:
                await interaction.followup.send(
                    "❌ Please provide a valid Roblox username.",
                    ephemeral=True
                )
                return
            
            logger.info(f"Searching for Roblox user: {searched_username}")
            roblox_data = await self.bloxlink_service.get_roblox_user_by_username(searched_username)
            
            if not roblox_data:
                logger.warning(f"Roblox user '{searched_username}' not found")
                await interaction.followup.send(
                    f"❌ User **{searched_username}** not found on Roblox.\n\n"
                    f"**Please verify:**\n"
                    f"• The username is spelled correctly\n"
                    f"• You are using the **username** (not display name)\n"
                    f"• The account exists and is not banned\n"
                    f"• Try searching for the user on Roblox.com first",
                    ephemeral=True
                )
                return
            
            # Extract information
            roblox_username_found = roblox_data.get("username", "Unknown")
            roblox_id = roblox_data.get("id", "Unknown")
            avatar_url = roblox_data.get("avatar_url", "")
            
            # Create induction embed
            embed = discord.Embed(
                title="🔥 Starting Induction Process 🔥",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            
            # Add recruit information
            embed.add_field(
                name="Recruit",
                value=f"**{roblox_username_found}**",
                inline=True
            )
            
            embed.add_field(
                name="Roblox ID",
                value=f"`{roblox_id}`",
                inline=True
            )
            
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            
            # Avatar
            embed.set_thumbnail(url=avatar_url)
            
            # Welcome message
            welcome_message = (
                f"Welcome to the **Age Of Warfare** induction process.\n"
                f"You will be guided through a series of steps to become an official member of the group.\n\n"
                f"**Next steps:**\n"
            )
            
            if instructions:
                welcome_message += f"{instructions}\n\n"
            else:
                welcome_message += (
                    "1. Read the server rules\n"
                    "2. Complete basic training\n"
                    "3. Wait for administration approval\n\n"
                )
            
            welcome_message += (
                "Please follow the provided instructions carefully.\n"
                "If you have any questions, contact the administration."
            )
            
            embed.add_field(
                name="📋 Instructions",
                value=welcome_message,
                inline=False
            )
            
            # Footer
            embed.set_footer(
                text=f"Started by {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            
            # Send message
            await interaction.followup.send(embed=embed)
            
            # Audit log
            await self.audit_service.log_operation(
                user_id=0,  # No Discord ID available, only Roblox username
                action_type="CREATE",
                data_type="induction",
                performed_by=interaction.user.id,
                purpose="Induction process started",
                details={
                    "roblox_username": roblox_username_found,
                    "roblox_id": roblox_id,
                    "instructions": instructions,
                    "searched_username": searched_username
                }
            )
            
            logger.info(
                f"Induction started for Roblox user {roblox_username_found} (ID: {roblox_id}) "
                f"by {interaction.user.id}"
            )
            
        except Exception as e:
            logger.error(f"Error in induction command: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Error starting induction process. Please check the logs.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(InductionCog(bot))

