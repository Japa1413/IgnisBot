# cogs/event_buttons.py
from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands

from utils.event_presets import EVENT_PRESETS
from utils.event_announcement import post_event_announcement


class SalamandersEventView(discord.ui.View):
    """Three rows of buttons (green / red / grey) that post Salamanders-themed events."""
    def __init__(self, bot: commands.Bot, *, timeout: float | None = 300):
        super().__init__(timeout=timeout)
        self.bot = bot

    # Row 1: GREEN (rites & training)
    @discord.ui.button(label="Rite of Flame", style=discord.ButtonStyle.success, custom_id="slm_rite_of_flame")
    async def btn_rite_of_flame(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._dispatch(interaction, "rite_of_flame")

    @discord.ui.button(label="Forge Drill", style=discord.ButtonStyle.success, custom_id="slm_forge_drill")
    async def btn_forge_drill(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._dispatch(interaction, "forge_drill")

    @discord.ui.button(label="Promethean Training", style=discord.ButtonStyle.success, custom_id="slm_promethean_training")
    async def btn_promethean(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._dispatch(interaction, "promethean_training")

    # Row 2: RED (raids & muster)
    @discord.ui.button(label="Internal Practice Raid", style=discord.ButtonStyle.danger, custom_id="slm_internal_raid", row=1)
    async def btn_internal_raid(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._dispatch(interaction, "internal_raid")

    @discord.ui.button(label="Practice Raid", style=discord.ButtonStyle.danger, custom_id="slm_practice_raid", row=1)
    async def btn_practice_raid(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._dispatch(interaction, "practice_raid")

    @discord.ui.button(label="Forge Muster", style=discord.ButtonStyle.danger, custom_id="slm_forge_muster", row=1)
    async def btn_forge_muster(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._dispatch(interaction, "forge_muster")

    # Row 3: GREY (social & custom)
    @discord.ui.button(label="Hearthfire Night", style=discord.ButtonStyle.secondary, custom_id="slm_hearthfire_night", row=2)
    async def btn_hearthfire(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._dispatch(interaction, "hearthfire_night")

    @discord.ui.button(label="Custom", style=discord.ButtonStyle.secondary, custom_id="slm_custom", row=2)
    async def btn_custom(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_message(
            "🛠️ Custom event coming soon (we’ll open a modal to collect title/time/location).",
            ephemeral=True
        )

    async def _dispatch(self, interaction: discord.Interaction, key: str):
        await interaction.response.defer(ephemeral=True, thinking=True)

        preset = EVENT_PRESETS.get(key)
        if not preset:
            await interaction.followup.send("❌ Event preset not found.", ephemeral=True)
            return

        target = interaction.channel
        author_icon = interaction.user.display_avatar.url if interaction.user.display_avatar else None

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


class SalamandersEventPanel(commands.Cog):
    """Posts the Salamanders-themed Event Hosting panel and wires button actions."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="event_panel", description="Post the Salamanders Event Hosting panel.")
    @app_commands.describe(channel="Optional: target channel (defaults to current)")
    @app_commands.guild_only()
    async def event_panel(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None):
        await interaction.response.defer(ephemeral=True, thinking=True)

        target = channel or interaction.channel

        embed = discord.Embed(
            title="🔥 Event Hosting — Salamanders",
            description=(
                "Welcome to the Forge-Temple of Nocturne.\n"
                "Select the rite you wish to initiate and stand ready to heed the Promethean creed. "
                "Steel is made strong by fire; so too are the sons of Vulkan."
            ),
            color=discord.Color.from_str("#2f3136")
        )
        # Banner/art — change to your Salamanders image
        embed.set_image(url="https://i.imgur.com/OGSWrjU.png")
        embed.set_footer(
            text="Vulkan Lives • For Nocturne. For the Forge.",
            icon_url="https://cdn.discordapp.com/emojis/1158979646512177253.webp?size=128&quality=lossless"
        )

        await target.send(embed=embed, view=SalamandersEventView(self.bot))
        await interaction.followup.send(f"✅ Salamanders Event Panel posted in {target.mention}.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(SalamandersEventPanel(bot))