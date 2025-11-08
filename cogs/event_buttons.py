"""
Salamanders Event Panel - Interactive event hosting system with buttons.
"""

from __future__ import annotations

import asyncio
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
        # CRITICAL: Check if there's an active event BEFORE posting
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        
        if event_panel_cog is None:
            logger.error("Event panel cog not found! Cannot check for active events.")
            await interaction.response.send_message(
                "❌ Internal error: Event panel system not available.",
                ephemeral=True
            )
            return
        
        if event_panel_cog.is_event_active():
            active_info = event_panel_cog.get_active_event_info()
            logger.warning(f"🚫 BLOCKED PatrolDescriptionModal submission attempt: {self.event_key} - Active event: {active_info}")
            error_msg = (
                "❌ **There is already an active event!**\n\n"
                f"{active_info}\n\n"
                "You must end the current event before posting a new one. "
                "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
            )
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        custom_description = self.description_input.value
        
        # Post event with custom description
        await _post_event_with_description(
            bot=self.bot,
            interaction=interaction,
            event_key=self.event_key,
            custom_description=custom_description,
            custom_link=None,
            host_user=self.host_user
        )


class TrainingEventModal(discord.ui.Modal):
    """Base modal for training events (Combat Training, Basic Training, IPR, PR, Rally) with mandatory description and link."""
    
    description_input = discord.ui.TextInput(
        label="Description *",
        placeholder="Enter event description (required)",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )
    
    private_server_link_input = discord.ui.TextInput(
        label="Private Server Link *",
        placeholder="https://www.roblox.com/games/.../private-servers/...",
        style=discord.TextStyle.short,
        required=True,
        max_length=200
    )
    
    def __init__(self, bot: commands.Bot, event_key: str, host_user: discord.Member, modal_title: str):
        super().__init__(title=modal_title)
        self.bot = bot
        self.event_key = event_key
        self.host_user = host_user
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission with description and mandatory link."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        custom_description = self.description_input.value.strip()
        custom_link = self.private_server_link_input.value.strip() if self.private_server_link_input.value else None
        
        # Validate description is not empty
        if not custom_description:
            await interaction.followup.send(
                "❌ Description is required. Please try again.",
                ephemeral=True
            )
            return
        
        # Validate link is provided and not empty
        if not custom_link:
            await interaction.followup.send(
                "❌ Private server link is required. Please provide a valid Roblox private server link.",
                ephemeral=True
            )
            return
        
        # Validate link format
        if not (custom_link.startswith("http://") or custom_link.startswith("https://")):
            await interaction.followup.send(
                "❌ Invalid link format. Please provide a valid URL starting with http:// or https://",
                ephemeral=True
            )
            return
        
        # Post event with custom description and link
        await _post_event_with_description(
            bot=self.bot,
            interaction=interaction,
            event_key=self.event_key,
            custom_description=custom_description,
            custom_link=custom_link,
            host_user=self.host_user
        )


class CombatTrainingModal(TrainingEventModal):
    """Modal for Combat Training event."""
    def __init__(self, bot: commands.Bot, event_key: str, host_user: discord.Member):
        super().__init__(bot, event_key, host_user, "Combat Training Event")


class BasicTrainingModal(TrainingEventModal):
    """Modal for Basic Training event."""
    def __init__(self, bot: commands.Bot, event_key: str, host_user: discord.Member):
        super().__init__(bot, event_key, host_user, "Basic Training Event")


class InternalRaidModal(TrainingEventModal):
    """Modal for Internal Practice Raid event."""
    def __init__(self, bot: commands.Bot, event_key: str, host_user: discord.Member):
        super().__init__(bot, event_key, host_user, "Internal Practice Raid Event")


class PracticeRaidModal(TrainingEventModal):
    """Modal for Practice Raid event."""
    def __init__(self, bot: commands.Bot, event_key: str, host_user: discord.Member):
        super().__init__(bot, event_key, host_user, "Practice Raid Event")


