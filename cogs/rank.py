# cogs/rank.py
from __future__ import annotations

import re
from typing import Optional, Dict, List

import discord
from discord.ext import commands
from discord import app_commands

from utils.database import get_pool

# -----------------------------
# RANKS & PRIORITY (highest wins)
# -----------------------------
HIGH_COMMAND = [
    "Emperor Of Mankind",
    "Primarch",
    "First Captain",
    "Commander",
    "Preator",
]

GREAT_COMPANY = [
    "Marshal",
    "Consulate",
    "Flamewrought",
    "Cindermarked",
    "Pyroclast Sentinel",
]

COMPANY = [
    "Captain",
    "1st Lieutenant",
    "2nd Lieutenant",
    "Veteran Sergeant",
    "Legion Sergeant",
]

SPECIALIST = [
    "Chaplain",
    "Techmarine",
    "Terminator Squad",
    "Apothecarion",
    "Vexillarius",
    "Destroyer",
    "Signal Marine",
]

LEGIONARIES = [
    "Legion Elite",
    "Legion Veteran",
    "Support Squad",
    "Legionary",
    "Inductii",
]

MORTALS = [
    "Emberbrand Proving",
    "Crucible Neophyte",
    "Obsidian Trialborn",
    "Emberbound Initiate",
    "Civitas Aspirant",
]

# Final priority list (lowest -> highest). We'll pick the HIGHEST present.
# This can be overridden by config service
ROLE_PRIORITY: List[str] = (
    MORTALS
    + LEGIONARIES
    + SPECIALIST
    + COMPANY
    + GREAT_COMPANY
    + HIGH_COMMAND
)

# Try to load priority from config service
try:
    from services.config_service import get_config_service
    config_service = get_config_service()
    config_priority = config_service.get_role_priority()
    if config_priority:
        ROLE_PRIORITY = config_priority
except Exception:
    # Use default if config service fails
    pass

# fast membership set
ALL_RANKS_SET = set(ROLE_PRIORITY)

# Nickname prefix pattern like "6. "
PREFIX_RE = re.compile(r"^\d+\.\s*")


def _extract_username_from_nick(nick: Optional[str], role_name: str, fallback: str) -> str:
    """
    Try to derive the Roblox username from nickname:
    - Strip our numeric prefix if present.
    - If nickname starts with the role name, strip it and use the remainder's last token.
    - Otherwise, if multiple tokens, use last token.
    - Fallback to provided fallback (member.name).
    """
    if not nick:
        return fallback

    base = PREFIX_RE.sub("", nick).strip()

    # If it starts with the role name, strip that
    if base.lower().startswith(role_name.lower()):
        rest = base[len(role_name):].strip()
        if rest:
            return rest.split()[-1]

    parts = base.split()
    if len(parts) >= 2:
        return parts[-1]

    return fallback


