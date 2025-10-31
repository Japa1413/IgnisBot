#!/usr/bin/env python3
"""
Script Automatizado de Organização de Documentação

Organiza e valida toda a documentação do projeto de acordo com o padrão definido.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json
import sys

# Categorias e mapeamento
CATEGORIES = {
    "01_GESTAO_PROJETO": {
        "keywords": ["resumo", "executivo", "status", "progresso", "auditoria", "resultado", "teste"],
        "description": "Gestão e planejamento de projeto"
    },
    "02_ARQUITETURA": {
        "keywords": ["arquitetura", "design", "sistema", "revisao", "seguranca", "analise"],
        "description": "Documentação técnica de arquitetura"
    },
    "03_DESENVOLVIMENTO": {
        "keywords": ["setup", "configuracao", "guia", "desenvolvimento", "dpo"],
        "description": "Guias de desenvolvimento"
    },
    "04_TESTES": {
        "keywords": ["teste", "test", "validacao", "qa"],
        "description": "Documentação de testes"
    },
    "05_OPERACAO": {
        "keywords": ["operacao", "instrucoes", "canal", "env", "deploy"],
        "description": "Guias operacionais"
    },
    "06_LEGAL_COMPLIANCE": {
        "keywords": ["legal", "privacy", "privacidade", "termos", "sla", "lgpd", "compliance", "conformidade", "politica"],
        "description": "Documentação legal e conformidade"
    },
    "07_AUDITORIA": {
        "keywords": ["auditoria", "audit", "relatorio", "conformidade"],
        "description": "Relatórios de auditoria"
    },
    "08_REFERENCIA": {
        "keywords": ["indice", "checklist", "referencia", "resumo", "performance"],
        "description": "Documentos de referência rápida"
    },
    "09_OTIMIZACAO": {
        "keywords": ["otimizacao", "performance", "cache", "fase", "melhorias", "roadmap", "monitoramento", "validacao"],
        "description": "Otimizações e performance"
    }
}

# Arquivos que devem ficar na raiz de docs/
ROOT_DOCS = ["README.md", "PADRAO_DOCUMENTACAO.md", "CATALOGO_DOCUMENTACAO.md"]

# Arquivos de resumo que devem ir para 08_REFERENCIA
SUMMARY_FILES = ["RESUMO", "RESUMO_", "RESUMO_FINAL", "RESUMO_EXECUTIVO"]


def categorize_file(filename: str) -> Optional[str]:
    """Determina a categoria de um arquivo baseado no nome"""
    filename_lower = filename.lower()
    
    # Verificar cada categoria
    for category, info in CATEGORIES.items():
        for keyword in info["keywords"]:
            if keyword in filename_lower:
                return category
    
    return None


def find_orphan_docs(root_dir: Path) -> List[Path]:
    """Encontra documentos que estão fora do lugar"""
    orphans = []
    
    # Procurar na raiz do projeto
    for md_file in root_dir.glob("*.md"):
        if md_file.name not in ["README.md"]:
            orphans.append(md_file)
    
    # Procurar na raiz de docs/ (exceto os permitidos)
    docs_root = root_dir / "docs"
    if docs_root.exists():
        for md_file in docs_root.glob("*.md"):
            if md_file.name not in ROOT_DOCS:
                orphans.append(md_file)
    
    return orphans


def organize_documentation(root_dir: Path, dry_run: bool = False) -> Dict:
    """Organiza toda a documentação"""
    results = {
        "moved": [],
        "errors": [],
        "kept": [],
        "created_catalog": False
    }
    
    docs_dir = root_dir / "docs"
    if not docs_dir.exists():
        results["errors"].append("Diretório docs/ não encontrado")
        return results
    
    # Criar categorias se não existirem
    for category in CATEGORIES.keys():
        category_dir = docs_dir / category
        if not category_dir.exists():
            if not dry_run:
                category_dir.mkdir(parents=True, exist_ok=True)
                # Criar README.md básico
                readme_path = category_dir / "README.md"
                if not readme_path.exists():
                    readme_content = f"# {CATEGORIES[category]['description']}\n\n**Categoria:** {category}\n\n---\n\nDocumentos nesta categoria: {CATEGORIES[category]['description']}\n"
                    readme_path.write_text(readme_content, encoding='utf-8')
            print(f"✅ Criado diretório: {category}")
    
    # Encontrar e organizar documentos órfãos
    orphans = find_orphan_docs(root_dir)
    
    for orphan in orphans:
        category = categorize_file(orphan.name)
        
        if category:
            target_dir = docs_dir / category
            target_path = target_dir / orphan.name
            
            if orphan != target_path:
                try:
                    if not dry_run:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        orphan.rename(target_path)
                    results["moved"].append({
                        "from": str(orphan.relative_to(root_dir)),
                        "to": str(target_path.relative_to(root_dir)),
                        "category": category
                    })
                    print(f"📦 Movido: {orphan.name} → {target_path.relative_to(root_dir)}")
                except Exception as e:
                    results["errors"].append(f"Erro ao mover {orphan.name}: {e}")
            else:
                results["kept"].append(str(orphan.relative_to(root_dir)))
        else:
            # Se não encontrou categoria, mover para 08_REFERENCIA (resumos gerais)
            if any(summary in orphan.name.upper() for summary in SUMMARY_FILES):
                category = "08_REFERENCIA"
                target_dir = docs_dir / category
                target_path = target_dir / orphan.name
                
                if orphan != target_path:
                    try:
                        if not dry_run:
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            orphan.rename(target_path)
                        results["moved"].append({
                            "from": str(orphan.relative_to(root_dir)),
                            "to": str(target_path.relative_to(root_dir)),
                            "category": category
                        })
                        print(f"📦 Movido (resumo): {orphan.name} → {target_path.relative_to(root_dir)}")
                    except Exception as e:
                        results["errors"].append(f"Erro ao mover {orphan.name}: {e}")
            else:
                results["errors"].append(f"Não foi possível categorizar: {orphan.name}")
    
    # Atualizar catálogo e README
    if not dry_run:
        update_catalog(docs_dir)
        update_readme_references(root_dir)
        results["created_catalog"] = True
    
    return results


def update_readme_references(root_dir: Path):
    """Atualiza referências no README.md após organização"""
    try:
        from corrigir_referencias_readme import fix_references
        readme_path = root_dir / "README.md"
        if readme_path.exists():
            fix_references(readme_path, dry_run=False)
    except ImportError:
        pass  # Script não disponível

def update_catalog(docs_dir: Path):
    """Atualiza o catálogo de documentação"""
    current_date = datetime.now().strftime("%d/%m/%Y")
    catalog_content = """# 📚 CATÁLOGO COMPLETO DE DOCUMENTAÇÃO - IGNISBOT

