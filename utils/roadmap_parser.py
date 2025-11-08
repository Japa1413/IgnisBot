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


def get_latest_roadmap_data() -> Dict[str, any]:
    """
    Extract roadmap data from all documentation files.
    
    Returns:
        Dictionary with title, description, features, fixes, and upcoming
    """
    all_content = []
    
    # Read all relevant documentation files
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
    
    if not all_content:
        logger.warning("No documentation files found")
        return {
            "title": "Roadmap Update",
            "description": "No recent updates found in documentation.",
            "features": [],
            "fixes": [],
            "upcoming": []
        }
    
    # Combine all content
    combined_content = "\n\n".join(all_content)
    
    # Extract information
    features = extract_features(combined_content)
    fixes = extract_fixes(combined_content)
    upcoming = extract_upcoming(combined_content)
    
    # Get the most recent date from CHANGELOG
    latest_date = None
    if CHANGELOG_FILE.exists():
        changelog_content = read_documentation_file(CHANGELOG_FILE)
        if changelog_content:
            # Look for date patterns
            date_pattern = r"##\s+\[?(\d{4}-\d{2}-\d{2})\]?"
            dates = re.findall(date_pattern, changelog_content)
            if dates:
                latest_date = dates[0]
    
    # Generate title
    if latest_date:
        title = f"IgnisBot Development Update - {latest_date}"
    else:
        title = f"IgnisBot Development Update - {datetime.now().strftime('%Y-%m-%d')}"
    
    # Generate description
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
    
    return {
        "title": title,
        "description": description,
        "features": features[:10],  # Limit to 10 most recent
        "fixes": fixes[:10],  # Limit to 10 most recent
        "upcoming": upcoming[:10]  # Limit to 10 most recent
    }


def format_roadmap_items(items: List[str]) -> str:
    """Format a list of items for Discord embed."""
    if not items:
        return "None"
    
    # Format as bullet points, limit length
    formatted = []
    for item in items:
        # Clean up markdown formatting
        item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)  # Remove bold
        item = re.sub(r'`(.+?)`', r'\1', item)  # Remove code blocks
        item = item.strip()
        if item:
            formatted.append(f"• {item}")
    
    result = "\n".join(formatted)
    
    # Discord embed field limit is 1024 characters
    if len(result) > 1000:
        result = result[:1000] + "\n... (more in documentation)"
    
    return result

