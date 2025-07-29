"""Configuration group management module.

This module provides functionality for loading and managing different types of
configuration groups including monitoring groups, user groups, reporting groups, and templates.
Scheduler functionality has been removed in v2.2.
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from .config_loader import ConfigLoader, ConfigurationError


logger = logging.getLogger(__name__)


class GroupManager:
    """Manages different types of configuration groups."""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize group manager with config loader."""
        self.loader = config_loader
        self._group_cache = {}
    
    def load_monitoring_group(self, group_name: str) -> Dict[str, Any]:
        """Load monitoring group configuration."""
        file_path = self.loader.config_root / "monitoring_groups" / f"{group_name}.py"
        config = self.loader.load_python_config(file_path)
        
        # Validate group type
        if config.get("group_type") != "monitoring_group":
            raise ConfigurationError(
                f"Monitoring group file must have group_type='monitoring_group'. "
                f"File: {file_path}"
            )
        
        return config
    
    def load_user_group(self, group_name: str) -> Dict[str, Any]:
        """Load user group configuration."""
        file_path = self.loader.config_root / "user_groups" / f"{group_name}.py"
        config = self.loader.load_python_config(file_path)
        
        # Validate group type
        if config.get("group_type") != "user_group":
            raise ConfigurationError(
                f"User group file must have group_type='user_group'. "
                f"File: {file_path}"
            )
        
        return config
    
    def load_reporting_group(self, group_name: str) -> Dict[str, Any]:
        """Load reporting group configuration."""
        file_path = self.loader.config_root / "reporting_groups" / f"{group_name}.py"
        config = self.loader.load_python_config(file_path)
        
        # Validate group type
        if config.get("group_type") != "reporting_group":
            raise ConfigurationError(
                f"Reporting group file must have group_type='reporting_group'. "
                f"File: {file_path}"
            )
        
        return config
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load display template configuration."""
        file_path = self.loader.config_root / "result_display_templates" / f"{template_name}.py"
        config = self.loader.load_python_config(file_path)
        
        # Validate group type
        if config.get("group_type") != "template":
            raise ConfigurationError(
                f"Template file must have group_type='template'. "
                f"File: {file_path}"
            )
        
        return config
    
    def list_groups(self, group_type: Optional[str] = None) -> Dict[str, List[str]]:
        """List all available groups by type."""
        group_types = {
            "monitoring": "monitoring_groups",
            "user": "user_groups", 
            "reporting": "reporting_groups",
            "template": "result_display_templates"
        }
        
        if group_type and group_type not in group_types:
            raise ConfigurationError(f"Unknown group type: {group_type}")
        
        result = {}
        types_to_check = [group_type] if group_type else group_types.keys()
        
        for gtype in types_to_check:
            folder_name = group_types[gtype]
            folder_path = self.loader.config_root / folder_name
            
            groups = []
            if folder_path.exists():
                for file_path in folder_path.glob("*.py"):
                    if file_path.name != "__init__.py":
                        group_name = file_path.stem
                        groups.append(group_name)
            
            result[gtype] = sorted(groups)
        
        return result
    
    def list_monitoring_groups(self) -> List[str]:
        """List available monitoring groups."""
        return self._list_groups_by_type("monitoring_groups")
    
    def list_user_groups(self) -> List[str]:
        """List available user groups."""
        return self._list_groups_by_type("user_groups")
    
    def list_reporting_groups(self) -> List[str]:
        """List available reporting groups."""
        return self._list_groups_by_type("reporting_groups")
    
    def list_templates(self) -> List[str]:
        """List available templates."""
        return self._list_groups_by_type("result_display_templates")
    
    def _list_groups_by_type(self, group_type_dir: str) -> List[str]:
        """List groups in a specific directory."""
        groups = []
        group_dir = self.loader.config_root / group_type_dir
        
        if group_dir.exists():
            for file_path in group_dir.glob("*.py"):
                if file_path.name != "__init__.py":
                    groups.append(file_path.stem)
        
        return sorted(groups)
    
    def calculate_monitoring_groups_hash(self, group_names: List[str]) -> str:
        """Calculate hash for monitoring group combination."""
        from ..utils import calculate_monitoring_groups_hash
        return calculate_monitoring_groups_hash(group_names)
    
    def group_exists(self, group_type: str, group_name: str) -> bool:
        """Check if a specific group exists."""
        type_mappings = {
            "monitoring": "monitoring_groups",
            "user": "user_groups",
            "reporting": "reporting_groups",
            "template": "result_display_templates"
        }
        
        if group_type not in type_mappings:
            return False
        
        folder_name = type_mappings[group_type]
        return self.loader.config_exists(folder_name, group_name)
    
    def get_group_path(self, group_type: str, group_name: str) -> Path:
        """Get path to a specific group configuration file."""
        type_mappings = {
            "monitoring": "monitoring_groups",
            "user": "user_groups",
            "reporting": "reporting_groups",
            "template": "result_display_templates"
        }
        
        if group_type not in type_mappings:
            raise ConfigurationError(f"Unknown group type: {group_type}")
        
        folder_name = type_mappings[group_type]
        return self.loader.get_config_path(folder_name, group_name)
    
    def get_group_statistics(self) -> Dict[str, Any]:
        """Get statistics about configuration groups."""
        stats = {
            "total_groups": 0,
            "by_type": {},
            "auto_discovery_groups": []
        }
        
        groups = self.list_groups()
        
        for group_type, group_list in groups.items():
            stats["by_type"][group_type] = len(group_list)
            stats["total_groups"] += len(group_list)
            
            # Check for auto-discovery groups
            for group_name in group_list:
                try:
                    if group_type == "monitoring":
                        config = self.load_monitoring_group(group_name)
                    elif group_type == "user":
                        config = self.load_user_group(group_name)
                    elif group_type == "reporting":
                        config = self.load_reporting_group(group_name)
                    else:
                        continue
                    
                    if config.get("auto_discovery", False):
                        stats["auto_discovery_groups"].append(f"{group_type}:{group_name}")
                except Exception:
                    continue
        
        return stats 