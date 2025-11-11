"""
Configuração do IgnisBot - Carregamento de Variáveis de Ambiente

⚠️ ATENÇÃO: CREDENCIAIS REMOVIDAS POR SEGURANÇA
Este arquivo agora carrega configurações de variáveis de ambiente.
Configure o arquivo .env com suas credenciais antes de executar o bot.

IMPORTANTE:
- NUNCA faça commit do arquivo .env
- Revogue as credenciais antigas que estavam hardcoded aqui
- Use o arquivo env.example como template
"""

import os
from typing import Optional
from pathlib import Path

# Carregar variáveis de ambiente do arquivo .env se existir
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # dotenv não instalado, tentar usar variáveis do sistema
    pass


def _get_env(key: str, default: Optional[str] = None, required: bool = True) -> str:
    """
    Obtém variável de ambiente com validação.
    
    Args:
        key: Nome da variável de ambiente
        default: Valor padrão se não encontrado
        required: Se True, levanta erro se variável não encontrada
    
    Returns:
        Valor da variável de ambiente
    
    Raises:
        ValueError: Se required=True e variável não encontrada
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(
            f"❌ Variável de ambiente '{key}' não configurada!\n"
            f"Configure no arquivo .env ou como variável de sistema.\n"
            f"Veja env.example para referência."
        )
    return value


# ============================================
# DISCORD CONFIGURATION
# ============================================
TOKEN = _get_env("DISCORD_TOKEN", required=True)
CLIENT_ID = _get_env("DISCORD_CLIENT_ID", required=True)
GUILD_ID = int(_get_env("DISCORD_GUILD_ID", required=True))

# ============================================
# DATABASE CONFIGURATION
# ============================================
DB_HOST = _get_env("DB_HOST", default="localhost")
DB_USER = _get_env("DB_USER", required=True)
DB_PASSWORD = _get_env("DB_PASSWORD", required=True)
DB_NAME = _get_env("DB_NAME", default="ignis")
DB_PORT = int(_get_env("DB_PORT", default="3306"))

# OPTIMIZAÇÃO FASE 2: Pool de conexões configurável
DB_POOL_MIN = int(_get_env("DB_POOL_MIN", default="2"))
DB_POOL_MAX = int(_get_env("DB_POOL_MAX", default="10"))

# ============================================
# CHANNEL IDs (Configuráveis via ambiente)
# ============================================
VC_CHANNEL_ID = int(_get_env("VC_CHANNEL_IDS", default="1375977001617199216"))
# Todos os comandos restritos agora usam o mesmo canal
# Se o usuário quiser usar o canal servitor-terminal, configure no .env:
# STAFF_CMDS_CHANNEL_ID=1375941286267326530
STAFF_CMDS_CHANNEL_ID = int(_get_env("STAFF_CMDS_CHANNEL_ID", default="1375941286267326530"))
USERINFO_CHANNEL_ID = int(_get_env("USERINFO_CHANNEL_ID", default="1375941286267326530"))
SUMMARY_CHANNEL_FALLBACK_ID = int(_get_env("SUMMARY_CHANNEL_FALLBACK_ID", default="1375807338094530753"))

# Allowed Voice Channel IDs (parse de string separada por vírgula)
_allowed_vc_str = _get_env("ALLOWED_VC_IDS", default="")
ALLOWED_VC_IDS = {
    int(cid.strip()) for cid in _allowed_vc_str.split(",") if cid.strip()
} if _allowed_vc_str else {
    1386490773431783434,
    1375941286267326524,
    1375941286267326525,
    1375941286267326526,
    1375941286267326527,
}

# ============================================
# LOGGING CONFIGURATION
# ============================================
LOG_LEVEL = _get_env("LOG_LEVEL", default="INFO")
LOG_FILE = _get_env("LOG_FILE", default="logs/ignisbot.log")
LOG_MAX_SIZE = int(_get_env("LOG_MAX_SIZE", default="10485760"))
LOG_BACKUP_COUNT = int(_get_env("LOG_BACKUP_COUNT", default="5"))

# ============================================
# PRIVACY & COMPLIANCE
# ============================================
PRIVACY_POLICY_URL = _get_env("PRIVACY_POLICY_URL", default="")
TERMS_OF_USE_URL = _get_env("TERMS_OF_USE_URL", default="")
CONTROLLER_EMAIL = _get_env("CONTROLLER_EMAIL", default="")

# ============================================
# SECURITY
# ============================================
ENABLE_RATE_LIMITING = _get_env("ENABLE_RATE_LIMITING", default="true").lower() == "true"
RATE_LIMIT_REQUESTS_PER_MINUTE = int(_get_env("RATE_LIMIT_REQUESTS_PER_MINUTE", default="60"))

# ============================================
# ROBLOX CONFIGURATION
# ============================================
ROBLOX_COOKIE = _get_env("ROBLOX_COOKIE", default="", required=False)  # Required for group operations

# ============================================
# APPLICATION
# ============================================
APP_ENV = _get_env("APP_ENV", default="production")
DEBUG = _get_env("DEBUG", default="false").lower() == "true"