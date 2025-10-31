# cogs/legal.py
"""
Cog de Documentos Legais

Exibe Política de Privacidade, Termos de Uso e outras documentações legais.
"""

from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands

from utils.config import PRIVACY_POLICY_URL, TERMS_OF_USE_URL, CONTROLLER_EMAIL
from pathlib import Path
from utils.consent_manager import check_consent_required, give_consent


class LegalCog(commands.Cog):
    """Cog para exibição de documentos legais"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(
        name="privacy",
        description="Display IgnisBot Privacy Policy"
    )
    async def privacy(self, interaction: discord.Interaction):
        """Exibe informações sobre a Política de Privacidade"""
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title="🔒 Privacy Policy - IgnisBot",
            description=(
                "**LGPD Compliance (Brazilian General Data Protection Law)**\n\n"
                "IgnisBot complies with the Brazilian General Data Protection Law (LGPD - Law No. 13.709/2018).\n\n"
                "**Data Collected:**\n"
                "• Discord ID (user_id)\n"
                "• Points and system progress\n"
                "• Rank/classification\n"
                "• Bot usage information (command logs)\n\n"
                "**Purpose:**\n"
                "Data is collected to provide gamification and ranking features within the Discord server.\n\n"
                "**Your Rights (LGPD Art. 18):**\n"
                "• Access your data (`/export_my_data`)\n"
                "• Correct incomplete data\n"
                "• Request deletion (`/delete_my_data`)\n"
                "• Revoke consent (`/consent revoke`)\n\n"
                "**Contact:**\n"
                f"For privacy inquiries: {CONTROLLER_EMAIL if CONTROLLER_EMAIL else 'Configure CONTROLLER_EMAIL in .env'}\n\n"
                f"📄 **Full Version:** {PRIVACY_POLICY_URL if PRIVACY_POLICY_URL else 'Full document under development'}"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Last updated: 2025-10-31 | Version 1.0")
        
        # Check if consent is required
        needs_consent = await check_consent_required(interaction.user.id)
        if needs_consent:
            embed.add_field(
                name="⚠️ Consent Required",
                value=(
                    "You need to grant consent to use the bot.\n"
                    "Use `/consent grant` after reading the policy."
                ),
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(
        name="terms",
        description="Display IgnisBot Terms of Use"
    )
    async def terms(self, interaction: discord.Interaction):
        """Exibe os Termos de Uso"""
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title="📋 Terms of Use - IgnisBot",
            description=(
                "**By using IgnisBot, you agree to:**\n\n"
                "**1. Service Usage**\n"
                "• The bot is provided 'as is', without warranties\n"
                "• You are responsible for proper use of the bot\n"
                "• Inappropriate use may result in a ban\n\n"
                "**2. Personal Data**\n"
                "• Your data is processed according to the Privacy Policy\n"
                "• You have rights guaranteed by LGPD\n"
                "• Use `/privacy` for more information\n\n"
                "**3. Limitations**\n"
                "• Service may be interrupted for maintenance\n"
                "• No 24/7 availability guarantee\n"
                "• Data may be lost in case of critical failure\n\n"
                "**4. Intellectual Property**\n"
                "• The bot's source code is property of its developers\n"
                "• Unauthorized reproduction is not allowed\n\n"
                f"📄 **Full Version:** {TERMS_OF_USE_URL if TERMS_OF_USE_URL else 'See: docs/TERMS_USO.md in repository'}"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Last updated: 2025-10-31 | Version 1.0")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(
        name="sla",
        description="Display Service Level Agreement (SLA) information"
    )
    async def sla(self, interaction: discord.Interaction):
        """Exibe informações sobre disponibilidade e suporte"""
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title="📊 Service Level Agreement (SLA) - IgnisBot",
            description=(
                "**Availability and Support Commitments**\n\n"
                "**🎯 Availability:**\n"
                "• Target: 99% monthly uptime\n"
                "• Maximum downtime: 7.2 hours/month\n"
                "• Current status: Standard Level\n\n"
                "**⚡ Performance:**\n"
                "• Simple commands: ≤ 2 seconds\n"
                "• Database commands: ≤ 5 seconds\n"
                "• Complex commands: ≤ 10 seconds\n\n"
                "**🛠️ Support:**\n"
                "• Critical (bot offline): 4 hours\n"
                "• High (essential error): 24 hours\n"
                "• Medium (bug): 72 hours\n"
                "• Low (suggestion): 1 week\n\n"
                "**💾 Backup:**\n"
                "• Database: Daily (7-day retention)\n"
                "• Audit logs: 6 months (LGPD)\n"
                "• RTO: ≤ 4 hours | RPO: 24 hours\n\n"
                f"📄 **Full Document:** See `docs/SLA.md` in repository"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Last updated: 2025-10-31 | Version 1.0")
        
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(LegalCog(bot))

