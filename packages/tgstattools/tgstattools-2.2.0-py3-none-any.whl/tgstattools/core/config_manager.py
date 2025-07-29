"""
Configuration management system for TgStatTools.

This module provides backward compatibility for the refactored configuration system.
The functionality has been moved to tgstattools.core.config package.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from .config import ConfigManager as NewConfigManager, ConfigurationError, get_env_value

logger = logging.getLogger(__name__)


# Backward compatibility - delegate to new modular system
class ConfigManager(NewConfigManager):
    """
    Manages loading and validation of configuration files.
    
    This class now inherits from the new modular ConfigManager
    and provides full backward compatibility.
    """
    pass


# Re-export for backward compatibility
__all__ = ['ConfigManager', 'ConfigurationError', 'get_env_value'] 