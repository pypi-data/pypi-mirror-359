"""
Core system modules for TgStatTools.

This package contains the core functionality:
- Database operations and migrations
- Configuration management 
- Telegram API integration
- Statistics collection
- Report generation
- Template processing
- Data viewing and analysis
"""

# Import and re-export main classes for convenience
from .database import Database
from .config_manager import ConfigManager
from .statistics import StatisticsCollector
from .telegram_client import TelegramClient, TelegramClientWrapper
from .template_processor import TemplateProcessor, StatisticsData, UserStatistics, ChatStatistics
from .reporter import Reporter, ReportDeliveryError
from .data_viewer import DataViewer, DataViewError, PeriodRange

# Export main classes
__all__ = [
    # Database
    'Database',
    # Configuration
    'ConfigManager',
    # Statistics
    'StatisticsCollector',
    # Telegram
    'TelegramClient',
    'TelegramClientWrapper',
    # Template Processing
    'TemplateProcessor',
    'StatisticsData',
    'UserStatistics',
    'ChatStatistics',
    # Reporting
    'Reporter',
    'ReportDeliveryError',
    # Data Viewing
    'DataViewer',
    'DataViewError',
    'PeriodRange'
]

# Core modules are imported individually as needed 