**Versão:** 3.0  
**Data:** {date}  
**Última atualização automática:** {date}

---

## ✅ ESTRUTURA ORGANIZADA

Todos os documentos foram organizados automaticamente conforme padrão definido em `PADRAO_DOCUMENTACAO.md`.

---

## 📁 DOCUMENTOS POR CATEGORIA

""".format(date=current_date)
    
    total_docs = 0
    
    for category in sorted(CATEGORIES.keys()):
        category_dir = docs_dir / category
        if not category_dir.exists():
            continue
        
        docs = sorted([f.name for f in category_dir.glob("*.md") if f.name != "README.md"])
        if not docs:
            continue
        
        catalog_content += f"\n### {category.replace('_', ' ').title()} (`docs/{category}/`)\n\n"
        catalog_content += f"**Descrição:** {CATEGORIES[category]['description']}\n\n"
        catalog_content += "| Documento | Status |\n"
        catalog_content += "|-----------|--------|\n"
        
        for doc in docs:
            catalog_content += f"| `{doc}` | ✅ Organizado |\n"
        
        catalog_content += f"\n**Total:** {len(docs)} documentos\n\n"
        catalog_content += "---\n"
        
        total_docs += len(docs)
    
    # Adicionar documentos na raiz de docs/
    root_docs = sorted([f.name for f in docs_dir.glob("*.md") if f.name in ROOT_DOCS])
    if root_docs:
        catalog_content += "\n### Documentos de Configuração (`docs/`)\n\n"
        catalog_content += "| Documento | Status |\n"
        catalog_content += "|-----------|--------|\n"
        for doc in root_docs:
            catalog_content += f"| `{doc}` | ✅ Organizado |\n"
        catalog_content += f"\n**Total:** {len(root_docs)} documentos\n\n"
        total_docs += len(root_docs)
    
    catalog_content += f"\n---\n\n## 📊 ESTATÍSTICAS\n\n"
    catalog_content += f"- **Total de documentos:** {total_docs}\n"
    catalog_content += f"- **Categorias:** {len(CATEGORIES)}\n"
    catalog_content += f"- **Última atualização:** {current_date} {datetime.now().strftime('%H:%M:%S')}\n"
    
    catalog_content += "\n---\n\n"
    catalog_content += "**Nota:** Este catálogo é atualizado automaticamente pelo script `scripts/organizar_documentacao.py`\n"
    
    catalog_path = docs_dir / "CATALOGO_DOCUMENTACAO.md"
    catalog_path.write_text(catalog_content, encoding='utf-8')
    print(f"✅ Catálogo atualizado: {catalog_path}")


def validate_structure(docs_dir: Path) -> Dict:
    """Valida a estrutura de documentação"""
    issues = {
        "orphans": [],
        "missing_readme": [],
        "wrong_location": []
    }
    
    # Verificar documentos órfãos
    orphans = find_orphan_docs(docs_dir.parent)
    issues["orphans"] = [str(o.relative_to(docs_dir.parent)) for o in orphans]
    
    # Verificar README em cada categoria
    for category in CATEGORIES.keys():
        category_dir = docs_dir / category
        if category_dir.exists():
            readme_path = category_dir / "README.md"
            if not readme_path.exists():
                issues["missing_readme"].append(category)
    
    return issues


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Organizar documentação do projeto")
    parser.add_argument("--dry-run", action="store_true", help="Apenas simular, não fazer mudanças")
    parser.add_argument("--validate", action="store_true", help="Apenas validar estrutura")
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent.parent
    
    print("=" * 60)
    print("ORGANIZAÇÃO AUTOMATIZADA DE DOCUMENTAÇÃO")
    print("=" * 60)
    print()
    
    if args.validate:
        print("🔍 Validando estrutura...")
        issues = validate_structure(root_dir / "docs")
        
        if issues["orphans"]:
            print(f"\n⚠️ Documentos fora do lugar ({len(issues['orphans'])}):")
            for orphan in issues["orphans"]:
                print(f"  - {orphan}")
        else:
            print("\n✅ Nenhum documento órfão encontrado")
        
        if issues["missing_readme"]:
            print(f"\n⚠️ README.md faltando ({len(issues['missing_readme'])}):")
            for cat in issues["missing_readme"]:
                print(f"  - {cat}")
        else:
            print("\n✅ Todos os README.md presentes")
        
        if not issues["orphans"] and not issues["missing_readme"]:
            print("\n✅ Estrutura válida!")
        
        return
    
    if args.dry_run:
        print("🔍 Modo DRY-RUN (simulação)")
        print()
    
    results = organize_documentation(root_dir, dry_run=args.dry_run)
    
    print()
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"📦 Documentos movidos: {len(results['moved'])}")
    print(f"✅ Documentos mantidos: {len(results['kept'])}")
    print(f"❌ Erros: {len(results['errors'])}")
    
    if results["errors"]:
        print("\n⚠️ Erros encontrados:")
        for error in results["errors"]:
            print(f"  - {error}")
    
    if results["created_catalog"]:
        print("\n✅ Catálogo atualizado")


if __name__ == "__main__":
    main()

