# ignis_main.py
from __future__ import annotations

import asyncio
import discord
from discord.ext import commands
from discord import app_commands

from utils.config import TOKEN, GUILD_ID, VC_CHANNEL_ID
from utils.database import initialize_db, ensure_user_exists
from utils.voice_logs import handle_voice_state_update
from utils.logger import get_logger

logger = get_logger(__name__)

# COGs
from cogs.userinfo import UserInfoCog
from cogs.vc_log import VCLogCog
from cogs.add import AddPointsCog
from cogs.remove import RemovePointsCog
from cogs.leaderboard import LeaderboardCog
from cogs.data_privacy import DataPrivacyCog
from cogs.legal import LegalCog
from cogs.cache_stats import CacheStatsCog
# If you have event_buttons.py as an extension with setup(bot), you can load it via load_extension

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class IgnisBot(commands.Bot):
    def __init__(self):
        # Use a TEXT prefix different from "/" to avoid conflicts with slash commands
        super().__init__(command_prefix="!", intents=intents)
        # Remove default help (we'll keep the hybrid /help)
        self.remove_command("help")

    async def setup_hook(self):
        # 1) Database first
        await initialize_db()

        # 2) Load COGs (classes already imported)
        await self.add_cog(UserInfoCog(self))
        await self.add_cog(VCLogCog(self))
        await self.add_cog(AddPointsCog(self))
        await self.add_cog(RemovePointsCog(self))
        await self.add_cog(LeaderboardCog(self))
        await self.add_cog(DataPrivacyCog(self))
        await self.add_cog(LegalCog(self))
        await self.add_cog(CacheStatsCog(self))

        # 3) (Optional) Load extensions with setup(bot)
        # await self.load_extension("cogs.event_buttons")


bot = IgnisBot()


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Game(name="Loyalty is its own reward.")
    )
    logger.info(f"🔥 Logged in as {bot.user} (id={bot.user.id})")
    
    # Sync slash commands after bot is ready
    await asyncio.sleep(1)  # Small delay to ensure everything is loaded
    
    guild = discord.Object(id=GUILD_ID)
    try:
        # List registered commands for debug
        all_commands = list(bot.tree.walk_commands(guild=None))
        logger.info(f"📋 Found {len(all_commands)} commands in tree")
        
        if all_commands:
            cmd_list = [f"{c.name} ({type(c).__name__})" for c in all_commands[:10]]
            logger.info(f"   Sample commands: {', '.join(cmd_list)}")
        
        # Try to sync guild commands
        try:
            synced = await bot.tree.sync(guild=guild)
            logger.info(f"✅ Synced {len(synced)} commands for guild {GUILD_ID}")
            if synced:
                cmd_names = [c.name for c in synced]
                logger.info(f"→ Commands synced: {', '.join(cmd_names)}")
            else:
                logger.warning("⚠️ Sync returned 0 commands. Trying global sync as fallback...")
                # Try global sync as fallback
                synced_global = await bot.tree.sync()
                logger.info(f"✅ Synced {len(synced_global)} commands globally")
                if synced_global:
                    cmd_names = [c.name for c in synced_global]
                    logger.info(f"→ Global commands: {', '.join(cmd_names)}")
        except discord.HTTPException as http_err:
            logger.error(f"❌ HTTP error during sync: {http_err}")
            logger.error(f"   Status: {http_err.status}, Response: {http_err.text}")
        except discord.Forbidden as e:
            logger.warning(f"⚠️ Missing access to sync guild commands: {e}")
            logger.warning("   Make sure the bot has 'applications.commands' scope and proper permissions.")
            logger.warning("   Check: https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=0&scope=bot%20applications.commands")
    except Exception as e:
        logger.error(f"❌ Unexpected sync error: {e}", exc_info=True)


