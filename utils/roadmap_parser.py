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
        # Extract list items (lines starting with -, *, or numbered)
        item_pattern = r"[-*]\s+(.+?)(?=\n[-*]|\n\n|\Z)"
        items = re.findall(item_pattern, section_content, re.MULTILINE)
        # Also try numbered lists
        numbered_pattern = r"^\d+\.\s+(.+?)$"
        numbered_items = re.findall(numbered_pattern, section_content, re.MULTILINE)
        items.extend(numbered_items)
    
    # Clean items
    items = [item.strip() for item in items if item.strip()]
    return items


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
    
    # Remove duplicates while preserving order
    seen_features = set()
    unique_features = []
    for item in features:
        item_lower = item.lower()
        if item_lower not in seen_features:
            seen_features.add(item_lower)
            unique_features.append(item)
    features = unique_features
    
    seen_fixes = set()
    unique_fixes = []
    for item in fixes:
        item_lower = item.lower()
        if item_lower not in seen_fixes:
            seen_fixes.add(item_lower)
            unique_fixes.append(item)
    fixes = unique_fixes
    
    seen_upcoming = set()
    unique_upcoming = []
    for item in upcoming:
        item_lower = item.lower()
        if item_lower not in seen_upcoming:
            seen_upcoming.add(item_lower)
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
    # Common translations (expanded dictionary)
    translations = {
        # Common words
        "documentação": "documentation",
        "Documentação": "Documentation",
        "agendamento": "scheduling",
        "Agendamento": "Scheduling",
        "implementação": "implementation",
        "Implementação": "Implementation",
        "melhorias": "improvements",
        "Melhorias": "Improvements",
        "correções": "fixes",
        "Correções": "Fixes",
        "funcionalidades": "features",
        "Funcionalidades": "Features",
        "sistema": "system",
        "Sistema": "System",
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
        # Common phrases
        "de": "of",
        "De": "Of",
        "para": "for",
        "Para": "For",
        "com": "with",
        "Com": "With",
        "sem": "without",
        "Sem": "Without",
        # Technical terms
        "automação": "automation",
        "Automação": "Automation",
        "integração": "integration",
        "Integração": "Integration",
        "configuração": "configuration",
        "Configuração": "Configuration",
        "otimização": "optimization",
        "Otimização": "Optimization",
        "monitoramento": "monitoring",
        "Monitoramento": "Monitoring",
        "gerenciamento": "management",
        "Gerenciamento": "Management",
        # Actions
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
    
    # Replace common phrases
    phrase_translations = {
        "Documentação de agendamento": "Scheduling documentation",
        "Sistema de": "System for",
        "Comando de": "Command for",
        "Botão de": "Button for",
        "Canal de": "Channel for",
        "Melhorias no": "Improvements to",
        "Correções no": "Fixes to",
        "Implementação de": "Implementation of",
    }
    
    for pt_phrase, en_phrase in phrase_translations.items():
        result = result.replace(pt_phrase, en_phrase)
    
    # Replace individual words
    for pt, en in translations.items():
        # Use word boundaries to avoid partial replacements
        result = re.sub(r'\b' + re.escape(pt) + r'\b', en, result)
    
    return result


def format_roadmap_items(items: List[str]) -> str:
    """Format a list of items for Discord embed (always in English)."""
    if not items:
        return "None"
    
    # Format as bullet points, limit length
    formatted = []
    for item in items:
        # Clean up markdown formatting
        item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)  # Remove bold
        item = re.sub(r'`(.+?)`', r'\1', item)  # Remove code blocks
        item = item.strip()
        
        # Translate to English if needed
        item = translate_to_english(item)
        
        if item:
            formatted.append(f"• {item}")
    
    result = "\n".join(formatted)
    
    # Discord embed field limit is 1024 characters
    if len(result) > 1000:
        result = result[:1000] + "\n... (more in documentation)"
    
    return result