class RallyModal(TrainingEventModal):
    """Modal for Rally event."""
    def __init__(self, bot: commands.Bot, event_key: str, host_user: discord.Member):
        super().__init__(bot, event_key, host_user, "Rally Event")


class CustomEventTitleView(discord.ui.View):
    """View for selecting preset title or entering custom title for custom events."""
    
    def __init__(self, bot: commands.Bot, host_user: discord.Member):
        super().__init__(timeout=300)
        self.bot = bot
        self.host_user = host_user
    
    @discord.ui.button(label="++ Gamenight ++", style=discord.ButtonStyle.primary, row=0)
    async def btn_gamenight(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Select Gamenight preset title."""
        # CRITICAL: Check if there's an active event BEFORE opening modal
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        
        if event_panel_cog is None:
            logger.error("Event panel cog not found! Cannot check for active events.")
            await interaction.response.send_message(
                "❌ Internal error: Event panel system not available.",
                ephemeral=True
            )
            return
        
        if event_panel_cog.is_event_active():
            active_info = event_panel_cog.get_active_event_info()
            logger.warning(f"🚫 BLOCKED Gamenight event posting attempt - Active event: {active_info}")
            error_msg = (
                "❌ **There is already an active event!**\n\n"
                f"{active_info}\n\n"
                "You must end the current event before posting a new one. "
                "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
            )
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        modal = CustomEventModal(self.bot, self.host_user, preset_title="++ Gamenight ++")
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Custom Title", style=discord.ButtonStyle.secondary, row=0)
    async def btn_custom_title(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Open modal for custom title input."""
        # CRITICAL: Check if there's an active event BEFORE opening modal
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        
        if event_panel_cog is None:
            logger.error("Event panel cog not found! Cannot check for active events.")
            await interaction.response.send_message(
                "❌ Internal error: Event panel system not available.",
                ephemeral=True
            )
            return
        
        if event_panel_cog.is_event_active():
            active_info = event_panel_cog.get_active_event_info()
            logger.warning(f"🚫 BLOCKED Custom Title event posting attempt - Active event: {active_info}")
            error_msg = (
                "❌ **There is already an active event!**\n\n"
                f"{active_info}\n\n"
                "You must end the current event before posting a new one. "
                "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
            )
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        modal = CustomEventModal(self.bot, self.host_user, preset_title=None)
        await interaction.response.send_modal(modal)


class CustomEventModal(discord.ui.Modal):
    """Modal for custom events with title selection/input and description."""
    
    def __init__(self, bot: commands.Bot, host_user: discord.Member, preset_title: str | None = None):
        super().__init__(title="Custom Event")
        self.bot = bot
        self.host_user = host_user
        
        # Create title input dynamically to support preset title
        self.title_input = discord.ui.TextInput(
            label="Event Title *",
            placeholder="++ Your Event Title ++ (format required)",
            style=discord.TextStyle.short,
            required=True,
            max_length=100,
            default=preset_title if preset_title else ""
        )
        self.add_item(self.title_input)
        
        self.description_input = discord.ui.TextInput(
            label="Description *",
            placeholder="Enter event description (required)",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        self.add_item(self.description_input)
        
        self.private_server_link_input = discord.ui.TextInput(
            label="Private Server Link (Optional)",
            placeholder="https://www.roblox.com/games/.../private-servers/...",
            style=discord.TextStyle.short,
            required=False,
            max_length=200
        )
        self.add_item(self.private_server_link_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission with title, description and optional link."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        custom_title = self.title_input.value.strip()
        custom_description = self.description_input.value.strip()
        custom_link = self.private_server_link_input.value.strip() if self.private_server_link_input.value else None
        
        # Validate title format: must be ++ Text ++
        if not custom_title.startswith("++ ") or not custom_title.endswith(" ++"):
            await interaction.followup.send(
                "❌ Invalid title format. Title must be in format: ++ Your Title ++\n"
                "Example: ++ Gamenight ++",
                ephemeral=True
            )
            return
        
        # Validate description is not empty
        if not custom_description:
            await interaction.followup.send(
                "❌ Description is required. Please try again.",
                ephemeral=True
            )
            return
        
        # Validate link format if provided
        if custom_link and not (custom_link.startswith("http://") or custom_link.startswith("https://")):
            await interaction.followup.send(
                "❌ Invalid link format. Please provide a valid URL starting with http:// or https://",
                ephemeral=True
            )
            return
        
        # Post custom event
        await _post_custom_event(
            bot=self.bot,
            interaction=interaction,
            custom_title=custom_title,
            custom_description=custom_description,
            custom_link=custom_link,
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
        # CRITICAL: Check if there's an active event BEFORE posting
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        
        if event_panel_cog is None:
            logger.error("Event panel cog not found! Cannot check for active events.")
            await interaction.response.send_message(
                "❌ Internal error: Event panel system not available.",
                ephemeral=True
            )
            return
        
        if event_panel_cog.is_event_active():
            active_info = event_panel_cog.get_active_event_info()
            logger.warning(f"🚫 BLOCKED event confirmation attempt: {self.event_key} - Active event: {active_info}")
            error_msg = (
                "❌ **There is already an active event!**\n\n"
                f"{active_info}\n\n"
                "You must end the current event before posting a new one. "
                "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
            )
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        await _post_event_with_description(
            bot=self.bot,
            interaction=interaction,
            event_key=self.event_key,
            custom_description=None,
            custom_link=None,
            host_user=interaction.user
        )
    
    @discord.ui.button(label="Confirm with Description", style=discord.ButtonStyle.danger)
    async def confirm_with_desc_button(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Open modal for description."""
        # CRITICAL: Check if there's an active event BEFORE opening modal
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        
        if event_panel_cog is None:
            logger.error("Event panel cog not found! Cannot check for active events.")
            await interaction.response.send_message(
                "❌ Internal error: Event panel system not available.",
                ephemeral=True
            )
            return
        
        if event_panel_cog.is_event_active():
            active_info = event_panel_cog.get_active_event_info()
            logger.warning(f"🚫 BLOCKED event confirmation with description attempt: {self.event_key} - Active event: {active_info}")
            error_msg = (
                "❌ **There is already an active event!**\n\n"
                f"{active_info}\n\n"
                "You must end the current event before posting a new one. "
                "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
            )
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        modal = PatrolDescriptionModal(
            bot=self.bot,
            event_key=self.event_key,
            host_user=interaction.user
        )
        await interaction.response.send_modal(modal)


class EventEndView(discord.ui.View):
    """View with End button for active events."""
    
    def __init__(self, bot: commands.Bot, end_message_id: int, host_user: discord.Member):
        super().__init__(timeout=None)  # Persistent
        self.bot = bot
        self.end_message_id = end_message_id  # ID of the "End" message itself
        self.host_user = host_user
        
        # Create button dynamically with unique custom_id
        button = discord.ui.Button(
            label="End",
            style=discord.ButtonStyle.danger,
            custom_id=f"event_end_{end_message_id}" if end_message_id > 0 else "event_end_temp"
        )
        button.callback = self.end_event_button
        self.add_item(button)
    
    async def end_event_button(self, interaction: discord.Interaction):
        """End the event and clean up."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        # Clear active event first
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        if event_panel_cog:
            event_panel_cog.clear_active_event()
        
        # Delete the End message from event-publishing channel
        end_channel = self.bot.get_channel(EVENT_PANEL_CHANNEL_ID)
        if isinstance(end_channel, discord.TextChannel):
            try:
                end_message = await end_channel.fetch_message(self.end_message_id)
                await end_message.delete()
                logger.info(f"Deleted event end message {self.end_message_id}")
            except discord.NotFound:
                logger.warning(f"Event end message {self.end_message_id} not found")
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


async def _post_custom_event(
    bot: commands.Bot,
    interaction: discord.Interaction,
    custom_title: str,
    custom_description: str,
    custom_link: str | None,
    host_user: discord.Member
):
    """Post custom event announcement with custom title, description and optional link."""
    # Check if there's an active event BEFORE posting
    from cogs.event_buttons import get_event_panel_cog
    event_panel_cog = get_event_panel_cog(bot)
    
    if event_panel_cog is None:
        logger.error("❌ Event panel cog not found! Cannot check for active events.")
        await interaction.followup.send("❌ Internal error: Event panel system not available.", ephemeral=True)
        return
    
    # CRITICAL: Check for active event BEFORE posting anything
    if event_panel_cog.is_event_active():
        active_info = event_panel_cog.get_active_event_info()
        logger.warning(f"🚫 BLOCKED custom event posting attempt - Active event: {active_info}")
        error_msg = (
            "❌ **There is already an active event!**\n\n"
            f"{active_info}\n\n"
            "You must end the current event before posting a new one. "
            "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
        )
        await interaction.followup.send(error_msg, ephemeral=True)
        return
    
    logger.info(f"✅ No active event found, proceeding with custom event posting: {custom_title}")
    
    try:
        # Use default link if not provided
        default_link = "https://www.roblox.com/games/99813489644549/Averium-Invicta-The-Grave-World"
        event_link = custom_link if custom_link else default_link
        
        # Post event announcement
        announcement_message = await post_event_announcement(
            bot,
            channel_id=EVENT_ANNOUNCEMENT_CHANNEL_ID,
            title=custom_title,
            description=custom_description,
            when="",
            location="",
            link=event_link,
            color=0x95A5A6,  # Grey color for custom events
            ping_role_id=None,
            image_url="https://i.pinimg.com/originals/97/10/32/9710328fc2d70322bab4d6d05da6e9ba.jpg",  # Custom event image
            footer_text="For Nocturne. For Vulkan.",
            footer_icon=None,
            author_name=host_user.mention,
            author_icon=None,
        )
        
        # Get the message ID from the announcement
        event_message_id = announcement_message.id if announcement_message else None
        
        # Post End control message in event-publishing channel
        end_channel = bot.get_channel(EVENT_PANEL_CHANNEL_ID)
        end_message_id = None
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
            end_embed.set_footer(text=f"Event: {custom_title} • Host: {host_user.display_name}")
            
            # First send message without view to get message ID
            end_message = await end_channel.send(embed=end_embed)
            end_message_id = end_message.id
            
            # Now create view with actual message ID
            end_view = EventEndView(bot, end_message.id, host_user)
            await end_message.edit(view=end_view)
        
        # Mark event as active IMMEDIATELY after posting
        if event_panel_cog and event_message_id and end_message_id:
            event_panel_cog.set_active_event(
                event_message_id=event_message_id,
                end_message_id=end_message_id,
                host_user=host_user,
                event_title=custom_title
            )
            logger.info(f"✅ Custom event marked as active: {custom_title} (Event ID: {event_message_id}, End ID: {end_message_id})")
        else:
            logger.error(f"❌ Failed to mark custom event as active! event_panel_cog={event_panel_cog is not None}, event_message_id={event_message_id}, end_message_id={end_message_id}")
        
        await interaction.followup.send(f"✅ Posted **{custom_title}** event.", ephemeral=True)
        logger.info(f"Custom event '{custom_title}' posted by {host_user.id}")
    
    except Exception as e:
        logger.error(f"Error posting custom event announcement: {e}", exc_info=True)
        await interaction.followup.send(
            f"❌ Error posting event: {str(e)}",
            ephemeral=True
        )


async def _post_event_with_description(
    bot: commands.Bot,
    interaction: discord.Interaction,
    event_key: str,
    custom_description: str | None,
    custom_link: str | None = None,
    host_user: discord.Member = None
):
    """Post event announcement with optional custom description."""
    # Check if there's an active event BEFORE posting
    from cogs.event_buttons import get_event_panel_cog
    event_panel_cog = get_event_panel_cog(bot)
    
    if event_panel_cog is None:
        logger.error("❌ Event panel cog not found! Cannot check for active events.")
        await interaction.followup.send("❌ Internal error: Event panel system not available.", ephemeral=True)
        return
    
    # CRITICAL: Check for active event BEFORE posting anything
    if event_panel_cog.is_event_active():
        active_info = event_panel_cog.get_active_event_info()
        logger.warning(f"🚫 BLOCKED event posting attempt: {event_key} - Active event: {active_info}")
        error_msg = (
            "❌ **There is already an active event!**\n\n"
            f"{active_info}\n\n"
            "You must end the current event before posting a new one. "
            "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
        )
        await interaction.followup.send(error_msg, ephemeral=True)
        return
    
    logger.info(f"✅ No active event found, proceeding with event posting: {event_key}")
    
    preset = EVENT_PRESETS.get(event_key)
    if not preset:
        await interaction.followup.send("❌ Event preset not found.", ephemeral=True)
        return
    
    # Use custom description if provided, otherwise use preset description (only if not empty)
    if custom_description:
        final_description = custom_description
    else:
        # Only use preset description if it exists and is not empty
        final_description = preset.get('description', '').strip() if preset.get('description') else None
    
    try:
        # Post event announcement
        # All events with image_url in preset get their specific images
        event_image_url = preset.get("image_url") if preset.get("image_url") else None
        
        # Use custom link if provided, otherwise use preset link, otherwise use default
        event_link = custom_link if custom_link else preset.get("link")
        
        # Post event announcement and get message ID
        announcement_message = await post_event_announcement(
            bot,
            channel_id=EVENT_ANNOUNCEMENT_CHANNEL_ID,
            title=preset["title"],
            description=final_description if final_description else "",
            when="",  # Not used anymore
            location="",  # Not used anymore
            link=event_link,  # Use custom link if provided, otherwise preset/default
            color=preset.get("color", 0x2B2D31),
            ping_role_id=None,  # Will use Salamanders role automatically
            image_url=event_image_url,  # Patrol and Combat Training events have images
            footer_text="For Nocturne. For Vulkan.",
            footer_icon=None,  # Will use specified icon automatically
            author_name=host_user.mention,  # Host field in description (not "Posted by")
            author_icon=None,  # No author icon (no "Posted by" section)
        )
        
        # Get the message ID from the announcement
        event_message_id = announcement_message.id if announcement_message else None
        
        # Post End control message in event-publishing channel
        end_channel = bot.get_channel(EVENT_PANEL_CHANNEL_ID)
        end_message_id = None
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
            end_message_id = end_message.id
            
            # Now create view with actual message ID
            end_view = EventEndView(bot, end_message.id, host_user)
            await end_message.edit(view=end_view)
        
        # Mark event as active IMMEDIATELY after posting
        if event_panel_cog and event_message_id and end_message_id:
            event_panel_cog.set_active_event(
                event_message_id=event_message_id,
                end_message_id=end_message_id,
                host_user=host_user,
                event_title=preset['title']
            )
            logger.info(f"✅ Event marked as active: {preset['title']} (Event ID: {event_message_id}, End ID: {end_message_id})")
            # Verify it was set correctly
            if not event_panel_cog.is_event_active():
                logger.error(f"❌ CRITICAL: Event was set as active but is_event_active() returns False!")
        else:
            logger.error(f"❌ Failed to mark event as active! event_panel_cog={event_panel_cog is not None}, event_message_id={event_message_id}, end_message_id={end_message_id}")
            if not event_message_id:
                logger.error("  Reason: event_message_id is None")
            if not end_message_id:
                logger.error("  Reason: end_message_id is None")
        
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
        # CRITICAL: Check if there's an active event BEFORE showing confirmation
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        
        if event_panel_cog is None:
            logger.error("Event panel cog not found! Cannot check for active events.")
            await interaction.response.send_message(
                "❌ Internal error: Event panel system not available.",
                ephemeral=True
            )
            return
        
        if event_panel_cog.is_event_active():
            active_info = event_panel_cog.get_active_event_info()
            logger.warning(f"🚫 BLOCKED Patrol event posting attempt - Active event: {active_info}")
            error_msg = (
                "❌ **There is already an active event!**\n\n"
                f"{active_info}\n\n"
                "You must end the current event before posting a new one. "
                "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
            )
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        # No active event - proceed with confirmation
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
        """Open modal for Combat Training event (description required, link optional)."""
        # Check if there's an active event
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        
        if event_panel_cog is None:
            logger.error("Event panel cog not found! Cannot check for active events.")
            await interaction.response.send_message(
                "❌ Internal error: Event panel system not available.",
                ephemeral=True
            )
            return
        
        if event_panel_cog.is_event_active():
            active_info = event_panel_cog.get_active_event_info()
            logger.warning(f"Blocked event posting attempt: combat_training - Active event: {active_info}")
            error_msg = (
                "❌ **There is already an active event!**\n\n"
                f"{active_info}\n\n"
                "You must end the current event before posting a new one. "
                "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
            )
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        # Open modal directly (description is required)
        modal = CombatTrainingModal(
            bot=self.bot,
            event_key="combat_training",
            host_user=interaction.user
        )
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(
        label="Basic Training",
        style=discord.ButtonStyle.success,
        custom_id="slm_basic_training",
        row=0
    )
    async def btn_basic_training(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Open modal for Basic Training event (description required, link required)."""
        # Check if there's an active event
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        
        if event_panel_cog is None:
            logger.error("Event panel cog not found! Cannot check for active events.")
            await interaction.response.send_message(
                "❌ Internal error: Event panel system not available.",
                ephemeral=True
            )
            return
        
        if event_panel_cog.is_event_active():
            active_info = event_panel_cog.get_active_event_info()
            logger.warning(f"Blocked event posting attempt: basic_training - Active event: {active_info}")
            error_msg = (
                "❌ **There is already an active event!**\n\n"
                f"{active_info}\n\n"
                "You must end the current event before posting a new one. "
                "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
            )
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        # Open modal directly (description and link are required)
        modal = BasicTrainingModal(
            bot=self.bot,
            event_key="basic_training",
            host_user=interaction.user
        )
        await interaction.response.send_modal(modal)
    
    # Row 1: RED (raids & rally)
    @discord.ui.button(
        label="Internal Practice Raid",
        style=discord.ButtonStyle.danger,
        custom_id="slm_internal_raid",
        row=1
    )
    async def btn_internal_raid(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Open modal for Internal Practice Raid event (description required, link required)."""
        # Check if there's an active event
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        
        if event_panel_cog is None:
            logger.error("Event panel cog not found! Cannot check for active events.")
            await interaction.response.send_message(
                "❌ Internal error: Event panel system not available.",
                ephemeral=True
            )
            return
        
        if event_panel_cog.is_event_active():
            active_info = event_panel_cog.get_active_event_info()
            logger.warning(f"Blocked event posting attempt: internal_raid - Active event: {active_info}")
            error_msg = (
                "❌ **There is already an active event!**\n\n"
                f"{active_info}\n\n"
                "You must end the current event before posting a new one. "
                "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
            )
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        # Open modal directly
        modal = InternalRaidModal(
            bot=self.bot,
            event_key="internal_raid",
            host_user=interaction.user
        )
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(
        label="Practice Raid",
        style=discord.ButtonStyle.danger,
        custom_id="slm_practice_raid",
        row=1
    )
    async def btn_practice_raid(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Open modal for Practice Raid event (description required, link required)."""
        # Check if there's an active event
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        
        if event_panel_cog is None:
            logger.error("Event panel cog not found! Cannot check for active events.")
            await interaction.response.send_message(
                "❌ Internal error: Event panel system not available.",
                ephemeral=True
            )
            return
        
        if event_panel_cog.is_event_active():
            active_info = event_panel_cog.get_active_event_info()
            logger.warning(f"Blocked event posting attempt: practice_raid - Active event: {active_info}")
            error_msg = (
                "❌ **There is already an active event!**\n\n"
                f"{active_info}\n\n"
                "You must end the current event before posting a new one. "
                "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
            )
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        # Open modal directly
        modal = PracticeRaidModal(
            bot=self.bot,
            event_key="practice_raid",
            host_user=interaction.user
        )
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(
        label="Rally",
        style=discord.ButtonStyle.danger,
        custom_id="slm_rally",
        row=1
    )
    async def btn_rally(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Open modal for Rally event (description required, link required)."""
        # Check if there's an active event
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        
        if event_panel_cog is None:
            logger.error("Event panel cog not found! Cannot check for active events.")
            await interaction.response.send_message(
                "❌ Internal error: Event panel system not available.",
                ephemeral=True
            )
            return
        
        if event_panel_cog.is_event_active():
            active_info = event_panel_cog.get_active_event_info()
            logger.warning(f"Blocked event posting attempt: rally - Active event: {active_info}")
            error_msg = (
                "❌ **There is already an active event!**\n\n"
                f"{active_info}\n\n"
                "You must end the current event before posting a new one. "
                "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
            )
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        # Open modal directly
        modal = RallyModal(
            bot=self.bot,
            event_key="rally",
            host_user=interaction.user
        )
        await interaction.response.send_modal(modal)
    
    # Row 2: GREY (custom)
    @discord.ui.button(
        label="Custom",
        style=discord.ButtonStyle.secondary,
        custom_id="slm_custom",
        row=2
    )
    async def btn_custom(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Open modal for custom event with title selection/input."""
        # Check if there's an active event
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        
        if event_panel_cog is None:
            logger.error("Event panel cog not found! Cannot check for active events.")
            await interaction.response.send_message(
                "❌ Internal error: Event panel system not available.",
                ephemeral=True
            )
            return
        
        if event_panel_cog.is_event_active():
            active_info = event_panel_cog.get_active_event_info()
            logger.warning(f"Blocked custom event posting attempt - Active event: {active_info}")
            error_msg = (
                "❌ **There is already an active event!**\n\n"
                f"{active_info}\n\n"
                "You must end the current event before posting a new one. "
                "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
            )
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        # Create view with title selection options
        view = CustomEventTitleView(self.bot, interaction.user)
        embed = discord.Embed(
            title="Custom Event",
            description=(
                "Choose a preset title or enter a custom one.\n\n"
                "**Format required:** ++ Your Title ++\n"
                "**Example:** ++ Gamenight ++\n\n"
                "The ++ ++ symbols are mandatory around the text."
            ),
            color=discord.Color.greyple()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def _dispatch(self, interaction: discord.Interaction, key: str):
        """Dispatch event announcement based on preset key."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        # Check if there's an active event
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(self.bot)
        
        if event_panel_cog is None:
            logger.error("Event panel cog not found! Cannot check for active events.")
        elif event_panel_cog.is_event_active():
            active_info = event_panel_cog.get_active_event_info()
            logger.warning(f"Blocked event posting attempt: {key} - Active event: {active_info}")
            error_msg = (
                "❌ **There is already an active event!**\n\n"
                f"{active_info}\n\n"
                "You must end the current event before posting a new one. "
                "Please find the **End** button in the event-publishing channel and click it to finalize the ongoing event."
            )
            await interaction.followup.send(error_msg, ephemeral=True)
            return
        else:
            logger.debug(f"No active event found, proceeding with event posting: {key}")
        
        preset = EVENT_PRESETS.get(key)
        if not preset:
            await interaction.followup.send("❌ Event preset not found.", ephemeral=True)
            return
        
        # Use _post_event_with_description for all events to ensure consistency
        await _post_event_with_description(
            bot=self.bot,
            interaction=interaction,
            event_key=key,
            custom_description=None,
            custom_link=None,
            host_user=interaction.user
        )


class SalamandersEventPanel(commands.Cog):
    """Posts the Salamanders-themed Event Hosting panel and wires button actions."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.panel_message_id: int | None = None
        # Track active event to prevent multiple events at once
        self.active_event: dict | None = None  # {event_message_id, end_message_id, host_user, event_title}
    
    def is_event_active(self) -> bool:
        """Check if there is currently an active event."""
        is_active = self.active_event is not None
        if is_active:
            logger.debug(f"Event active check: TRUE - {self.active_event.get('event_title', 'Unknown')}")
        else:
            logger.debug("Event active check: FALSE - No active event")
        return is_active
    
    def set_active_event(self, event_message_id: int, end_message_id: int, host_user: discord.Member, event_title: str):
        """Mark an event as active."""
        self.active_event = {
            "event_message_id": event_message_id,
            "end_message_id": end_message_id,
            "host_user": host_user,
            "event_title": event_title
        }
        logger.info(f"Active event set: {event_title} by {host_user.id}")
    
    def clear_active_event(self):
        """Clear the active event."""
        if self.active_event:
            logger.info(f"Active event cleared: {self.active_event.get('event_title', 'Unknown')}")
        self.active_event = None
    
    def get_active_event_info(self) -> str | None:
        """Get information about the active event for error messages."""
        if not self.active_event:
            return None
        host = self.active_event["host_user"]
        title = self.active_event["event_title"]
        return f"**{title}** hosted by {host.mention}"
    
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
        Deletes ALL messages in the channel and posts new panel.
        """
        channel = self.bot.get_channel(EVENT_PANEL_CHANNEL_ID)
        if not isinstance(channel, discord.TextChannel):
            logger.error(f"Event panel channel {EVENT_PANEL_CHANNEL_ID} not found or invalid")
            return
        
        try:
            # Check bot permissions
            bot_member = channel.guild.get_member(self.bot.user.id)
            if bot_member:
                perms = channel.permissions_for(bot_member)
                if not perms.manage_messages:
                    logger.error(f"❌ Bot does not have 'Manage Messages' permission in channel {EVENT_PANEL_CHANNEL_ID}")
                    logger.error("   Please grant the bot 'Manage Messages' permission in the event panel channel")
                    return
            
            # Delete ALL messages in the channel using purge (more efficient)
            # First, try to purge all messages (bulk delete is faster)
            deleted_count = 0
            iteration = 0
            
            # Use purge to delete all messages (including bot's own)
            # Purge has a limit of 100 messages per call, so we need to loop
            # Pass a lambda that always returns True to delete all messages
            logger.info(f"Starting channel cleanup for {EVENT_PANEL_CHANNEL_ID}...")
            while True:
                iteration += 1
                purged = await channel.purge(limit=100, check=lambda m: True)
                deleted_count += len(purged)
                
                if len(purged) > 0:
                    logger.debug(f"Purge iteration {iteration}: deleted {len(purged)} messages")
                
                if len(purged) < 100:
                    # No more messages to delete
                    break
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
            
            if deleted_count > 0:
                logger.info(f"✅ Deleted {deleted_count} messages from event panel channel")
            else:
                logger.info("Channel was already empty")
            
            # Small delay before posting new message
            await asyncio.sleep(1)
            
            # Post new panel
            embed = await self._create_panel_embed()
            view = SalamandersEventView(self.bot)
            message = await channel.send(embed=embed, view=view)
            self.panel_message_id = message.id
            
            logger.info(f"✅ Event panel posted in channel {EVENT_PANEL_CHANNEL_ID} (message ID: {message.id})")
        
        except discord.errors.Forbidden:
            logger.error(f"❌ No permission to manage messages in channel {EVENT_PANEL_CHANNEL_ID}")
            logger.error("   Bot needs 'Manage Messages' permission in the event panel channel")
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
    logger.info("Salamanders Event Panel cog loaded")


def get_event_panel_cog(bot: commands.Bot) -> SalamandersEventPanel | None:
    """Helper to get the event panel cog instance."""
    # Try to get by name first
    cog = bot.get_cog("SalamandersEventPanel")
    if cog:
        return cog
    
    # Fallback: search by type
    for cog_instance in bot.cogs.values():
        if isinstance(cog_instance, SalamandersEventPanel):
            return cog_instance
    
    return None
