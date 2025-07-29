"""
Statistics utilities module for TgStatTools.

This module provides utility functions for statistics operations,
including user name resolution, hash calculation, and data validation.
"""

import logging
from typing import List
from datetime import date
from ..utils import calculate_monitoring_groups_hash, calculate_percentage, validate_group_config

logger = logging.getLogger(__name__)


class StatisticsUtils:
    """Utility functions for statistics operations."""
    
    def __init__(self, telegram_client, database):
        """Initialize utils with required dependencies."""
        self.telegram_client = telegram_client
        self.database = database
        self.logger = logging.getLogger(__name__)
    
    async def get_user_name(self, user_id: int) -> str:
        """
        Get user name with caching and fallback logic.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User's display name or fallback string
        """
        try:
            user = await self.telegram_client.get_entity(user_id)
            if user.first_name and user.last_name:
                return f"{user.first_name} {user.last_name}"
            elif user.first_name:
                return user.first_name
            elif user.username:
                return f"@{user.username}"
            else:
                return f"User {user_id}"
        except Exception:
            # Fallback to generic name if user lookup fails
            return f"User {user_id}"
    
    def calculate_monitoring_groups_hash(self, groups: List[str]) -> str:
        """Calculate consistent hash for monitoring groups combination."""
        return calculate_monitoring_groups_hash(groups)
    
    def collection_exists(self, target_date: date, monitoring_groups_hash: str) -> bool:
        """
        Check if collection already exists for given date and groups.
        
        Args:
            target_date: Date to check for existing collection
            monitoring_groups_hash: Hash of monitoring groups combination
            
        Returns:
            True if collection exists, False otherwise
        """
        try:
            return self.database.collection_exists(target_date, monitoring_groups_hash)
        except Exception as e:
            self.logger.error(f"Error checking collection existence: {e}")
            return False
    
    def validate_monitoring_group_config(self, group_config: dict) -> bool:
        """Validate monitoring group configuration."""
        return validate_group_config(group_config, "monitoring_group")
    
    def is_auto_discovery_group(self, group_config: dict) -> bool:
        """
        Determine if monitoring group uses auto-discovery.
        
        Args:
            group_config: Configuration dictionary to check
            
        Returns:
            True if group uses auto-discovery
        """
        # Method 1: Missing chat_ids key
        if "chat_ids" not in group_config:
            return True
        
        # Method 2: Explicit auto_discovery flag
        if group_config.get("auto_discovery") is True:
            return True
        
        return False
    
    def calculate_percentage(self, part: int, total: int) -> float:
        """Calculate percentage with proper handling of edge cases."""
        return calculate_percentage(part, total) 