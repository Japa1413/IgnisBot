# cogs/admin_sync.py
from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands
from utils.config import GUILD_ID

class AdminSync(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sync", description="Force app-commands sync.")
    @app_commands.describe(scope="Where to sync: guild | global | clear")
    async def sync(self, interaction: discord.Interaction, scope: str = "guild"):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need Administrator permission.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        tree = self.bot.tree
        guild_obj = discord.Object(id=GUILD_ID)

        try:
            if scope.lower() == "guild":
                self.bot.tree.copy_global_to(guild=guild_obj)  # opcional
                cmds = await tree.sync(guild=guild_obj)
                await interaction.followup.send(f"✅ Synced **{len(cmds)}** commands to guild.", ephemeral=True)

            elif scope.lower() == "global":
                cmds = await tree.sync()
                await interaction.followup.send(
                    f"🌐 Submitted **{len(cmds)}** global commands (may take up to ~1h).",
                    ephemeral=True
                )

            elif scope.lower() == "clear":
                # Limpa TODOS os comandos do guild e reaplica
                tree.clear_commands(guild=guild_obj)
                await tree.sync(guild=guild_obj)

                # (opcional) limpar globais tbm — cuidado, deleta tudo global
                # tree.clear_commands(guild=None)
                # await tree.sync()

                # Recarregar cogs e sincronizar de novo
                await interaction.followup.send("🧹 Cleared guild commands. Re-syncing…", ephemeral=True)
                self.bot.tree.copy_global_to(guild=guild_obj)
                cmds = await tree.sync(guild=guild_obj)
                await interaction.followup.send(f"✅ Re-synced **{len(cmds)}** commands to guild.", ephemeral=True)

            else:
                await interaction.followup.send("Use: `guild`, `global` or `clear`.", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Sync error: `{e}`", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminSync(bot))