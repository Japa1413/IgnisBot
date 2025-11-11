#!/usr/bin/env python3
"""
Script para atualizar automaticamente as seções do roadmap
que o parser precisa para detectar mudanças.

Este script garante que sempre que houver atualizações,
as seções "New Features", "Fixes & Improvements" e "Upcoming Features"
estejam atualizadas no ROADMAP_MELHORIAS.md.
"""

import re
from pathlib import Path
from datetime import datetime

ROADMAP_FILE = Path("docs/02_ARQUITETURA/ROADMAP_MELHORIAS.md")
CHANGELOG_FILE = Path("CHANGELOG.md")


def extract_from_changelog() -> dict:
    """Extrai informações do CHANGELOG.md na seção [Unreleased]."""
    if not CHANGELOG_FILE.exists():
        return {"added": [], "changed": [], "fixed": []}
    
    content = CHANGELOG_FILE.read_text(encoding='utf-8')
    
    # Encontrar seção [Unreleased]
    unreleased_match = re.search(
        r"##\s+\[Unreleased\].*?(?=##\s+\[|\Z)",
        content,
        re.DOTALL | re.IGNORECASE
    )
    
    if not unreleased_match:
        return {"added": [], "changed": [], "fixed": []}
    
    unreleased_content = unreleased_match.group(0)
    
    # Extrair Added
    added_match = re.search(
        r"#### Added\s*\n(.*?)(?=#### |### |## |\Z)",
        unreleased_content,
        re.DOTALL | re.IGNORECASE
    )
    added_items = []
    if added_match:
        # Extrair itens de lista
        items = re.findall(
            r"[-*]\s+(.+?)(?=\n[-*]|\n\n|\Z)",
            added_match.group(1),
            re.MULTILINE
        )
        added_items = [item.strip() for item in items if item.strip()]
    
    # Extrair Changed
    changed_match = re.search(
        r"#### Changed\s*\n(.*?)(?=#### |### |## |\Z)",
        unreleased_content,
        re.DOTALL | re.IGNORECASE
    )
    changed_items = []
    if changed_match:
        items = re.findall(
            r"[-*]\s+(.+?)(?=\n[-*]|\n\n|\Z)",
            changed_match.group(1),
            re.MULTILINE
        )
        changed_items = [item.strip() for item in items if item.strip()]
    
    # Extrair Fixed
    fixed_match = re.search(
        r"#### Fixed\s*\n(.*?)(?=#### |### |## |\Z)",
        unreleased_content,
        re.DOTALL | re.IGNORECASE
    )
    fixed_items = []
    if fixed_match:
        items = re.findall(
            r"[-*]\s+(.+?)(?=\n[-*]|\n\n|\Z)",
            fixed_match.group(1),
            re.MULTILINE
        )
        fixed_items = [item.strip() for item in items if item.strip()]
    
    return {
        "added": added_items,
        "changed": changed_items,
        "fixed": fixed_items
    }


def update_roadmap_sections():
    """Atualiza as seções do roadmap com informações do CHANGELOG."""
    if not ROADMAP_FILE.exists():
        print(f"Arquivo nao encontrado: {ROADMAP_FILE}")
        return False
    
    content = ROADMAP_FILE.read_text(encoding='utf-8')
    
    # Extrair informações do CHANGELOG
    changelog_data = extract_from_changelog()
    
    # Preparar conteúdo para New Features
    new_features = []
    for item in changelog_data["added"]:
        # Limpar formatação markdown excessiva
        clean_item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)
        clean_item = re.sub(r'`(.+?)`', r'\1', clean_item)
        if clean_item.strip():
            new_features.append(f"- {clean_item.strip()}")
    
    # Preparar conteúdo para Fixes
    fixes = []
    for item in changelog_data["changed"]:
        clean_item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)
        clean_item = re.sub(r'`(.+?)`', r'\1', clean_item)
        if clean_item.strip():
            fixes.append(f"- {clean_item.strip()}")
    
    for item in changelog_data["fixed"]:
        clean_item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)
        clean_item = re.sub(r'`(.+?)`', r'\1', clean_item)
        if clean_item.strip():
            fixes.append(f"- {clean_item.strip()}")
    
    # Atualizar seção New Features
    if new_features:
        new_features_section = "### New Features\n\n" + "\n".join(new_features[:10])  # Limitar a 10 itens
        # Substituir ou adicionar seção
        if re.search(r"### New Features", content, re.IGNORECASE):
            # Substituir seção existente
            pattern = r"### New Features.*?(?=### |## |\Z)"
            content = re.sub(
                pattern,
                new_features_section + "\n\n",
                content,
                flags=re.DOTALL | re.IGNORECASE
            )
        else:
            # Adicionar após "## ✅ MELHORIAS IMPLEMENTADAS"
            content = re.sub(
                r"(## ✅ MELHORIAS IMPLEMENTADAS\s*\n)",
                r"\1\n" + new_features_section + "\n\n",
                content,
                flags=re.IGNORECASE
            )
    
    # Atualizar seção Fixes & Improvements
    if fixes:
        fixes_section = "### Fixes & Improvements\n\n" + "\n".join(fixes[:10])  # Limitar a 10 itens
        if re.search(r"### Fixes & Improvements", content, re.IGNORECASE):
            pattern = r"### Fixes & Improvements.*?(?=### |## |\Z)"
            content = re.sub(
                pattern,
                fixes_section + "\n\n",
                content,
                flags=re.DOTALL | re.IGNORECASE
            )
        else:
            # Adicionar após New Features
            content = re.sub(
                r"(### New Features.*?\n\n)",
                r"\1" + fixes_section + "\n\n",
                content,
                flags=re.DOTALL | re.IGNORECASE
            )
    
    # Salvar arquivo
    ROADMAP_FILE.write_text(content, encoding='utf-8')
    print(f"Roadmap atualizado: {ROADMAP_FILE}")
    print(f"   - {len(new_features)} new features")
    print(f"   - {len(fixes)} fixes & improvements")
    
    return True


if __name__ == "__main__":
    import sys
    import io
    # Fix encoding for Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("Atualizando secoes do roadmap...")
    success = update_roadmap_sections()
    if success:
        print("Concluido!")
    else:
        print("Erro ao atualizar roadmap")

