#!/usr/bin/env python3
"""
Validation Script: Verificar se plano de resposta a incidentes está completo

Valida se todas as informações necessárias estão preenchidas e acessíveis.
"""

from __future__ import annotations

import sys
from pathlib import Path
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

DOCS_DIR = Path(__file__).parent.parent / "docs"
INCIDENT_PLAN = DOCS_DIR / "06_LEGAL_COMPLIANCE" / "PLANO_INCIDENTES.md"
POLITICA = DOCS_DIR / "06_LEGAL_COMPLIANCE" / "POLITICA_PRIVACIDADE.md"
CONFIG_FILE = Path(__file__).parent.parent / "utils" / "config.py"


def check_placeholders(file_path: Path, patterns: list) -> list:
    """Check for placeholder patterns in file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        issues = []
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Found placeholder: {pattern}")
        
        return issues
    except Exception as e:
        return [f"Error reading file: {e}"]


def validate_incident_plan():
    """Validate incident response plan"""
    print("Validating Incident Response Plan...")
    print("=" * 60)
    
    all_ok = True
    placeholders = [
        r'\[NOME DO DPO\]',
        r'\[EMAIL\]',
        r'\[DEFINIR',
        r'\[DEFINIR NOME',
        r'\[Configurar CONTROLLER_EMAIL'
    ]
    
    # Check PLANO_INCIDENTES.md
    if INCIDENT_PLAN.exists():
        issues = check_placeholders(INCIDENT_PLAN, placeholders)
        if issues:
            print(f"\n⚠️ Issues in {INCIDENT_PLAN.name}:")
            for issue in issues:
                print(f"  - {issue}")
            all_ok = False
        else:
            print(f"✅ {INCIDENT_PLAN.name} - No placeholders found")
    else:
        print(f"❌ {INCIDENT_PLAN} not found")
        all_ok = False
    
    # Check POLITICA_PRIVACIDADE.md
    if POLITICA.exists():
        issues = check_placeholders(POLITICA, placeholders)
        if issues:
            print(f"\n⚠️ Issues in {POLITICA.name}:")
            for issue in issues:
                print(f"  - {issue}")
            all_ok = False
        else:
            print(f"✅ {POLITICA.name} - No placeholders found")
    else:
        print(f"❌ {POLITICA} not found")
        all_ok = False
    
    # Check config.py for CONTROLLER_EMAIL validation
    if CONFIG_FILE.exists():
        content = CONFIG_FILE.read_text(encoding='utf-8')
        if 'CONTROLLER_EMAIL' in content:
            if 'default=""' in content or 'default=None' in content:
                print(f"\n⚠️ CONTROLLER_EMAIL has empty default - should be configured")
                all_ok = False
            else:
                print(f"✅ CONTROLLER_EMAIL found in config")
        else:
            print(f"❌ CONTROLLER_EMAIL not found in config")
            all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ All validations passed!")
        return 0
    else:
        print("⚠️ Some validations failed - see above")
        return 1


if __name__ == "__main__":
    exit_code = validate_incident_plan()
    sys.exit(exit_code)

