"""
Role Sync Handler - Automatic rank synchronization from Discord roles.

Detects when Bloxlink updates a user's Discord roles (via /update command)
and automatically syncs the rank to the database.
"""

from __future__ import annotations

import discord
from discord.ext import commands
from typing import Optional

from services.progression_service import ProgressionService
from services.audit_service import AuditService
from services.config_service import get_config_service
from services.bloxlink_service import BloxlinkService
from services.roblox_groups_service import get_roblox_groups_service, AOW_GROUP_IDS
from utils.rank_paths import ALL_PATHS, DEFAULT_PATH
from utils.logger import get_logger
from utils.config import GUILD_ID

logger = get_logger(__name__)

# Main group ID for checking rank
MAIN_GROUP_ID = 6340169

# Rank to nickname prefix mapping
RANK_NICKNAME_PREFIX = {
    # Mortals (Pre-Induction)
    "Civitas Aspirant": "IA",
    "Emberbound Initiate": "IA",
    "Obsidian Trialborn": "IA",
    "Crucible Neophyte": "IA",
    "Emberbrand Proving": "IA",
    
    # Legionaries
    "Inductii": "IG",
    "Legionary": "6",
    "Ashborn Legionary": "6",
    "Support Squad": "6",
    "Legion Veteran": "6",
    "Flamehardened Veteran": "6",
    "Legion Elite": "6",
    
    # Specialist
    "Techmarine": "A",
    "Chaplain": "A",
    "Apothecarion": "A",
    "Vexillarius": "A",
    "Destroyer": "A",
    "Signal Marine": "A",
    "Terminator Squad": "A",
    
    # Company ranks - will use company number from database
    "Cindershield Sergeant": None,  # Use company from DB
    "Emberblade Veteran Sergeant": None,  # Use company from DB
    "2nd Lieutenant (Furnace Warden)": None,  # Use company from DB
    "1st Lieutenant (Pyre Watcher)": None,  # Use company from DB
    "Flameborne Captain": None,  # Use company from DB
    
    # Great Company
    "Pyroclast Sentinel": None,  # Use company from DB
    "Cindermarked": None,  # Use company from DB
    "Flamewrought": None,  # Use company from DB
    "Consulate": None,  # Use company from DB
    "Marshal": None,  # Use company from DB
    
    # High Command
    "Preator": None,  # Use company from DB
    "Commander": None,  # Use company from DB
    "First Captain": None,  # Use company from DB
    "Primarch": None,  # Use company from DB
    "Emperor Of Mankind": None,  # Use company from DB
}


