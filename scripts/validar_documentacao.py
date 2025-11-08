#!/usr/bin/env python3
"""
Validador de Documentação

Valida se a documentação está organizada corretamente.
Pode ser usado como Git hook ou CI/CD check.
"""

import sys
from pathlib import Path
from organizar_documentacao import validate_structure, find_orphan_docs, CATEGORIES, ROOT_DOCS

def check_documentation():
    """Valida a documentação e retorna código de saída apropriado"""
    root_dir = Path(__file__).parent.parent
    docs_dir = root_dir / "docs"
    
    if not docs_dir.exists():
        print("[ERRO] Diretorio docs/ nao encontrado")
        return 1
    
    print("[VALIDACAO] Validando estrutura de documentacao...")
    print()
    
    issues = validate_structure(docs_dir)
    errors_found = False
    
    # Verificar documentos órfãos
    orphans = find_orphan_docs(root_dir)
    if orphans:
        print(f"[ERRO] Documentos fora do lugar ({len(orphans)}):")
        for orphan in orphans:
            print(f"   - {orphan.relative_to(root_dir)}")
        errors_found = True
        print()
    
    # Verificar READMEs faltando
    if issues["missing_readme"]:
        print(f"[WARN] README.md faltando ({len(issues['missing_readme'])}):")
        for cat in issues["missing_readme"]:
            print(f"   - {cat}")
        print()
    
    if not errors_found:
        print("[OK] Documentacao organizada corretamente!")
        return 0
    else:
        print("💡 Execute 'python scripts/organizar_documentacao.py' para organizar automaticamente")
        return 1


if __name__ == "__main__":
    sys.exit(check_documentation())

