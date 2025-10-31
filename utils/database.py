# utils/database.py
from __future__ import annotations

import asyncio
import aiomysql
from typing import Optional
from utils.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_POOL_MIN, DB_POOL_MAX
from utils.logger import get_logger

logger = get_logger(__name__)

_POOL: Optional[aiomysql.Pool] = None

_CONN_KW = dict(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    db=DB_NAME,
    charset="utf8mb4",
    autocommit=True,
    connect_timeout=5,   # <-- suportado
    # read_timeout / write_timeout NÃO são suportados pelo aiomysql
)

async def initialize_db():
    """Create a global connection pool and ensure tables exist."""
    global _POOL
    if _POOL is None:
        # OPTIMIZAÇÃO FASE 2: Pool configurável via ambiente
        _POOL = await aiomysql.create_pool(
            minsize=DB_POOL_MIN,
            maxsize=DB_POOL_MAX,
            **_CONN_KW
        )
        logger.info(f"Database pool inicializado: {DB_POOL_MIN}-{DB_POOL_MAX} conexões")

    async with _POOL.acquire() as conn:
        async with conn.cursor() as cursor:
            # Tabela principal de usuários
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    points INT DEFAULT 0,
                    `rank` VARCHAR(50) DEFAULT 'Civitas aspirant',
                    progress INT DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de consentimento LGPD
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_consent (
                    user_id BIGINT PRIMARY KEY,
                    consent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    consent_version VARCHAR(20) DEFAULT '1.0',
                    base_legal VARCHAR(50) DEFAULT 'consentimento',
                    consent_given BOOLEAN DEFAULT FALSE,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabela de auditoria de dados pessoais (LGPD Art. 10)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_audit_log (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    action_type VARCHAR(50) NOT NULL,
                    data_type VARCHAR(100) NOT NULL,
                    performed_by BIGINT,
                    purpose TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    details JSON,
                    INDEX idx_user_id (user_id),
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_action_type (action_type)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Índice para otimizar queries de leaderboard (ORDER BY points DESC)
            # Verificar se o índice já existe antes de criar (IF NOT EXISTS não funciona em todas versões MySQL)
            try:
                await cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM information_schema.statistics 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'users' 
                    AND index_name = 'idx_points'
                """)
                result = await cursor.fetchone()
                index_exists = result[0] > 0 if result else False
                
                if not index_exists:
                    await cursor.execute("""
                        CREATE INDEX idx_points 
                        ON users(points DESC)
                    """)
                    logger.info("Índice idx_points criado com sucesso")
                else:
                    logger.debug("Índice idx_points já existe")
            except Exception as e:
                # Se der erro ao verificar/criar índice, apenas logar e continuar
                logger.warning(f"Erro ao criar índice idx_points: {e}. Continuando sem índice.")

async def get_user(user_id: int, use_cache: bool = True):
    """
    Obtém dados do usuário.
    
    Args:
        user_id: ID do usuário
        use_cache: Se True, usa cache com TTL (padrão: True)
    
    Returns:
        Dict com dados do usuário ou None se não encontrado
    
    Raises:
        RuntimeError: Se o pool de banco não estiver inicializado
    """
    # OPTIMIZAÇÃO FASE 2: Usar cache se habilitado
    if use_cache:
        try:
            from utils.cache import get_user_cached
            return await get_user_cached(user_id)
        except ImportError:
            # Cache não disponível, continuar sem cache
            pass
        except Exception as e:
            # Em caso de erro no cache, fazer query direta
            logger = get_logger(__name__) if 'logger' not in dir() else None
            if logger:
                logger.warning(f"Erro no cache, fazendo query direta: {e}")
    
    # Query direta ao banco
    if _POOL is None:
        raise RuntimeError("DB pool not initialized. Call initialize_db() first.")
    async with _POOL.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT user_id, points, `rank`, progress FROM users WHERE user_id = %s",
                (user_id,)
            )
            return await cursor.fetchone()

async def create_user(user_id: int):
    if _POOL is None:
        raise RuntimeError("DB pool not initialized. Call initialize_db() first.")
    async with _POOL.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO users (user_id, points, `rank`) VALUES (%s, 0, 'Civitas aspirant')",
                (user_id,)
            )
    
    # OPTIMIZAÇÃO FASE 2: Invalidar cache (usuário foi criado)
    try:
        from utils.cache import invalidate_user_cache
        invalidate_user_cache(user_id)
    except Exception:
        pass
    
    # OPTIMIZAÇÃO: Auditoria assíncrona (não bloqueia resposta)
    try:
        from utils.audit_log import log_data_operation
        asyncio.create_task(log_data_operation(
            user_id=user_id,
            action_type="CREATE",
            data_type="user_data",
            purpose="Criação de novo registro de usuário"
        ))
    except Exception:
        pass  # Não falhar se auditoria não estiver disponível

async def update_points(user_id: int, points: int, performed_by: int = None, purpose: str = None) -> int:
    """
    Atualiza os pontos do usuário e retorna o novo valor.
    
    Args:
        user_id: ID do usuário
        points: Quantidade de pontos a adicionar/subtrair
        performed_by: ID de quem realizou a ação (opcional)
        purpose: Propósito da atualização (opcional)
    
    Returns:
        Novo valor de points após atualização
    
    Raises:
        RuntimeError: Se o pool não foi inicializado
    """
    if _POOL is None:
        raise RuntimeError("DB pool not initialized. Call initialize_db() first.")
    
    # OPTIMIZAÇÃO FASE 2: Invalidar cache antes de atualizar
    try:
        from utils.cache import invalidate_user_cache
        invalidate_user_cache(user_id)
    except Exception:
        pass
    
    async with _POOL.acquire() as conn:
        async with conn.cursor() as cursor:
            # Atualizar pontos
            await cursor.execute(
                "UPDATE users SET points = points + %s WHERE user_id = %s",
                (points, user_id)
            )
            
            # Buscar novo valor na mesma conexão (otimizado)
            await cursor.execute(
                "SELECT points FROM users WHERE user_id = %s",
                (user_id,)
            )
            result = await cursor.fetchone()
            new_points = int(result[0]) if result else 0
    
    # OPTIMIZAÇÃO: Auditoria assíncrona (não bloqueia resposta)
    try:
        from utils.audit_log import log_data_operation
        asyncio.create_task(log_data_operation(
            user_id=user_id,
            action_type="UPDATE",
            data_type="points",
            performed_by=performed_by,
            purpose=purpose or f"Atualização de pontos: {'+' if points > 0 else ''}{points}"
        ))
    except Exception:
        pass  # Não falhar se auditoria não estiver disponível
    
    return new_points

async def ensure_user_exists(user_id: int):
    """Garante que o usuário existe no banco, criando se necessário"""
    # Usar cache=false para garantir verificação precisa
    if not await get_user(user_id, use_cache=False):
        await create_user(user_id)

def get_pool():
    """
    Obtém o pool de conexões do banco de dados.
    
    Returns:
        aiomysql.Pool ou None se não inicializado
    
    Raises:
        RuntimeError: Se o pool não foi inicializado
    """
    if _POOL is None:
        raise RuntimeError("DB pool not initialized. Call initialize_db() first.")
    return _POOL