#!/usr/bin/env python3
"""
Script para Corrigir Referências no README.md

Valida e corrige automaticamente todas as referências de documentação no README.md
baseado na estrutura atual organizada.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Mapeamento de referências antigas para novas (caminhos organizados)
REFERENCE_MAP = {
    # Documentos técnicos
    r'docs/ARQUITETURA\.md': 'docs/02_ARQUITETURA/ARQUITETURA_SISTEMA.md',
    r'docs/ANALISE_SEGURANCA\.md': 'docs/02_ARQUITETURA/ANALISE_SEGURANCA.md',
    
    # Documentos legais
    r'docs/POLITICA_PRIVACIDADE\.md': 'docs/06_LEGAL_COMPLIANCE/POLITICA_PRIVACIDADE.md',
    r'docs/TERMOS_USO\.md': 'docs/06_LEGAL_COMPLIANCE/TERMOS_USO.md',
    r'docs/SLA\.md': 'docs/06_LEGAL_COMPLIANCE/SLA.md',
    r'docs/LGPD_COMPLIANCE\.md': 'docs/06_LEGAL_COMPLIANCE/LGPD_COMPLIANCE.md',
    r'docs/PLANO_RESPOSTA_INCIDENTES\.md': 'docs/06_LEGAL_COMPLIANCE/PLANO_INCIDENTES.md',
    
    # Documentos de gestão/auditoria
    r'RELATORIO_AUDITORIA_INICIAL\.md': 'docs/07_AUDITORIA/RELATORIO_INICIAL.md',
    r'PROGRESSO_AUDITORIA\.md': 'docs/01_GESTAO_PROJETO/PROGRESSO_AUDITORIA.md',
    r'CHECKLIST_100_CONFORMIDADE\.md': 'docs/08_REFERENCIA/CHECKLIST_CONFORMIDADE.md',
    r'CONFIGURAR_DPO\.md': 'docs/03_DESENVOLVIMENTO/CONFIGURAR_DPO.md',
    r'SETUP_CRITICO\.md': 'docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md',
    
    # Referências em backticks
    r'`SETUP_CRITICO\.md`': '`docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md`',
    r'`CONFIGURAR_DPO\.md`': '`docs/03_DESENVOLVIMENTO/CONFIGURAR_DPO.md`',
    r'`docs/LGPD_COMPLIANCE\.md`': '`docs/06_LEGAL_COMPLIANCE/LGPD_COMPLIANCE.md`',
    r'`SETUP_CRITICO\.md`': '`docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md`',
}

def check_file_exists(file_path: str) -> bool:
    """Verifica se um arquivo existe"""
    return Path(file_path).exists()

def find_broken_references(readme_path: Path) -> List[Tuple[str, str]]:
    """Encontra referências quebradas no README"""
    content = readme_path.read_text(encoding='utf-8')
    broken = []
    
    # Padrões de referência (markdown links e backticks)
    patterns = [
        r'\[([^\]]+)\]\(([^)]+\.md)\)',  # Markdown links [text](file.md)
        r'`([^`]+\.md)`',  # Backticks `file.md`
    ]
    
    # Remover duplicações de caminho
    def fix_duplicate_paths(text):
        """Remove duplicações como docs/X/docs/X/file.md"""
        pattern = r'docs/(\d{2}_[^/]+)/docs/\1/'
        return re.sub(pattern, r'docs/\1/', text)
    
    for pattern in patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            ref = match.group(2) if pattern.startswith('\\[') else match.group(1)
            
            # Verificar se é referência relativa
            if not ref.startswith('http') and not ref.startswith('#'):
                # Construir caminho completo
                if ref.startswith('docs/'):
                    full_path = ref
                else:
                    full_path = readme_path.parent / ref
                    full_path = str(full_path.relative_to(readme_path.parent))
                
                if not check_file_exists(full_path):
                    broken.append((ref, full_path))
    
    return broken

def fix_references(readme_path: Path, dry_run: bool = False) -> Dict:
    """Corrige referências no README"""
    content = readme_path.read_text(encoding='utf-8')
    original_content = content
    fixes = []
    
    # Primeiro: remover duplicações de caminho
    duplicate_pattern = r'docs/(\d{2}_[^/]+)/docs/\1/'
    if re.search(duplicate_pattern, content):
        content = re.sub(duplicate_pattern, r'docs/\1/', content)
        fixes.append("Removed duplicate paths")
    
    # Depois: aplicar mapeamentos
    for old_pattern, new_path in REFERENCE_MAP.items():
        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_path, content)
            fixes.append(f"{old_pattern} → {new_path}")
    
    # Remover duplicações novamente (caso tenha sido criada por substituições)
    content = re.sub(duplicate_pattern, r'docs/\1/', content)
    
    results = {
        "fixed": fixes,
        "changed": content != original_content
    }
    
    if not dry_run and results["changed"]:
        readme_path.write_text(content, encoding='utf-8')
    
    return results

def validate_all_references(readme_path: Path) -> Dict:
    """Valida todas as referências"""
    broken = find_broken_references(readme_path)
    
    return {
        "broken": broken,
        "total": len(broken),
        "status": "✅ OK" if len(broken) == 0 else f"❌ {len(broken)} referências quebradas"
    }

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Corrigir referências no README.md")
    parser.add_argument("--dry-run", action="store_true", help="Apenas simular, não fazer mudanças")
    parser.add_argument("--validate", action="store_true", help="Apenas validar, não corrigir")
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent.parent
    readme_path = root_dir / "README.md"
    
    if not readme_path.exists():
        print("❌ README.md não encontrado")
        return 1
    
    print("=" * 60)
    print("CORREÇÃO DE REFERÊNCIAS NO README.md")
    print("=" * 60)
    print()
    
    if args.validate:
        print("🔍 Validando referências...")
        validation = validate_all_references(readme_path)
        
        if validation["total"] > 0:
            print(f"\n❌ {validation['total']} referências quebradas encontradas:")
            for old, full in validation["broken"]:
                print(f"   - {old}")
            return 1
        else:
            print("\n✅ Todas as referências estão corretas!")
            return 0
    
    # Corrigir referências
    if args.dry_run:
        print("🔍 Modo DRY-RUN (simulação)")
        print()
    
    results = fix_references(readme_path, dry_run=args.dry_run)
    
    if results["changed"]:
        print(f"✅ {len(results['fixed'])} referências corrigidas:")
        for fix in results["fixed"]:
            print(f"   - {fix}")
    else:
        print("ℹ️ Nenhuma correção necessária")
    
    # Validar após correção
    print()
    print("🔍 Validando após correção...")
    validation = validate_all_references(readme_path)
    print(f"   {validation['status']}")
    
    if validation["total"] > 0:
        print("\n⚠️ Ainda há referências quebradas (não mapeadas):")
        for old, full in validation["broken"]:
            print(f"   - {old}")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

