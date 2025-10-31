# set_log_channel.py
import discord
from discord.ext import commands
from discord import app_commands

class SetLogChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_log_channel", description="Configures the log channel.")
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # Save log channel ID in bot memory
        self.bot.log_channel_id = channel.id

        # Save the log channel ID to a file
        with open("log_channel.txt", "w") as f:
            f.write(str(channel.id))

        await interaction.response.send_message(f"✅ Log channel set to: {channel.mention}")

async def setup(bot):
    await bot.add_cog(SetLogChannel(bot))
