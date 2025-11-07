# ignis_main.py
from __future__ import annotations

import asyncio
import discord
from discord.ext import commands
from discord import app_commands

from utils.config import TOKEN, GUILD_ID
from utils.database import initialize_db, ensure_user_exists
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
from cogs.induction import InductionCog
from cogs.rank import RankCog
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

        # 2) Setup event handlers (NEW - Architecture Phase 3)
        from events.handlers import setup_audit_handler, setup_cache_handler
        setup_audit_handler(self)
        setup_cache_handler(self)

        # 3) Load COGs (classes already imported)
        # Use corrected userinfo with progression system
        await self.add_cog(UserInfoCog(self))
        await self.add_cog(VCLogCog(self))
        await self.add_cog(AddPointsCog(self))
        await self.add_cog(RemovePointsCog(self))
        await self.add_cog(LeaderboardCog(self))
        await self.add_cog(DataPrivacyCog(self))
        await self.add_cog(LegalCog(self))
        await self.add_cog(CacheStatsCog(self))
        await self.add_cog(InductionCog(self))
        await self.add_cog(RankCog(self))  # Rank management (nickname formatting, company mapping)

        # 4) Gamification Handlers DISABLED - Using manual progression system
        # from events.gamification_handlers import setup
        # await setup(self)

        # 5) Role Sync Handler - Automatic rank sync from Discord roles (Bloxlink /update)
        from events.role_sync_handler import setup as setup_role_sync
        await setup_role_sync(self)
        
        # 6) Member Activity Log - Monitor voice channels and member join/leave
        from cogs.member_activity_log import setup as setup_member_activity_log
        await setup_member_activity_log(self)
        
        # 7) Salamanders Event Panel - Auto-post event hosting panel
        from cogs.event_buttons import setup as setup_event_panel
        await setup_event_panel(self)
        
        # 8) (Optional) Load other extensions
        # await self.load_extension("cogs.other")


bot = IgnisBot()


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Game(name="Loyalty is its own reward.")
    )
    logger.info(f"🔥 Logged in as {bot.user} (id={bot.user.id})")
    
    if not hasattr(bot, 'ready_count'):
        bot.ready_count = 0
    bot.ready_count += 1
    
    if bot.ready_count > 1:
        logger.warning("⚠️ Bot reconnected (ready_count > 1). Skipping initialization.")
        return
    
    # Sync slash commands after bot is ready
    await asyncio.sleep(2)  # Increased delay to ensure all cogs are fully loaded
    
    guild = discord.Object(id=GUILD_ID)
    try:
        # List registered commands for debug
        all_commands = list(bot.tree.walk_commands(guild=None))
        logger.info(f"📋 Found {len(all_commands)} commands in tree")
        
        if all_commands:
            cmd_list = [f"{c.name} ({type(c).__name__})" for c in all_commands[:10]]
            logger.info(f"   Sample commands: {', '.join(cmd_list)}")
        
        # OPTIMIZATION: Copy global commands to guild before syncing
        # This ensures guild commands are available even if global sync is used
        try:
            bot.tree.copy_global_to(guild=guild)
            logger.debug("Copied global commands to guild")
        except Exception as e:
            logger.warning(f"Could not copy global commands to guild: {e}")
        
        # Try to sync guild commands first
        try:
            synced = await bot.tree.sync(guild=guild)
            logger.info(f"✅ Synced {len(synced)} commands for guild {GUILD_ID}")
            if synced:
                cmd_names = [c.name for c in synced]
                logger.info(f"→ Guild commands synced: {', '.join(cmd_names[:10])}{'...' if len(cmd_names) > 10 else ''}")
            else:
                logger.warning("⚠️ Guild sync returned 0 commands. This may be normal if commands are global-only.")
                logger.info("Attempting global sync as fallback...")
                # Try global sync as fallback
                synced_global = await bot.tree.sync()
                logger.info(f"✅ Synced {len(synced_global)} commands globally")
                if synced_global:
                    cmd_names = [c.name for c in synced_global]
                    logger.info(f"→ Global commands synced: {', '.join(cmd_names[:10])}{'...' if len(cmd_names) > 10 else ''}")
                    logger.info("Note: Global commands may take up to 1 hour to propagate to all servers.")
        except discord.HTTPException as http_err:
            logger.error(f"❌ HTTP error during sync: {http_err}")
            logger.error(f"   Status: {http_err.status}, Response: {http_err.text}")
            # Try global sync as last resort
            try:
                logger.info("Attempting global sync as last resort...")
                synced_global = await bot.tree.sync()
                logger.info(f"✅ Global sync succeeded: {len(synced_global)} commands")
            except Exception as e2:
                logger.error(f"❌ Global sync also failed: {e2}")
        except discord.Forbidden as e:
            logger.warning(f"⚠️ Missing access to sync guild commands: {e}")
            logger.warning("   Attempting global sync instead...")
            try:
                synced_global = await bot.tree.sync()
                logger.info(f"✅ Global sync succeeded: {len(synced_global)} commands")
            except Exception as e2:
                logger.error(f"❌ Global sync failed: {e2}")
            logger.warning("   Make sure the bot has 'applications.commands' scope and proper permissions.")
            logger.warning("   Check: https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=0&scope=bot%20applications.commands")
    except Exception as e:
        logger.error(f"❌ Unexpected sync error: {e}", exc_info=True)
    
    # Auto-post/update event panel after a short delay to ensure everything is loaded
    async def post_event_panel_delayed():
        await asyncio.sleep(3)  # Wait 3 seconds for all cogs to be ready
        from cogs.event_buttons import get_event_panel_cog
        event_panel_cog = get_event_panel_cog(bot)
        if event_panel_cog:
            await event_panel_cog.post_or_update_panel()
        else:
            logger.warning("Event panel cog not found, skipping auto-post")
    
    # Schedule panel posting
    bot.loop.create_task(post_event_panel_delayed())


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
                    # Try to get allowed channel name
                    allowed_channel = bot.get_channel(STAFF_CMDS_CHANNEL_ID)
                    channel_name = f"**#{allowed_channel.name}**" if allowed_channel else f"channel with ID `{STAFF_CMDS_CHANNEL_ID}`"
                    current_channel_name = f"#{interaction.channel.name}" if interaction.channel else "unknown channel"
                    error_msg = f"❌ The `/{cmd_name}` command can only be used in {channel_name}.\n📍 You are currently in: **{current_channel_name}**"
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


# Voice state updates are now handled by MemberActivityLogCog
# Old handler removed to avoid conflicts
# @bot.event
# async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
#     await handle_voice_state_update(member, before, after, VC_CHANNEL_ID)


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
