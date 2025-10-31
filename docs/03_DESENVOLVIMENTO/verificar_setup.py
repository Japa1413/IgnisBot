#!/usr/bin/env python3
"""
Script de Verificação de Setup - IgnisBot
Verifica se tudo está configurado corretamente antes de executar o bot.
"""

import sys
import os
from pathlib import Path

def verificar_arquivo_env():
    """Verifica se o arquivo .env existe e tem as variáveis necessárias"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado!")
        print("   → Copie env.example para .env: cp env.example .env")
        print("   → Edite .env com suas credenciais")
        return False
    
    # Ler .env e verificar variáveis obrigatórias
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        obrigatorias = [
            "DISCORD_TOKEN",
            "DISCORD_CLIENT_ID", 
            "DISCORD_GUILD_ID",
            "DB_USER",
            "DB_PASSWORD"
        ]
        
        faltando = []
        for var in obrigatorias:
            if not os.getenv(var):
                faltando.append(var)
        
        if faltando:
            print(f"⚠️ Variáveis de ambiente faltando: {', '.join(faltando)}")
            print("   → Configure no arquivo .env")
            return False
        
        print("✅ Arquivo .env configurado corretamente")
        return True
    except ImportError:
        print("⚠️ python-dotenv não instalado")
        print("   → Execute: pip install python-dotenv")
        return False

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    dependencias = {
        "discord": "discord.py",
        "aiomysql": "aiomysql",
        "dotenv": "python-dotenv"
    }
    
    faltando = []
    for modulo, nome in dependencias.items():
        try:
            __import__(modulo)
            print(f"✅ {nome} instalado")
        except ImportError:
            print(f"❌ {nome} NÃO instalado")
            faltando.append(nome)
    
    if faltando:
        print(f"\n⚠️ Instale as dependências faltantes:")
        print(f"   → pip install {' '.join(faltando)}")
        print(f"   → Ou: pip install -r requirements.txt")
        return False
    
    return True

def verificar_estrutura():
    """Verifica se a estrutura de arquivos está correta"""
    arquivos_obrigatorios = [
        "ignis_main.py",
        "utils/config.py",
        "utils/database.py",
        "cogs/data_privacy.py",
        "cogs/legal.py"
    ]
    
    todos_ok = True
    for arquivo in arquivos_obrigatorios:
        if Path(arquivo).exists():
            print(f"✅ {arquivo} existe")
        else:
            print(f"❌ {arquivo} NÃO encontrado")
            todos_ok = False
    
    return todos_ok

def verificar_banco_dados():
    """Tenta conectar ao banco de dados"""
    try:
        from utils.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
        import aiomysql
        import asyncio
        
        async def testar_conexao():
            try:
                conn = await aiomysql.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    db=DB_NAME,
                    connect_timeout=5
                )
                conn.close()
                print("✅ Conexão com banco de dados OK")
                return True
            except Exception as e:
                print(f"❌ Erro ao conectar ao banco: {e}")
                print("   → Verifique se o MySQL está rodando")
                print("   → Verifique as credenciais no .env")
                return False
        
        return asyncio.run(testar_conexao())
    except Exception as e:
        print(f"⚠️ Não foi possível verificar banco de dados: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 VERIFICAÇÃO DE SETUP - IGNISBOT")
    print("=" * 60)
    print()
    
    checks = []
    
    print("📦 Verificando dependências...")
    checks.append(("Dependências", verificar_dependencias()))
    print()
    
    print("📁 Verificando estrutura de arquivos...")
    checks.append(("Estrutura", verificar_estrutura()))
    print()
    
    print("⚙️ Verificando configuração (.env)...")
    checks.append(("Configuração", verificar_arquivo_env()))
    print()
    
    print("💾 Verificando banco de dados...")
    checks.append(("Banco de Dados", verificar_banco_dados()))
    print()
    
    print("=" * 60)
    print("📊 RESULTADO:")
    print("=" * 60)
    
    todos_ok = all(check[1] for check in checks)
    
    for nome, status in checks:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {nome}")
    
    print()
    
    if todos_ok:
        print("🎉 TUDO PRONTO! Você pode executar o bot com:")
        print("   → python ignis_main.py")
    else:
        print("⚠️ ALGUMAS VERIFICAÇÕES FALHARAM")
        print("   → Corrija os problemas acima antes de executar")
    
    print("=" * 60)
    
    return 0 if todos_ok else 1

if __name__ == "__main__":
    sys.exit(main())

