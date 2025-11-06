"""
Salamanders Event Panel - Interactive event hosting system with buttons.
"""

from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands
from utils.event_presets import EVENT_PRESETS
from utils.event_announcement import post_event_announcement
from utils.logger import get_logger

logger = get_logger(__name__)

# Channel ID where the event panel is posted
EVENT_PANEL_CHANNEL_ID = 1435795622077923371

# Channel ID where events are posted
EVENT_ANNOUNCEMENT_CHANNEL_ID = 1375941286078709790

# Banner image URL (High quality ArtStation image)
SALAMANDERS_BANNER_URL = "https://cdna.artstation.com/p/assets/images/images/036/435/864/large/jacob-loren-salamander-web.jpg?1617683294"


# ============================================================================
# Event Confirmation and Control Views
# ============================================================================

class PatrolDescriptionModal(discord.ui.Modal, title="Confirmation Modal (PATROL)"):
    """Modal for entering event description."""
    
    description_input = discord.ui.TextInput(
        label="Description *",
        placeholder="eg. Join Loyalist team.",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )
    
    def __init__(self, bot: commands.Bot, event_key: str, host_user: discord.Member):
        super().__init__()
        self.bot = bot
        self.event_key = event_key
        self.host_user = host_user
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission with description."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        custom_description = self.description_input.value
        
        # Post event with custom description
        await _post_event_with_description(
            bot=self.bot,
            interaction=interaction,
            event_key=self.event_key,
            custom_description=custom_description,
            host_user=self.host_user
        )