class RankCog(commands.Cog):
    """
    Apply Salamanders naming format based on designated company per rank:

        "<company>. <rank> <roblox_username>"

    - Company numbers are stored per-rank in MySQL (role_company_map).
    - On role/nickname changes (after Bloxlink /update), Ignis re-applies the format.
    - Admin slash commands to manage the mapping.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -----------------------------
    # DB Pool & Schema
    # -----------------------------
    async def _ensure_table(self):
        pool = get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS role_company_map (
                        role_name VARCHAR(100) PRIMARY KEY,
                        company INT NOT NULL
                    )
                """)

    async def _get_company_for_role(self, role_name: str) -> Optional[int]:
        pool = get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT company FROM role_company_map WHERE role_name = %s",
                    (role_name,)
                )
                row = await cur.fetchone()
                return int(row[0]) if row else None

    async def _set_company_for_role(self, role_name: str, company: int):
        pool = get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO role_company_map (role_name, company)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE company = VALUES(company)
                    """,
                    (role_name, company)
                )

    async def _remove_company_for_role(self, role_name: str):
        pool = get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM role_company_map WHERE role_name = %s",
                    (role_name,)
                )

    async def _list_company_map(self) -> Dict[str, int]:
        pool = get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT role_name, company FROM role_company_map")
                rows = await cur.fetchall()
                return {r: int(c) for (r, c) in rows}

    # -----------------------------
    # Core logic
    # -----------------------------
    def _find_top_rank(self, member: discord.Member) -> Optional[str]:
        """
        Return the highest-priority rank the member has (based on ROLE_PRIORITY),
        or None if none of the known ranks are present.
        """
        names = [r.name for r in member.roles if r.name != "@everyone"]
        present = [n for n in names if n in ALL_RANKS_SET]
        if not present:
            return None
        # sort present by ROLE_PRIORITY index, highest wins
        present.sort(key=lambda n: ROLE_PRIORITY.index(n))
        return present[-1]

    async def _apply_nickname(self, member: discord.Member):
        """
        Apply "<company>. <rank> <username>" if:
        - Member has a known rank
        - That rank has a designated company in the DB
        - Bot has manage_nicknames
        """
        if member.bot:
            return

        guild = member.guild
        me = guild.me or guild.get_member(self.bot.user.id)
        if not me or not me.guild_permissions.manage_nicknames:
            return  # lacking perms

        top_rank = self._find_top_rank(member)
        if not top_rank:
            return

        await self._ensure_table()
        company = await self._get_company_for_role(top_rank)
        if company is None:
            # No mapping yet for this rank; skip silently
            return

        current = member.nick or member.name
        username = _extract_username_from_nick(current, top_rank, fallback=member.name)
        new_nick = f"{company}. {top_rank} {username}"

        # Trim to 32 chars if needed
        if len(new_nick) > 32:
            # try short form: "<company>. <username>"
            short = f"{company}. {username}"
            new_nick = short[:32]

        # If already equivalent (ignoring numeric prefix differences), skip
        base_current = PREFIX_RE.sub("", current or "").strip().lower()
        base_new = PREFIX_RE.sub("", new_nick).strip().lower()
        if base_current == base_new and current == new_nick:
            return

        try:
            await member.edit(nick=new_nick, reason="Ignis: apply designated company format")
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

    # -----------------------------
    # Events: react to Bloxlink /update
    # -----------------------------
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        roles_changed = {r.id for r in before.roles} != {r.id for r in after.roles}
        nick_changed = (before.nick or "") != (after.nick or "")
        if roles_changed or nick_changed:
            await self._apply_nickname(after)

    # -----------------------------
    # Commands
    # -----------------------------
    group = app_commands.Group(
        name="company",
        description="Manage designated company per rank."
    )

    @group.command(name="set", description="Set the designated company for a rank.")
    @app_commands.describe(
        role="Rank role name (must match the Discord role name exactly)",
        company="Company number (integer)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def company_set(self, interaction: discord.Interaction, role: str, company: int):
        await interaction.response.defer(ephemeral=True)
        if role not in ALL_RANKS_SET:
            await interaction.followup.send("❌ Unknown rank. Make sure you typed the exact role name.", ephemeral=True)
            return

        await self._ensure_table()
        await self._set_company_for_role(role, company)
        await interaction.followup.send(f"✅ Set **{role}** → Company **{company}**.", ephemeral=True)

    @group.command(name="get", description="Show the designated company for a rank.")
    @app_commands.describe(role="Rank role name (exact)")
    @app_commands.checks.has_permissions(administrator=True)
    async def company_get(self, interaction: discord.Interaction, role: str):
        await interaction.response.defer(ephemeral=True)
        if role not in ALL_RANKS_SET:
            await interaction.followup.send("❌ Unknown rank.", ephemeral=True)
            return
        await self._ensure_table()
        company = await self._get_company_for_role(role)
        if company is None:
            await interaction.followup.send(f"ℹ️ No company set for **{role}**.", ephemeral=True)
        else:
            await interaction.followup.send(f"📌 **{role}** → Company **{company}**.", ephemeral=True)

    @group.command(name="list", description="List all rank→company mappings.")
    @app_commands.checks.has_permissions(administrator=True)
    async def company_list(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self._ensure_table()
        mapping = await self._list_company_map()
        if not mapping:
            await interaction.followup.send("No mappings set yet.", ephemeral=True)
            return

        # Build a sorted, readable list by role priority
        lines = []
        for role in ROLE_PRIORITY:
            if role in mapping:
                lines.append(f"**{mapping[role]}** — {role}")
        text = "\n".join(lines) if lines else "No mappings set yet."
        embed = discord.Embed(title="Designated Companies", description=text, color=discord.Color.dark_green())
        await interaction.followup.send(embed=embed, ephemeral=True)

    @group.command(name="remove", description="Remove designated company for a rank.")
    @app_commands.describe(role="Rank role name (exact)")
    @app_commands.checks.has_permissions(administrator=True)
    async def company_remove(self, interaction: discord.Interaction, role: str):
        await interaction.response.defer(ephemeral=True)
        if role not in ALL_RANKS_SET:
            await interaction.followup.send("❌ Unknown rank.", ephemeral=True)
            return
        await self._ensure_table()
        await self._remove_company_for_role(role)
        await interaction.followup.send(f"🗑️ Removed mapping for **{role}**.", ephemeral=True)

    @app_commands.command(name="rank_refresh", description="Re-apply Salamanders company prefix to a member's nickname.")
    @app_commands.describe(member="Member to refresh (defaults to yourself)")
    @app_commands.guild_only()
    async def rank_refresh(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        await interaction.response.defer(ephemeral=True, thinking=True)
        target = member or interaction.user
        await self._apply_nickname(target)
        await interaction.followup.send(f"✅ Rank format refreshed for {target.mention}.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RankCog(bot))