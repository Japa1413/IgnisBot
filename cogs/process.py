"""
Process Cog - Process management for new members.

Manages the process with Bloxlink integration,
creating private channels and displaying Roblox information.
"""

from __future__ import annotations

import asyncio
import aiohttp
import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timezone, timedelta
from io import BytesIO

from services.bloxlink_service import BloxlinkService
from services.roblox_groups_service import get_roblox_groups_service, AOW_GROUP_IDS
from services.roblox_outfits_service import get_roblox_outfits_service
from services.audit_service import AuditService
from services.progression_service import ProgressionService
from utils.checks import appcmd_channel_only, appcmd_moderator_or_owner
from utils.config import GUILD_ID, ROBLOX_COOKIE
from utils.logger import get_logger

logger = get_logger(__name__)

# Specific channel for process commands
PROCESS_CHANNEL_ID = 1375941286267326532

# Category ID for process channels
PROCESS_CATEGORY_ID = 1375941285633855599

# Salamanders theme colors
SALAMANDERS_GREEN = 0x2ECC71
SALAMANDERS_DARK_GREEN = 0x27AE60
SALAMANDERS_RED = 0xE74C3C

# Channel ID for verify command mention
VERIFY_CHANNEL_ID = 1375941286267326532


class InductionConfirmationView(discord.ui.View):
    """View with Confirm and Cancel buttons for induction process"""
    
    def __init__(self, roblox_username: str, roblox_id: int, is_in_group: bool, has_pending_request: bool):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.roblox_username = roblox_username
        self.roblox_id = roblox_id
        self.is_in_group = is_in_group
        self.has_pending_request = has_pending_request
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success, row=0)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirm button - proceeds with induction process"""
        await interaction.response.defer(ephemeral=False)
        
        # Disable buttons
        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)
        
        # Clear previous button messages
        if interaction.channel and isinstance(interaction.channel, discord.TextChannel):
            await self._clear_previous_button_messages(interaction.channel, interaction.client.user)
        
        # Proceed with induction process
        await self._execute_induction_process(interaction)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=0)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel button - cancels the operation"""
        await interaction.response.defer(ephemeral=False)
        
        # Disable buttons
        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)
        
        # Send cancellation message
        cancel_embed = discord.Embed(
            title="Operation Cancelled",
            description=f"The induction process for **{self.roblox_username}** has been cancelled.",
            color=SALAMANDERS_RED,
            timestamp=discord.utils.utcnow()
        )
        cancel_embed.set_footer(
            text="Age of Warfare • Process System",
            icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
        )
        
        await interaction.followup.send(embed=cancel_embed)
        logger.info(f"[INDUCTION] Process cancelled for {self.roblox_username}")
    
    async def _clear_previous_button_messages(self, channel: discord.TextChannel, bot_user: discord.ClientUser):
        """Clear previous button messages from this view"""
        try:
            async for message in channel.history(limit=10):
                if message.author == bot_user and message.embeds:
                    for embed in message.embeds:
                        if "Induction Process Confirmation" in embed.title or "Operation Cancelled" in embed.title:
                            try:
                                await message.delete()
                            except:
                                pass
        except Exception as e:
            logger.warning(f"[INDUCTION] Error clearing messages: {e}")
    
    async def _execute_induction_process(self, interaction: discord.Interaction):
        """Execute the actual induction process"""
        try:
            # Get services
            groups_service = get_roblox_groups_service()
            progression_service = ProgressionService()
            audit_service = AuditService()
            
            # Main group for accepting requests: 6340169
            # Secondary group for rank change: 6496437
            MAIN_GROUP_ID = 6340169  # Group to accept user
            RANK_CHANGE_GROUP_ID = 6496437  # Group to change rank from 238 to 240
            
            if self.is_in_group:
                # User is already in main group, proceed to rank change
                logger.info(f"[INDUCTION] User {self.roblox_username} is already in main group, proceeding to rank change")
            else:
                # Step 1: Accept user to main group (NO rank change, just accept)
                # We try to accept directly - the API will return a clear error if there's no pending request
                logger.info(f"[INDUCTION] Attempting to accept user {self.roblox_username} (ID: {self.roblox_id}) to group {MAIN_GROUP_ID}")
                accept_result = await groups_service.accept_user_to_group(
                    group_id=MAIN_GROUP_ID,
                    roblox_user_id=self.roblox_id,
                    roblox_cookie=ROBLOX_COOKIE
                )
                
                if not accept_result.get("success"):
                    # Check if it's a "no pending request" error
                    error_message = accept_result.get('message', 'Unknown error')
                    error_type = accept_result.get('error', '')
                    
                    # If it's a 404 or "no pending request" error, show helpful message
                    if "404" in error_type or "no pending request" in error_message.lower() or "does not have a pending" in error_message.lower():
                        error_embed = discord.Embed(
                            title="No Pending Request",
                            description=f"User **{self.roblox_username}** does not have a pending join request for the group (ID: {MAIN_GROUP_ID}).",
                            color=discord.Color.orange(),
                            timestamp=discord.utils.utcnow()
                        )
                        error_embed.add_field(
                            name="What to do",
                            value=f"Please ask the user to request to join the group first:\nhttps://www.roblox.com/groups/{MAIN_GROUP_ID}",
                            inline=False
                        )
                        error_embed.set_footer(
                            text="Age of Warfare • Process System",
                            icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
                        )
                        await interaction.followup.send(embed=error_embed)
                        logger.warning(f"[INDUCTION] User {self.roblox_username} does not have pending request: {error_message}")
                        return
                    else:
                        # Other errors (authentication, permission, etc.)
                        error_embed = discord.Embed(
                            title="Error Accepting User",
                            description=f"Could not accept user to group: {error_message}",
                            color=SALAMANDERS_RED,
                            timestamp=discord.utils.utcnow()
                        )
                        error_embed.set_footer(
                            text="Age of Warfare • Process System",
                            icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
                        )
                        await interaction.followup.send(embed=error_embed)
                        logger.error(f"[INDUCTION] Failed to accept user: {error_type}")
                        return
                
                logger.info(f"[INDUCTION] User accepted to main group: {accept_result.get('message')}")
            
            # Step 2: Change rank in secondary group (6496437) from rank 238 to 240
            logger.info(f"[INDUCTION] Fetching roles for rank change group {RANK_CHANGE_GROUP_ID}")
            rank_change_roles = await groups_service.get_group_roles(RANK_CHANGE_GROUP_ID)
            
            if not rank_change_roles:
                error_embed = discord.Embed(
                    title="Error",
                    description="Could not fetch roles for rank change group. Please try again later.",
                    color=SALAMANDERS_RED,
                    timestamp=discord.utils.utcnow()
                )
                error_embed.set_footer(
                    text="Age of Warfare • Process System",
                    icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
                )
                await interaction.followup.send(embed=error_embed)
                logger.error(f"[INDUCTION] Could not fetch roles for group {RANK_CHANGE_GROUP_ID}")
                return
            
            # Find role with rank 240
            target_role = None
            target_role_id = None
            
            for role in rank_change_roles:
                if role.get("rank") == 240:
                    target_role = role.get("name")
                    target_role_id = role.get("id")
                    break
            
            if not target_role_id:
                error_embed = discord.Embed(
                    title="Error",
                    description=f"Could not find role with rank 240 in group {RANK_CHANGE_GROUP_ID}. Please contact an administrator.",
                    color=SALAMANDERS_RED,
                    timestamp=discord.utils.utcnow()
                )
                error_embed.set_footer(
                    text="Age of Warfare • Process System",
                    icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
                )
                await interaction.followup.send(embed=error_embed)
                logger.error(f"[INDUCTION] Could not find role with rank 240 in group {RANK_CHANGE_GROUP_ID}")
                return
            
            logger.info(f"[INDUCTION] Target role for rank change: {target_role} (ID: {target_role_id}, Rank: 240)")
            
            # Check if user is in the rank change group
            is_in_rank_group = await groups_service.is_user_in_group(self.roblox_id, RANK_CHANGE_GROUP_ID)
            
            if not is_in_rank_group:
                error_embed = discord.Embed(
                    title="Error",
                    description=f"User **{self.roblox_username}** is not a member of the rank change group (ID: {RANK_CHANGE_GROUP_ID}). Please ensure the user is in this group first.",
                    color=SALAMANDERS_RED,
                    timestamp=discord.utils.utcnow()
                )
                error_embed.set_footer(
                    text="Age of Warfare • Process System",
                    icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
                )
                await interaction.followup.send(embed=error_embed)
                logger.error(f"[INDUCTION] User {self.roblox_username} is not in rank change group {RANK_CHANGE_GROUP_ID}")
                return
            
            # Check current rank in the rank change group
            current_rank_info = await groups_service.get_user_rank_in_group(self.roblox_id, RANK_CHANGE_GROUP_ID)
            current_rank = current_rank_info.get("rank", 0) if current_rank_info else 0
            
            if current_rank == 240:
                # User already has rank 240
                info_embed = discord.Embed(
                    title="Rank Already Set",
                    description=f"User **{self.roblox_username}** already has rank 240 in the rank change group.",
                    color=SALAMANDERS_GREEN,
                    timestamp=discord.utils.utcnow()
                )
                info_embed.add_field(name="Current Rank", value=f"240 ({current_rank_info.get('role', 'Unknown')})", inline=True)
                info_embed.set_footer(
                    text="Age of Warfare • Process System",
                    icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
                )
                await interaction.followup.send(embed=info_embed)
                logger.info(f"[INDUCTION] User {self.roblox_username} already has rank 240")
                return
            
            # Change rank from 238 to 240
            logger.info(f"[INDUCTION] Changing rank from {current_rank} to 240 for user {self.roblox_username} in group {RANK_CHANGE_GROUP_ID}")
            rank_change_result = await groups_service.set_user_rank(
                group_id=RANK_CHANGE_GROUP_ID,
                roblox_user_id=self.roblox_id,
                role_id=target_role_id,
                roblox_cookie=ROBLOX_COOKIE
            )
            
            if not rank_change_result.get("success"):
                error_embed = discord.Embed(
                    title="Error Changing Rank",
                    description=f"Could not change user rank: {rank_change_result.get('message', 'Unknown error')}",
                    color=SALAMANDERS_RED,
                    timestamp=discord.utils.utcnow()
                )
                error_embed.add_field(name="Current Rank", value=str(current_rank), inline=True)
                error_embed.add_field(name="Target Rank", value="240", inline=True)
                error_embed.set_footer(
                    text="Age of Warfare • Process System",
                    icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
                )
                await interaction.followup.send(embed=error_embed)
                logger.error(f"[INDUCTION] Failed to change rank: {rank_change_result.get('error')}")
                return
            
            logger.info(f"[INDUCTION] Rank changed successfully: {rank_change_result.get('message')}")
            
            # Step 3: Get group names for display
            main_group_info = await groups_service.get_group_info(MAIN_GROUP_ID)
            rank_group_info = await groups_service.get_group_info(RANK_CHANGE_GROUP_ID)
            
            main_group_name = main_group_info.get("name", f"Group {MAIN_GROUP_ID}") if main_group_info else f"Group {MAIN_GROUP_ID}"
            rank_group_name = rank_group_info.get("name", f"Group {RANK_CHANGE_GROUP_ID}") if rank_group_info else f"Group {RANK_CHANGE_GROUP_ID}"
            
            # Step 4: Update Ignis database
            # Set rank based on the rank change (rank 240 role name) and path to "legionary"
            logger.info(f"[INDUCTION] Updating Ignis database for user {interaction.user.id}")
            try:
                # Use the target role name from rank change as the rank
                await progression_service.set_rank(
                    user_id=interaction.user.id,
                    rank=target_role,
                    path="legionary",
                    set_by=interaction.user.id
                )
                
                # Log the operation
                await audit_service.log_operation(
                    user_id=interaction.user.id,
                    action_type="CREATE",
                    data_type="induction",
                    performed_by=interaction.user.id,
                    purpose="Induction process completed - user accepted to Roblox group and rank changed",
                    details={
                        "roblox_username": self.roblox_username,
                        "roblox_id": self.roblox_id,
                        "main_group_id": MAIN_GROUP_ID,
                        "rank_change_group_id": RANK_CHANGE_GROUP_ID,
                        "target_role": target_role,
                        "target_role_id": target_role_id,
                        "rank_change": f"{current_rank} -> 240",
                        "path": "legionary"
                    }
                )
                
                logger.info(f"[INDUCTION] Database updated successfully for user {interaction.user.id}")
            except Exception as e:
                logger.error(f"[INDUCTION] Error updating database: {e}", exc_info=True)
                # Continue anyway - group operations succeeded
            
            # Step 5: Get rank information for main group
            main_group_rank_info = None
            main_group_rank_name = "N/A"
            if not self.is_in_group:
                # User was just accepted, get their rank in main group
                main_group_rank_info = await groups_service.get_user_rank_in_group(self.roblox_id, MAIN_GROUP_ID)
                if main_group_rank_info:
                    main_group_rank_name = main_group_rank_info.get("role", "N/A")
            
            # Step 6: Create unified success embed with all information
            unified_embed = discord.Embed(
                title="Induction Process Complete",
                description=f"The induction process has been successfully completed for **{self.roblox_username}**.",
                color=SALAMANDERS_GREEN,
                timestamp=discord.utils.utcnow()
            )
            
            # Groups section - unified display
            groups_info = []
            
            # Main group information
            if not self.is_in_group:
                groups_info.append(f"✅ **{main_group_name}**\n   Status: Accepted\n   Rank: {main_group_rank_name}")
            else:
                # User was already in group, get current rank
                if main_group_rank_info is None:
                    main_group_rank_info = await groups_service.get_user_rank_in_group(self.roblox_id, MAIN_GROUP_ID)
                if main_group_rank_info:
                    main_group_rank_name = main_group_rank_info.get("role", "N/A")
                groups_info.append(f"✅ **{main_group_name}**\n   Status: Already Member\n   Rank: {main_group_rank_name}")
            
            # Rank change group information
            groups_info.append(f"✅ **{rank_group_name}**\n   Status: Rank Changed\n   Rank: {current_rank} → {target_role}")
            
            unified_embed.add_field(
                name="Groups",
                value="\n\n".join(groups_info),
                inline=False
            )
            
            # Final instruction
            verify_channel = interaction.guild.get_channel(VERIFY_CHANNEL_ID)
            if verify_channel:
                unified_embed.add_field(
                    name="Next Step",
                    value=f"Please use the `/update` command in {verify_channel.mention} to complete the verification process.",
                    inline=False
                )
            else:
                unified_embed.add_field(
                    name="Next Step",
                    value="Please use the `/update` command in the verification channel to complete the verification process.",
                    inline=False
                )
            
            unified_embed.set_footer(
                text="Age of Warfare • Process System",
                icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
            )
            
            await interaction.followup.send(embed=unified_embed)
            logger.info(f"[INDUCTION] ✅ Induction process completed successfully for {self.roblox_username}")
            
        except Exception as e:
            logger.error(f"[INDUCTION] Error in induction process: {e}", exc_info=True)
            error_embed = discord.Embed(
                title="Error",
                description=f"An error occurred during the induction process: {str(e)[:200]}",
                color=SALAMANDERS_RED,
                timestamp=discord.utils.utcnow()
            )
            error_embed.set_footer(
                text="Age of Warfare • Process System",
                icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
            )
            await interaction.followup.send(embed=error_embed)


