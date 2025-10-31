# utils/consent_manager.py
"""
Gerenciador de Consentimento LGPD

Gerencia consentimento de usuários para processamento de dados pessoais,
conforme requisitos da LGPD (Art. 7º, I) e GDPR (Art. 6º, 1(a)).
"""

from __future__ import annotations

from typing import Optional, Dict
from datetime import datetime
import aiomysql
from utils.database import get_pool

# Versão atual da política de privacidade
CURRENT_CONSENT_VERSION = "1.0"

# Base legal padrão (pode ser alterada conforme necessário)
DEFAULT_BASE_LEGAL = "consentimento"  # LGPD Art. 7º, I


async def has_consent(user_id: int) -> bool:
    """
    Verifica se o usuário deu consentimento para processamento de dados.
    
    Args:
        user_id: ID do usuário
    
    Returns:
        True se o usuário deu consentimento, False caso contrário
    
    Raises:
        RuntimeError: Se o pool de banco não estiver inicializado
    """
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("""
                SELECT consent_given
                FROM user_consent
                WHERE user_id = %s
            """, (user_id,))
            
            result = await cursor.fetchone()
            return result and result.get("consent_given", False)


async def give_consent(
    user_id: int,
    base_legal: str = DEFAULT_BASE_LEGAL,
    version: str = CURRENT_CONSENT_VERSION
) -> bool:
    """
    Registra consentimento do usuário para processamento de dados.
    
    Args:
        user_id: ID do usuário
        base_legal: Base legal para processamento (padrão: "consentimento")
        version: Versão da política de privacidade aceita
    
    Returns:
        True se o consentimento foi registrado com sucesso
    
    Raises:
        RuntimeError: Se o pool de banco não estiver inicializado
    """
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # Usar INSERT ... ON DUPLICATE KEY UPDATE para upsert
            await cursor.execute("""
                INSERT INTO user_consent 
                (user_id, consent_date, consent_version, base_legal, consent_given)
                VALUES (%s, NOW(), %s, %s, TRUE)
                ON DUPLICATE KEY UPDATE
                    consent_date = NOW(),
                    consent_version = %s,
                    base_legal = %s,
                    consent_given = TRUE,
                    updated_at = NOW()
            """, (user_id, version, base_legal, version, base_legal))
            
            return True


async def revoke_consent(user_id: int) -> bool:
    """
    Revoga o consentimento do usuário (LGPD Art. 18, VI).
    
    Quando o consentimento é revogado, os dados ainda podem ser mantidos
    se houver outra base legal aplicável (ex: cumprimento de obrigação legal).
    A exclusão completa deve ser feita via delete_user_data().
    
    Args:
        user_id: ID do usuário
    
    Returns:
        True se o consentimento foi revogado com sucesso
    
    Raises:
        RuntimeError: Se o pool de banco não estiver inicializado
    """
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                UPDATE user_consent
                SET consent_given = FALSE,
                    updated_at = NOW()
                WHERE user_id = %s
            """, (user_id,))
            
            return cursor.rowcount > 0


async def get_consent_info(user_id: int) -> Optional[Dict]:
    """
    Obtém informações sobre o consentimento do usuário.
    
    Args:
        user_id: ID do usuário
    
    Returns:
        Dict com informações de consentimento ou None se não encontrado
    
    Raises:
        RuntimeError: Se o pool de banco não estiver inicializado
    """
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("""
                SELECT 
                    user_id,
                    consent_date,
                    consent_version,
                    base_legal,
                    consent_given,
                    updated_at
                FROM user_consent
                WHERE user_id = %s
            """, (user_id,))
            
            return await cursor.fetchone()


async def check_consent_required(user_id: int) -> bool:
    """
    Verifica se o usuário precisa dar consentimento.
    
    Retorna True se:
    - O usuário não tem registro de consentimento, OU
    - O consentimento foi dado em versão antiga da política
    
    Args:
        user_id: ID do usuário
    
    Returns:
        True se o consentimento é necessário
    """
    consent_info = await get_consent_info(user_id)
    
    if not consent_info:
        return True  # Sem registro = precisa dar consentimento
    
    if not consent_info.get("consent_given", False):
        return True  # Consentimento revogado
    
    # Verificar se a versão do consentimento está atualizada
    consent_version = consent_info.get("consent_version", "0.0")
    return consent_version != CURRENT_CONSENT_VERSION

