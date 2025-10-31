# cogs/userinfo.py
from __future__ import annotations
import re
from typing import Optional, Tuple, Dict

import discord
from discord.ext import commands
from discord import app_commands

from utils.database import get_user
from utils.checks import cmd_channel_only, appcmd_channel_only
from utils.config import USERINFO_CHANNEL_ID

# ---------------- Rank thresholds ----------------
RANK_LADDER: Dict[str, int] = {
    "Civitas aspirant": 0,
    "Emberbound Initiate": 20,
    "Obsidian Trialborn": 40,
    "Crucible Neophyte": 60,
    "Emberbrand Proving": 80,
    "Inductii": 100,
    "Legionary": 120,
    "Support Squad": 160,
    "Legion Veteran": 200,
    "Legion Elite": 260,
    "Signal Marine": 320,
    "Destroyer": 380,
    "Vexillarius": 440,
    "Apothecarion": 500,
    "Terminator Squad": 560,
    "Techmarine": 620,
    "Chaplain": 680,
    "Legion Sergeant": 740,
    "Veteran Sergeant": 820,
    "2nd Lieutenant": 900,
    "1st Lieutenant": 1000,
    "Captain": 1100,
    "Pyroclast Sentinel": 1250,
    "Cindermarked": 1400,
    "Flamewrought": 1600,
    "Consulate": 1800,
    "Marshal": 2000,
    "Preator": 2300,
    "Commander": 2600,
    "First Captain": 3000,
    "Primarch": 999_999,
    "Emperor Of Mankind": 9_999_999,
}

AWARD_KEYWORDS = ("Seal", "Medal", "Citation", "Laurel", "Commendation")
SPECIALTY_ROLES = (
    "Apothecarion", "Techmarine", "Chaplain",
    "Vexillarius", "Destroyer", "Signal Marine",
    "Terminator Squad",
)
COMPANY_PREFIX_RE = re.compile(r"^(\d+)\.\s")

def _progress_to_next(points: int, current_rank: str) -> Tuple[int, int, str]:
    ordered = sorted(RANK_LADDER.items(), key=lambda kv: kv[1])
    current_threshold = RANK_LADDER.get(current_rank, 0)
    next_name, next_threshold = "Max Rank", current_threshold
    for name, thresh in ordered:
        if thresh > current_threshold:
            next_name, next_threshold = name, thresh
            break
    if next_threshold <= current_threshold:
        return (0, 0, "Max Rank")
    gained = max(0, points - current_threshold)
    needed = max(1, next_threshold - current_threshold)
    gained = min(gained, needed)
    return gained, needed, next_name

def _progress_bar(g: int, n: int, w: int = 12) -> str:
    if n <= 0: return "▰" * w
    filled = max(0, min(w, int(round((g / n) * w))))
    return f"{'▰'*filled}{'▱'*(w-filled)}"

def _company_from_nick(member: discord.Member) -> str | None:
    nick = member.nick or ""
    m = COMPANY_PREFIX_RE.match(nick)
    if not m: return None
    n = m.group(1)
    if n == "1": return "1st Battle\nCompany"
    if n.endswith("1"): return f"{n}st Battle\nCompany"
    if n.endswith("2"): return f"{n}nd Battle\nCompany"
    if n.endswith("3"): return f"{n}rd Battle\nCompany"
    return f"{n}th Battle\nCompany"

def _find_specialty(member: discord.Member) -> str | None:
    names = {r.name for r in member.roles if r.name != "@everyone"}
    for spec in SPECIALTY_ROLES:
        if spec in names: return spec
    return None

def _collect_awards(member: discord.Member) -> str:
    awards = []
    for r in member.roles:
        if r.name == "@everyone": continue
        if any(k.lower() in r.name.lower() for k in AWARD_KEYWORDS):
            awards.append(getattr(r, "mention", r.name))
    return ", ".join(awards) if awards else "None"

class UserInfoCog(commands.Cog):
    """Cog for /userinfo and !userinfo (hybrid)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="userinfo", description="Displays a Salamanders-styled user info card.")
    @app_commands.describe(member="User to inspect (defaults to you)")
    @cmd_channel_only(USERINFO_CHANNEL_ID)         # prefix/hybrid guard
    @appcmd_channel_only(USERINFO_CHANNEL_ID)      # slash guard
    async def userinfo(self, ctx: commands.Context, member: discord.Member | None = None):
        if ctx.guild is None:
            await ctx.reply("This command must be used in a server.", mention_author=False)
            return

        member = member or ctx.author
        avatar_url = getattr(member.display_avatar, "url", None)

        db_user = await get_user(member.id)
        points = int(db_user["points"]) if db_user and "points" in db_user else 0
        current_rank = (db_user.get("rank") if db_user else None) or "Civitas aspirant"

        gained, needed, next_rank = _progress_to_next(points, current_rank)
        bar = _progress_bar(gained, needed, 12)
        progress_line = f"({gained}/{needed})" if needed > 0 else "(Max)"

        company = _company_from_nick(member) or "Unknown"
        specialty = _find_specialty(member) or "No Specialty"
        awards = _collect_awards(member)

        gold_studs = 0
        silver_studs = 0

        embed = discord.Embed(title=member.name, color=discord.Color.dark_green())
        if avatar_url: embed.set_thumbnail(url=avatar_url)

        embed.add_field(name="Points", value=f"│  {points}", inline=True)
        embed.add_field(name="Rank", value=f"│  {current_rank}", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        embed.add_field(name="\u200b", value=("+" * 66), inline=False)

        embed.add_field(name="Point Progress", value=f"`{bar}`\n{progress_line}", inline=True)
        embed.add_field(name="Next Rank", value=f"│  {next_rank}", inline=True)
        embed.add_field(name="Awards", value=f"{awards}", inline=True)

        embed.add_field(name="\u200b", value=("+" * 66), inline=False)

        embed.add_field(name="Company", value=f"│  {company}", inline=True)
        embed.add_field(name="Speciality", value=f"│  {specialty}", inline=True)
        embed.add_field(
            name="Service Studs",
            value=f"│  Gold Studs: {gold_studs}\n│  Silver Studs: {silver_studs}",
            inline=True
        )

        footer_icon = getattr(ctx.author.display_avatar, "url", None)
        embed.set_footer(text=f"{ctx.author.display_name}", icon_url=footer_icon)

        await ctx.reply(embed=embed, mention_author=False)

async def setup(bot: commands.Bot):
    await bot.add_cog(UserInfoCog(bot))