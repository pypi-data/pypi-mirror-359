"""
Configuration management system for TgStatTools.

This package provides a modular configuration management system with:
- ConfigLoader: Loading and parsing Python configuration files
- ConfigValidator: Validation of configuration data and schemas
- GroupManager: Management of configuration groups (monitoring, user, reporting, etc.)
- EnvironmentManager: Environment variables and .env file handling
- ConfigFactory: Creation of example configurations
- ConfigManager: Unified interface for backward compatibility
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from .config_loader import ConfigLoader, ConfigurationError
from .config_validator import ConfigValidator
from .group_manager import GroupManager
from .environment_manager import EnvironmentManager
from .config_factory import ConfigFactory


logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Unified configuration management interface.
    
    This class aggregates all configuration services and provides
    backward compatibility with the original ConfigManager API.
    """
    
    def __init__(self, config_root: Optional[Path] = None):
        """Initialize configuration manager with all services."""
        self.config_root = config_root or Path("config")
        
        # Initialize core services
        self.loader = ConfigLoader(self.config_root)
        self.validator = ConfigValidator(self.loader)
        self.groups = GroupManager(self.loader)
        self.environment = EnvironmentManager(self.config_root)
        self.factory = ConfigFactory(self.config_root)
        
        logger.debug(f"ConfigManager initialized with root: {self.config_root}")
    
    # Backward compatibility: ConfigLoader methods
    def validate_file_format(self, file_path: Path) -> None:
        """Validate that file format is allowed."""
        return self.loader.validate_file_format(file_path)
    
    def load_python_config(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from Python file with 'data = {...}' format."""
        return self.loader.load_python_config(file_path)
    
    # Backward compatibility: GroupManager methods
    def load_monitoring_group(self, group_name: str) -> Dict[str, Any]:
        """Load monitoring group configuration."""
        return self.groups.load_monitoring_group(group_name)
    
    def load_user_group(self, group_name: str) -> Dict[str, Any]:
        """Load user group configuration."""
        return self.groups.load_user_group(group_name)
    
    def load_reporting_group(self, group_name: str) -> Dict[str, Any]:
        """Load reporting group configuration."""
        return self.groups.load_reporting_group(group_name)
    
    # Schedule functionality removed in v2.2
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load display template configuration."""
        return self.groups.load_template(template_name)
    
    def list_groups(self, group_type: Optional[str] = None) -> Dict[str, List[str]]:
        """List all available groups by type."""
        return self.groups.list_groups(group_type)
    
    def list_monitoring_groups(self) -> List[str]:
        """List available monitoring groups."""
        return self.groups.list_monitoring_groups()
    
    def list_user_groups(self) -> List[str]:
        """List available user groups."""
        return self.groups.list_user_groups()
    
    def list_reporting_groups(self) -> List[str]:
        """List available reporting groups."""
        return self.groups.list_reporting_groups()
    
    def get_monitoring_groups(self) -> Dict[str, Dict[str, Any]]:
        """Get all monitoring groups configurations."""
        groups = {}
        for group_name in self.list_monitoring_groups():
            try:
                groups[group_name] = self.load_monitoring_group(group_name)
            except Exception as e:
                logger.warning(f"Failed to load monitoring group {group_name}: {e}")
        return groups
    
    def get_user_groups(self) -> Dict[str, Dict[str, Any]]:
        """Get all user groups configurations."""
        groups = {}
        for group_name in self.list_user_groups():
            try:
                groups[group_name] = self.load_user_group(group_name)
            except Exception as e:
                logger.warning(f"Failed to load user group {group_name}: {e}")
        return groups
    
    def get_reporting_groups(self) -> Dict[str, Dict[str, Any]]:
        """Get all reporting groups configurations."""
        groups = {}
        for group_name in self.list_reporting_groups():
            try:
                groups[group_name] = self.load_reporting_group(group_name)
            except Exception as e:
                logger.warning(f"Failed to load reporting group {group_name}: {e}")
        return groups
    
    def calculate_monitoring_groups_hash(self, group_names: List[str]) -> str:
        """Calculate hash for monitoring group combination."""
        return self.groups.calculate_monitoring_groups_hash(group_names)
    
    # Backward compatibility: ConfigValidator methods
    def validate_essential_configs(self) -> bool:
        """Validate essential configurations required for daemon startup."""
        return self.validator.validate_essential_configs()
    
    def validate_all_configs(self) -> List[str]:
        """Validate all configuration files and return list of errors."""
        return self.validator.validate_all_configs()
    
    def is_auto_discovery_group(self, config_data: Dict[str, Any]) -> bool:
        """Determine if a group uses auto-discovery based on content."""
        return self.validator.is_auto_discovery_group(config_data)
    
    # Backward compatibility: EnvironmentManager methods
    def get_env_value(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable value."""
        return self.environment.get_env_value(key, default)
    
    def load_env_config(self) -> Dict[str, str]:
        """Load environment configuration from .env file."""
        return self.environment.load_env_config()
    
    # Backward compatibility: ConfigFactory methods
    def create_example_configs(self, overwrite: bool = False) -> List[str]:
        """Create example configuration files."""
        return self.factory.create_example_configs(overwrite)
    
    # Backward compatibility: Legacy methods that need to be preserved
    def _load_config_file(self, file_path: str) -> Dict[str, Any]:
        """Load configuration file with format validation (legacy method)."""
        return self.loader.load_config_file(file_path)
    
    def _validate_monitoring_group(self, config: Dict[str, Any]) -> None:
        """Validate monitoring group configuration (legacy method)."""
        return self.validator.validate_monitoring_group(config)
    
    def _validate_user_group(self, config: Dict[str, Any]) -> None:
        """Validate user group configuration (legacy method)."""
        return self.validator.validate_user_group(config)
    
    # Schedule validation removed in v2.2
    
    def _validate_template(self, config: Dict[str, Any]) -> None:
        """Validate template configuration (legacy method)."""
        return self.validator.validate_template(config)
    
    def _list_groups_by_type(self, group_type_dir: str) -> List[str]:
        """List groups in a specific directory (legacy method)."""
        return self.groups._list_groups_by_type(group_type_dir)
    
    def _is_valid_time_format(self, time_str: str) -> bool:
        """Check if time string is in HH:MM format (legacy method)."""
        return self.validator._is_valid_time_format(time_str)
    
    # New enhanced methods
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all configuration services."""
        return {
            "config_root": str(self.config_root),
            "loader_stats": self.loader.get_config_stats(),
            "environment_summary": self.environment.get_env_summary(),
            "group_statistics": self.groups.get_group_statistics(),
            "validation_errors": len(self.validator.validate_all_configs()),
            "services_initialized": True
        }
    
    def get_full_configuration_report(self) -> Dict[str, Any]:
        """Get comprehensive configuration report."""
        return {
            "status": self.get_service_status(),
            "validation_errors": self.validator.validate_all_configs(),
            "groups": self.groups.list_groups(),
            "environment": self.environment.get_env_summary(),
            "essential_configs_valid": self.validator.validate_essential_configs()
        }


# Standalone function for backward compatibility
def get_env_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable value (standalone function for compatibility)."""
    import os
    return os.getenv(key, default)


# Export main classes and functions
__all__ = [
    'ConfigManager',
    'ConfigLoader', 
    'ConfigValidator',
    'GroupManager',
    'EnvironmentManager',
    'ConfigFactory',
    'ConfigurationError',
    'get_env_value'
] 