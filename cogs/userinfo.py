# cogs/userinfo.py
from __future__ import annotations

import re
from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands

from services.progression_service import ProgressionService
from utils.checks import cmd_channel_only, appcmd_channel_only
from utils.config import USERINFO_CHANNEL_ID
from utils.logger import get_logger

logger = get_logger(__name__)

# Award keywords
AWARD_KEYWORDS = ("Seal", "Medal", "Citation", "Laurel", "Commendation")
SPECIALTY_ROLES = (
    "Apothecarion", "Techmarine", "Chaplain",
    "Vexillarius", "Destroyer", "Signal Marine",
    "Terminator Squad",
)
COMPANY_PREFIX_RE = re.compile(r"^(\d+)\.\s")


def _company_from_nick(member: discord.Member) -> str | None:
    """Extract company from nickname"""
    nick = member.nick or ""
    m = COMPANY_PREFIX_RE.match(nick)
    if not m:
        return None
    n = m.group(1)
    if n == "1":
        return "1st Battle\nCompany"
    if n.endswith("1"):
        return f"{n}st Battle\nCompany"
    if n.endswith("2"):
        return f"{n}nd Battle\nCompany"
    if n.endswith("3"):
        return f"{n}rd Battle\nCompany"
    return f"{n}th Battle\nCompany"


def _find_specialty(member: discord.Member) -> str | None:
    """Find specialty role"""
    names = {r.name for r in member.roles if r.name != "@everyone"}
    for spec in SPECIALTY_ROLES:
        if spec in names:
            return spec
    return None


def _collect_awards(member: discord.Member) -> str:
    """Collect award roles"""
    awards = []
    for r in member.roles:
        if r.name == "@everyone":
            continue
        if any(k.lower() in r.name.lower() for k in AWARD_KEYWORDS):
            awards.append(getattr(r, "mention", r.name))
    return ", ".join(awards) if awards else "None"


class UserInfoCog(commands.Cog):
    """Cog for /userinfo command with corrected progression display"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.progression_service = ProgressionService()

    @commands.hybrid_command(name="userinfo", description="Displays user information with progression.")
    @app_commands.describe(member="User to inspect (defaults to you)")
    @cmd_channel_only(USERINFO_CHANNEL_ID)  # prefix/hybrid guard
    @appcmd_channel_only(USERINFO_CHANNEL_ID)  # slash guard
    async def userinfo(self, ctx: commands.Context, member: discord.Member | None = None):
        if ctx.guild is None:
            await ctx.reply("This command must be used in a server.", mention_author=False)
            return

        member = member or ctx.author
        avatar_url = getattr(member.display_avatar, "url", None)

        try:
            # Get user progression info
            user_info = await self.progression_service.get_user_info(member.id)
            
            # Extract additional info from Discord member
            company = _company_from_nick(member) or "Unknown"
            specialty = _find_specialty(member) or "No Specialty"
            awards = _collect_awards(member)
            
            # Service studs (placeholder for now)
            gold_studs = 0
            silver_studs = 0
            
            # Build embed with Warhammer terminal aesthetic (clean version)
            embed = discord.Embed(
                title=f"— TERMINAL: {member.display_name.upper()} —",
                color=discord.Color.from_rgb(0, 255, 0)  # Bright green terminal color
            )
            
            if avatar_url:
                embed.set_thumbnail(url=avatar_url)
            
            # Clean separator line
            embed.add_field(
                name="\u200b",
                value="╠═══════════════════════════════════════════════════════════╣",
                inline=False
            )
            
            # Top section: Points and Rank (clean text, no code blocks)
            embed.add_field(
                name="[POINTS]",
                value=f"> {user_info['points']}",
                inline=True
            )
            embed.add_field(
                name="[RANK]",
                value=f"> {user_info['rank']}",
                inline=True
            )
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            
            # Clean separator
            embed.add_field(
                name="\u200b",
                value="╠═══════════════════════════════════════════════════════════╣",
                inline=False
            )
            
            # Progress section: Point Progress (bar in code block, numbers as text)
            # Sacred protocol: Show bar + actual points (even if exceeds limit)
            # Use the formatted display string from progression service
            progress_display_value = user_info.get('progress_display', f"{user_info['points']} / {user_info['rank_limit']}")
            progress_display = f"```{user_info['progress_bar']}```\n{progress_display_value}"
            
            embed.add_field(
                name="[PROGRESS]",
                value=progress_display,
                inline=True
            )
            
            # Next Rank - may be split across lines if long
            next_rank_value = user_info['next_rank']
            if len(next_rank_value) > 15 and " " in next_rank_value:
                # Split long rank names
                parts = next_rank_value.split(" ", 1)
                next_rank_value = f"{parts[0]}\n{parts[1]}"
            
            embed.add_field(
                name="[NEXT_RANK]",
                value=f"> {next_rank_value}",
                inline=True
            )
            embed.add_field(
                name="[AWARDS]",
                value=f"> {awards}",
                inline=True
            )
            
            # Clean separator
            embed.add_field(
                name="\u200b",
                value="╠═══════════════════════════════════════════════════════════╣",
                inline=False
            )
            
            # Bottom section: Company, Speciality, Service Studs (clean text)
            embed.add_field(
                name="[COMPANY]",
                value=f"> {company}",
                inline=True
            )
            embed.add_field(
                name="[SPECIALITY]",
                value=f"> {specialty}",
                inline=True
            )
            embed.add_field(
                name="[SERVICE_STUDS]",
                value=f"> Gold: {gold_studs}\n> Silver: {silver_studs}",
                inline=True
            )
            
            # Clean terminal footer
            embed.set_footer(text="╚═══ IGNIS TERMINAL v2.0 ─ STATUS: OPERATIONAL ═══╝")
            
            await ctx.reply(embed=embed, mention_author=False)
            
        except Exception as e:
            logger.error(f"Error in userinfo command: {e}", exc_info=True)
            await ctx.reply("❌ Error retrieving user information.", mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(UserInfoCog(bot))
