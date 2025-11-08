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

from utils.checks import appcmd_moderator_or_owner
from utils.logger import get_logger
from utils.roadmap_parser import get_latest_roadmap_data, format_roadmap_items

logger = get_logger(__name__)

# Channel ID for roadmap announcements
ROADMAP_CHANNEL_ID = 1375941285839638536

# Salamanders role ID to mention
SALAMANDERS_ROLE_ID = 1435800430516113511

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
            
            # Send the embed with role mention
            await roadmap_channel.send(content=role_mention, embed=embed)
            
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
    
    async def _post_roadmap_automatically(self) -> bool:
        """
        Post roadmap update automatically based on documentation.
        
        Returns:
            True if posted, False otherwise
        """
        try:
            # Get roadmap data from documentation
            roadmap_data = get_latest_roadmap_data()
            
            # Create hash of the roadmap data to detect changes
            data_string = f"{roadmap_data['title']}{roadmap_data['description']}{len(roadmap_data['features'])}{len(roadmap_data['fixes'])}{len(roadmap_data['upcoming'])}"
            current_hash = hashlib.md5(data_string.encode()).hexdigest()
            
            # Check if roadmap has changed since last post
            if current_hash == self.last_roadmap_hash:
                logger.debug("[ROADMAP] No changes detected, skipping auto-post")
                return False
            
            # Get the roadmap channel
            roadmap_channel = self.bot.get_channel(ROADMAP_CHANNEL_ID)
            if not isinstance(roadmap_channel, discord.TextChannel):
                logger.error(f"[ROADMAP] Channel {ROADMAP_CHANNEL_ID} not found")
                return False
            
            # Get Salamanders role
            guild = roadmap_channel.guild
            if not guild:
                return False
            
            salamanders_role = guild.get_role(SALAMANDERS_ROLE_ID)
            role_mention = salamanders_role.mention if salamanders_role else "@Salamanders"
            
            # Create embed
            embed = discord.Embed(
                title=f"🚀 {roadmap_data['title']}",
                description=roadmap_data['description'],
                color=SALAMANDERS_GREEN,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Add sections if available
            if roadmap_data['features']:
                embed.add_field(
                    name="✨ New Features",
                    value=format_roadmap_items(roadmap_data['features']),
                    inline=False
                )
            
            if roadmap_data['fixes']:
                embed.add_field(
                    name="🔧 Fixes & Improvements",
                    value=format_roadmap_items(roadmap_data['fixes']),
                    inline=False
                )
            
            if roadmap_data['upcoming']:
                embed.add_field(
                    name="📋 Upcoming",
                    value=format_roadmap_items(roadmap_data['upcoming']),
                    inline=False
                )
            
            # Set footer
            embed.set_footer(
                text="IgnisBot Development Roadmap • Age of Warfare",
                icon_url=SALAMANDERS_FOOTER_ICON
            )
            
            # Post the embed
            await roadmap_channel.send(content=role_mention, embed=embed)
            
            # Update tracking
            self.last_roadmap_post = datetime.now(timezone.utc)
            self.last_roadmap_hash = current_hash
            
            logger.info(f"[ROADMAP] Auto-posted roadmap update: {roadmap_data['title']}")
            return True
            
        except Exception as e:
            logger.error(f"[ROADMAP] Error auto-posting roadmap: {e}", exc_info=True)
            return False
    
    @tasks.loop(hours=6)  # Check every 6 hours
    async def auto_post_roadmap(self):
        """Automatically post roadmap updates based on documentation changes."""
        if not self.bot.is_ready():
            return
        
        logger.info("[ROADMAP] Checking for roadmap updates...")
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
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Post roadmap on bot startup if documentation has changed."""
        # Wait a bit for everything to initialize
        await asyncio.sleep(60)  # Wait 1 minute after ready
        
        # Post initial roadmap if it's the first time or if documentation changed
        if self.last_roadmap_hash is None:
            logger.info("[ROADMAP] Posting initial roadmap on startup...")
            await self._post_roadmap_automatically()


async def setup(bot: commands.Bot):
    await bot.add_cog(RoadmapCog(bot))

