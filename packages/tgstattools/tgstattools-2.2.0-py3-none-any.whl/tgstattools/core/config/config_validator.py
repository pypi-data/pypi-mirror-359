"""
Configuration validation.

This module handles validation of configuration data and schemas
for different types of configurations (groups, schedules, templates).
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
from .config_loader import ConfigLoader, ConfigurationError


logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates configuration data and schemas."""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize validator with config loader."""
        self.loader = config_loader
    
    def validate_essential_configs(self) -> bool:
        """
        Validate essential configurations required for daemon startup.
        
        Returns:
            True if all essential configs are valid, False otherwise
        """
        try:
            # Check .env file
            env_file = self.loader.config_root / ".env"
            if not env_file.exists():
                logger.error("Missing .env file - required for Telegram API credentials")
                return False
            
                    # Schedules functionality removed in v2.2
            
            # Check if at least one monitoring group exists
            monitoring_dir = self.loader.config_root / "monitoring_groups"
            if not monitoring_dir.exists() or not list(monitoring_dir.glob("*.py")):
                logger.warning("No monitoring groups configured - data collection will not work")
            
            logger.info("Essential configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Essential configuration validation failed: {e}")
            return False
    
    def validate_all_configs(self) -> List[str]:
        """Validate all configuration files and return list of errors."""
        errors = []
        
        # Check for forbidden file formats
        errors.extend(self.loader.check_forbidden_formats())
        
        # Validate each group type
        group_folders = {
            "monitoring_groups": "monitoring_group",
            "user_groups": "user_group",
            "reporting_groups": "reporting_group", 
            # "schedules": "schedule",  # Removed in v2.2
            "result_display_templates": "template"
        }
        
        for folder_name, expected_type in group_folders.items():
            folder_path = self.loader.config_root / folder_name
            if not folder_path.exists():
                continue
                
            for file_path in folder_path.glob("*.py"):
                if file_path.name == "__init__.py":
                    continue
                    
                try:
                    config = self.loader.load_python_config(file_path)
                    
                    # Check group_type matches location
                    actual_type = config.get("group_type")
                    if actual_type != expected_type:
                        errors.append(
                            f"Group type mismatch in {file_path}: "
                            f"expected '{expected_type}', got '{actual_type}'"
                        )
                    
                    # Additional validation per type
                                # Schedule validation removed in v2.2
                    elif expected_type == "template":
                        self._validate_template_config(config, file_path, errors)
                        
                except Exception as e:
                    errors.append(f"Error loading {file_path}: {e}")
        
        return errors
    
    # Schedule validation method removed in v2.2
    
    def _validate_template_config(self, config: Dict[str, Any], file_path: Path, errors: List[str]) -> None:
        """Validate template configuration."""
        required_sections = ["filters", "sorting", "formatting", "options"]
        
        for section in required_sections:
            if section not in config:
                errors.append(f"Template missing '{section}' section: {file_path}")
    
    def _is_valid_time_format(self, time_str: str) -> bool:
        """Check if time string is in HH:MM format."""
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False
    
    def is_auto_discovery_group(self, config_data: Dict[str, Any]) -> bool:
        """
        Determine if a group uses auto-discovery based on content.
        
        Priority: explicit auto_discovery flag > missing keys
        
        Auto-discovery is enabled if:
        1. Required key is missing (chat_ids for monitoring/reporting, users for user groups)
        2. OR auto_discovery: true is explicitly set
        
        Auto-discovery is disabled if:
        1. auto_discovery: false is explicitly set (overrides missing keys)
        2. OR required keys are present and no explicit flag
        """
        group_type = config_data.get("group_type")
        
        # Check explicit auto_discovery flag first (highest priority)
        explicit_flag = config_data.get("auto_discovery")
        if explicit_flag is not None:
            return bool(explicit_flag)
        
        # If no explicit flag, check for missing required keys
        if group_type == "monitoring_group":
            return "chat_ids" not in config_data or not config_data.get("chat_ids")
        elif group_type == "user_group":
            return "users" not in config_data or not config_data.get("users")
        elif group_type == "reporting_group":
            return "chat_ids" not in config_data or not config_data.get("chat_ids")
        
        return False
    
    def validate_monitoring_group(self, config: Dict[str, Any]) -> None:
        """Validate monitoring group configuration (raises exception)."""
        required_fields = ["group_type", "description"]
        
        for field in required_fields:
            if field not in config:
                raise ConfigurationError(f"Monitoring group missing required field: {field}")
        
        if config["group_type"] != "monitoring_group":
            raise ConfigurationError("Monitoring group must have group_type='monitoring_group'")
    
    def validate_user_group(self, config: Dict[str, Any]) -> None:
        """Validate user group configuration (raises exception)."""
        required_fields = ["group_type", "description"]
        
        for field in required_fields:
            if field not in config:
                raise ConfigurationError(f"User group missing required field: {field}")
        
        if config["group_type"] != "user_group":
            raise ConfigurationError("User group must have group_type='user_group'")
    
    # Schedule validation method removed in v2.2
    
    def validate_template(self, config: Dict[str, Any]) -> None:
        """Validate template configuration (raises exception)."""
        required_fields = ["group_type", "name", "description"]
        required_sections = ["filters", "sorting", "formatting", "options"]
        
        for field in required_fields:
            if field not in config:
                raise ConfigurationError(f"Template missing required field: {field}")
        
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(f"Template missing required section: {section}")
        
        if config["group_type"] != "template":
            raise ConfigurationError("Template must have group_type='template'")