# Handler de erros para app_commands (slash commands)
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Global handler for slash command errors"""
    error_handled = False
    
    if isinstance(error, app_commands.CheckFailure):
        # Validation error (wrong channel, permissions, etc.)
        error_msg = "❌ You cannot use this command here or do not have sufficient permissions."
        
        # More specific message for channel restrictions
        if interaction.command:
            cmd_name = interaction.command.name
            from utils.config import STAFF_CMDS_CHANNEL_ID
            if cmd_name in ['add', 'remove', 'vc_log', 'userinfo']:
                try:
                    # Tentar obter o nome do canal permitido
                    allowed_channel = bot.get_channel(STAFF_CMDS_CHANNEL_ID)
                    channel_name = f"**#{allowed_channel.name}**" if allowed_channel else f"canal com ID `{STAFF_CMDS_CHANNEL_ID}`"
                    current_channel_name = f"#{interaction.channel.name}" if interaction.channel else "canal desconhecido"
                    error_msg = f"❌ The `/{cmd_name}` command can only be used in {channel_name}.\n📍 Você está atualmente em: **{current_channel_name}**"
                except Exception:
                    error_msg = f"❌ The `/{cmd_name}` command can only be used in a specific channel (ID: {STAFF_CMDS_CHANNEL_ID})."
        
        try:
            if interaction.response.is_done():
                await interaction.followup.send(error_msg, ephemeral=True)
            else:
                await interaction.response.send_message(error_msg, ephemeral=True)
            error_handled = True
        except Exception:
            pass
            
    elif isinstance(error, app_commands.CommandNotFound):
        error_msg = "❌ Command not found. It may still be syncing (wait 1-2 minutes)."
        try:
            if interaction.response.is_done():
                await interaction.followup.send(error_msg, ephemeral=True)
            else:
                await interaction.response.send_message(error_msg, ephemeral=True)
            error_handled = True
        except Exception:
            pass
    
    # Log error
    cmd_name = interaction.command.name if interaction.command else 'unknown'
    logger.error(f"Error in app command '{cmd_name}': {error}", exc_info=True)
    
    # If not handled, try to send generic message
    if not error_handled:
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred while processing the command. Please try again.",
                    ephemeral=True
                )
        except Exception:
            pass

# Ensure ensure_user_exists also works for slash commands
@bot.listen("on_interaction")
async def _ensure_user_for_slash(interaction: discord.Interaction):
    try:
        if interaction.type == discord.InteractionType.application_command and interaction.user:
            await ensure_user_exists(interaction.user.id)
    except Exception as e:
        # Don't break handler flow
        logger.warning(f"[ensure_user_exists] interaction error: {e}")


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    # Voice logs handler (if applicable)
    await handle_voice_state_update(member, before, after, VC_CHANNEL_ID)


@bot.hybrid_command()
async def help(ctx: commands.Context):
    """Displays a list of available commands."""
    prefix = "/"
    embed = discord.Embed(title="Command List", color=discord.Color.dark_red())
    embed.timestamp = discord.utils.utcnow()

    try:
        icon_url = ctx.author.display_avatar.url
    except Exception:
        icon_url = None
    embed.set_footer(text=f"{ctx.author.name}", icon_url=icon_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1158979646512177253.webp?size=128&quality=lossless")

    # List only loaded commands (text and hybrid)
    commands_list = sorted(bot.commands, key=lambda c: c.name)
    for command in commands_list:
        if not command.hidden:
            embed.add_field(
                name=f"{prefix}{command.name}",
                value=command.help or "No description available.",
                inline=False,
            )
    
    # Add privacy information
    embed.add_field(
        name="\u200b",
        value="**📋 Privacy:** Use `/privacy`, `/terms`, `/sla` for legal documentation",
        inline=False
    )
    embed.add_field(
        name="\u200b",
        value="**🔒 Your LGPD Rights:** `/export_my_data`, `/delete_my_data`, `/correct_my_data`, `/consent`",
        inline=False
    )
    
    await ctx.send(embed=embed)


def main():
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
