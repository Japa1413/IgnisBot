# cogs/data_privacy.py
"""
Cog de Privacidade de Dados - Conformidade LGPD/GDPR

Implementa comandos para exercício de direitos dos titulares de dados:
- /export_my_data: Exportar dados pessoais (LGPD Art. 18, II e V)
- /delete_my_data: Exercer direito ao esquecimento (LGPD Art. 18, VI)
- /consent: Gerenciar consentimento para processamento de dados
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands

from utils.database import get_user, get_pool
from utils.consent_manager import (
    has_consent,
    give_consent,
    revoke_consent,
    get_consent_info,
    check_consent_required
)
from utils.audit_log import (
    log_data_operation,
    get_user_audit_history,
    delete_user_audit_logs
)
from utils.logger import get_logger, log_data_access

logger = get_logger(__name__)


class DataPrivacyCog(commands.Cog):
    """Cog para gerenciamento de privacidade de dados (LGPD/GDPR)"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(
        name="export_my_data",
        description="Export your stored personal data (LGPD Art. 18, II and V)"
    )
    async def export_my_data(self, interaction: discord.Interaction):
        """
        Exporta todos os dados pessoais do usuário em formato JSON.
        Atende aos direitos de acesso e portabilidade (LGPD Art. 18, II e V).
        """
        await interaction.response.defer(ephemeral=True)
        
        user_id = interaction.user.id
        
        try:
            # Registrar acesso
            await log_data_operation(
                user_id=user_id,
                action_type="EXPORT",
                data_type="user_data",
                performed_by=user_id,
                purpose="Exercise of access and portability rights (LGPD Art. 18, II and V)"
            )
            log_data_access(user_id, "EXPORT", "user_data", user_id, "Access rights")
            
            # Coletar dados do usuário
            user_data = await get_user(user_id)
            consent_info = await get_consent_info(user_id)
            audit_history = await get_user_audit_history(user_id, limit=50)
            
            # Montar dados exportáveis
            export_data = {
                "export_date": datetime.utcnow().isoformat(),
                "user_id": str(user_id),
                "discord_username": interaction.user.name,
                "discord_display_name": interaction.user.display_name,
                "discord_account_created": interaction.user.created_at.isoformat() if interaction.user.created_at else None,
                "user_data": {
                    "points": user_data.get("points", 0) if user_data else 0,
                    "rank": user_data.get("rank", "Civitas aspirant") if user_data else "Civitas aspirant",
                    "progress": user_data.get("progress", 0) if user_data else 0,
                    "created_at": user_data.get("created_at").isoformat() if user_data and user_data.get("created_at") else None,
                    "updated_at": user_data.get("updated_at").isoformat() if user_data and user_data.get("updated_at") else None,
                } if user_data else {},
                "consent_info": consent_info if consent_info else None,
                "audit_history": audit_history[:50] if audit_history else []
            }
            
            # Criar arquivo JSON
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
            
            # Enviar como arquivo
            file = discord.File(
                fp=json_data.encode('utf-8'),
                filename=f"ignisbot_data_export_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            embed = discord.Embed(
                title="📥 Personal Data Export",
                description="Your data has been successfully exported in accordance with LGPD Art. 18, II and V.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="📋 Included Data",
                value="• User data (points, rank, progress)\n• Consent information\n• Audit history (last 50 records)",
                inline=False
            )
            embed.add_field(
                name="📅 Export Date",
                value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
                inline=False
            )
            embed.set_footer(text="This file contains sensitive personal data. Keep it secure.")
            
            await interaction.followup.send(embed=embed, file=file, ephemeral=True)
            logger.info(f"User {user_id} exported their data")
            
        except Exception as e:
            logger.error(f"Error exporting data for user {user_id}: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Error exporting your data. Please contact support.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="delete_my_data",
        description="Exercise your right to be forgotten - deletes ALL your data (LGPD Art. 18, VI)"
    )
    async def delete_my_data(self, interaction: discord.Interaction):
        """
        Permite ao usuário exercer seu direito ao esquecimento (LGPD Art. 18, VI).
        ATENÇÃO: Esta ação é IRREVERSÍVEL.
        """
        await interaction.response.defer(ephemeral=True)
        
        user_id = interaction.user.id
        
        # Criar view de confirmação
        view = ConfirmDeleteView(user_id, self)
        
        embed = discord.Embed(
            title="⚠️ Data Deletion Confirmation",
            description=(
                "You are about to exercise your **right to be forgotten** (LGPD Art. 18, VI).\n\n"
                "**This action is IRREVERSIBLE and will:**\n"
                "• Delete all your personal data (points, rank, progress)\n"
                "• Delete consent information\n"
                "• Delete audit history\n\n"
                "**Are you sure?**"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="This action cannot be undone.")
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    async def execute_delete(self, user_id: int, interaction: discord.Interaction):
        """Executa a exclusão de dados após confirmação"""
        try:
            pool = get_pool()
            
            # Registrar operação ANTES de deletar
            await log_data_operation(
                user_id=user_id,
                action_type="DELETE",
                data_type="all_user_data",
                performed_by=user_id,
                purpose="Exercise of right to be forgotten (LGPD Art. 18, VI)"
            )
            
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Delete user data (CASCADE will delete consent and audit_log)
                    await cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                    
                    deleted_rows = cursor.rowcount
            
            log_data_access(user_id, "DELETE", "all_user_data", user_id, "Right to be forgotten")
            
            embed = discord.Embed(
                title="✅ Data Deleted",
                description=(
                    f"All your personal data has been successfully deleted.\n\n"
                    f"**Records deleted:** {deleted_rows}\n\n"
                    "Your right to be forgotten has been exercised in accordance with LGPD Art. 18, VI."
                ),
                color=discord.Color.green()
            )
            embed.set_footer(text="Thank you for using IgnisBot!")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"User {user_id} deleted all their data (right to be forgotten)")
            
        except Exception as e:
            logger.error(f"Error deleting data for user {user_id}: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Error deleting your data. Please contact support.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="consent",
        description="Manage consent for personal data processing"
    )
    @app_commands.describe(
        action="Action to perform"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Status - Check current status", value="status"),
        app_commands.Choice(name="Grant - Grant consent", value="grant"),
        app_commands.Choice(name="Revoke - Revoke consent", value="revoke"),
    ])
    async def consent(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str] = None
    ):
        """
        Gerencia consentimento para processamento de dados pessoais (LGPD Art. 7º, I).
        
        Ações disponíveis:
        - grant: Conceder consentimento
        - revoke: Revogar consentimento
        - status: Verificar status atual
        """
        await interaction.response.defer(ephemeral=True)
        
        user_id = interaction.user.id
        
        try:
            action_value = action.value if hasattr(action, 'value') else (action if isinstance(action, str) else "status")
            
            if action_value == "grant":
                await give_consent(user_id)
                await log_data_operation(
                    user_id=user_id,
                    action_type="UPDATE",
                    data_type="consent",
                    performed_by=user_id,
                    purpose="Consent granted by user"
                )
                
                embed = discord.Embed(
                    title="✅ Consent Granted",
                    description="Your consent for data processing has been recorded.",
                    color=discord.Color.green()
                )
                
            elif action_value == "revoke":
                await revoke_consent(user_id)
                await log_data_operation(
                    user_id=user_id,
                    action_type="UPDATE",
                    data_type="consent",
                    performed_by=user_id,
                    purpose="Consent revoked by user"
                )
                
                embed = discord.Embed(
                    title="⚠️ Consent Revoked",
                    description=(
                        "Your consent has been revoked.\n\n"
                        "**Note:** Some data may be retained if there is another applicable legal basis."
                    ),
                    color=discord.Color.orange()
                )
                
            else:  # status
                consent_info = await get_consent_info(user_id)
                has_consent_val = await has_consent(user_id)
                
                if consent_info:
                    embed = discord.Embed(
                        title="📋 Consent Status",
                        color=discord.Color.blue()
                    )
                    embed.add_field(
                        name="Status",
                        value="✅ Active" if has_consent_val else "❌ Revoked",
                        inline=False
                    )
                    embed.add_field(
                        name="Consent Date",
                        value=f"<t:{int(consent_info['consent_date'].timestamp())}:F>" if consent_info.get("consent_date") else "N/A",
                        inline=True
                    )
                    embed.add_field(
                        name="Policy Version",
                        value=consent_info.get("consent_version", "N/A"),
                        inline=True
                    )
                    embed.add_field(
                        name="Legal Basis",
                        value=consent_info.get("base_legal", "N/A"),
                        inline=False
                    )
                else:
                    embed = discord.Embed(
                        title="❌ Consent Not Registered",
                        description="You have not yet granted consent for data processing.",
                        color=discord.Color.orange()
                    )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"User {user_id} checked/updated consent: {action}")
            
        except Exception as e:
            logger.error(f"Error managing consent for user {user_id}: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Error processing consent request.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="correct_my_data",
        description="Request correction of incorrect data (LGPD Art. 18, III)"
    )
    @app_commands.describe(
        field="Field to correct (points, rank, etc.)",
        current_value="Current value (optional)",
        correct_value="Desired correct value",
        reason="Reason for correction"
    )
    async def correct_my_data(
        self,
        interaction: discord.Interaction,
        field: str,
        correct_value: str,
        current_value: str | None = None,
        reason: str | None = None
    ):
        """
        Permite ao usuário solicitar correção de dados incorretos (LGPD Art. 18, III).
        
        A solicitação será registrada e um administrador revisará e aprovará.
        """
        await interaction.response.defer(ephemeral=True)
        
        user_id = interaction.user.id
        
        # Validar campo
        allowed_fields = ["points", "rank", "progress"]
        if field.lower() not in allowed_fields:
            await interaction.followup.send(
                f"❌ Invalid field. Allowed fields: {', '.join(allowed_fields)}",
                ephemeral=True
            )
            return
        
        try:
            # Registrar solicitação em audit log
            await log_data_operation(
                user_id=user_id,
                action_type="REQUEST",
                data_type=f"correction_{field}",
                performed_by=user_id,
                purpose="Data correction request (LGPD Art. 18, III)",
                details={
                    "field": field,
                    "current_value": current_value,
                    "correct_value": correct_value,
                    "reason": reason,
                    "status": "pending_review"
                }
            )
            
            # Buscar canal de administração (ou criar sistema de tickets)
            embed = discord.Embed(
                title="📝 Data Correction Request",
                description=(
                    "Your correction request has been recorded in accordance with LGPD Art. 18, III.\n\n"
                    "**Request:**\n"
                    f"• Field: `{field}`\n"
                    f"• Current value: `{current_value or 'Not provided'}`\n"
                    f"• Correct value: `{correct_value}`\n"
                    f"• Reason: `{reason or 'Not provided'}`\n\n"
                    "**Next Steps:**\n"
                    "An administrator will review your request shortly. "
                    "You will be notified when the correction is approved or denied."
                ),
                color=discord.Color.blue()
            )
            embed.set_footer(text="LGPD Art. 18, III - Right to Rectification")
            embed.timestamp = discord.utils.utcnow()
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Nota: Aqui você pode implementar um sistema de tickets/notificação para admins
            # Por enquanto, apenas registra no audit log
            logger.info(
                f"User {user_id} requested correction of field {field}: "
                f"{current_value} -> {correct_value}"
            )
            
            log_data_access(
                user_id, "REQUEST", f"correction_{field}", user_id,
                "Solicitação de correção de dados"
            )
            
        except Exception as e:
            logger.error(f"Error processing correction request for user {user_id}: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Error processing correction request. "
                "Please contact support.",
                ephemeral=True
            )


class ConfirmDeleteView(discord.ui.View):
    """View de confirmação para exclusão de dados"""
    
    def __init__(self, user_id: int, cog: DataPrivacyCog):
        super().__init__(timeout=300)  # 5 minutos
        self.user_id = user_id
        self.cog = cog
        self.confirmed = False
    
    @discord.ui.button(label="Yes, Delete Everything", style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Only the requester can confirm this action.",
                ephemeral=True
            )
            return
        
        self.confirmed = True
        self.stop()
        
        await self.cog.execute_delete(self.user_id, interaction)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Only the requester can cancel this action.",
                ephemeral=True
            )
            return
        
        self.confirmed = False
        self.stop()
        
        embed = discord.Embed(
            title="✅ Operation Cancelled",
            description="Data deletion has been cancelled. Your data remains safe.",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=None)


async def setup(bot: commands.Bot):
    await bot.add_cog(DataPrivacyCog(bot))

