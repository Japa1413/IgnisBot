"""
Member Activity Log - Monitor member activity events and log to Discord channel.

This cog monitors:
- Member join/leave ALL voice channels (with timestamps) - NO RESTRICTIONS
- Member switch between ANY voice channels (with timestamps)
- Member join/leave guild (with full Discord and Roblox profile information)

IMPORTANT: All voice channels are monitored without exception. No channel filtering is applied.
"""

from __future__ import annotations

import discord
from discord.ext import commands
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from utils.logger import get_logger
from services.bloxlink_service import BloxlinkService

logger = get_logger(__name__)

# Channel ID for activity logs
ACTIVITY_LOG_CHANNEL_ID = 1375941287357710362


class MemberActivityLogCog(commands.Cog):
    """Monitor and log member activity events"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bloxlink_service = BloxlinkService()
        # Track voice join times: {user_id: datetime}
        self._voice_join_times: Dict[int, datetime] = {}
    
    async def _get_log_channel(self) -> Optional[discord.TextChannel]:
        """Get the activity log channel"""
        channel = self.bot.get_channel(ACTIVITY_LOG_CHANNEL_ID)
        if isinstance(channel, discord.TextChannel):
            return channel
        return None
    
    async def _create_roblox_embed_section(
        self,
        member: discord.Member,
        embed: discord.Embed
    ) -> None:
        """
        Add Roblox profile information to embed.
        
        Args:
            member: Discord member
            embed: Embed to add information to
        """
        try:
            # Get Roblox data via Bloxlink
            roblox_data = await self.bloxlink_service.get_roblox_user(
                discord_id=member.id,
                guild_id=member.guild.id if member.guild else None
            )
            
            if roblox_data:
                embed.add_field(
                    name="**Roblox Profile**",
                    value=(
                        f"**Username:** {roblox_data.get('username', 'N/A')}\n"
                        f"**User ID:** `{roblox_data.get('id', 'N/A')}`\n"
                        f"**Verified:** ✅ Yes\n"
                        f"**Avatar:** [View Profile](https://www.roblox.com/users/{roblox_data.get('id', '')}/profile)"
                    ),
                    inline=False
                )
                
                # Add Roblox avatar as thumbnail if available
                avatar_url = roblox_data.get('avatar_url')
                if avatar_url:
                    embed.set_thumbnail(url=avatar_url)
            else:
                embed.add_field(
                    name="**Roblox Profile**",
                    value="❌ Not verified via Bloxlink",
                    inline=False
                )
        except Exception as e:
            logger.warning(f"Error fetching Roblox data for {member.id}: {e}")
            embed.add_field(
                name="**Roblox Profile**",
                value="⚠️ Error fetching Roblox data",
                inline=False
            )
    
    async def _create_discord_profile_embed(
        self,
        member: discord.Member,
        title: str,
        color: discord.Color,
        description: Optional[str] = None
    ) -> discord.Embed:
        """
        Create a rich embed with full Discord and Roblox profile information.
        
        Args:
            member: Discord member
            title: Embed title
            color: Embed color
            description: Optional description
        
        Returns:
            Discord embed with full profile information
        """
        embed = discord.Embed(
            title=title,
            description=description or "",
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Discord Profile Information
        joined_server_text = f"<t:{int(member.joined_at.timestamp())}:F>" if member.joined_at else "N/A"
        embed.add_field(
            name="**Discord Profile**",
            value=(
                f"**Username:** {member.name}\n"
                f"**Display Name:** {member.display_name}\n"
                f"**User ID:** `{member.id}`\n"
                f"**Account Created:** <t:{int(member.created_at.timestamp())}:F>\n"
                f"**Joined Server:** {joined_server_text}"
            ),
            inline=False
        )
        
        # Roles
        roles = [role.mention for role in member.roles[1:]]  # Exclude @everyone
        if roles:
            roles_text = ", ".join(roles[:10])  # Limit to 10 roles
            if len(roles) > 10:
                roles_text += f" (+{len(roles) - 10} more)"
            embed.add_field(
                name="**Roles**",
                value=roles_text or "None",
                inline=False
            )
        
        # Add Roblox profile information
        await self._create_roblox_embed_section(member, embed)
        
        # Set Discord avatar as main image
        if member.avatar:
            embed.set_image(url=member.avatar.url)
        
        # Footer
        embed.set_footer(text=f"Vulkan Activity Log")
        
        return embed
    
    async def _create_voice_activity_embed(
        self,
        member: discord.Member,
        action: str,  # "joined", "left", or "moved"
        channel: discord.VoiceChannel | discord.StageChannel,
        previous_channel: Optional[discord.VoiceChannel | discord.StageChannel] = None,
        duration: Optional[float] = None
    ) -> discord.Embed:
        """
        Create embed for voice channel activity with appropriate colors.
        
        Args:
            member: Discord member
            action: "joined", "left", or "moved"
            channel: Voice channel
            previous_channel: Previous channel (for "moved" action)
            duration: Duration in seconds (if left)
        
        Returns:
            Discord embed with appropriate color
        """
        current_time = datetime.now(timezone.utc)
        time_str = current_time.strftime("%H:%M")
        
        if action == "joined":
            embed = discord.Embed(
                title="🎤 Member Joined",
                description=f"{member.mention} joined 🔊 {channel.mention}",
                color=discord.Color.green(),
                timestamp=current_time
            )
        
        elif action == "left":
            embed = discord.Embed(
                title="🔇 Member Left",
                description=f"{member.mention} left 🔊 {channel.mention}",
                color=discord.Color.red(),
                timestamp=current_time
            )
        
        elif action == "moved" and previous_channel:
            embed = discord.Embed(
                title="🔄 Member Moved",
                description=f"{member.mention} moved from 🔊 {previous_channel.mention} to 🔊 {channel.mention}",
                color=discord.Color.purple(),
                timestamp=current_time
            )
        else:
            # Fallback embed
            embed = discord.Embed(
                title="Voice Activity",
                description=f"{member.mention} - {action}",
                color=discord.Color.blue(),
                timestamp=current_time
            )
        
        # Set member avatar as thumbnail
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        # Footer with member name (Discord timestamp is shown automatically via embed.timestamp)
        embed.set_footer(
            text=f"{member.display_name} • Activity Log"
        )
        
        return embed
    
    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        """
        Monitor voice channel join/leave events for ALL voice channels.
        
        This listener monitors EVERY voice channel in the server without any restrictions.
        Logs are created for:
        - Joining any voice channel (green embed)
        - Leaving any voice channel (red embed)
        - Moving between any voice channels (purple embed)
        
        Args:
            member: Discord member
            before: Previous voice state
            after: New voice state
        """
        # Ignore bots
        if member.bot:
            return
        
        log_channel = await self._get_log_channel()
        if not log_channel:
            return
        
        try:
            # Member joined a voice channel
            if before.channel is None and after.channel is not None:
                self._voice_join_times[member.id] = datetime.now(timezone.utc)
                
                embed = await self._create_voice_activity_embed(
                    member=member,
                    action="joined",
                    channel=after.channel
                )
                
                await log_channel.send(embed=embed)
                logger.debug(f"Logged voice join: {member.id} -> {after.channel.name}")
            
            # Member left a voice channel
            elif before.channel is not None and after.channel is None:
                join_time = self._voice_join_times.pop(member.id, None)
                duration = None
                
                if join_time:
                    duration = (datetime.now(timezone.utc) - join_time).total_seconds()
                
                embed = await self._create_voice_activity_embed(
                    member=member,
                    action="left",
                    channel=before.channel,
                    duration=duration
                )
                
                await log_channel.send(embed=embed)
                logger.debug(f"Logged voice leave: {member.id} from {before.channel.name}")
            
            # Member switched voice channels
            elif before.channel is not None and after.channel is not None and before.channel != after.channel:
                # Record time spent in previous channel
                join_time = self._voice_join_times.get(member.id)
                
                # Start tracking new channel
                self._voice_join_times[member.id] = datetime.now(timezone.utc)
                
                embed = await self._create_voice_activity_embed(
                    member=member,
                    action="moved",
                    channel=after.channel,
                    previous_channel=before.channel
                )
                
                await log_channel.send(embed=embed)
                logger.debug(f"Logged voice switch: {member.id} {before.channel.name} -> {after.channel.name}")
        
        except Exception as e:
            logger.error(f"Error logging voice activity for {member.id}: {e}", exc_info=True)
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Monitor when a member joins the server.
        
        Args:
            member: Discord member that joined
        """
        # Ignore bots
        if member.bot:
            return
        
        log_channel = await self._get_log_channel()
        if not log_channel:
            return
        
        try:
            embed = await self._create_discord_profile_embed(
                member=member,
                title="🟢 Member Joined Server",
                color=discord.Color.green(),
                description=f"{member.mention} has joined the server."
            )
            
            await log_channel.send(embed=embed)
            logger.info(f"Logged member join: {member.id} ({member.name})")
        
        except Exception as e:
            logger.error(f"Error logging member join for {member.id}: {e}", exc_info=True)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """
        Monitor when a member leaves the server.
        
        Args:
            member: Discord member that left
        """
        # Ignore bots
        if member.bot:
            return
        
        log_channel = await self._get_log_channel()
        if not log_channel:
            return
        
        try:
            embed = await self._create_discord_profile_embed(
                member=member,
                title="🔴 Member Left Server",
                color=discord.Color.red(),
                description=f"{member.mention} has left the server."
            )
            
            await log_channel.send(embed=embed)
            logger.info(f"Logged member leave: {member.id} ({member.name})")
        
        except Exception as e:
            logger.error(f"Error logging member leave for {member.id}: {e}", exc_info=True)


async def setup(bot: commands.Bot):
    """Load the member activity log cog"""
    await bot.add_cog(MemberActivityLogCog(bot))
    logger.info("Member Activity Log handler loaded (voice & member join/leave monitoring active)")

