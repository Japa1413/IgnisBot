#!/usr/bin/env python3
"""
Script para Atualizar README.md Automaticamente

Atualiza o README.md com informações atualizadas do projeto.
Pode ser executado periodicamente para manter sincronizado.
"""

import re
from pathlib import Path
from datetime import datetime
from corrigir_referencias_readme import fix_references, validate_all_references

def update_stats_in_readme(readme_path: Path):
    """Atualiza estatísticas no README"""
    content = readme_path.read_text(encoding='utf-8')
    
    # Contar documentos
    docs_dir = readme_path.parent / "docs"
    total_docs = len(list(docs_dir.rglob("*.md")))
    
    # Contar comandos
    cogs_dir = readme_path.parent / "cogs"
    if cogs_dir.exists():
        total_commands = len([f for f in cogs_dir.glob("*.py") if f.stem != "__init__"])
    else:
        total_commands = 0
    
    # Atualizar seção de estatísticas se existir
    stats_pattern = r'(\*\*Total de documentos:\*\*\s*)\d+'
    if re.search(stats_pattern, content):
        content = re.sub(stats_pattern, f'\\g<1>{total_docs}', content)
    
    readme_path.write_text(content, encoding='utf-8')
    return {"docs": total_docs, "commands": total_commands}

def main():
    """Função principal"""
    root_dir = Path(__file__).parent.parent
    readme_path = root_dir / "README.md"
    
    if not readme_path.exists():
        print("❌ README.md não encontrado")
        return 1
    
    print("=" * 60)
    print("ATUALIZAÇÃO AUTOMÁTICA DO README.md")
    print("=" * 60)
    print()
    
    # Corrigir referências
    print("🔧 Corrigindo referências...")
    fix_results = fix_references(readme_path, dry_run=False)
    if fix_results["changed"]:
        print(f"✅ {len(fix_results['fixed'])} referências corrigidas")
    else:
        print("ℹ️ Nenhuma correção necessária")
    
    # Atualizar estatísticas
    print("\n📊 Atualizando estatísticas...")
    stats = update_stats_in_readme(readme_path)
    print(f"   Documentos: {stats['docs']}")
    print(f"   Comandos: {stats['commands']}")
    
    # Validar
    print("\n🔍 Validando...")
    validation = validate_all_references(readme_path)
    print(f"   {validation['status']}")
    
    if validation["total"] > 0:
        print("\n⚠️ Ainda há referências quebradas:")
        for old, full in validation["broken"][:5]:  # Mostrar apenas 5 primeiros
            print(f"   - {old}")
    
    print("\n✅ README.md atualizado!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

