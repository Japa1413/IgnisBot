#!/usr/bin/env python3
"""
Script para atualizar datas nos documentos

Atualiza referências de "2024" para "2025-10-31" e padroniza formatos de data.
"""

from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime

# Data padrão para atualização
CURRENT_DATE = "2025-10-31"
CURRENT_YEAR = "2025"

# Padrões a serem atualizados
PATTERNS = [
    # Última atualização: 2024
    (r"Última atualização.*2024", f"Última atualização: {CURRENT_DATE}"),
    (r"Última Atualização.*2024", f"Última Atualização: {CURRENT_DATE}"),
    (r"Data.*2024", f"Data: {CURRENT_DATE}"),
    (r"Data da Análise.*2024", f"Data da Análise: {CURRENT_DATE}"),
    (r"Atualizado em.*2024", f"Atualizado em: {CURRENT_DATE}"),
    (r"Data de Conclusão.*2024", f"Data de Conclusão: {CURRENT_DATE}"),
]

# Diretório de documentos
DOCS_DIR = Path(__file__).parent.parent / "docs"


def update_file(file_path: Path) -> bool:
    """Atualiza datas em um arquivo"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Aplicar padrões
        for pattern, replacement in PATTERNS:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # Só escrever se houve mudanças
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return False


def main():
    """Main entry point"""
    updated_count = 0
    
    # Encontrar todos os arquivos .md
    for md_file in DOCS_DIR.rglob("*.md"):
        if update_file(md_file):
            updated_count += 1
            print(f"✅ Atualizado: {md_file.relative_to(DOCS_DIR.parent)}")
    
    print(f"\n✅ Total de arquivos atualizados: {updated_count}")


if __name__ == "__main__":
    main()

