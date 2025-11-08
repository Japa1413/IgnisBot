"""
Configuration Service - Manages editable role-to-rank mappings and system configuration.

This service provides an easy way to edit Discord role to rank mappings
without modifying code. All configuration is stored in JSON files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# Path to configuration file
CONFIG_DIR = Path(__file__).parent.parent / "config"
ROLES_RANKS_CONFIG = CONFIG_DIR / "roles_ranks.json"


class ConfigService:
    """Service for managing editable configuration"""
    
    def __init__(self):
        """Initialize configuration service"""
        self.config_dir = CONFIG_DIR
        self.config_file = ROLES_RANKS_CONFIG
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self._config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"Configuration loaded from {self.config_file}")
                    return config
            else:
                # Create default configuration
                logger.warning(f"Configuration file not found, creating default at {self.config_file}")
                default_config = self._get_default_config()
                self._save_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}", exc_info=True)
            # Return default config on error
            return self._get_default_config()
    
    def _save_config(self, config: Dict) -> bool:
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}", exc_info=True)
            return False
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "version": "1.0",
            "last_updated": "2025-01-XX",
            "role_to_rank_mapping": {
                "High Command": {
                    "Emperor Of Mankind": "Emperor Of Mankind",
                    "Primarch": "Primarch",
                    "First Captain": "First Captain",
                    "Commander": "Commander",
                    "Preator": "Preator"
                },
                "Great Company": {
                    "Marshal": "Marshal",
                    "Consulate": "Consulate",
                    "Flamewrought": "Flamewrought",
                    "Cindermarked": "Cindermarked",
                    "Pyroclast Sentinel": "Pyroclast Sentinel"
                },
                "Company": {
                    "Captain": "Flameborne Captain",
                    "1st Lieutenant": "1st Lieutenant (Pyre Watcher)",
                    "1st Lieutenant (Pyre Watcher)": "1st Lieutenant (Pyre Watcher)",
                    "2nd Lieutenant": "2nd Lieutenant (Furnace Warden)",
                    "2nd Lieutenant (Furnace Warden)": "2nd Lieutenant (Furnace Warden)",
                    "Veteran Sergeant": "Emberblade Veteran Sergeant",
                    "Emberblade Veteran Sergeant": "Emberblade Veteran Sergeant",
                    "Legion Sergeant": "Cindershield Sergeant",
                    "Cindershield Sergeant": "Cindershield Sergeant",
                    "Flameborne Captain": "Flameborne Captain"
                },
                "Specialist": {
                    "Chaplain": "Chaplain",
                    "Techmarine": "Techmarine",
                    "Terminator Squad": "Terminator Squad",
                    "Apothecarion": "Apothecarion",
                    "Vexillarius": "Vexillarius",
                    "Destroyer": "Destroyer",
                    "Signal Marine": "Signal Marine"
                },
                "Legionaries": {
                    "Legion Elite": "Flamehardened Veteran",
                    "Legion Veteran": "Flamehardened Veteran",
                    "Support Squad": "Flamehardened Veteran",
                    "Legionary": "Ashborn Legionary",
                    "Inductii": "Inductii"
                },
                "Mortals": {
                    "Emberbrand Proving": "Emberbrand Proving",
                    "Crucible Neophyte": "Crucible Neophyte",
                    "Obsidian Trialborn": "Obsidian Trialborn",
                    "Emberbound Initiate": "Emberbound Initiate",
                    "Civitas Aspirant": "Civitas Aspirant"
                }
            },
            "role_priority": {
                "order": [
                    "Civitas Aspirant",
                    "Emberbound Initiate",
                    "Obsidian Trialborn",
                    "Crucible Neophyte",
                    "Emberbrand Proving",
                    "Inductii",
                    "Legionary",
                    "Support Squad",
                    "Legion Veteran",
                    "Legion Elite",
                    "Signal Marine",
                    "Destroyer",
                    "Vexillarius",
                    "Apothecarion",
                    "Terminator Squad",
                    "Techmarine",
                    "Chaplain",
                    "Legion Sergeant",
                    "Veteran Sergeant",
                    "2nd Lieutenant",
                    "1st Lieutenant",
                    "Captain",
                    "Pyroclast Sentinel",
                    "Cindermarked",
                    "Flamewrought",
                    "Consulate",
                    "Marshal",
                    "Preator",
                    "Commander",
                    "First Captain",
                    "Primarch",
                    "Emperor Of Mankind"
                ]
            }
        }
    
    def get_role_to_rank_map(self) -> Dict[str, str]:
        """
        Get flat dictionary mapping Discord role names to system rank names.
        
        Returns:
            Dict mapping role_name -> rank_name
        """
        mapping = {}
        role_mapping = self._config.get("role_to_rank_mapping", {})
        
        # Flatten nested structure
        for category, roles in role_mapping.items():
            if isinstance(roles, dict):
                mapping.update(roles)
        
        return mapping
    
    def get_role_priority(self) -> List[str]:
        """
        Get list of roles in priority order (lowest to highest).
        
        Returns:
            List of role names in priority order
        """
        priority_config = self._config.get("role_priority", {})
        return priority_config.get("order", [])
    
    def add_role_mapping(self, discord_role: str, system_rank: str, category: str = "Custom") -> bool:
        """
        Add or update a role-to-rank mapping.
        
        Args:
            discord_role: Discord role name
            system_rank: System rank name
            category: Category for organization (default: "Custom")
        
        Returns:
            True if successful, False otherwise
        """
        if "role_to_rank_mapping" not in self._config:
            self._config["role_to_rank_mapping"] = {}
        
        if category not in self._config["role_to_rank_mapping"]:
            self._config["role_to_rank_mapping"][category] = {}
        
        self._config["role_to_rank_mapping"][category][discord_role] = system_rank
        
        # Reload config
        self._config = self._load_config()
        
        return self._save_config(self._config)
    
    def remove_role_mapping(self, discord_role: str) -> bool:
        """
        Remove a role-to-rank mapping.
        
        Args:
            discord_role: Discord role name to remove
        
        Returns:
            True if successful, False otherwise
        """
        role_mapping = self._config.get("role_to_rank_mapping", {})
        
        for category, roles in role_mapping.items():
            if isinstance(roles, dict) and discord_role in roles:
                del roles[discord_role]
                return self._save_config(self._config)
        
        logger.warning(f"Role mapping '{discord_role}' not found")
        return False
    
    def list_all_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        List all role-to-rank mappings organized by category.
        
        Returns:
            Dict with category -> {role: rank} mappings
        """
        return self._config.get("role_to_rank_mapping", {})
    
    def reload_config(self) -> bool:
        """Reload configuration from file"""
        self._config = self._load_config()
        return True


# Singleton instance
_config_service: Optional[ConfigService] = None


def get_config_service() -> ConfigService:
    """Get singleton ConfigService instance"""
    global _config_service
    if _config_service is None:
        _config_service = ConfigService()
    return _config_service

