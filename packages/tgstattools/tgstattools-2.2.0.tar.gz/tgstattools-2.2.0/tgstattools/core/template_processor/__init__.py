"""
Template processing engine for formatting and displaying statistics data.

This module provides a unified interface for template processing,
delegating to specialized components for different responsibilities.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from ..config_manager import ConfigManager
from .data_models import StatisticsData, UserStatistics, ChatStatistics
from .template_loader import TemplateLoader
from .data_filter import DataFilter  
from .message_formatter import MessageFormatter
from .percentage_calculator import PercentageCalculator

logger = logging.getLogger(__name__)

# Export main classes and data models
__all__ = [
    'TemplateProcessor', 'StatisticsData', 'UserStatistics', 'ChatStatistics',
    'TemplateLoader', 'DataFilter', 'MessageFormatter', 'PercentageCalculator'
]


class TemplateProcessor:
    """Unified interface for template processing."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize template processor with specialized components."""
        self.config_manager = config_manager or ConfigManager()
        
        # Initialize specialized components
        self.template_loader = TemplateLoader(self.config_manager)
        self.data_filter = DataFilter()
        self.message_formatter = MessageFormatter()
        
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load and validate a display template."""
        return self.template_loader.load_template(template_name)
    
    def filter_and_sort_data(self, data: StatisticsData, template: Dict[str, Any]) -> StatisticsData:
        """Apply template filters and sorting to statistics data."""
        return self.data_filter.filter_and_sort_data(data, template)
    
    def format_statistics(self, data: StatisticsData, template_name: str, 
                         user_group: str = None, monitoring_group: str = None) -> str:
        """Format statistics data using specified template."""
        logger.debug(f"Formatting statistics with template: {template_name}")
        
        template = self.load_template(template_name)
        filtered_data = self.filter_and_sort_data(data, template)
        return self.message_formatter.format_statistics(filtered_data, template, user_group, monitoring_group)
    
    def format_as_json(self, data: StatisticsData, template_name: str) -> str:
        """Format statistics data as JSON."""
        logger.debug(f"Formatting statistics as JSON with template: {template_name}")
        
        template = self.load_template(template_name)
        filtered_data = self.filter_and_sort_data(data, template)
        return self.message_formatter.format_as_json(filtered_data, template_name)
    
    def split_long_message(self, message: str, max_length: int = 4096) -> List[str]:
        """Split long message into chunks for Telegram."""
        return self.message_formatter.split_long_message(message, max_length)
    
    def recalculate_percentages(self, users: List[UserStatistics], chats: List[ChatStatistics]) -> Tuple[List[UserStatistics], List[ChatStatistics]]:
        """Recalculate percentages after filtering."""
        return self.data_filter.recalculate_percentages(users, chats)
    
    # Template management methods
    def clear_template_cache(self) -> None:
        """Clear template cache."""
        self.template_loader.clear_cache()
    
    def get_cached_templates(self) -> List[str]:
        """Get list of cached template names."""
        return self.template_loader.get_cached_templates() 