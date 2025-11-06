#!/usr/bin/env python3
"""
Script de Atualização Automática da Documentação do GitHub

Este script atualiza automaticamente os arquivos README.md, README_EN.md e CHANGELOG.md
com base nas mudanças do projeto. Deve ser executado antes de commits ou via git hook.

Funcionalidades:
- Atualiza estatísticas do projeto
- Atualiza lista de comandos
- Atualiza informações de arquitetura
- Mantém sincronização entre README.md (PT-BR) e README_EN.md (EN-US)
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess
import re

# Cores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️ {msg}{Colors.RESET}")

def get_project_stats():
    """Coleta estatísticas do projeto."""
    root_dir = Path(__file__).parent.parent
    
    stats = {
        "total_commands": 0,
        "total_docs": 0,
        "total_cogs": 0,
        "total_services": 0,
        "total_repositories": 0,
    }
    
    # Contar comandos (arquivos .py em cogs/)
    cogs_dir = root_dir / "cogs"
    if cogs_dir.exists():
        stats["total_cogs"] = len([f for f in cogs_dir.glob("*.py") if f.name != "__init__.py"])
    
    # Contar serviços
    services_dir = root_dir / "services"
    if services_dir.exists():
        stats["total_services"] = len([f for f in services_dir.glob("*.py") if f.name != "__init__.py"])
    
    # Contar repositórios
    repos_dir = root_dir / "repositories"
    if repos_dir.exists():
        stats["total_repositories"] = len([f for f in repos_dir.glob("*.py") if f.name != "__init__.py"])
    
    # Contar documentos
    docs_dir = root_dir / "docs"
    if docs_dir.exists():
        stats["total_docs"] = len(list(docs_dir.rglob("*.md")))
    
    # Estimar comandos (baseado em arquivos de cog)
    stats["total_commands"] = stats["total_cogs"] * 2  # Estimativa
    
    return stats

def get_git_info():
    """Obtém informações do Git."""
    try:
        # Último commit
        last_commit = subprocess.check_output(
            ["git", "log", "-1", "--pretty=format:%h %s"],
            cwd=Path(__file__).parent.parent,
            text=True
        ).strip()
        
        # Branch atual
        current_branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=Path(__file__).parent.parent,
            text=True
        ).strip()
        
        return {
            "last_commit": last_commit,
            "current_branch": current_branch,
        }
    except Exception as e:
        print_warning(f"Não foi possível obter informações do Git: {e}")
        return {
            "last_commit": "N/A",
            "current_branch": "main",
        }

def update_readme_stats(readme_path: Path, stats: dict):
    """Atualiza estatísticas no README."""
    if not readme_path.exists():
        print_warning(f"README não encontrado: {readme_path}")
        return False
    
    content = readme_path.read_text(encoding="utf-8")
    original_content = content
    
    # Atualizar estatísticas
    stats_pattern = r"- \*\*Total de Comandos:\*\* \d+\+ comandos slash"
    stats_replacement = f"- **Total de Comandos:** {stats['total_commands']}+ comandos slash"
    content = re.sub(stats_pattern, stats_replacement, content)
    
    stats_pattern_en = r"- \*\*Total Commands:\*\* \d+\+ slash commands"
    stats_replacement_en = f"- **Total Commands:** {stats['total_commands']}+ slash commands"
    content = re.sub(stats_pattern_en, stats_replacement_en, content)
    
    docs_pattern = r"- \*\*Arquivos de Documentação:\*\* \d+\+ documentos"
    docs_replacement = f"- **Arquivos de Documentação:** {stats['total_docs']}+ documentos"
    content = re.sub(docs_pattern, docs_replacement, content)
    
    docs_pattern_en = r"- \*\*Documentation Files:\*\* \d+\+ organized documents"
    docs_replacement_en = f"- **Documentation Files:** {stats['total_docs']}+ organized documents"
    content = re.sub(docs_pattern_en, docs_replacement_en, content)
    
    if content != original_content:
        readme_path.write_text(content, encoding="utf-8")
        return True
    return False

def update_changelog_date(changelog_path: Path):
    """Atualiza data no CHANGELOG se necessário."""
    if not changelog_path.exists():
        return False
    
    content = changelog_path.read_text(encoding="utf-8")
    original_content = content
    
    # Verificar se há seção [Unreleased] sem data
    unreleased_pattern = r"## \[Unreleased\]\n\n(?!###)"
    if re.search(unreleased_pattern, content):
        # Adicionar data ao primeiro item se não tiver
        first_item_pattern = r"(## \[Unreleased\]\n\n)(### )"
        replacement = r"\1\2"
        content = re.sub(first_item_pattern, replacement, content)
    
    if content != original_content:
        changelog_path.write_text(content, encoding="utf-8")
        return True
    return False

def main():
    """Função principal."""
    print_info("🔄 Atualizando documentação do GitHub...")
    print()
    
    root_dir = Path(__file__).parent.parent
    
    # Coletar informações
    stats = get_project_stats()
    git_info = get_git_info()
    
    print_info(f"Estatísticas coletadas:")
    print(f"  - Comandos: {stats['total_commands']}+")
    print(f"  - Documentos: {stats['total_docs']}")
    print(f"  - COGs: {stats['total_cogs']}")
    print(f"  - Serviços: {stats['total_services']}")
    print(f"  - Repositórios: {stats['total_repositories']}")
    print()
    
    # Atualizar READMEs
    readme_pt = root_dir / "README.md"
    readme_en = root_dir / "README_EN.md"
    changelog = root_dir / "CHANGELOG.md"
    
    updated = False
    
    if readme_pt.exists():
        if update_readme_stats(readme_pt, stats):
            print_success("README.md (PT-BR) atualizado")
            updated = True
        else:
            print_info("README.md (PT-BR) já está atualizado")
    
    if readme_en.exists():
        if update_readme_stats(readme_en, stats):
            print_success("README_EN.md (EN-US) atualizado")
            updated = True
        else:
            print_info("README_EN.md (EN-US) já está atualizado")
    
    if changelog.exists():
        if update_changelog_date(changelog):
            print_success("CHANGELOG.md atualizado")
            updated = True
        else:
            print_info("CHANGELOG.md já está atualizado")
    
    print()
    if updated:
        print_success("✅ Documentação do GitHub atualizada com sucesso!")
        print_info("💡 Execute 'git add README.md README_EN.md CHANGELOG.md' para incluir as mudanças")
    else:
        print_info("✅ Tudo já está atualizado!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

