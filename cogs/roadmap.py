"""
Roadmap Cog - Development roadmap announcements.

Allows moderators to post development roadmap updates
and automatically posts updates based on documentation.
"""

from __future__ import annotations

import asyncio
import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timezone, timedelta
from typing import Optional
import hashlib
import re

from utils.checks import appcmd_moderator_or_owner
from utils.logger import get_logger
from utils.roadmap_parser import get_latest_roadmap_data, format_roadmap_items

logger = get_logger(__name__)

# Channel ID for roadmap announcements
ROADMAP_CHANNEL_ID = 1375941285839638536

# Salamanders role ID to mention
SALAMANDERS_ROLE_ID = 1376831480931815424

# Salamanders footer icon
SALAMANDERS_FOOTER_ICON = "https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"

# Salamanders theme colors
SALAMANDERS_GREEN = 0x2ECC71


class RoadmapCog(commands.Cog):
    """Cog for posting development roadmap updates"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_roadmap_post: Optional[datetime] = None
        self.last_roadmap_hash: Optional[str] = None
        self.startup_posted: bool = False  # Flag to ensure only one post on startup
        self._posting_lock: asyncio.Lock = asyncio.Lock()  # Lock to prevent concurrent posts
        # Start automatic posting task
        self.auto_post_roadmap.start()
    
    @app_commands.command(
        name="roadmap",
        description="Post a development roadmap update to the announcements channel"
    )
    @app_commands.describe(
        title="Title of the roadmap update",
        description="Main description of the update (what was changed/added)",
        features="New features added (optional, use newlines for multiple)",
        fixes="Bug fixes and improvements (optional, use newlines for multiple)",
        upcoming="Upcoming features (optional, use newlines for multiple)"
    )
    @appcmd_moderator_or_owner()
    async def roadmap(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        features: str = "",
        fixes: str = "",
        upcoming: str = ""
    ):
        """
        Post a development roadmap update.
        
        Creates a beautiful embed with the latest IgnisBot updates
        and mentions the Salamanders role.
        """
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        try:
            # Get the roadmap channel
            roadmap_channel = self.bot.get_channel(ROADMAP_CHANNEL_ID)
            if not isinstance(roadmap_channel, discord.TextChannel):
                await interaction.followup.send(
                    "❌ Roadmap channel not found. Please check the channel ID.",
                    ephemeral=True
                )
                return
            
            # Get Salamanders role for mention
            guild = interaction.guild
            if not guild:
                await interaction.followup.send(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return
            
            salamanders_role = guild.get_role(SALAMANDERS_ROLE_ID)
            role_mention = salamanders_role.mention if salamanders_role else "@Salamanders"
            
            # Create the roadmap embed
            embed = discord.Embed(
                title=f"🚀 {title}",
                description=description,
                color=SALAMANDERS_GREEN,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Add features section if provided
            if features and features.strip():
                embed.add_field(
                    name="✨ New Features",
                    value=features.strip(),
                    inline=False
                )
            
            # Add fixes section if provided
            if fixes and fixes.strip():
                embed.add_field(
                    name="🔧 Fixes & Improvements",
                    value=fixes.strip(),
                    inline=False
                )
            
            # Add upcoming section if provided
            if upcoming and upcoming.strip():
                embed.add_field(
                    name="📋 Upcoming",
                    value=upcoming.strip(),
                    inline=False
                )
            
            # Set footer with Salamanders icon
            embed.set_footer(
                text="IgnisBot Development Roadmap • Age of Warfare",
                icon_url=SALAMANDERS_FOOTER_ICON
            )
            
            # Send the embed (without role mention to avoid mass pings)
            await roadmap_channel.send(embed=embed)
            
            # Send confirmation to command executor
            await interaction.followup.send(
                f"✅ Roadmap update posted in {roadmap_channel.mention}",
                ephemeral=True
            )
            
            logger.info(
                f"Roadmap update posted by {interaction.user.id} "
                f"in channel {ROADMAP_CHANNEL_ID}"
            )
            
        except Exception as e:
            logger.error(f"Error posting roadmap update: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Error posting roadmap update. Please check the logs.",
                ephemeral=True
            )
    
    async def _check_if_message_exists(self, channel: discord.TextChannel, title: str, check_recent: bool = True, time_window: timedelta = timedelta(minutes=5)) -> bool:
        """
        Check if a message with the same title already exists in the channel.
        
        Args:
            channel: The channel to check
            title: The title to search for
            check_recent: If True, only check messages within time_window
            time_window: Time window to check for recent messages
        
        Returns:
            True if message exists, False otherwise
        """
        try:
            # For recent check, only look at last 15 messages within time window
            limit = 15 if check_recent else 30
            cutoff_time = datetime.now(timezone.utc) - time_window if check_recent else None
            
            async for message in channel.history(limit=limit):
                # Skip if checking recent and message is too old
                if check_recent and cutoff_time and message.created_at < cutoff_time:
                    continue
                    
                if message.author == self.bot.user and message.embeds:
                    for embed in message.embeds:
                        if embed.title:
                            # Check if titles match (normalize for comparison)
                            embed_title_clean = embed.title.replace("🚀", "").strip()
                            title_clean = title.replace("🚀", "").strip()
                            
                            # Check if titles are similar (same base title)
                            if title_clean in embed_title_clean or embed_title_clean in title_clean:
                                logger.debug(f"[ROADMAP] Found existing message with title: {embed.title}")
                                return True
                            
                            # Also check if it's the same date-based title
                            if "Development Update" in embed_title_clean and "Development Update" in title_clean:
                                # Extract dates and compare
                                date_pattern = r"(\d{4}-\d{2}-\d{2})"
                                embed_date = re.search(date_pattern, embed_title_clean)
                                title_date = re.search(date_pattern, title_clean)
                                if embed_date and title_date and embed_date.group(1) == title_date.group(1):
                                    logger.debug(f"[ROADMAP] Found existing message with same date: {embed.title}")
                                    return True
        except Exception as e:
            logger.warning(f"[ROADMAP] Error checking channel history: {e}")
        
        return False
    
    async def _post_roadmap_automatically(self, force_post: bool = False) -> bool:
        """
        Post roadmap update automatically based on documentation.
        
        Args:
            force_post: If True, post even if hash hasn't changed (for startup)
        
        Returns:
            True if posted, False otherwise
        """
        # Use lock to prevent concurrent posts
        async with self._posting_lock:
            return await self._post_roadmap_automatically_internal(force_post)
    
    async def _post_roadmap_automatically_internal(self, force_post: bool = False) -> bool:
        """
        Internal method to post roadmap - called with lock held.
        """
        try:
            # Get roadmap data from documentation
            roadmap_data = get_latest_roadmap_data()
            
            # Use the comprehensive hash from parser
            current_hash = roadmap_data.get('content_hash', '')
            
            # If no hash, create one from data
            if not current_hash:
                data_string = f"{roadmap_data['title']}{roadmap_data['description']}{len(roadmap_data['features'])}{len(roadmap_data['fixes'])}{len(roadmap_data['upcoming'])}"
                current_hash = hashlib.md5(data_string.encode()).hexdigest()
            
            # Get the roadmap channel first to check for duplicates
            roadmap_channel = self.bot.get_channel(ROADMAP_CHANNEL_ID)
            if not isinstance(roadmap_channel, discord.TextChannel):
                logger.error(f"[ROADMAP] Channel {ROADMAP_CHANNEL_ID} not found")
                return False
            
            # Check if message with same title already exists
            # For force_post, check recent messages (last 10 minutes) more strictly
            # For normal post, check all recent messages
            check_recent = force_post  # Only check recent for force_post
            time_window = timedelta(minutes=10) if force_post else timedelta(minutes=30)
            
            if await self._check_if_message_exists(roadmap_channel, roadmap_data['title'], check_recent=check_recent, time_window=time_window):
                logger.info(f"[ROADMAP] Message with title '{roadmap_data['title']}' already exists (within {time_window.total_seconds()/60:.0f}min), skipping to avoid duplicate")
                # Update hash to prevent repeated checks
                self.last_roadmap_hash = current_hash
                return False
            
            # Additional check: if we posted very recently (within last 5 minutes), skip
            if self.last_roadmap_post:
                time_since_last = datetime.now(timezone.utc) - self.last_roadmap_post
                if time_since_last < timedelta(minutes=5):
                    logger.info(f"[ROADMAP] Posted recently ({time_since_last.total_seconds():.0f}s ago), skipping to avoid duplicate")
                    return False
            
            # Check if roadmap has changed since last post (unless forced)
            if not force_post and current_hash == self.last_roadmap_hash:
                logger.debug(f"[ROADMAP] No changes detected (hash: {current_hash[:8]}...), skipping auto-post")
                return False
            
            # If forced post but content is same, use original title (don't add timestamp)
            # The duplicate check above will prevent multiple posts
            if force_post and current_hash == self.last_roadmap_hash:
                logger.info(f"[ROADMAP] Force post with same content, using original title")
            
            logger.info(f"[ROADMAP] Posting roadmap update. Old hash: {self.last_roadmap_hash[:8] if self.last_roadmap_hash else 'None'}..., New hash: {current_hash[:8]}...")
            logger.info(f"[ROADMAP] Roadmap data - Features: {len(roadmap_data.get('features', []))}, Fixes: {len(roadmap_data.get('fixes', []))}, Upcoming: {len(roadmap_data.get('upcoming', []))}")
            logger.info(f"[ROADMAP] Title: {roadmap_data.get('title')}, Description: {roadmap_data.get('description')[:100]}...")
            
            # Get Salamanders role
            guild = roadmap_channel.guild
            if not guild:
                return False
            
            salamanders_role = guild.get_role(SALAMANDERS_ROLE_ID)
            role_mention = salamanders_role.mention if salamanders_role else "@Salamanders"
            
            # Create embed with unique identifier in footer to prevent duplicates
            embed = discord.Embed(
                title=f"🚀 {roadmap_data['title']}",
                description=roadmap_data['description'],
                color=SALAMANDERS_GREEN,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Add sections if available (only if they have content)
            features_text = format_roadmap_items(roadmap_data['features']) if roadmap_data['features'] else None
            fixes_text = format_roadmap_items(roadmap_data['fixes']) if roadmap_data['fixes'] else None
            upcoming_text = format_roadmap_items(roadmap_data['upcoming']) if roadmap_data['upcoming'] else None
            
            # Only add fields if they have meaningful content
            if features_text and features_text != "None":
                embed.add_field(
                    name="✨ New Features",
                    value=features_text,
                    inline=False
                )
            
            if fixes_text and fixes_text != "None":
                embed.add_field(
                    name="🔧 Fixes & Improvements",
                    value=fixes_text,
                    inline=False
                )
            
            if upcoming_text and upcoming_text != "None":
                embed.add_field(
                    name="📋 Upcoming",
                    value=upcoming_text,
                    inline=False
                )
            
            # Always add content - if no features/fixes, show what we have
            # But prioritize showing actual content
            if not any([features_text and features_text != "None", 
                       fixes_text and fixes_text != "None", 
                       upcoming_text and upcoming_text != "None"]):
                # If we have features or fixes in the data but they're empty after formatting, log it
                if roadmap_data.get('features') or roadmap_data.get('fixes'):
                    logger.warning(f"[ROADMAP] Has data but formatted empty - Features: {len(roadmap_data.get('features', []))}, Fixes: {len(roadmap_data.get('fixes', []))}")
                embed.add_field(
                    name="ℹ️ Status",
                    value="Development continues with ongoing improvements. Check documentation for details.",
                    inline=False
                )
            
            # Set footer
            embed.set_footer(
                text="IgnisBot Development Roadmap • Age of Warfare",
                icon_url=SALAMANDERS_FOOTER_ICON
            )
            
            # Post the embed (without role mention to avoid mass pings)
            await roadmap_channel.send(embed=embed)
            
            # Update tracking
            self.last_roadmap_post = datetime.now(timezone.utc)
            self.last_roadmap_hash = current_hash
            
            logger.info(
                f"[ROADMAP] ✅ Auto-posted roadmap update: {roadmap_data['title']}\n"
                f"  Features: {len(roadmap_data['features'])}, "
                f"Fixes: {len(roadmap_data['fixes'])}, "
                f"Upcoming: {len(roadmap_data['upcoming'])}"
            )
            return True
            
        except Exception as e:
            logger.error(f"[ROADMAP] Error auto-posting roadmap: {e}", exc_info=True)
            return False
    
    @tasks.loop(hours=2)  # Check every 2 hours (reduced from 6 for faster updates)
    async def auto_post_roadmap(self):
        """Automatically post roadmap updates based on documentation changes."""
        if not self.bot.is_ready():
            return
        
        logger.info("[ROADMAP] 🔍 Checking for roadmap updates...")
        posted = await self._post_roadmap_automatically()
        
        if posted:
            logger.info("[ROADMAP] ✅ Roadmap update posted automatically")
        else:
            logger.debug("[ROADMAP] No new updates to post")
    
    @auto_post_roadmap.before_loop
    async def before_auto_post_roadmap(self):
        """Wait until bot is ready before starting the task."""
        await self.bot.wait_until_ready()
        # Wait additional 30 seconds for all cogs to load
        await asyncio.sleep(30)
    
    def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.auto_post_roadmap.cancel()
    
    async def _post_on_startup(self):
        """Post roadmap on bot startup - called from setup_hook with delay."""
        # Use bot-level flag to prevent multiple cogs from posting
        if not hasattr(self.bot, 'roadmap_startup_posted'):
            self.bot.roadmap_startup_posted = False
        
        # Prevent multiple posts
        if self.bot.roadmap_startup_posted or self.startup_posted:
            logger.debug("[ROADMAP] Startup post already done, skipping")
            return
        
        # Wait for bot to be fully ready
        await self.bot.wait_until_ready()
        await asyncio.sleep(35)  # Wait 35 seconds after ready for all cogs to load
        
        # Double-check bot is ready
        if not self.bot.is_ready():
            logger.debug("[ROADMAP] Bot not ready yet, skipping startup post")
            return
        
        # Mark as posted BEFORE posting to prevent race conditions (both flags)
        self.bot.roadmap_startup_posted = True
        self.startup_posted = True
        
        # Always post on startup (force_post=True) to ensure latest info is shared
        logger.info("[ROADMAP] Posting roadmap update on startup (forced)...")
        posted = await self._post_roadmap_automatically(force_post=True)
        
        if posted:
            logger.info("[ROADMAP] ✅ Roadmap update posted on startup")
        else:
            logger.info("[ROADMAP] Roadmap update skipped (duplicate or no changes)")
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Post roadmap on bot startup - only on first ready."""
        # Only post on first ready (not reconnections)
        if not hasattr(self.bot, 'ready_count'):
            self.bot.ready_count = 0
        self.bot.ready_count += 1
        
        # Only post on first ready and if not already posted
        if self.bot.ready_count == 1 and not self.startup_posted:
            # Check bot-level flag too
            if not hasattr(self.bot, 'roadmap_startup_posted') or not self.bot.roadmap_startup_posted:
                # Schedule post with delay to avoid conflicts
                logger.info(f"[ROADMAP] Scheduling startup post (ready_count={self.bot.ready_count})")
                self.bot.loop.create_task(self._post_on_startup())
            else:
                logger.debug("[ROADMAP] Startup post already scheduled by another instance")
        else:
            logger.debug(f"[ROADMAP] Bot reconnected (ready_count={self.bot.ready_count}, startup_posted={self.startup_posted}), skipping startup post")


async def setup(bot: commands.Bot):
    await bot.add_cog(RoadmapCog(bot))

