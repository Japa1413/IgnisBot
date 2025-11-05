#!/usr/bin/env python3
"""
Script para encontrar todos os placeholders em documentos

Encontra placeholders como [DEFINIR], [NOME], [EMAIL], etc. que precisam ser preenchidos.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs"

# Padrões de placeholders
PLACEHOLDER_PATTERNS = [
    r'\[DEFINIR[^\]]*\]',
    r'\[NOME[^\]]*\]',
    r'\[EMAIL[^\]]*\]',
    r'\[Configurar[^\]]*\]',
    r'\[SEU[^\]]*\]',
    r'\[A DEFINIR[^\]]*\]',
    r'placeholder',
]

def find_placeholders(file_path: Path) -> list:
    """Find placeholders in a file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        found = []
        
        for pattern in PLACEHOLDER_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Get context (line number and surrounding text)
                line_num = content[:match.start()].count('\n') + 1
                lines = content.split('\n')
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                
                found.append({
                    'pattern': pattern,
                    'match': match.group(),
                    'line': line_num,
                    'context': line_content.strip()[:100]
                })
        
        return found
    except Exception as e:
        return [{'error': str(e)}]

def main():
    """Main entry point"""
    all_placeholders = {}
    
    # Find all markdown files
    for md_file in DOCS_DIR.rglob("*.md"):
        placeholders = find_placeholders(md_file)
        if placeholders:
            all_placeholders[str(md_file.relative_to(DOCS_DIR.parent))] = placeholders
    
    # Print results
    if all_placeholders:
        print("🔍 PLACEHOLDERS ENCONTRADOS:\n")
        print("=" * 80)
        
        for file_path, placeholders in sorted(all_placeholders.items()):
            print(f"\n📄 {file_path}")
            print("-" * 80)
            
            for item in placeholders:
                if 'error' in item:
                    print(f"  ❌ Erro: {item['error']}")
                else:
                    print(f"  Linha {item['line']:4d}: {item['match']}")
                    print(f"            {item['context']}")
        
        print("\n" + "=" * 80)
        print(f"\n📊 Total de arquivos com placeholders: {len(all_placeholders)}")
        
        total_placeholders = sum(len(p) for p in all_placeholders.values())
        print(f"📊 Total de placeholders encontrados: {total_placeholders}")
        
        return 1
    else:
        print("✅ Nenhum placeholder encontrado!")
        return 0

if __name__ == "__main__":
    sys.exit(main())

