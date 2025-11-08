"""
Gamenight Role Assignment - Auto-role system with button toggle.
"""

from __future__ import annotations

import discord
from discord.ext import commands
from utils.logger import get_logger

logger = get_logger(__name__)

# Channel ID where the role assignment message is posted
GAMENIGHT_ROLE_CHANNEL_ID = 1375941286267326533

# Role ID to assign/remove
GAMENIGHT_ROLE_ID = 1375941284161912833


class GamenightRoleView(discord.ui.View):
    """View with button to toggle Gamenight role."""
    
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)  # Persistent view
        self.bot = bot
    
    @discord.ui.button(
        label="Gamenight Role",
        style=discord.ButtonStyle.primary,
        custom_id="gamenight_role_toggle"
    )
    async def toggle_role_button(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Toggle Gamenight role for the user."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        # Get the role
        role = interaction.guild.get_role(GAMENIGHT_ROLE_ID)
        if role is None:
            await interaction.followup.send(
                "❌ Error: Gamenight role not found. Please contact an administrator.",
                ephemeral=True
            )
            logger.error(f"Gamenight role {GAMENIGHT_ROLE_ID} not found in guild {interaction.guild.id}")
            return
        
        # Get the member
        member = interaction.user
        if not isinstance(member, discord.Member):
            await interaction.followup.send(
                "❌ Error: Could not retrieve member information.",
                ephemeral=True
            )
            return
        
        # Toggle role
        try:
            if role in member.roles:
                # Remove role
                await member.remove_roles(role, reason="User toggled Gamenight role via button")
                await interaction.followup.send(
                    f"✅ **Gamenight Role** has been **removed** from you.",
                    ephemeral=True
                )
                logger.info(f"Removed Gamenight role from {member.id} ({member.display_name})")
            else:
                # Add role
                await member.add_roles(role, reason="User toggled Gamenight role via button")
                await interaction.followup.send(
                    f"✅ **Gamenight Role** has been **assigned** to you.",
                    ephemeral=True
                )
                logger.info(f"Assigned Gamenight role to {member.id} ({member.display_name})")
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Error: Bot doesn't have permission to manage roles. Please contact an administrator.",
                ephemeral=True
            )
            logger.error(f"Bot lacks permission to manage roles in guild {interaction.guild.id}")
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"❌ Error: Failed to update role. Please try again later.",
                ephemeral=True
            )
            logger.error(f"HTTP error while toggling Gamenight role: {e}")
        except Exception as e:
            await interaction.followup.send(
                "❌ An unexpected error occurred. Please try again later.",
                ephemeral=True
            )
            logger.error(f"Unexpected error while toggling Gamenight role: {e}", exc_info=True)


class GamenightRoleCog(commands.Cog):
    """Cog for managing Gamenight role assignment panel."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.panel_message_id: int | None = None
    
    async def post_or_update_panel(self):
        """Post or update the Gamenight role assignment panel."""
        channel = self.bot.get_channel(GAMENIGHT_ROLE_CHANNEL_ID)
        if not isinstance(channel, discord.TextChannel):
            logger.error(f"Channel {GAMENIGHT_ROLE_CHANNEL_ID} not found or is not a text channel")
            return
        
        # Delete all existing messages in the channel
        try:
            async for message in channel.history(limit=100):
                try:
                    await message.delete()
                    logger.debug(f"Deleted message {message.id} from Gamenight role channel")
                except discord.NotFound:
                    pass  # Message already deleted
                except discord.Forbidden:
                    logger.warning(f"No permission to delete message {message.id}")
                except Exception as e:
                    logger.warning(f"Error deleting message {message.id}: {e}")
        except Exception as e:
            logger.error(f"Error cleaning Gamenight role channel: {e}")
        
        # Create embed
        embed = discord.Embed(
            title="++ Gamenight Role Assignment ++",
            description=(
                "Click the button to add or remove the Gamenight role from yourself.\n\n"
                "Receive or remove roles by selecting them below:"
            ),
            color=discord.Color.blue()
        )
        
        # Post the panel
        try:
            view = GamenightRoleView(self.bot)
            message = await channel.send(embed=embed, view=view)
            self.panel_message_id = message.id
            logger.info(f"Posted Gamenight role assignment panel (Message ID: {self.panel_message_id})")
        except Exception as e:
            logger.error(f"Error posting Gamenight role assignment panel: {e}", exc_info=True)
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Post panel when bot is ready."""
        # Wait a bit to ensure all cogs are loaded
        import asyncio
        await asyncio.sleep(3)
        
        # Only post on first ready (not on reconnects)
        if not hasattr(self.bot, 'gamenight_role_posted'):
            self.bot.gamenight_role_posted = True
            logger.info("Posting Gamenight role assignment panel...")
            await self.post_or_update_panel()


async def setup(bot: commands.Bot):
    """Setup function for the cog."""
    await bot.add_cog(GamenightRoleCog(bot))
    logger.info("GamenightRoleCog loaded")