class RoleSyncHandler(commands.Cog):
    """
    Handler for automatic rank synchronization from Discord roles.
    
    When Bloxlink updates a user's roles via /update command,
    this handler detects the change and updates the database.
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.progression_service = ProgressionService()
        self.audit_service = AuditService()
        self.config_service = get_config_service()
        self.bloxlink_service = BloxlinkService()
        self.groups_service = get_roblox_groups_service()
        
        # Load role-to-rank mapping from configuration service
        # This allows easy editing without code changes
        self.role_to_rank_map = self.config_service.get_role_to_rank_map()
        
        # Fallback to hardcoded map if config is empty (backward compatibility)
        if not self.role_to_rank_map:
            logger.warning("Config service returned empty map, using fallback")
            self.role_to_rank_map = {
            # High Command
            "Emperor Of Mankind": "Emperor Of Mankind",
            "Primarch": "Primarch",
            "First Captain": "First Captain",
            "Commander": "Commander",
            "Preator": "Preator",  # Note: typo in Discord role name
            
            # Great Company
            "Marshal": "Marshal",
            "Consulate": "Consulate",
            "Flamewrought": "Flamewrought",
            "Cindermarked": "Cindermarked",
            "Pyroclast Sentinel": "Pyroclast Sentinel",
            
            # Company - Note: Some Discord roles may have slightly different names
            "Captain": "Flameborne Captain",  # Maps to Flameborne Captain
            "1st Lieutenant": "1st Lieutenant (Pyre Watcher)",
            "2nd Lieutenant": "2nd Lieutenant (Furnace Warden)",
            "Veteran Sergeant": "Emberblade Veteran Sergeant",
            "Legion Sergeant": "Cindershield Sergeant",
            # Handle variations (if role names match exactly)
            "1st Lieutenant (Pyre Watcher)": "1st Lieutenant (Pyre Watcher)",
            "2nd Lieutenant (Furnace Warden)": "2nd Lieutenant (Furnace Warden)",
            "Emberblade Veteran Sergeant": "Emberblade Veteran Sergeant",
            "Cindershield Sergeant": "Cindershield Sergeant",
            "Flameborne Captain": "Flameborne Captain",
            
            # Specialist
            "Chaplain": "Chaplain",
            "Techmarine": "Techmarine",
            "Terminator Squad": "Terminator Squad",
            "Apothecarion": "Apothecarion",
            "Vexillarius": "Vexillarius",
            "Destroyer": "Destroyer",
            "Signal Marine": "Signal Marine",
            
            # Legionaries
            "Legion Elite": "Flamehardened Veteran",
            "Legion Veteran": "Flamehardened Veteran",
            "Support Squad": "Flamehardened Veteran",
            "Legionary": "Ashborn Legionary",
            "Inductii": "Inductii",
            
            # Mortals (Pre-Induction Path)
            "Emberbrand Proving": "Emberbrand Proving",
            "Crucible Neophyte": "Crucible Neophyte",
            "Obsidian Trialborn": "Obsidian Trialborn",
            "Emberbound Initiate": "Emberbound Initiate",
            "Civitas Aspirant": "Civitas Aspirant",
        }
        
        # List of roles that should trigger rank updates
        self.tracked_roles = set(self.role_to_rank_map.keys())
    
    def _find_highest_rank_role(self, member: discord.Member) -> Optional[str]:
        """
        Find the highest priority rank role from the member's roles.
        
        Uses the same priority system as RankCog.
        
        Args:
            member: Discord member
        
        Returns:
            Role name or None if no tracked role found
        """
        # Get all role names (excluding @everyone)
        role_names = {r.name for r in member.roles if r.name != "@everyone"}
        
        # Find roles that are tracked
        tracked_present = [r for r in role_names if r in self.tracked_roles]
        
        if not tracked_present:
            return None
        
        # Use priority from cogs/rank.py
        from cogs.rank import ROLE_PRIORITY
        
        # Sort by priority (highest wins)
        tracked_present.sort(key=lambda r: ROLE_PRIORITY.index(r) if r in ROLE_PRIORITY else -1, reverse=True)
        
        return tracked_present[0] if tracked_present else None
    
    def _map_role_to_rank(self, role_name: str) -> Optional[str]:
        """
        Map Discord role name to system rank name.
        
        Args:
            role_name: Discord role name
        
        Returns:
            System rank name or None if not mappable
        """
        return self.role_to_rank_map.get(role_name)
    
    def _determine_path_from_rank(self, rank: str) -> str:
        """
        Determine which path a rank belongs to.
        
        Args:
            rank: Rank name
        
        Returns:
            Path identifier
        """
        # Check all paths
        for path_name, path in ALL_PATHS.items():
            # Check if rank is in this path
            for req in path.ranks:
                if req.current_rank == rank or req.next_rank == rank:
                    return path_name
        
        # Default to pre_induction for unknown ranks
        return DEFAULT_PATH
    
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """
        Detect when a member's roles are updated (e.g., by Bloxlink /update).
        
        This is triggered when Bloxlink updates roles after a user is promoted
        in the Roblox group.
        """
        # Only process if roles actually changed (compare role IDs, not objects)
        if {r.id for r in before.roles} == {r.id for r in after.roles}:
            return
        
        # Get guild
        if not after.guild:
            return
        
        # Find highest rank role before and after
        before_role = self._find_highest_rank_role(before)
        after_role = self._find_highest_rank_role(after)
        
        # If no change in tracked roles, ignore
        if before_role == after_role:
            return
        
        # If no tracked role after update, ignore (might be a demotion or removal)
        if not after_role:
            logger.debug(f"Member {after.id} no longer has tracked roles, skipping update")
            return
        
        # Map role to rank
        new_rank = self._map_role_to_rank(after_role)
        if not new_rank:
            logger.warning(f"Could not map Discord role '{after_role}' to system rank for user {after.id}")
            return
        
        try:
            # Get current rank from database
            user_data = await self.progression_service.user_repo.get_or_create(after.id)
            current_rank = user_data.get("rank", "Civitas Aspirant")
            
            # If rank hasn't changed, skip update
            if current_rank == new_rank:
                logger.debug(f"Rank for user {after.id} already matches Discord role '{after_role}' ({new_rank})")
                return
            
            # Determine path
            path = self._determine_path_from_rank(new_rank)
            
            # Update rank in database
            await self.progression_service.set_rank(
                user_id=after.id,
                rank=new_rank,
                path=path,
                set_by=0  # System update (0 = automatic)
            )
            
            # Log the operation
            await self.audit_service.log_operation(
                user_id=after.id,
                action_type="UPDATE",
                data_type="rank_sync",
                performed_by=0,  # System update
                purpose="Automatic rank sync from Discord role update (Bloxlink /update)",
                details={
                    "discord_role": after_role,
                    "system_rank": new_rank,
                    "old_rank": current_rank,
                    "path": path,
                    "trigger": "bloxlink_update"
                }
            )
            
            logger.info(
                f"Rank synced for user {after.id} ({after.display_name}): "
                f"{current_rank} -> {new_rank} (from Discord role: {after_role})"
            )
            
            # Get company number based on Roblox rank
            company_number = await self._get_company_for_user(after)
            
            # Update nickname with format: {Prefix} {group-rank} {roblox-name}
            await self._update_nickname(after, new_rank, company_number)
            
        except Exception as e:
            logger.error(
                f"Error syncing rank for user {after.id} after role update: {e}",
                exc_info=True
            )
    
    async def _update_nickname(self, member: discord.Member, system_rank: str):
        """
        Update member's nickname to format: {Prefix} {group-rank} {roblox-name}
        
        Prefix can be:
        - Fixed prefix from RANK_NICKNAME_PREFIX (e.g., "IA", "IG", "6", "A")
        - Company number from database (for ranks that need company)
        
        Args:
            member: Discord member
            system_rank: System rank name (from database)
        """
        try:
            # Check bot permissions
            guild = member.guild
            me = guild.me or guild.get_member(self.bot.user.id)
            if not me or not me.guild_permissions.manage_nicknames:
                logger.debug(f"Bot doesn't have manage_nicknames permission in guild {guild.id}")
                return
            
            # Get Discord role name
            after_role = self._find_highest_rank_role(member)
            if not after_role:
                logger.debug(f"No tracked role found for member {member.id}, skipping nickname update")
                return
            
            # Get prefix for this rank
            prefix = RANK_NICKNAME_PREFIX.get(system_rank)
            
            # If prefix is None, try to get company number
            if prefix is None:
                # First, try company_number parameter (from Roblox rank)
                if company_number is not None:
                    prefix = str(company_number)
                else:
                    # Fallback: try to get company number from database
                    from cogs.rank import RankCog
                    rank_cog = self.bot.get_cog("RankCog")
                    if rank_cog:
                        await rank_cog._ensure_table()
                        company = await rank_cog._get_company_for_role(after_role)
                        if company is not None:
                            prefix = str(company)
                        else:
                            logger.debug(f"No prefix or company set for rank {system_rank}, skipping nickname update")
                            return
                    else:
                        logger.debug(f"No RankCog found and no prefix for {system_rank}, skipping nickname update")
                        return
            
            # Get Roblox user data via Bloxlink
            roblox_data = await self.bloxlink_service.get_roblox_user(
                discord_id=member.id,
                guild_id=guild.id
            )
            
            if not roblox_data:
                logger.debug(f"User {member.id} not verified by Bloxlink, skipping nickname update")
                return
            
            roblox_username = roblox_data.get("username", member.name)
            roblox_id = roblox_data.get("id")
            
            if not roblox_id:
                logger.warning(f"Roblox ID not found for user {member.id}")
                return
            
            # Get rank from Roblox group (main group: 6340169)
            roblox_rank_info = await self.groups_service.get_user_rank_in_group(roblox_id, MAIN_GROUP_ID)
            
            if not roblox_rank_info:
                logger.debug(f"User {roblox_username} (ID: {roblox_id}) not in main group {MAIN_GROUP_ID}")
                # Still update nickname without Roblox rank
                group_rank = "N/A"
            else:
                group_rank = roblox_rank_info.get("role", "N/A")
            
            # Format nickname: {Prefix} {group-rank} {roblox-name}
            new_nickname = f"{prefix}. {group_rank} {roblox_username}"
            
            # Discord nickname limit is 32 characters
            if len(new_nickname) > 32:
                # Try shorter format: {Prefix} {roblox-name}
                new_nickname = f"{prefix}. {roblox_username}"
                if len(new_nickname) > 32:
                    # Last resort: just prefix and truncated username
                    max_username_len = 32 - len(f"{prefix}. ") - 3  # -3 for "..."
                    truncated_username = roblox_username[:max_username_len] + "..." if len(roblox_username) > max_username_len else roblox_username
                    new_nickname = f"{prefix}. {truncated_username}"
            
            # Check if nickname needs updating
            if member.nick == new_nickname:
                logger.debug(f"Nickname for {member.id} already correct: {new_nickname}")
                return
            
            # Update nickname
            try:
                await member.edit(nick=new_nickname, reason="Ignis: Auto-update nickname after Bloxlink /update")
                logger.info(
                    f"Nickname updated for {member.id} ({member.display_name}): "
                    f"'{member.nick}' -> '{new_nickname}'"
                )
            except discord.Forbidden:
                logger.warning(f"No permission to edit nickname for {member.id}")
            except discord.HTTPException as e:
                logger.error(f"HTTP error updating nickname for {member.id}: {e}")
            
        except Exception as e:
            logger.error(
                f"Error updating nickname for user {member.id}: {e}",
                exc_info=True
            )
    

async def setup(bot: commands.Bot):
    """Setup function to load the cog"""
    await bot.add_cog(RoleSyncHandler(bot))
    logger.info("Role sync handler loaded (automatic rank synchronization active)")

