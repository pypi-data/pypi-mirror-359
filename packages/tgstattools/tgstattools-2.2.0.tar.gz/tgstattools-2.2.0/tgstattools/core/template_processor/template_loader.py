"""
Template loading and validation for TgStatTools.

This module handles loading template configurations from files
and validating their structure and required fields.
"""

import logging
from typing import Dict, Any, Optional
from ..config_manager import ConfigManager

logger = logging.getLogger(__name__)


class TemplateLoader:
    """Handles template loading and validation."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize template loader."""
        self.config_manager = config_manager or ConfigManager()
        self._template_cache = {}
        
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load and validate a display template."""
        if template_name in self._template_cache:
            return self._template_cache[template_name]
            
        logger.debug(f"Loading template: {template_name}")
        
        try:
            template_config = self.config_manager.load_template(template_name)
            self.validate_template(template_config, template_name)
            self._template_cache[template_name] = template_config
            return template_config
            
        except Exception as e:
            logger.error(f"Failed to load template '{template_name}': {e}")
            raise
    
    def validate_template(self, template: Dict[str, Any], name: str) -> None:
        """Validate template structure and required fields."""
        required_sections = ['filters', 'sorting', 'formatting', 'options']
        
        for section in required_sections:
            if section not in template:
                raise ValueError(f"Template '{name}' missing required section: {section}")
        
        # Validate filters section
        filters = template['filters']
        for entity_type in ['users', 'chats']:
            if entity_type not in filters:
                raise ValueError(f"Template '{name}' missing filters.{entity_type}")
            
            entity_filters = filters[entity_type]
            if 'min_messages' not in entity_filters:
                raise ValueError(f"Template '{name}' missing filters.{entity_type}.min_messages")
            if 'show_zero_activity' not in entity_filters:
                raise ValueError(f"Template '{name}' missing filters.{entity_type}.show_zero_activity")
        
        # Validate sorting section
        sorting = template['sorting']
        for entity_type in ['users', 'chats']:
            if entity_type not in sorting:
                raise ValueError(f"Template '{name}' missing sorting.{entity_type}")
            if sorting[entity_type] not in ['asc', 'desc']:
                raise ValueError(f"Template '{name}' invalid sorting.{entity_type}: must be 'asc' or 'desc'")
        
        # Validate formatting section
        formatting = template['formatting']
        required_format_keys = [
            'header', 'total', 'user_section_header', 'user_line',
            'chat_section_header', 'chat_line'
        ]
        for key in required_format_keys:
            if key not in formatting:
                raise ValueError(f"Template '{name}' missing formatting.{key}")
    
    def clear_cache(self) -> None:
        """Clear template cache."""
        self._template_cache.clear()
    
    def get_cached_templates(self) -> list:
        """Get list of cached template names."""
        return list(self._template_cache.keys()) 