class ProcessButtonsView(discord.ui.View):
    """View with buttons for the process embed"""
    
    def __init__(self, roblox_username: str, roblox_id: int, main_embed_message_id: int = None):
        super().__init__(timeout=None)  # Persistent view
        self.roblox_username = roblox_username
        self.roblox_id = roblox_id
        self.main_embed_message_id = main_embed_message_id  # ID of the main embed (to preserve it)
        
        # Add Profile Link as a link button (opens directly without permission)
        if self.roblox_id and self.roblox_id != "Unknown":
            profile_url = f"https://www.roblox.com/users/{self.roblox_id}/profile"
            link_button = discord.ui.Button(
                label="Profile Link",
                style=discord.ButtonStyle.link,
                url=profile_url,
                row=1,
                emoji="🔗"
            )
            self.add_item(link_button)
    
    async def _clear_previous_button_messages(self, channel: discord.TextChannel, bot_user: discord.ClientUser):
        """Clear previous button messages, but keep the main embed"""
        try:
            if not channel:
                return
            
            # Get bot member to check permissions
            bot_member = channel.guild.get_member(bot_user.id)
            if bot_member:
                perms = channel.permissions_for(bot_member)
                if not perms.manage_messages:
                    logger.warning(f"[PROCESS] Bot doesn't have manage_messages permission in channel {channel.id}")
                    return
            
            # Get recent messages from bot (last 50)
            messages_to_delete = []
            async for message in channel.history(limit=50):
                # Skip the main embed message
                if message.id == self.main_embed_message_id:
                    continue
                
                # Only delete messages from the bot
                if message.author == bot_user:
                    messages_to_delete.append(message)
            
            # Delete messages in batches (Discord limit is 100)
            if messages_to_delete:
                # Delete in chunks of 100
                for i in range(0, len(messages_to_delete), 100):
                    chunk = messages_to_delete[i:i+100]
                    try:
                        await channel.delete_messages(chunk)
                        logger.info(f"[PROCESS] Deleted {len(chunk)} previous button messages")
                    except discord.HTTPException as e:
                        logger.warning(f"[PROCESS] Could not delete some messages: {e}")
                        # Try deleting individually if bulk delete fails
                        for msg in chunk:
                            try:
                                await msg.delete()
                            except:
                                pass
        except Exception as e:
            logger.error(f"[PROCESS] Error clearing previous messages: {e}", exc_info=True)
    
    @discord.ui.button(label="Group(s) Check", style=discord.ButtonStyle.success, row=0)
    async def group_check_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Group check button - checks user's Roblox groups"""
        await interaction.response.defer(ephemeral=False)  # Changed to False - visible in chat
        
        # Clear previous button messages
        if interaction.channel and isinstance(interaction.channel, discord.TextChannel):
            await self._clear_previous_button_messages(interaction.channel, interaction.client.user)
        
        try:
            # Get Roblox Groups service
            groups_service = get_roblox_groups_service()
            
            # Get list of groups to check
            from services.roblox_groups_service import AOW_GROUP_IDS
            
            logger.info(f"[GROUP CHECK] Checking {len(AOW_GROUP_IDS)} groups for user {self.roblox_username} (ID: {self.roblox_id})")
            
            # Check user in specified groups
            found_groups = await groups_service.check_user_in_groups(self.roblox_id, AOW_GROUP_IDS)
            
            # Create beautiful embed with results
            embed = discord.Embed(
                title=f"Group Check — {self.roblox_username}",
                description="╔═══════════════════════════════════════════════════════════╗",
                color=SALAMANDERS_GREEN if found_groups else SALAMANDERS_RED,
                timestamp=discord.utils.utcnow()
            )
            
            # Only show groups where user was found
            if found_groups:
                # Add separator
                embed.add_field(
                    name="\u200b",
                    value="╠═══════════════════════════════════════════════════════════╣",
                    inline=False
                )
                
                # Create field for each found group with beautiful formatting
                for group in found_groups:
                    group_name = group.get('name', 'Unknown Group')
                    rank = group.get('rank', 0)
                    role = group.get('role', 'Unknown')
                    
                    embed.add_field(
                        name=f"▸ {group_name}",
                        value=(
                            f"```\n"
                            f"Rank: {rank}\n"
                            f"Role: {role}\n"
                            f"```"
                        ),
                        inline=False
                    )
                
                # Add separator before summary
                embed.add_field(
                    name="\u200b",
                    value="╠═══════════════════════════════════════════════════════════╣",
                    inline=False
                )
                
                # Summary with beautiful formatting
                embed.add_field(
                    name="Summary",
                    value=(
                        f"```\n"
                        f"Groups Found: {len(found_groups)}/{len(AOW_GROUP_IDS)}\n"
                        f"User: {self.roblox_username}\n"
                        f"```"
                    ),
                    inline=False
                )
                
                # Closing separator
                embed.add_field(
                    name="\u200b",
                    value="╚═══════════════════════════════════════════════════════════╝",
                    inline=False
                )
                
                embed.set_footer(
                    text="Age of Warfare • Process System",
                    icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
                )
                
                await interaction.followup.send(embed=embed)  # Removed ephemeral - visible in chat
                logger.info(f"[GROUP CHECK] ✅ Group check completed for {self.roblox_username} - Found {len(found_groups)} groups")
            else:
                # User not found in any of the specified groups - simple message, no embed
                logger.info(f"[GROUP CHECK] User {self.roblox_username} not found in any of the specified groups")
                await interaction.followup.send(
                    f"User **{self.roblox_username}** was not found in any of the specified groups."
                )  # Removed ephemeral - visible in chat
                return
            
        except Exception as e:
            logger.error(f"[GROUP CHECK] Error checking groups: {e}", exc_info=True)
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred while checking groups: {str(e)[:200]}",
                color=SALAMANDERS_RED,
                timestamp=discord.utils.utcnow()
            )
            error_embed.set_footer(
                text="Age of Warfare • Process System",
                icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
            )
            await interaction.followup.send(embed=error_embed)  # Removed ephemeral - visible in chat
    
    @discord.ui.button(label="Outfit(s) Check", style=discord.ButtonStyle.success, row=0)
    async def outfit_check_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Outfit check button - checks user's Roblox outfits"""
        await interaction.response.defer(ephemeral=False)  # Changed to False - visible in chat
        
        # Clear previous button messages
        if interaction.channel and isinstance(interaction.channel, discord.TextChannel):
            await self._clear_previous_button_messages(interaction.channel, interaction.client.user)
        
        try:
            # Get Roblox Outfits service
            outfits_service = get_roblox_outfits_service()
            
            logger.info(f"[OUTFIT CHECK HARD TEST] Checking outfits for user {self.roblox_username} (ID: {self.roblox_id})")
            
            # Get user outfits
            outfits = await outfits_service.get_user_outfits(self.roblox_id, limit=50)
            
            logger.info(f"[OUTFIT CHECK HARD TEST] Received {len(outfits)} outfits from service")
            
            if not outfits:
                # User has no outfits - send simple message
                await interaction.followup.send(
                    f"User **{self.roblox_username}** has no saved outfits."
                )
                logger.warning(f"[OUTFIT CHECK HARD TEST] User {self.roblox_username} has no outfits")
                return
            
            # Log outfit details for debugging
            logger.info(f"[OUTFIT CHECK HARD TEST] Processing {len(outfits)} outfits")
            for idx, outfit in enumerate(outfits[:5], 1):
                logger.info(f"[OUTFIT CHECK HARD TEST] Outfit {idx}: ID={outfit.get('id')}, Name={outfit.get('name')}, Thumbnail={outfit.get('thumbnail_url', 'NONE')}")
            
            # Download and send images directly as files (JPG/PNG), NOT as embeds
            # Only user-created outfits (isEditable: True) are included
            sent_count = 0
            failed_count = 0
            
            logger.info(f"[OUTFIT CHECK] Processing {len(outfits)} user-created outfits for user {self.roblox_username} (isEditable: True only)")
            
            # Use a single HTTP session for all requests (more efficient)
            # Optimized: Send all images in rapid sequence - MAXIMUM SPEED
            async with aiohttp.ClientSession() as session:
                for idx, outfit in enumerate(outfits):
                    # No delay - maximum speed, send all images as fast as possible
                    # Discord API will handle rate limiting if needed
                    outfit_id = outfit.get("id")
                    outfit_name = outfit.get("name", "Unnamed Outfit")
                    thumbnail_url = outfit.get("thumbnail_url")
                    fallback_url = outfit.get("thumbnail_url_fallback")
                    cdn_url = outfit.get("cdn_url")
                    
                    if not outfit_id:
                        logger.warning(f"[OUTFIT CHECK HARD TEST] ⚠️ No outfit ID for outfit: {outfit}")
                        failed_count += 1
                        continue
                    
                    # Try multiple strategies to get the image
                    image_data = None
                    extension = 'png'
                    
                    # Strategy 1: Use the CORRECT Roblox Thumbnails API endpoint
                    # Format: https://thumbnails.roblox.com/v1/users/outfits?userOutfitIds={outfitId}
                    try:
                        correct_thumbnail_url = f"https://thumbnails.roblox.com/v1/users/outfits?userOutfitIds={outfit_id}&size=420x420&format=Png"
                        logger.info(f"[OUTFIT CHECK] Strategy 1: Using CORRECT API endpoint for {outfit_name} (ID: {outfit_id})")
                        async with session.get(correct_thumbnail_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                            logger.info(f"[OUTFIT CHECK] Strategy 1 response status: {response.status} for {outfit_id}")
                            if response.status == 200:
                                content_type = response.headers.get('Content-Type', '')
                                logger.info(f"[OUTFIT CHECK] Strategy 1 content-type: {content_type} for {outfit_id}")
                                
                                if 'application/json' in content_type:
                                    # API returns JSON with data array
                                    json_data = await response.json()
                                    logger.info(f"[OUTFIT CHECK] Strategy 1 JSON response keys: {list(json_data.keys())} for {outfit_id}")
                                    
                                    if json_data.get('data') and len(json_data['data']) > 0:
                                        image_url = json_data['data'][0].get('imageUrl')
                                        if image_url:
                                            logger.info(f"[OUTFIT CHECK] Got image URL from API: {image_url[:100]}...")
                                            async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=15)) as img_response:
                                                logger.info(f"[OUTFIT CHECK] Image URL response status: {img_response.status}")
                                                if img_response.status == 200:
                                                    image_data = await img_response.read()
                                                    extension = 'png'
                                                    logger.info(f"[OUTFIT CHECK] ✅ Downloaded image via CORRECT API (Strategy 1) for {outfit_name} ({len(image_data)} bytes)")
                                                else:
                                                    logger.warning(f"[OUTFIT CHECK] Image URL returned {img_response.status}")
                                        else:
                                            logger.warning(f"[OUTFIT CHECK] No imageUrl in JSON data for {outfit_id}, data: {json_data.get('data')}")
                                    else:
                                        logger.warning(f"[OUTFIT CHECK] No data array in JSON response for {outfit_id}")
                                else:
                                    # Direct image response (unlikely but possible)
                                    image_data = await response.read()
                                    if 'jpeg' in content_type or 'jpg' in content_type:
                                        extension = 'jpg'
                                    logger.info(f"[OUTFIT CHECK] ✅ Downloaded image directly (Strategy 1) for {outfit_name} ({len(image_data)} bytes)")
                            elif response.status == 429:
                                logger.warning(f"[OUTFIT CHECK] Strategy 1: Rate limited (429) for {outfit_id}, will try other strategies")
                            else:
                                response_text = await response.text()
                                logger.warning(f"[OUTFIT CHECK] Strategy 1 returned status {response.status} for {outfit_id}, response: {response_text[:200]}")
                    except Exception as e:
                        logger.error(f"[OUTFIT CHECK] Strategy 1 exception for {outfit_id}: {e}", exc_info=True)
                    
                    # Strategy 2: Try outfit-3d endpoint (if Strategy 1 failed)
                    if not image_data and thumbnail_url:
                        try:
                            logger.info(f"[OUTFIT CHECK] Strategy 2: Trying outfit-3d URL for {outfit_name} (ID: {outfit_id})")
                            async with session.get(thumbnail_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                                logger.info(f"[OUTFIT CHECK] Strategy 2 response status: {response.status} for {outfit_id}")
                                if response.status == 200:
                                    content_type = response.headers.get('Content-Type', '')
                                    logger.info(f"[OUTFIT CHECK] Strategy 2 content-type: {content_type} for {outfit_id}")
                                    
                                    if 'application/json' in content_type:
                                        json_data = await response.json()
                                        logger.info(f"[OUTFIT CHECK] Strategy 2 JSON response keys: {list(json_data.keys())} for {outfit_id}")
                                        
                                        if json_data.get('data') and len(json_data['data']) > 0:
                                            image_url = json_data['data'][0].get('imageUrl')
                                            if image_url:
                                                logger.info(f"[OUTFIT CHECK] Got image URL from API (Strategy 2): {image_url[:100]}...")
                                                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=15)) as img_response:
                                                    if img_response.status == 200:
                                                        image_data = await img_response.read()
                                                        extension = 'png'
                                                        logger.info(f"[OUTFIT CHECK] ✅ Downloaded image via API (Strategy 2) for {outfit_name} ({len(image_data)} bytes)")
                                    else:
                                        image_data = await response.read()
                                        if 'jpeg' in content_type or 'jpg' in content_type:
                                            extension = 'jpg'
                                        logger.info(f"[OUTFIT CHECK] ✅ Downloaded image directly (Strategy 2) for {outfit_name} ({len(image_data)} bytes)")
                                else:
                                    logger.warning(f"[OUTFIT CHECK] Strategy 2 returned status {response.status} for {outfit_id}")
                        except Exception as e:
                            logger.error(f"[OUTFIT CHECK] Strategy 2 exception for {outfit_id}: {e}", exc_info=True)
                    
                    # Strategy 3: Try fallback URL (outfit without 3d) if Strategy 1 and 2 failed
                    if not image_data and fallback_url:
                        try:
                            logger.info(f"[OUTFIT CHECK] Strategy 3: Trying fallback URL for {outfit_name} (ID: {outfit_id})")
                            async with session.get(fallback_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                                logger.info(f"[OUTFIT CHECK] Strategy 3 response status: {response.status} for {outfit_id}")
                                if response.status == 200:
                                    content_type = response.headers.get('Content-Type', '')
                                    if 'application/json' in content_type:
                                        json_data = await response.json()
                                        if json_data.get('data') and len(json_data['data']) > 0:
                                            image_url = json_data['data'][0].get('imageUrl')
                                            if image_url:
                                                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=15)) as img_response:
                                                    if img_response.status == 200:
                                                        image_data = await img_response.read()
                                                        extension = 'png'
                                                        logger.info(f"[OUTFIT CHECK] ✅ Downloaded image via API (Strategy 3) for {outfit_name} ({len(image_data)} bytes)")
                                    else:
                                        image_data = await response.read()
                                        if 'jpeg' in content_type or 'jpg' in content_type:
                                            extension = 'jpg'
                                        logger.info(f"[OUTFIT CHECK] ✅ Downloaded image directly (Strategy 3) for {outfit_name} ({len(image_data)} bytes)")
                        except Exception as e:
                            logger.error(f"[OUTFIT CHECK] Strategy 3 exception for {outfit_id}: {e}", exc_info=True)
                    
                    # Send image if we got it
                    if image_data:
                        try:
                            # Create a file-like object from bytes
                            image_file = discord.File(
                                BytesIO(image_data),
                                filename=f"{outfit_name.replace(' ', '_').replace('/', '_')}_{outfit_id}.{extension}"
                            )
                            
                            # Send image directly as file (NO EMBED)
                            await interaction.followup.send(file=image_file)
                            sent_count += 1
                            
                            # No delay - maximum speed, send as fast as possible
                        except Exception as e:
                            logger.error(f"[OUTFIT CHECK HARD TEST] ❌ Error sending outfit {outfit_id}: {e}", exc_info=True)
                            failed_count += 1
                    else:
                        logger.warning(f"[OUTFIT CHECK HARD TEST] ⚠️ All strategies failed for outfit {outfit_id} ({outfit_name})")
                        failed_count += 1
            
            # Send beautiful completion embed
            completion_embed = discord.Embed(
                title="Outfit Identification Complete",
                description=f"The outfit identification process has been completed for **{self.roblox_username}**.",
                color=SALAMANDERS_GREEN,
                timestamp=discord.utils.utcnow()
            )
            completion_embed.set_footer(
                text="Age of Warfare • Process System",
                icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
            )
            
            await interaction.followup.send(embed=completion_embed)
            
            logger.info(f"[OUTFIT CHECK HARD TEST] ✅ Outfit check completed for {self.roblox_username} - Sent {sent_count} outfit images, {failed_count} failed out of {len(outfits)} user-created outfits")
            
        except Exception as e:
            logger.error(f"[OUTFIT CHECK] Error checking outfits: {e}", exc_info=True)
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred while checking outfits: {str(e)[:200]}",
                color=SALAMANDERS_RED,
                timestamp=discord.utils.utcnow()
            )
            error_embed.set_footer(
                text="Age of Warfare • Process System",
                icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
            )
            await interaction.followup.send(embed=error_embed)
    
    @discord.ui.button(label="Induction Process", style=discord.ButtonStyle.success, row=0)
    async def induction_process_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Induction process button - shows confirmation dialog before proceeding"""
        await interaction.response.defer(ephemeral=False)
        
        # Clear previous button messages
        if interaction.channel and isinstance(interaction.channel, discord.TextChannel):
            await self._clear_previous_button_messages(interaction.channel, interaction.client.user)
        
        try:
            # Get services
            groups_service = get_roblox_groups_service()
            
            # Main group for accepting requests: 6340169
            MAIN_GROUP_ID = 6340169  # Group to accept user
            
            # Check if Roblox cookie is configured
            if not ROBLOX_COOKIE:
                error_embed = discord.Embed(
                    title="Configuration Error",
                    description="Roblox cookie is not configured. Please set ROBLOX_COOKIE environment variable to enable group operations.",
                    color=SALAMANDERS_RED,
                    timestamp=discord.utils.utcnow()
                )
                error_embed.set_footer(
                    text="Age of Warfare • Process System",
                    icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
                )
                await interaction.followup.send(embed=error_embed)
                logger.warning("[INDUCTION] Roblox cookie not configured")
                return
            
            # Check if user is already in the main group
            logger.info(f"[INDUCTION] Checking if user {self.roblox_username} (ID: {self.roblox_id}) is already in group {MAIN_GROUP_ID}")
            is_in_group = await groups_service.is_user_in_group(self.roblox_id, MAIN_GROUP_ID)
            
            # Check if user has pending request
            has_pending_request = False
            if not is_in_group:
                logger.info(f"[INDUCTION] Checking pending request for user {self.roblox_username}")
                request_check = await groups_service.check_pending_request(
                    group_id=MAIN_GROUP_ID,
                    roblox_user_id=self.roblox_id,
                    roblox_cookie=ROBLOX_COOKIE
                )
                has_pending_request = request_check.get("has_request", False)
            
            # Get group names for display
            MAIN_GROUP_ID = 6340169
            RANK_CHANGE_GROUP_ID = 6496437
            
            main_group_info = await groups_service.get_group_info(MAIN_GROUP_ID)
            rank_group_info = await groups_service.get_group_info(RANK_CHANGE_GROUP_ID)
            
            main_group_name = main_group_info.get("name", f"Group {MAIN_GROUP_ID}") if main_group_info else f"Group {MAIN_GROUP_ID}"
            rank_group_name = rank_group_info.get("name", f"Group {RANK_CHANGE_GROUP_ID}") if rank_group_info else f"Group {RANK_CHANGE_GROUP_ID}"
            
            # Create confirmation embed
            if is_in_group:
                status_text = "✅ User is already a member of the group"
                status_color = SALAMANDERS_GREEN
            elif has_pending_request:
                status_text = "✅ User has a pending join request"
                status_color = SALAMANDERS_GREEN
            else:
                status_text = "⚠️ User does not have a pending join request"
                status_color = discord.Color.orange()
            
            confirmation_embed = discord.Embed(
                title="Induction Process Confirmation",
                description=f"Review the information below before proceeding with the induction process for **{self.roblox_username}**.",
                color=status_color,
                timestamp=discord.utils.utcnow()
            )
            
            # User information section
            confirmation_embed.add_field(
                name="Roblox Username",
                value=self.roblox_username,
                inline=True
            )
            confirmation_embed.add_field(
                name="Roblox ID",
                value=str(self.roblox_id),
                inline=True
            )
            confirmation_embed.add_field(
                name="\u200b",  # Empty field for spacing
                value="\u200b",
                inline=True
            )
            
            # Group status
            confirmation_embed.add_field(
                name="Group Status",
                value=status_text,
                inline=False
            )
            
            # What will happen section with group names
            what_will_happen = []
            if not is_in_group:
                what_will_happen.append(f"• Accept user to **{main_group_name}**")
            what_will_happen.append(f"• Change rank in **{rank_group_name}** (238 → 240)")
            what_will_happen.append("• Update Ignis database")
            
            confirmation_embed.add_field(
                name="What will happen",
                value="\n".join(what_will_happen),
                inline=False
            )
            
            confirmation_embed.set_footer(
                text="Age of Warfare • Process System",
                icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
            )
            
            # Create confirmation view with buttons
            confirmation_view = InductionConfirmationView(
                roblox_username=self.roblox_username,
                roblox_id=self.roblox_id,
                is_in_group=is_in_group,
                has_pending_request=has_pending_request
            )
            
            await interaction.followup.send(embed=confirmation_embed, view=confirmation_view)
            logger.info(f"[INDUCTION] Confirmation dialog shown for {self.roblox_username}")
            
        except Exception as e:
            logger.error(f"[INDUCTION] Error showing confirmation: {e}", exc_info=True)
            error_embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)[:200]}",
                color=SALAMANDERS_RED,
                timestamp=discord.utils.utcnow()
            )
            error_embed.set_footer(
                text="Age of Warfare • Process System",
                icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
            )
            await interaction.followup.send(embed=error_embed)
    
    @discord.ui.button(label="Close Process", style=discord.ButtonStyle.danger, row=1)
    async def close_process_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close process button - closes the channel"""
        await interaction.response.defer(ephemeral=True)
        
        # Check if user has permission to close (moderator or the channel creator)
        if not interaction.channel:
            await interaction.followup.send("❌ Channel not found.", ephemeral=True)
            return
        
        # Check if user is moderator or owner
        if not (interaction.user.guild_permissions.manage_channels or 
                interaction.user.guild_permissions.administrator or
                interaction.guild.owner_id == interaction.user.id):
            await interaction.followup.send(
                "❌ You don't have permission to close this process channel.",
                ephemeral=True
            )
            return
        
        try:
            # Delete the channel
            channel_name = interaction.channel.name
            await interaction.channel.delete()
            logger.info(f"Process channel '{channel_name}' closed by {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error closing process channel: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Error closing the channel. Please try again or contact an administrator.",
                ephemeral=True
            )
    
    # Profile Link button is now a link button added dynamically in __init__
    # This allows it to open directly without needing permission


