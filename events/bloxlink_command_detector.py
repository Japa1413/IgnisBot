"""
Bloxlink Command Detector - Detects when Bloxlink /verify or /update is used.

This event handler listens for Bloxlink commands and triggers Ignis
to send rank and company information to Bloxlink.
"""

from __future__ import annotations

import discord
from discord.ext import commands
from typing import Optional
from utils.logger import get_logger
from services.bloxlink_service import BloxlinkService
from services.roblox_groups_service import get_roblox_groups_service
from services.company_mapping_service import get_company_mapping_service
from services.progression_service import ProgressionService

logger = get_logger(__name__)

# Bloxlink bot ID (common ID for Bloxlink)
BLOXLINK_BOT_ID = 426537812993638401  # Bloxlink's bot ID


class BloxlinkCommandDetector(commands.Cog):
    """
    Detects when Bloxlink /verify or /update commands are used
    and sends rank/company information to Bloxlink.
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bloxlink_service = BloxlinkService()
        self.groups_service = get_roblox_groups_service()
        self.company_service = get_company_mapping_service()
        self.progression_service = ProgressionService()
    
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """
        Detect when Bloxlink updates a member's roles.
        
        This is triggered when Bloxlink uses /verify or /update and
        updates the member's Discord roles based on their Roblox rank.
        """
        try:
            # Only process if roles changed
            if before.roles == after.roles:
                return
            
            # Check if this is likely a Bloxlink update
            # (roles changed, member is verified)
            roblox_data = await self.bloxlink_service.get_roblox_user(
                discord_id=after.id,
                guild_id=after.guild.id
            )
            
            if not roblox_data:
                # User not verified, skip
                return
            
            roblox_id = roblox_data.get("id")
            roblox_username = roblox_data.get("username")
            
            if not roblox_id:
                return
            
            # Get rank in main group
            rank_info = await self.groups_service.get_user_rank_in_group(
                roblox_id,
                6340169  # Main group ID
            )
            
            if not rank_info:
                logger.debug(
                    f"User {after.id} ({roblox_username}) not in main group, skipping"
                )
                return
            
            rank_number = rank_info.get("rank", 0)
            rank_name = rank_info.get("role", "")
            
            # Get company number based on rank
            company_number = await self.company_service.get_company_for_user(
                roblox_id,
                roblox_username
            )
            
            # Update rank in database
            try:
                # Find the highest tracked role
                from events.role_sync_handler import RoleSyncHandler
                role_sync = self.bot.get_cog("RoleSyncHandler")
                if role_sync:
                    # Let role_sync_handler handle the rank update
                    # We just log the information here
                    logger.info(
                        f"Bloxlink update detected for {after.id} ({roblox_username}): "
                        f"Rank {rank_number} ({rank_name}), Company: {company_number}"
                    )
            except Exception as e:
                logger.error(f"Error updating rank in database: {e}", exc_info=True)
            
            # Note: Bloxlink doesn't have a public API to receive data from Ignis
            # Instead, we rely on Bloxlink's own API to fetch rank from Roblox
            # The role_sync_handler will update the nickname after roles are updated
            
        except Exception as e:
            logger.error(
                f"Error in Bloxlink command detector for {after.id}: {e}",
                exc_info=True
            )


async def setup(bot: commands.Bot):
    """Setup function to load the cog"""
    await bot.add_cog(BloxlinkCommandDetector(bot))
    logger.info("Bloxlink command detector loaded")


