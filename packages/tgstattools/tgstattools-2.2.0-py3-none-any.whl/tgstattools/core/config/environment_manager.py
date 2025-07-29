"""
Environment configuration management.

This module handles loading and management of environment variables
and .env file processing.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class EnvironmentManager:
    """Manages environment variables and .env file configuration."""
    
    def __init__(self, config_root: Path = None):
        """Initialize environment manager."""
        self.config_root = config_root or Path("config")
        self._env_loaded = False
        
        # Automatically load .env file if it exists
        self.load_env_file()
    
    def load_env_file(self) -> bool:
        """Load environment variables from .env file."""
        env_file = self.config_root / ".env"
        
        if env_file.exists():
            load_dotenv(env_file)
            logger.debug(f"Loaded environment variables from {env_file}")
            self._env_loaded = True
            return True
        else:
            logger.debug(f".env file not found at {env_file}")
            return False
    
    def get_env_value(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable value."""
        return os.getenv(key, default)
    
    def load_env_config(self) -> Dict[str, str]:
        """Load environment configuration from .env file."""
        env_config = {}
        env_keys = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'SESSION_STRING', 'DATABASE_PATH']
        
        for key in env_keys:
            value = self.get_env_value(key)
            if value:
                env_config[key] = value
        
        return env_config
    
    def validate_required_env_vars(self, required_vars: list = None) -> Dict[str, bool]:
        """
        Validate that required environment variables are set.
        
        Args:
            required_vars: List of required environment variable names.
                          If None, uses default Telegram API variables.
        
        Returns:
            Dict mapping variable names to whether they are set
        """
        if required_vars is None:
            required_vars = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH']
        
        validation_result = {}
        
        for var in required_vars:
            value = self.get_env_value(var)
            is_set = value is not None and value.strip() != ""
            validation_result[var] = is_set
            
            if not is_set:
                logger.warning(f"Required environment variable '{var}' is not set")
        
        return validation_result
    
    def get_database_path(self) -> str:
        """Get database path from environment or default."""
        return self.get_env_value('DATABASE_PATH', 'data/statistics.db')
    
    def get_telegram_config(self) -> Dict[str, Optional[str]]:
        """Get Telegram API configuration from environment."""
        return {
            'api_id': self.get_env_value('TELEGRAM_API_ID'),
            'api_hash': self.get_env_value('TELEGRAM_API_HASH'),
            'session_string': self.get_env_value('SESSION_STRING'),
        }
    
    def env_file_exists(self) -> bool:
        """Check if .env file exists."""
        return (self.config_root / ".env").exists()
    
    def get_env_file_path(self) -> Path:
        """Get path to .env file."""
        return self.config_root / ".env"
    
    def get_all_env_vars(self) -> Dict[str, str]:
        """Get all environment variables as a dictionary."""
        return dict(os.environ)
    
    def set_env_var(self, key: str, value: str) -> None:
        """Set environment variable (for current session only)."""
        os.environ[key] = value
        logger.debug(f"Set environment variable: {key}")
    
    def unset_env_var(self, key: str) -> None:
        """Unset environment variable (for current session only)."""
        if key in os.environ:
            del os.environ[key]
            logger.debug(f"Unset environment variable: {key}")
    
    def get_env_summary(self) -> Dict[str, any]:
        """Get summary of environment configuration status."""
        summary = {
            "env_file_exists": self.env_file_exists(),
            "env_file_loaded": self._env_loaded,
            "env_file_path": str(self.get_env_file_path()),
            "required_vars_status": self.validate_required_env_vars(),
            "telegram_config_complete": True,
            "database_path": self.get_database_path()
        }
        
        # Check if Telegram config is complete
        telegram_config = self.get_telegram_config()
        summary["telegram_config_complete"] = all([
            telegram_config.get('api_id'),
            telegram_config.get('api_hash')
        ])
        
        return summary 