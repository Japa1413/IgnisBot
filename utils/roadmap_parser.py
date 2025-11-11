"""
Roadmap Parser - Extract roadmap information from documentation files.

Reads development documentation and extracts information about
recent implementations, improvements, and upcoming features.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

# Paths to documentation files
DOCS_ROOT = Path("docs")
ROADMAP_FILE = DOCS_ROOT / "02_ARQUITETURA" / "ROADMAP_MELHORIAS.md"
IMPLEMENTACOES_FILE = DOCS_ROOT / "02_ARQUITETURA" / "IMPLEMENTACOES_COMPLETAS.md"
CHANGELOG_FILE = Path("CHANGELOG.md")
STATUS_FILE = DOCS_ROOT / "02_ARQUITETURA" / "STATUS_PROJETO.md"


def parse_markdown_section(content: str, section_title: str) -> List[str]:
    """
    Extract items from a markdown section.
    
    Args:
        content: Markdown content
        section_title: Title of the section to extract
    
    Returns:
        List of items found in the section
    """
    items = []
    
    # Pattern to find section and its content
    pattern = rf"##?\s*{re.escape(section_title)}.*?\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    
    if match:
        section_content = match.group(1)
        
        # First, extract main items with bold titles (e.g., "- **Title**")
        # This captures the main feature/fix titles
        bold_item_pattern = r"[-*]\s+\*\*(.+?)\*\*"
        bold_items = re.findall(bold_item_pattern, section_content, re.MULTILINE)
        items.extend([item.strip() for item in bold_items if item.strip()])
        
        # Then extract regular list items (lines starting with -, *)
        # But skip items that are sub-items (indented with spaces)
        item_pattern = r"^[-*]\s+(?!\*\*)(.+?)(?=\n|$)"
        regular_items = re.findall(item_pattern, section_content, re.MULTILINE)
        # Filter out items that are sub-items (have leading spaces before - or *)
        for item in regular_items:
            # Check if this line is indented (sub-item)
            line_match = re.search(rf"^[-*]\s+{re.escape(item)}", section_content, re.MULTILINE)
            if line_match:
                line_start = line_match.start()
                # Check if there are spaces before the - or *
                before_match = section_content[:line_start]
                if before_match and before_match[-1] not in ['\n', '\r']:
                    # This is likely a continuation, skip
                    continue
                # Check if line starts with spaces (indented)
                line_before = section_content[max(0, line_start-10):line_start]
                if not line_before.strip() or line_before.strip() == '':
                    # This is a top-level item
                    items.append(item.strip())
        
        # Also try numbered lists
        numbered_pattern = r"^\d+\.\s+(.+?)$"
        numbered_items = re.findall(numbered_pattern, section_content, re.MULTILINE)
        items.extend([item.strip() for item in numbered_items if item.strip()])
    
    # Clean items and remove duplicates
    cleaned_items = []
    seen = set()
    for item in items:
        item_clean = item.strip()
        if item_clean and item_clean.lower() not in seen:
            seen.add(item_clean.lower())
            cleaned_items.append(item_clean)
    
    return cleaned_items


def extract_features(content: str) -> List[str]:
    """Extract new features from documentation."""
    features = []
    
    # Look for various section titles
    section_titles = [
        "New Features",
        "Features",
        "Funcionalidades",
        "Implementações",
        "Implementações Completas",
        "Completed Features"
    ]
    
    for title in section_titles:
        items = parse_markdown_section(content, title)
        features.extend(items)
    
    # Also look for checkbox items that are checked
    checkbox_pattern = r"- \[x\]\s+(.+?)(?=\n|$)"
    checked_items = re.findall(checkbox_pattern, content, re.MULTILINE | re.IGNORECASE)
    features.extend([item.strip() for item in checked_items])
    
    return list(set(features))  # Remove duplicates


def extract_fixes(content: str) -> List[str]:
    """Extract bug fixes and improvements from documentation."""
    fixes = []
    
    section_titles = [
        "Fixes",
        "Bug Fixes",
        "Correções",
        "Improvements",
        "Melhorias",
        "Optimizations",
        "Otimizações"
    ]
    
    for title in section_titles:
        items = parse_markdown_section(content, title)
        fixes.extend(items)
    
    return list(set(fixes))


def extract_upcoming(content: str) -> List[str]:
    """Extract upcoming features from documentation."""
    upcoming = []
    
    section_titles = [
        "Upcoming",
        "Próximos Passos",
        "Next Steps",
        "Roadmap",
        "Planned Features",
        "Features Planejadas"
    ]
    
    for title in section_titles:
        items = parse_markdown_section(content, title)
        upcoming.extend(items)
    
    return list(set(upcoming))


def read_documentation_file(file_path: Path) -> Optional[str]:
    """Read a documentation file and return its content."""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            logger.warning(f"Documentation file not found: {file_path}")
            return None
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}", exc_info=True)
        return None


def get_file_modification_time(file_path: Path) -> Optional[datetime]:
    """Get the last modification time of a file."""
    try:
        if file_path.exists():
            return datetime.fromtimestamp(file_path.stat().st_mtime)
    except Exception as e:
        logger.warning(f"Error getting modification time for {file_path}: {e}")
    return None


def get_latest_roadmap_data() -> Dict[str, any]:
    """
    Extract roadmap data from all documentation files.
    Prioritizes most recently modified files and latest entries.
    
    Returns:
        Dictionary with title, description, features, fixes, and upcoming
    """
    all_content = []
    file_times = {}
    
    # Read all relevant documentation files with timestamps
    files_to_read = [
        ROADMAP_FILE,
        IMPLEMENTACOES_FILE,
        CHANGELOG_FILE,
        STATUS_FILE
    ]
    
    for file_path in files_to_read:
        content = read_documentation_file(file_path)
        if content:
            all_content.append(content)
            mod_time = get_file_modification_time(file_path)
            if mod_time:
                file_times[file_path.name] = mod_time
    
    if not all_content:
        logger.warning("No documentation files found")
        return {
            "title": "Roadmap Update",
            "description": "No recent updates found in documentation.",
            "features": [],
            "fixes": [],
            "upcoming": [],
            "content_hash": ""
        }
    
    # Combine all content
    combined_content = "\n\n".join(all_content)
    
    # Extract information
    features = extract_features(combined_content)
    fixes = extract_fixes(combined_content)
    upcoming = extract_upcoming(combined_content)
    
    # Get the most recent date from CHANGELOG (prioritize latest entries)
    latest_date = None
    if CHANGELOG_FILE.exists():
        changelog_content = read_documentation_file(CHANGELOG_FILE)
        if changelog_content:
            # First check for "Unreleased" section
            if "[Unreleased]" in changelog_content:
                # Look for date in Unreleased section (e.g., "### 🚀 Title (2025-01-11)")
                unreleased_date_pattern = r"###\s+.*?\((\d{4}-\d{2}-\d{2})\)"
                unreleased_dates = re.findall(unreleased_date_pattern, changelog_content)
                if unreleased_dates:
                    latest_date = unreleased_dates[0]  # Most recent date in Unreleased
            else:
                # Look for date patterns - get the FIRST (most recent) date
                date_pattern = r"##\s+\[?(\d{4}-\d{2}-\d{2})\]?"
                dates = re.findall(date_pattern, changelog_content)
                if dates:
                    latest_date = dates[0]  # First date is most recent
    
    # Also check for "Unreleased" section which is always most recent
    if CHANGELOG_FILE.exists():
        changelog_content = read_documentation_file(CHANGELOG_FILE)
        if changelog_content and "[Unreleased]" in changelog_content:
            # Extract items from Unreleased section
            unreleased_pattern = r"##\s+\[Unreleased\].*?(?=##\s+\[|\Z)"
            unreleased_match = re.search(unreleased_pattern, changelog_content, re.DOTALL | re.IGNORECASE)
            if unreleased_match:
                unreleased_content = unreleased_match.group(0)
                # Extract Added items from Unreleased
                added_pattern = r"#### Added\s*\n(.*?)(?=#### |### |## |\Z)"
                added_match = re.search(added_pattern, unreleased_content, re.DOTALL | re.IGNORECASE)
                if added_match:
                    added_items = re.findall(r"[-*]\s+(.+?)(?=\n[-*]|\n\n|\Z)", added_match.group(1), re.MULTILINE)
                    features.extend([item.strip() for item in added_items if item.strip()])
                
                # Extract Changed items from Unreleased
                changed_pattern = r"#### Changed\s*\n(.*?)(?=#### |### |## |\Z)"
                changed_match = re.search(changed_pattern, unreleased_content, re.DOTALL | re.IGNORECASE)
                if changed_match:
                    changed_items = re.findall(r"[-*]\s+(.+?)(?=\n[-*]|\n\n|\Z)", changed_match.group(1), re.MULTILINE)
                    fixes.extend([item.strip() for item in changed_items if item.strip()])
    
    # Clean and remove duplicates while preserving order
    def clean_item(item: str) -> str:
        """Clean markdown formatting from items."""
        # Remove bold markers
        item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)
        # Remove code blocks
        item = re.sub(r'`(.+?)`', r'\1', item)
        # Remove links [text](url) -> text
        item = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', item)
        # Remove checkmarks and emojis at start
        item = re.sub(r'^[✅❌🔧✨📋🎯🚀\s]+', '', item)
        # Clean whitespace
        item = item.strip()
        return item
    
    # Clean all items first
    features = [clean_item(item) for item in features if clean_item(item)]
    fixes = [clean_item(item) for item in fixes if clean_item(item)]
    upcoming = [clean_item(item) for item in upcoming if clean_item(item)]
    
    # Remove duplicates while preserving order (case-insensitive, normalized)
    def normalize_for_dedup(text: str) -> str:
        """Normalize text for duplicate detection."""
        # Remove special chars, lowercase, strip
        normalized = re.sub(r'[^\w\s]', '', text.lower().strip())
        # Remove extra spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized
    
    seen_features = set()
    unique_features = []
    for item in features:
        norm = normalize_for_dedup(item)
        if norm and norm not in seen_features and len(norm) > 3:  # Minimum length
            seen_features.add(norm)
            unique_features.append(item)
    features = unique_features
    
    seen_fixes = set()
    unique_fixes = []
    for item in fixes:
        norm = normalize_for_dedup(item)
        if norm and norm not in seen_fixes and len(norm) > 3:  # Minimum length
            seen_fixes.add(norm)
            unique_fixes.append(item)
    fixes = unique_fixes
    
    seen_upcoming = set()
    unique_upcoming = []
    for item in upcoming:
        norm = normalize_for_dedup(item)
        if norm and norm not in seen_upcoming and len(norm) > 3:  # Minimum length
            seen_upcoming.add(norm)
            unique_upcoming.append(item)
    upcoming = unique_upcoming
    
    # Generate title (always in English)
    if latest_date:
        title = f"IgnisBot Development Update - {latest_date}"
    else:
        # Use most recent file modification date
        if file_times:
            most_recent_file = max(file_times.items(), key=lambda x: x[1])
            title = f"IgnisBot Development Update - {most_recent_file[1].strftime('%Y-%m-%d')}"
        else:
            title = f"IgnisBot Development Update - {datetime.now().strftime('%Y-%m-%d')}"
    
    # Generate description (always in English)
    description_parts = []
    if features:
        description_parts.append(f"**{len(features)} new feature(s)** implemented")
    if fixes:
        description_parts.append(f"**{len(fixes)} improvement(s)** and bug fix(es)")
    if upcoming:
        description_parts.append(f"**{len(upcoming)} feature(s)** planned for future updates")
    
    if description_parts:
        description = "This update includes " + ", ".join(description_parts) + "."
    else:
        description = "Development continues with ongoing improvements and optimizations."
    
    # Create comprehensive hash for change detection
    # Include content, file modification times, and counts
    hash_content = f"{combined_content[:5000]}{str(file_times)}{len(features)}{len(fixes)}{len(upcoming)}"
    import hashlib as _hashlib
    content_hash = _hashlib.md5(hash_content.encode()).hexdigest()
    
    logger.info(f"[ROADMAP] Extracted {len(features)} features, {len(fixes)} fixes, {len(upcoming)} upcoming items")
    
    return {
        "title": title,
        "description": description,
        "features": features[:15],  # Increased limit to 15 most recent
        "fixes": fixes[:15],  # Increased limit to 15 most recent
        "upcoming": upcoming[:15],  # Increased limit to 15 most recent
        "content_hash": content_hash,
        "file_times": file_times
    }


def translate_to_english(text: str) -> str:
    """
    Translate Portuguese text to English for roadmap items.
    This is a basic implementation - for production, consider using a proper translation API.
    """
    # First, check if text is already in English (simple heuristic)
    # If text contains common Portuguese words, translate it
    portuguese_indicators = [
        'monitoramento', 'validação', 'correções', 'implementar', 'melhorar',
        'sistema', 'logs', 'comandos', 'cache', 'sincronização', 'métricas',
        'performance', 'alertas', 'dashboard', 'níveis', 'contexto', 'estruturado',
        'integração', 'ferramentas', 'Monitoramento', 'Validação', 'Correções',
        'Implementar', 'Melhorar', 'Sistema', 'Logs', 'Comandos', 'Cache',
        'Sincronização', 'Métricas', 'Performance', 'Alertas', 'Dashboard',
        'Níveis', 'Contexto', 'Estruturado', 'Integração', 'Ferramentas'
    ]
    
    # Check if text contains Portuguese indicators
    has_portuguese = any(indicator.lower() in text.lower() for indicator in portuguese_indicators)
    
    # If no Portuguese indicators found and text looks like English, return as-is
    if not has_portuguese and any(word.isalpha() and word[0].isupper() for word in text.split()[:3]):
        # Likely already in English
        return text
    
    # Common phrase translations (order matters - longer phrases first)
    phrase_translations = {
        # Upcoming features specific translations
        "Monitoramento e Validação das Correções": "Monitoring and Validation of Fixes",
        "Monitorar logs por 24-48 horas para confirmar ausência de erros": "Monitor logs for 24-48 hours to confirm absence of errors",
        "Testar comandos que usam cache em diferentes cenários": "Test commands that use cache in different scenarios",
        "Validar que sincronização de comandos continua funcionando": "Validate that command synchronization continues working",
        "Implementar Health Check System Avançado": "Implement Advanced Health Check System",
        "Métricas de performance (tempo de resposta, taxa de erro)": "Performance metrics (response time, error rate)",
        "Alertas automáticos para problemas críticos": "Automatic alerts for critical issues",
        "Dashboard de monitoramento": "Monitoring dashboard",
        "Melhorar Sistema de Logging": "Improve Logging System",
        "Implementar níveis de log mais granulares": "Implement more granular log levels",
        "Adicionar contexto estruturado (user_id, command_name, duration)": "Add structured context (user_id, command_name, duration)",
        "Criar dashboard de logs ou integração com ferramentas de monitoramento": "Create log dashboard or integration with monitoring tools",
        # Common phrases
        "Documentação de agendamento": "Scheduling documentation",
        "Sistema de": "System for",
        "Comando de": "Command for",
        "Botão de": "Button for",
        "Canal de": "Channel for",
        "Melhorias no": "Improvements to",
        "Correções no": "Fixes to",
        "Implementação de": "Implementation of",
        # Common words
        "monitoramento": "monitoring",
        "Monitoramento": "Monitoring",
        "validação": "validation",
        "Validação": "Validation",
        "correções": "fixes",
        "Correções": "Fixes",
        "implementar": "implement",
        "Implementar": "Implement",
        "melhorar": "improve",
        "Melhorar": "Improve",
        "sistema": "system",
        "Sistema": "System",
        "logs": "logs",
        "Logs": "Logs",
        "comandos": "commands",
        "Comandos": "Commands",
        "cache": "cache",
        "Cache": "Cache",
        "sincronização": "synchronization",
        "Sincronização": "Synchronization",
        "métricas": "metrics",
        "Métricas": "Metrics",
        "performance": "performance",
        "Performance": "Performance",
        "alertas": "alerts",
        "Alertas": "Alerts",
        "dashboard": "dashboard",
        "Dashboard": "Dashboard",
        "níveis": "levels",
        "Níveis": "Levels",
        "contexto": "context",
        "Contexto": "Context",
        "estruturado": "structured",
        "Estruturado": "Structured",
        "integração": "integration",
        "Integração": "Integration",
        "ferramentas": "tools",
        "Ferramentas": "Tools",
        "documentação": "documentation",
        "Documentação": "Documentation",
        "agendamento": "scheduling",
        "Agendamento": "Scheduling",
        "implementação": "implementation",
        "Implementação": "Implementation",
        "melhorias": "improvements",
        "Melhorias": "Improvements",
        "funcionalidades": "features",
        "Funcionalidades": "Features",
        "comando": "command",
        "Comando": "Command",
        "botão": "button",
        "Botão": "Button",
        "canal": "channel",
        "Canal": "Channel",
        "atualização": "update",
        "Atualização": "Update",
        "desenvolvimento": "development",
        "Desenvolvimento": "Development",
        "de": "of",
        "De": "Of",
        "para": "for",
        "Para": "For",
        "com": "with",
        "Com": "With",
        "sem": "without",
        "Sem": "Without",
        "automação": "automation",
        "Automação": "Automation",
        "configuração": "configuration",
        "Configuração": "Configuration",
        "otimização": "optimization",
        "Otimização": "Optimization",
        "gerenciamento": "management",
        "Gerenciamento": "Management",
        "criado": "created",
        "Criado": "Created",
        "adicionado": "added",
        "Adicionado": "Added",
        "atualizado": "updated",
        "Atualizado": "Updated",
        "corrigido": "fixed",
        "Corrigido": "Fixed",
        "melhorado": "improved",
        "Melhorado": "Improved",
        "implementado": "implemented",
        "Implementado": "Implemented",
    }
    
    # Simple word replacement (basic approach)
    # Replace longer phrases first, then individual words
    result = text
    
    # Replace common phrases (longer first to avoid partial matches)
    for pt_phrase, en_phrase in sorted(phrase_translations.items(), key=lambda x: len(x[0]), reverse=True):
        if pt_phrase in result:
            result = result.replace(pt_phrase, en_phrase)
    
    # If still contains Portuguese words, try word-by-word replacement
    # Only if the result still looks like Portuguese
    if any(word in result.lower() for word in ['monitoramento', 'validação', 'correções', 'implementar', 'melhorar']):
        # Try individual word replacement for remaining words
        word_translations = {
            "monitoramento": "monitoring",
            "validação": "validation",
            "correções": "fixes",
            "implementar": "implement",
            "melhorar": "improve",
            "sistema": "system",
            "logs": "logs",
            "comandos": "commands",
            "cache": "cache",
            "sincronização": "synchronization",
            "métricas": "metrics",
            "performance": "performance",
            "alertas": "alerts",
            "dashboard": "dashboard",
            "níveis": "levels",
            "contexto": "context",
            "estruturado": "structured",
            "integração": "integration",
            "ferramentas": "tools",
        }
        
        for pt, en in word_translations.items():
            # Use word boundaries to avoid partial replacements
            result = re.sub(r'\b' + re.escape(pt) + r'\b', en, result, flags=re.IGNORECASE)
    
    return result


def format_roadmap_items(items: List[str]) -> str:
    """Format a list of items for Discord embed (always in English)."""
    if not items:
        return "None"
    
    # Format as bullet points, limit length
    formatted = []
    for item in items:
        # Clean up markdown formatting first
        item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)  # Remove bold
        item = re.sub(r'`(.+?)`', r'\1', item)  # Remove code blocks
        item = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', item)  # Remove links [text](url) -> text
        item = item.strip()
        
        # Translate to English if needed (ALWAYS translate to ensure English)
        item = translate_to_english(item)
        
        # Final cleanup - remove any remaining Portuguese indicators
        if item:
            formatted.append(f"• {item}")
    
    result = "\n".join(formatted)
    
    # Discord embed field limit is 1024 characters
    if len(result) > 1000:
        result = result[:1000] + "\n... (more in documentation)"
    
    return result

