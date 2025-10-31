#!/usr/bin/env python3
"""
Manutenção Automatizada de Documentação

Executa manutenção periódica:
- Organiza documentos
- Atualiza catálogo
- Corrige datas
- Valida estrutura
"""

import sys
from pathlib import Path
from datetime import datetime
from organizar_documentacao import organize_documentation, update_catalog, validate_structure

def fix_dates_in_file(file_path: Path, current_date: str):
    """Corrige datas em um arquivo"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Padrões de data para corrigir
        patterns = [
            (r'Data:\s*\d{2}/\d{2}/\d{4}', f'Data: {current_date}'),
            (r'Date:\s*\d{2}/\d{2}/\d{4}', f'Date: {current_date}'),
            (r'última atualização:\s*\d{2}/\d{2}/\d{4}', f'Última atualização: {current_date}'),
            (r'Última atualização:\s*\d{2}/\d{2}/\d{4}', f'Última atualização: {current_date}'),
            (r'Last updated:\s*\d{2}/\d{2}/\d{4}', f'Last updated: {current_date}'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"⚠️ Erro ao corrigir datas em {file_path}: {e}")
        return False

def main():
    """Função principal de manutenção"""
    import re
    
    root_dir = Path(__file__).parent.parent
    docs_dir = root_dir / "docs"
    
    if not docs_dir.exists():
        print("❌ Diretório docs/ não encontrado")
        return 1
    
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    print("=" * 60)
    print("MANUTENÇÃO AUTOMATIZADA DE DOCUMENTAÇÃO")
    print("=" * 60)
    print()
    
    # 1. Organizar documentos
    print("📦 Passo 1: Organizando documentos...")
    results = organize_documentation(root_dir, dry_run=False)
    print(f"   Movidos: {len(results['moved'])}")
    print()
    
    # 2. Validar estrutura
    print("🔍 Passo 2: Validando estrutura...")
    issues = validate_structure(docs_dir)
    if not issues["orphans"]:
        print("   ✅ Estrutura válida")
    else:
        print(f"   ⚠️ {len(issues['orphans'])} documentos fora do lugar")
    print()
    
    # 3. Atualizar catálogo
    print("📚 Passo 3: Atualizando catálogo...")
    update_catalog(docs_dir)
    print("   ✅ Catálogo atualizado")
    print()
    
    print("=" * 60)
    print("✅ Manutenção concluída!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