class PatrolConfirmationView(discord.ui.View):
    """Confirmation view for Patrol event."""
    
    def __init__(self, bot: commands.Bot, event_key: str):
        super().__init__(timeout=300)
        self.bot = bot
        self.event_key = event_key
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Confirm without description."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        await _post_event_with_description(
            bot=self.bot,
            interaction=interaction,
            event_key=self.event_key,
            custom_description=None,
            host_user=interaction.user
        )
    
    @discord.ui.button(label="Confirm with Description", style=discord.ButtonStyle.danger)
    async def confirm_with_desc_button(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Open modal for description."""
        modal = PatrolDescriptionModal(
            bot=self.bot,
            event_key=self.event_key,
            host_user=interaction.user
        )
        await interaction.response.send_modal(modal)


class EventEndView(discord.ui.View):
    """View with End button for active events."""
    
    def __init__(self, bot: commands.Bot, event_message_id: int, host_user: discord.Member):
        super().__init__(timeout=None)  # Persistent
        self.bot = bot
        self.event_message_id = event_message_id
        self.host_user = host_user
        
        # Create button dynamically with unique custom_id
        button = discord.ui.Button(
            label="End",
            style=discord.ButtonStyle.danger,
            custom_id=f"event_end_{event_message_id}" if event_message_id > 0 else "event_end_temp"
        )
        button.callback = self.end_event_button
        self.add_item(button)
    
    async def end_event_button(self, interaction: discord.Interaction):
        """End the event and clean up."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        # Delete the End message from event-publishing channel
        end_channel = self.bot.get_channel(EVENT_PANEL_CHANNEL_ID)
        if isinstance(end_channel, discord.TextChannel):
            try:
                end_message = await end_channel.fetch_message(self.event_message_id)
                await end_message.delete()
                logger.info(f"Deleted event end message {self.event_message_id}")
            except discord.NotFound:
                logger.warning(f"Event end message {self.event_message_id} not found")
            except Exception as e:
                logger.error(f"Error deleting event end message: {e}")
        
        # Post conclusion message in announcement channel
        announcement_channel = self.bot.get_channel(EVENT_ANNOUNCEMENT_CHANNEL_ID)
        if isinstance(announcement_channel, discord.TextChannel):
            embed = discord.Embed(
                title="Event Concluded",
                description=f"The event hosted by {self.host_user.mention} has been concluded.",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text="Vulkan Activity Log")
            if self.host_user.avatar:
                embed.set_thumbnail(url=self.host_user.avatar.url)
            
            await announcement_channel.send(embed=embed)
            logger.info(f"Event concluded by {self.host_user.id}")
        
        await interaction.followup.send("✅ Event concluded successfully.", ephemeral=True)


async def _post_event_with_description(
    bot: commands.Bot,
    interaction: discord.Interaction,
    event_key: str,
    custom_description: str | None,
    host_user: discord.Member
):
    """Post event announcement with optional custom description."""
    preset = EVENT_PRESETS.get(event_key)
    if not preset:
        await interaction.followup.send("❌ Event preset not found.", ephemeral=True)
        return
    
    # Use custom description if provided, otherwise use preset description
    if custom_description:
        final_description = f"**Host:** {host_user.mention}\n**Description:** {custom_description}"
    else:
        final_description = f"**Host:** {host_user.mention}\n**Description:** {preset['description']}"
    
    try:
        # Post event announcement
        await post_event_announcement(
            bot,
            channel_id=EVENT_ANNOUNCEMENT_CHANNEL_ID,
            title=preset["title"],
            description=final_description,
            when=preset["when"],
            location=preset["location"],
            link=preset.get("link"),
            color=preset.get("color", 0x2B2D31),
            ping_role_id=preset.get("ping_role_id"),
            image_url=preset.get("image_url"),
            footer_text="For Nocturne. For Vulkan.",
            footer_icon=host_user.display_avatar.url if host_user.display_avatar else None,
            author_name=f"Posted by {host_user.display_name}",
            author_icon=host_user.display_avatar.url if host_user.display_avatar else None,
        )
        
        # Post End control message in event-publishing channel
        end_channel = bot.get_channel(EVENT_PANEL_CHANNEL_ID)
        if isinstance(end_channel, discord.TextChannel):
            end_embed = discord.Embed(
                title="Event End",
                description=(
                    "The forge bellows still, but this chapter draws to a close. "
                    "Stand ready to mark the end of this event when all duties are fulfilled."
                ),
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            end_embed.set_footer(text=f"Event: {preset['title']} • Host: {host_user.display_name}")
            
            # First send message without view to get message ID
            end_message = await end_channel.send(embed=end_embed)
            
            # Now create view with actual message ID
            end_view = EventEndView(bot, end_message.id, host_user)
            await end_message.edit(view=end_view)
        
        await interaction.followup.send(f"✅ Posted **{preset['title']}** event.", ephemeral=True)
        logger.info(f"Event '{preset['title']}' posted by {host_user.id}")
    
    except Exception as e:
        logger.error(f"Error posting event announcement: {e}", exc_info=True)
        await interaction.followup.send(
            f"❌ Error posting event: {str(e)}",
            ephemeral=True
        )


# ============================================================================
# Main Event Panel View
# ============================================================================

class SalamandersEventView(discord.ui.View):
    """Three rows of buttons (green / red / grey) that post Salamanders-themed events."""
    
    def __init__(self, bot: commands.Bot, *, timeout: float | None = None):
        super().__init__(timeout=timeout)  # None = persistent view
        self.bot = bot
    
    # Row 0: GREEN (patrol & training)
    @discord.ui.button(
        label="Patrol",
        style=discord.ButtonStyle.success,
        custom_id="slm_patrol",
        row=0
    )
    async def btn_patrol(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Show confirmation modal for Patrol event."""
        view = PatrolConfirmationView(self.bot, event_key="patrol")
        embed = discord.Embed(
            title="Confirming Process",
            description="Are you sure you want to start an event at this moment? If not, dismiss this message.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(
        label="Combat Training",
        style=discord.ButtonStyle.success,
        custom_id="slm_combat_training",
        row=0
    )
    async def btn_combat_training(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._dispatch(interaction, "combat_training")
    
    @discord.ui.button(
        label="Basic Training",
        style=discord.ButtonStyle.success,
        custom_id="slm_basic_training",
        row=0
    )
    async def btn_basic_training(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._dispatch(interaction, "basic_training")
    
    # Row 1: RED (raids & rally)
    @discord.ui.button(
        label="Internal Practice Raid",
        style=discord.ButtonStyle.danger,
        custom_id="slm_internal_raid",
        row=1
    )
    async def btn_internal_raid(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._dispatch(interaction, "internal_raid")
    
    @discord.ui.button(
        label="Practice Raid",
        style=discord.ButtonStyle.danger,
        custom_id="slm_practice_raid",
        row=1
    )
    async def btn_practice_raid(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._dispatch(interaction, "practice_raid")
    
    @discord.ui.button(
        label="Rally",
        style=discord.ButtonStyle.danger,
        custom_id="slm_rally",
        row=1
    )
    async def btn_rally(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._dispatch(interaction, "rally")
    
    # Row 2: GREY (custom)
    @discord.ui.button(
        label="Custom",
        style=discord.ButtonStyle.secondary,
        custom_id="slm_custom",
        row=2
    )
    async def btn_custom(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_message(
            "🛠️ Custom event coming soon (we'll open a modal to collect title/time/location).",
            ephemeral=True
        )
    
    async def _dispatch(self, interaction: discord.Interaction, key: str):
        """Dispatch event announcement based on preset key."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        preset = EVENT_PRESETS.get(key)
        if not preset:
            await interaction.followup.send("❌ Event preset not found.", ephemeral=True)
            return
        
        target = interaction.channel
        if not isinstance(target, (discord.TextChannel, discord.Thread)):
            await interaction.followup.send("❌ Invalid channel.", ephemeral=True)
            return
        
        author_icon = interaction.user.display_avatar.url if interaction.user.display_avatar else None
        
        try:
            await post_event_announcement(
                self.bot,
                channel_id=target.id,
                title=preset["title"],
                description=preset["description"],
                when=preset["when"],
                location=preset["location"],
                link=preset.get("link"),
                color=preset.get("color", 0x2B2D31),
                ping_role_id=preset.get("ping_role_id"),
                image_url=preset.get("image_url"),
                footer_text="For Nocturne. For Vulkan.",
                footer_icon=author_icon,
                author_name=f"Posted by {interaction.user.display_name}",
                author_icon=author_icon,
            )
            
            await interaction.followup.send(f"✅ Posted **{preset['title']}** here.", ephemeral=True)
            logger.info(f"Event '{preset['title']}' posted by {interaction.user.id} in channel {target.id}")
        
        except Exception as e:
            logger.error(f"Error posting event announcement: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Error posting event: {str(e)}",
                ephemeral=True
            )


class SalamandersEventPanel(commands.Cog):
    """Posts the Salamanders-themed Event Hosting panel and wires button actions."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.panel_message_id: int | None = None
    
    async def _create_panel_embed(self) -> discord.Embed:
        """Create the main event hosting panel embed."""
        embed = discord.Embed(
            title="Event Hosting",
            description=(
                "Welcome, brothers, to this sanctum of flame and forge, the hallowed halls of the XVIII Legion, the Salamanders.\n\n"
                "Here, amidst the heat of devotion and the anvil's song, you shall choose the emblem that marks the nature of the rite you wish to begin.\n\n"
                "Stand proud and steadfast, for every spark kindled here is a promise, a vow of duty, endurance, and compassion forged in fire.\n\n"
                "🔥 May the Flame guide your hand, and may Vulkan's light never fade. 🔥"
            ),
            color=discord.Color.from_str("#2f3136")
        )
        
        # Banner/art
        embed.set_image(url=SALAMANDERS_BANNER_URL)
        
        embed.set_footer(
            text="Vulkan Lives • For Nocturne. For the Forge.",
            icon_url="https://cdn.discordapp.com/emojis/1158979646512177253.webp?size=128&quality=lossless"
        )
        
        return embed
    
    async def post_or_update_panel(self) -> None:
        """
        Post or update the event panel in the designated channel.
        Deletes old message and posts new one to ensure freshness.
        """
        channel = self.bot.get_channel(EVENT_PANEL_CHANNEL_ID)
        if not isinstance(channel, discord.TextChannel):
            logger.error(f"Event panel channel {EVENT_PANEL_CHANNEL_ID} not found or invalid")
            return
        
        try:
            # Delete old panel message if we have its ID
            if self.panel_message_id:
                try:
                    old_message = await channel.fetch_message(self.panel_message_id)
                    await old_message.delete()
                    logger.debug(f"Deleted old event panel message {self.panel_message_id}")
                except discord.NotFound:
                    logger.debug(f"Old panel message {self.panel_message_id} not found (already deleted)")
                except Exception as e:
                    logger.warning(f"Error deleting old panel message: {e}")
            
            # Also try to find and delete any existing panel messages (by checking recent messages)
            # This helps if bot restarts and loses the message ID
            async for message in channel.history(limit=10):
                if message.author == self.bot.user and message.embeds:
                    embed = message.embeds[0]
                    if embed.title and "Event Hosting" in embed.title:
                        try:
                            await message.delete()
                            logger.debug(f"Deleted existing panel message {message.id}")
                        except Exception as e:
                            logger.warning(f"Error deleting existing panel message: {e}")
            
            # Post new panel
            embed = await self._create_panel_embed()
            view = SalamandersEventView(self.bot)
            message = await channel.send(embed=embed, view=view)
            self.panel_message_id = message.id
            
            logger.info(f"✅ Event panel posted in channel {EVENT_PANEL_CHANNEL_ID} (message ID: {message.id})")
        
        except Exception as e:
            logger.error(f"Error posting event panel: {e}", exc_info=True)
    
    @app_commands.command(name="event_panel", description="Post the Salamanders Event Hosting panel.")
    @app_commands.describe(channel="Optional: target channel (defaults to current)")
    @app_commands.guild_only()
    async def event_panel(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None):
        """Manual command to post the event panel."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        target = channel or interaction.channel
        if not isinstance(target, (discord.TextChannel, discord.Thread)):
            await interaction.followup.send("❌ Invalid channel.", ephemeral=True)
            return
        
        embed = await self._create_panel_embed()
        await target.send(embed=embed, view=SalamandersEventView(self.bot))
        
        await interaction.followup.send(f"✅ Salamanders Event Panel posted in {target.mention}.", ephemeral=True)
        logger.info(f"Event panel manually posted by {interaction.user.id} in channel {target.id}")


async def setup(bot: commands.Bot):
    """Load the Salamanders Event Panel cog."""
    cog = SalamandersEventPanel(bot)
    await bot.add_cog(cog)
    
    # Post panel automatically when bot is ready
    # We'll hook into on_ready via the main bot file
    logger.info("✅ Salamanders Event Panel cog loaded")


def get_event_panel_cog(bot: commands.Bot) -> SalamandersEventPanel | None:
    """Helper to get the event panel cog instance."""
    return bot.get_cog("SalamandersEventPanel")
