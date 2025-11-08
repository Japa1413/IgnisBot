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

from services.bloxlink_service import BloxlinkService
from services.audit_service import AuditService
from utils.checks import appcmd_channel_only, appcmd_moderator_or_owner
from utils.config import GUILD_ID
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


class ProcessButtonsView(discord.ui.View):
    """View with buttons for the process embed"""
    
    def __init__(self, roblox_username: str, roblox_id: int):
        super().__init__(timeout=None)  # Persistent view
        self.roblox_username = roblox_username
        self.roblox_id = roblox_id
        
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
    
    @discord.ui.button(label="Group(s) Check", style=discord.ButtonStyle.success, row=0)
    async def group_check_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Group check button - to be implemented in next step"""
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            "🔍 Group check functionality will be implemented in the next step.",
            ephemeral=True
        )
    
    @discord.ui.button(label="Outfit(s) Check", style=discord.ButtonStyle.success, row=0)
    async def outfit_check_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Outfit check button - to be implemented in next step"""
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            "👕 Outfit check functionality will be implemented in the next step.",
            ephemeral=True
        )
    
    @discord.ui.button(label="Induction Process", style=discord.ButtonStyle.success, row=0)
    async def induction_process_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Induction process button - to be implemented in next step"""
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            "⚔️ Induction process functionality will be implemented in the next step.",
            ephemeral=True
        )
    
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
            await process_channel.send(embed=embed, view=view)
            
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

