# utils/audit_log.py
"""
Sistema de Auditoria de Dados Pessoais (LGPD Art. 10)

Registra todas as operações realizadas com dados pessoais para conformidade legal.
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from datetime import datetime
import json
import aiomysql
from utils.database import get_pool


async def log_data_operation(
    user_id: int,
    action_type: str,
    data_type: str,
    performed_by: Optional[int] = None,
    purpose: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Registra uma operação com dados pessoais no banco de dados.
    
    Tipos de ação:
        - CREATE: Criação de registro
        - READ: Leitura de dados
        - UPDATE: Atualização de dados
        - DELETE: Exclusão de dados
        - EXPORT: Exportação de dados
        - ACCESS: Acesso geral aos dados
    
    Args:
        user_id: ID do usuário cujos dados foram manipulados
        action_type: Tipo de ação realizada
        data_type: Tipo de dado (user_data, points, rank, consent, etc.)
        performed_by: ID do usuário/admin que realizou a ação (None = próprio usuário)
        purpose: Finalidade da operação (ex: "Atualização de pontos por evento")
        details: Detalhes adicionais em formato dict (será serializado como JSON)
    
    Raises:
        RuntimeError: Se o pool de banco não estiver inicializado
    """
    pool = get_pool()
    
    details_json = json.dumps(details) if details else None
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO data_audit_log 
                (user_id, action_type, data_type, performed_by, purpose, details, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (
                user_id,
                action_type,
                data_type,
                performed_by,
                purpose,
                details_json
            ))


async def get_user_audit_history(
    user_id: int,
    limit: int = 100
) -> list[Dict[str, Any]]:
    """
    Obtém o histórico de auditoria de um usuário.
    
    Args:
        user_id: ID do usuário
        limit: Número máximo de registros a retornar
    
    Returns:
        Lista de registros de auditoria ordenados por timestamp (mais recente primeiro)
    
    Raises:
        RuntimeError: Se o pool de banco não estiver inicializado
    """
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("""
                SELECT 
                    id,
                    user_id,
                    action_type,
                    data_type,
                    performed_by,
                    purpose,
                    timestamp,
                    details
                FROM data_audit_log
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """, (user_id, limit))
            
            results = await cursor.fetchall()
            
            # Parse JSON details
            for record in results:
                if record.get("details"):
                    try:
                        record["details"] = json.loads(record["details"])
                    except (json.JSONDecodeError, TypeError):
                        record["details"] = {}
            
            return results


async def delete_user_audit_logs(user_id: int) -> int:
    """
    Remove todos os logs de auditoria de um usuário (usado quando usuário exerce direito ao esquecimento).
    
    Args:
        user_id: ID do usuário
    
    Returns:
        Número de registros deletados
    
    Raises:
        RuntimeError: Se o pool de banco não estiver inicializado
    """
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM data_audit_log
                WHERE user_id = %s
            """, (user_id,))
            
            return cursor.rowcount

