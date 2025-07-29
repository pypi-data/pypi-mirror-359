"""
User name resolution utilities.

This module provides centralized functionality for resolving and mapping
user names from configuration groups, avoiding code duplication across
different components.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from ..template_processor.data_models import UserStatistics

logger = logging.getLogger(__name__)


class UserNameResolver:
    """Centralized utility for user name resolution and mapping."""
    
    def __init__(self, config_manager=None):
        """Initialize name resolver with config manager."""
        self.config_manager = config_manager
    
    def apply_user_group_names(self, 
                              users: List[UserStatistics], 
                              user_group: str) -> List[UserStatistics]:
        """
        Apply user group name mappings to a list of UserStatistics objects.
        
        Args:
            users: List of UserStatistics objects to process
            user_group: Name of the user group configuration to use
            
        Returns:
            List of UserStatistics with names replaced according to configuration
        """
        if user_group == "all" or not self.config_manager:
            return users
        
        try:
            user_group_config = self.config_manager.load_user_group(user_group)
            users_config = user_group_config.get('users', {})
            
            return [
                UserStatistics(
                    user_id=user.user_id,
                    name=users_config.get(user.user_id, user.name),
                    messages=user.messages,
                    percentage=user.percentage
                )
                for user in users
            ]
            
        except Exception as e:
            logger.warning(f"Failed to apply user group names '{user_group}': {e}")
            return users
    
    def apply_user_group_names_to_dict_list(self, 
                                           users_data: List[Dict[str, Any]], 
                                           user_group: str) -> List[UserStatistics]:
        """
        Apply user group name mappings to a list of user data dictionaries.
        
        Args:
            users_data: List of user data dictionaries
            user_group: Name of the user group configuration to use
            
        Returns:
            List of UserStatistics with names replaced according to configuration
        """
        if user_group == "all" or not self.config_manager:
            return [
                UserStatistics(
                    user_id=user['user_id'],
                    name=user['name'],
                    messages=user['messages'],
                    percentage=user['percentage']
                )
                for user in users_data
            ]
        
        try:
            user_group_config = self.config_manager.load_user_group(user_group)
            users_config = user_group_config.get('users', {})
            
            return [
                UserStatistics(
                    user_id=user['user_id'],
                    name=users_config.get(user['user_id'], user['name']),
                    messages=user['messages'],
                    percentage=user['percentage']
                )
                for user in users_data
            ]
            
        except Exception as e:
            logger.warning(f"Failed to apply user group names '{user_group}': {e}")
            return [
                UserStatistics(
                    user_id=user['user_id'],
                    name=user['name'],
                    messages=user['messages'],
                    percentage=user['percentage']
                )
                for user in users_data
            ]
    
    def filter_and_map_users_by_group(self, 
                                     users: List[UserStatistics], 
                                     user_group: str) -> List[UserStatistics]:
        """
        Filter users by user group and apply name mappings.
        Combines filtering and name resolution in one step.
        
        Args:
            users: List of UserStatistics objects to filter and map
            user_group: Name of the user group configuration to use
            
        Returns:
            Filtered list with names replaced according to configuration
        """
        if user_group == "all" or not self.config_manager:
            return users
        
        try:
            user_group_config = self.config_manager.load_user_group(user_group)
            users_config = user_group_config.get('users', {})
            allowed_user_ids = set(users_config.keys())
            
            filtered_users = []
            for user in users:
                if user.user_id in allowed_user_ids:
                    # Apply name mapping from configuration
                    config_name = users_config.get(user.user_id, user.name)
                    
                    filtered_users.append(UserStatistics(
                        user_id=user.user_id,
                        name=config_name,
                        messages=user.messages,
                        percentage=user.percentage
                    ))
            
            return filtered_users
            
        except Exception as e:
            logger.warning(f"Failed to filter and map users for group '{user_group}': {e}")
            return users
    
    def get_mapped_name(self, user_id: int, current_name: str, user_group: str) -> str:
        """
        Get mapped name for a single user based on user group configuration.
        
        Args:
            user_id: User ID to look up
            current_name: Current name of the user
            user_group: Name of the user group configuration
            
        Returns:
            Mapped name from configuration or original name if not found
        """
        if user_group == "all" or not self.config_manager:
            return current_name
        
        try:
            user_group_config = self.config_manager.load_user_group(user_group)
            users_config = user_group_config.get('users', {})
            return users_config.get(user_id, current_name)
            
        except Exception as e:
            logger.warning(f"Failed to get mapped name for user {user_id}: {e}")
            return current_name 