class ProcessCog(commands.Cog):
    """Cog to manage process for new members"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bloxlink_service = BloxlinkService()
        self.audit_service = AuditService()
        # Track process channels and their last activity
        self.process_channels: dict[int, datetime] = {}  # channel_id -> last_activity
        self.inactivity_timeout = timedelta(minutes=5)  # 5 minutes of inactivity
        self.check_inactivity.start()  # Start the background task
    
    @app_commands.command(name="process", description="Start process for a player")
    @app_commands.describe(
        roblox_username="Player's Roblox nickname"
    )
    @appcmd_channel_only(PROCESS_CHANNEL_ID)
    @appcmd_moderator_or_owner()
    async def process(
        self,
        interaction: discord.Interaction,
        roblox_username: str
    ):
        """
        Start process for a player by Roblox nickname.
        Creates a private channel and posts the process embed.
        
        Requirements:
        - Valid Roblox nickname
        - User must be moderator or server owner
        - Command must be used in specific channel
        """
        # Defer immediately to avoid timeout (ephemeral - only visible to command executor)
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
        except Exception as e:
            logger.error(f"Error deferring interaction: {e}", exc_info=True)
            # Try to send error message if defer failed
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ Error processing command. Please try again.",
                        ephemeral=True
                    )
            except:
                pass
            return
        
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
            avatar_url = None
            
            # HARD TEST: Get 3D avatar render from Roblox API (the image below [ONLINE] on profile page)
            # This is the full body 3D render that appears on the user's profile
            # We'll try multiple strategies to ensure we get a working image URL
            if roblox_id and roblox_id != "Unknown":
                logger.info(f"[AVATAR TEST] Starting avatar fetch for {roblox_username_found} (ID: {roblox_id})")
                
                # Strategy 1: Try avatar-3d endpoint (full body 3D render - preferred)
                try:
                    thumbnail_url = f"https://thumbnails.roblox.com/v1/users/avatar-3d?userIds={roblox_id}&size=420x420&format=Png&isCircular=false"
                    logger.info(f"[AVATAR TEST] Strategy 1: Trying avatar-3d endpoint: {thumbnail_url}")
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(thumbnail_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                            if response.status == 200:
                                data = await response.json()
                                logger.info(f"[AVATAR TEST] Strategy 1 response: {data}")
                                # The API returns: {"data": [{"targetId": ..., "state": "Completed", "imageUrl": "..."}]}
                                if data.get("data") and len(data["data"]) > 0:
                                    image_data = data["data"][0]
                                    state = image_data.get("state")
                                    image_url = image_data.get("imageUrl")
                                    
                                    if state == "Completed" and image_url:
                                        avatar_url = image_url
                                        logger.info(f"[AVATAR TEST] ✅ Strategy 1 SUCCESS: {avatar_url[:100]}...")
                                    else:
                                        logger.warning(f"[AVATAR TEST] Strategy 1: state={state}, imageUrl={image_url}")
                                else:
                                    logger.warning(f"[AVATAR TEST] Strategy 1: Empty data array")
                            else:
                                logger.warning(f"[AVATAR TEST] Strategy 1: HTTP {response.status}")
                except asyncio.TimeoutError:
                    logger.warning(f"[AVATAR TEST] Strategy 1: Timeout")
                except Exception as e:
                    logger.error(f"[AVATAR TEST] Strategy 1 error: {e}", exc_info=True)
                
                # Strategy 2: If 3D render failed, try regular avatar endpoint
                if not avatar_url:
                    try:
                        logger.info(f"[AVATAR TEST] Strategy 2: Trying regular avatar endpoint...")
                        thumbnail_url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={roblox_id}&size=420x420&format=Png&isCircular=false"
                        
                        async with aiohttp.ClientSession() as session:
                            async with session.get(thumbnail_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    logger.info(f"[AVATAR TEST] Strategy 2 response: {data}")
                                    if data.get("data") and len(data["data"]) > 0:
                                        image_data = data["data"][0]
                                        if image_data.get("state") == "Completed" and image_data.get("imageUrl"):
                                            avatar_url = image_data.get("imageUrl")
                                            logger.info(f"[AVATAR TEST] ✅ Strategy 2 SUCCESS: {avatar_url[:100]}...")
                    except Exception as e:
                        logger.warning(f"[AVATAR TEST] Strategy 2 error: {e}")
                
                # Strategy 3: Fallback to direct bust-thumbnail URL (always works, but not 3D render)
                if not avatar_url:
                    logger.warning(f"[AVATAR TEST] Strategy 3: Using fallback bust-thumbnail")
                    avatar_url = f"https://www.roblox.com/bust-thumbnail/image?userId={roblox_id}&width=420&height=420&format=png"
                    logger.info(f"[AVATAR TEST] Strategy 3 fallback URL: {avatar_url}")
            else:
                logger.error(f"[AVATAR TEST] ❌ No roblox_id available for {roblox_username_found}")
            
            # Final validation and logging
            if avatar_url:
                logger.info(f"[AVATAR TEST] ✅ FINAL avatar URL for {roblox_username_found}: {avatar_url}")
            else:
                logger.error(f"[AVATAR TEST] ❌ NO AVATAR URL after all strategies for {roblox_username_found}")
            
            # Get guild
            guild = interaction.guild
            if not guild:
                await interaction.followup.send(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return
            
            # Create private channel name
            channel_name = f"{roblox_username_found.lower()}-process"
            
            # Check if channel already exists
            existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
            if existing_channel:
                await interaction.followup.send(
                    f"❌ A process channel for **{roblox_username_found}** already exists: {existing_channel.mention}",
                    ephemeral=True
                )
                return
            
            # Create channel overwrites - private only for the user who executed the command
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Everyone can't see
                interaction.user: discord.PermissionOverwrite(
                    view_channel=True,
                    read_messages=True,
                    send_messages=True,
                    read_message_history=True
                ),  # Command executor can see and use
                guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    read_messages=True,
                    send_messages=True,
                    manage_messages=True,
                    read_message_history=True
                )  # Bot can see and manage
            }
            
            # Get category
            category = guild.get_channel(PROCESS_CATEGORY_ID)
            if not category or not isinstance(category, discord.CategoryChannel):
                logger.warning(f"Category {PROCESS_CATEGORY_ID} not found, creating channel without category")
                category = None
            
            # Create the private channel
            try:
                process_channel = await guild.create_text_channel(
                    name=channel_name,
                    category=category,
                    overwrites=overwrites,
                    reason=f"Process channel created for {roblox_username_found} by {interaction.user.display_name}"
                )
                logger.info(f"Created process channel '{channel_name}' for {roblox_username_found} in category {PROCESS_CATEGORY_ID}")
            except discord.Forbidden:
                await interaction.followup.send(
                    "❌ I don't have permission to create channels. Please check my permissions.",
                    ephemeral=True
                )
                return
            except Exception as e:
                logger.error(f"Error creating process channel: {e}", exc_info=True)
                await interaction.followup.send(
                    "❌ Error creating process channel. Please check the logs.",
                    ephemeral=True
                )
                return
            
            # Create process embed with Salamanders theme
            embed = discord.Embed(
                title=f"{roblox_username_found}'s Process",
                color=SALAMANDERS_GREEN,
                timestamp=discord.utils.utcnow()
            )
            
            # Add sections as described in the image
            embed.add_field(
                name="Age of Warfare Check",
                value=(
                    "Pressing the 'Group Check(s)' button below will check the user's groups "
                    "to find if he is in the AoW group, and if he is in, the rank will also be sent. "
                    "It will also check if he is in other Legions' groups."
                ),
                inline=False
            )
            
            embed.add_field(
                name="Outfit Check",
                value=(
                    "Pressing the button below will check the user's outfits and send images of them."
                ),
                inline=False
            )
            
            embed.add_field(
                name="Induction Process",
                value=(
                    "Pressing the 'Induction Process' button will automatically accept the user "
                    "into the Legions' group and rank them accordingly. It will also rank the user "
                    "in the AoD group as Legiones Astartes."
                ),
                inline=False
            )
            
            embed.add_field(
                name="Roblox Profile",
                value=(
                    f"In-case any further information is required, the profile for **{roblox_username_found}** "
                    "will be available below via the gray button called 'Profile Link'"
                ),
                inline=False
            )
            
            # CRITICAL: Set avatar as image BEFORE footer (order matters for Discord embeds)
            # Use 3D render from profile (image below [ONLINE])
            if avatar_url:
                try:
                    logger.info(f"[AVATAR TEST] Setting embed image with URL: {avatar_url[:150]}...")
                    embed.set_image(url=avatar_url)
                    
                    # Verify the image was set
                    if hasattr(embed, 'image') and embed.image:
                        if hasattr(embed.image, 'url') and embed.image.url:
                            logger.info(f"[AVATAR TEST] ✅ Embed image confirmed: {embed.image.url[:150]}...")
                        else:
                            logger.error(f"[AVATAR TEST] ❌ embed.image.url is None or missing!")
                    else:
                        logger.error(f"[AVATAR TEST] ❌ embed.image is None after set_image!")
                except Exception as e:
                    logger.error(f"[AVATAR TEST] ❌ Exception setting embed image: {e}", exc_info=True)
                    # Try alternative method
                    try:
                        embed._image = {"url": avatar_url}
                        logger.info(f"[AVATAR TEST] ✅ Used alternative method to set image")
                    except Exception as e2:
                        logger.error(f"[AVATAR TEST] ❌ Alternative method also failed: {e2}")
            else:
                logger.error(f"[AVATAR TEST] ❌ No avatar URL available for {roblox_username_found} - embed will NOT have image")
            
            # Footer with Salamanders theme (set AFTER image)
            embed.set_footer(
                text="Age of Warfare • For Nocturne. For Vulkan.",
                icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
            )
            
            # Final verification before sending
            if avatar_url:
                logger.info(f"[AVATAR TEST] Final check - embed.image before send: {embed.image.url if embed.image else 'None'}")
            
            # Create view with buttons
            view = ProcessButtonsView(roblox_username_found, roblox_id)
            
            # Send embed to the new private channel
            main_message = await process_channel.send(embed=embed, view=view)
            
            # Store the main embed message ID in the view
            view.main_embed_message_id = main_message.id
            
            # Create beautiful embed response for the command (ephemeral - only visible to command executor)
            response_embed = discord.Embed(
                title="✅ Process Channel Created",
                description=(
                    f"**Channel:** {process_channel.mention}\n"
                    f"**Player:** {roblox_username_found}\n"
                    f"**Status:** Private (only visible to you)"
                ),
                color=SALAMANDERS_GREEN,
                timestamp=discord.utils.utcnow()
            )
            
            # Add warning about auto-closing (as shown in the image)
            response_embed.add_field(
                name="⚠️ Important Notice",
                value=(
                    "This channel will be automatically closed within **10 minutes of inactivity**.\n"
                    "Make sure to complete all necessary checks before the channel closes."
                ),
                inline=False
            )
            
            # Add footer with Salamanders theme
            response_embed.set_footer(
                text="Age of Warfare • Process Management",
                icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
            )
            
            # Send beautiful embed response
            await interaction.followup.send(embed=response_embed, ephemeral=True)
            
            # Register channel for inactivity monitoring
            self.process_channels[process_channel.id] = datetime.now(timezone.utc)
            logger.info(f"[INACTIVITY] Registered channel {process_channel.id} for inactivity monitoring (5 min timeout)")
            
            # Audit log
            await self.audit_service.log_operation(
                user_id=0,  # No Discord ID available, only Roblox username
                action_type="CREATE",
                data_type="process",
                performed_by=interaction.user.id,
                purpose="Process channel created",
                details={
                    "roblox_username": roblox_username_found,
                    "roblox_id": roblox_id,
                    "channel_id": process_channel.id,
                    "channel_name": channel_name,
                    "searched_username": searched_username
                }
            )
            
            logger.info(
                f"Process started for Roblox user {roblox_username_found} (ID: {roblox_id}) "
                f"by {interaction.user.id} in channel {process_channel.id}"
            )
            
        except Exception as e:
            logger.error(f"Error in process command: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Error starting process. Please check the logs.",
                ephemeral=True
            )
    
    @tasks.loop(minutes=1)  # Check every minute
    async def check_inactivity(self):
        """Check for inactive process channels and close them after 5 minutes"""
        if not self.bot.is_ready():
            return
        
        current_time = datetime.now(timezone.utc)
        channels_to_close = []
        
        for channel_id, last_activity in list(self.process_channels.items()):
            # Check if channel still exists
            channel = self.bot.get_channel(channel_id)
            if not channel:
                # Channel was deleted manually, remove from tracking
                logger.info(f"[INACTIVITY] Channel {channel_id} no longer exists, removing from tracking")
                self.process_channels.pop(channel_id, None)
                continue
            
            # Calculate inactivity duration
            inactivity_duration = current_time - last_activity
            
            if inactivity_duration >= self.inactivity_timeout:
                channels_to_close.append((channel, inactivity_duration))
            else:
                # Log remaining time for debugging
                remaining = self.inactivity_timeout - inactivity_duration
                logger.debug(f"[INACTIVITY] Channel {channel_id} still active, {remaining.total_seconds():.0f}s remaining")
        
        # Close inactive channels
        for channel, duration in channels_to_close:
            try:
                logger.info(f"[INACTIVITY] Closing channel {channel.id} after {duration.total_seconds():.0f}s of inactivity")
                
                # Send a final message before closing
                try:
                    closing_embed = discord.Embed(
                        title="⚠️ Channel Closing",
                        description=(
                            "This channel has been inactive for **5 minutes**.\n"
                            "The channel will now be automatically closed."
                        ),
                        color=discord.Color.orange(),
                        timestamp=discord.utils.utcnow()
                    )
                    closing_embed.set_footer(
                        text="Age of Warfare • Auto-Close System",
                        icon_url="https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
                    )
                    await channel.send(embed=closing_embed)
                    await asyncio.sleep(2)  # Give time for message to send
                except Exception as e:
                    logger.warning(f"[INACTIVITY] Could not send closing message: {e}")
                
                # Delete the channel
                await channel.delete(reason="Auto-closed after 5 minutes of inactivity")
                logger.info(f"[INACTIVITY] ✅ Successfully closed channel {channel.id}")
                
                # Remove from tracking
                self.process_channels.pop(channel.id, None)
                
            except discord.Forbidden:
                logger.error(f"[INACTIVITY] ❌ No permission to delete channel {channel.id}")
                self.process_channels.pop(channel.id, None)
            except discord.NotFound:
                logger.warning(f"[INACTIVITY] Channel {channel.id} already deleted")
                self.process_channels.pop(channel.id, None)
            except Exception as e:
                logger.error(f"[INACTIVITY] ❌ Error closing channel {channel.id}: {e}", exc_info=True)
    
    @check_inactivity.before_loop
    async def before_check_inactivity(self):
        """Wait until bot is ready before starting the task"""
        await self.bot.wait_until_ready()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.check_inactivity.cancel()
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Update last activity when a message is sent in a process channel"""
        if message.author.bot:
            return
        
        if message.channel.id in self.process_channels:
            self.process_channels[message.channel.id] = datetime.now(timezone.utc)
            logger.debug(f"[INACTIVITY] Updated activity for channel {message.channel.id}")
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Update last activity when an interaction occurs in a process channel"""
        if not hasattr(interaction, 'channel') or not interaction.channel:
            return
        
        if interaction.channel.id in self.process_channels:
            self.process_channels[interaction.channel.id] = datetime.now(timezone.utc)
            logger.debug(f"[INACTIVITY] Updated activity for channel {interaction.channel.id} (interaction)")


async def setup(bot: commands.Bot):
    await bot.add_cog(ProcessCog(bot))

