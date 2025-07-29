"""
Data processing functionality for data viewing.

This module provides:
- User group filtering and processing
- Data transformation and formatting
- Statistics data structure creation
- Data validation and cleanup
"""

import logging
from typing import Dict, Any, List, Optional

from .period_manager import PeriodRange
from ..template_processor import StatisticsData, UserStatistics, ChatStatistics
from ..user_utils import UserNameResolver

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles data processing, filtering, and transformation operations."""
    
    def __init__(self, config_manager=None):
        """Initialize data processor."""
        self.config_manager = config_manager
        self.name_resolver = UserNameResolver(config_manager)
    
    async def process_statistics_data(self, 
                                    raw_data: Dict[str, Any],
                                    period_range: PeriodRange,
                                    user_group: str = "all") -> StatisticsData:
        """Process raw data into StatisticsData structure."""
        logger.debug(f"Processing statistics data for period: {period_range.description}")
        
        try:
            # Filter users if specific user group is requested
            filtered_users = await self._filter_users_by_group(raw_data['users'], user_group)
            
            # Process chat data
            processed_chats = self._process_chat_data(raw_data['chats'])
            
            # Build StatisticsData object
            statistics_data = StatisticsData(
                date=period_range.description,
                total_messages=raw_data['total_messages'],
                users=filtered_users,
                chats=processed_chats,
                monitoring_groups_used=raw_data['monitoring_groups_used'],
                collection_completed_at=raw_data.get('collection_completed_at', '')
            )
            
            logger.debug(f"Processed statistics: {len(filtered_users)} users, {len(processed_chats)} chats, {raw_data['total_messages']} total messages")
            return statistics_data
            
        except Exception as e:
            logger.error(f"Failed to process statistics data: {e}")
            raise
    
    # Mock data generation removed - use real database data only
    
    async def _filter_users_by_group(self, users_data: List[Dict[str, Any]], user_group: str) -> List[UserStatistics]:
        """Filter users based on user group configuration."""
        if user_group == "all":
            # Return all users
            return [
                UserStatistics(
                    user_id=user['user_id'],
                    name=user['name'],
                    messages=user['messages'],
                    percentage=user['percentage']
                )
                for user in users_data
            ]
        
        if not self.config_manager:
            logger.warning("Config manager not configured, returning all users")
            return [
                UserStatistics(
                    user_id=user['user_id'],
                    name=user['name'],
                    messages=user['messages'],
                    percentage=user['percentage']
                )
                for user in users_data
            ]
        
        # Filter based on user group configuration
        try:
            user_group_config = self.config_manager.load_user_group(user_group)
            
            if self.config_manager.is_auto_discovery_group(user_group_config):
                return await self._filter_auto_discovery_users(users_data, user_group_config)
            else:
                return await self._filter_explicit_users(users_data, user_group_config)
                
        except Exception as e:
            logger.error(f"Failed to filter users by group '{user_group}': {e}")
            # Fallback to all users
            return [
                UserStatistics(
                    user_id=user['user_id'],
                    name=user['name'],
                    messages=user['messages'],
                    percentage=user['percentage']
                )
                for user in users_data
            ]
    
    async def _filter_auto_discovery_users(self, users_data: List[Dict[str, Any]], 
                                         user_group_config: Dict[str, Any]) -> List[UserStatistics]:
        """Filter users for auto-discovery group."""
        filtered_users = []
        filters = user_group_config.get('filters', {})
        min_activity = filters.get('min_activity', 0)
        
        for user in users_data:
            if user['messages'] >= min_activity:
                filtered_users.append(
                    UserStatistics(
                        user_id=user['user_id'],
                        name=user['name'],
                        messages=user['messages'],
                        percentage=user['percentage']
                    )
                )
        
        logger.debug(f"Auto-discovery filter: {len(filtered_users)}/{len(users_data)} users (min_activity: {min_activity})")
        return filtered_users
    
    async def _filter_explicit_users(self, users_data: List[Dict[str, Any]], 
                                    user_group_config: Dict[str, Any]) -> List[UserStatistics]:
        """Filter users for explicit user group using centralized name resolver."""
        users_config = user_group_config.get('users', {})
        allowed_user_ids = set(users_config.keys())
        
        # Filter users first
        filtered_data = [user for user in users_data if user['user_id'] in allowed_user_ids]
        
        # Apply name resolution using centralized utility
        # Extract user group name from config (assuming it's available in context)
        user_group_name = user_group_config.get('name', 'unknown')
        filtered_users = self.name_resolver.apply_user_group_names_to_dict_list(filtered_data, user_group_name)
        
        logger.debug(f"Explicit filter: {len(filtered_users)}/{len(users_data)} users (allowed: {len(allowed_user_ids)})")
        return filtered_users
    
    def _process_chat_data(self, chats_data: List[Dict[str, Any]]) -> List[ChatStatistics]:
        """Process raw chat data into ChatStatistics objects."""
        return [
            ChatStatistics(
                chat_id=chat['chat_id'],
                title=chat['title'],
                messages=chat['messages'],
                percentage=chat['percentage']
            )
            for chat in chats_data
        ]
    
    def validate_data_structure(self, data: Dict[str, Any]) -> bool:
        """Validate that data has the expected structure."""
        required_fields = ['total_messages', 'users', 'chats', 'monitoring_groups_used']
        
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate users structure
        if not isinstance(data['users'], list):
            logger.error("Users field must be a list")
            return False
        
        for user in data['users']:
            if not all(field in user for field in ['user_id', 'name', 'messages', 'percentage']):
                logger.error(f"Invalid user structure: {user}")
                return False
        
        # Validate chats structure
        if not isinstance(data['chats'], list):
            logger.error("Chats field must be a list")
            return False
        
        for chat in data['chats']:
            if not all(field in chat for field in ['chat_id', 'title', 'messages', 'percentage']):
                logger.error(f"Invalid chat structure: {chat}")
                return False
        
        return True 