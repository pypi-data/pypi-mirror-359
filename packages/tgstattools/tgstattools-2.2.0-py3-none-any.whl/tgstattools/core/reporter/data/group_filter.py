"""
Group filtering utilities.

This module handles filtering data by monitoring groups and user groups.
Single Responsibility: Applying group-based filters to statistics data.
"""

import logging
from typing import Dict, Any, List, Set
from ...template_processor.data_models import UserStatistics, ChatStatistics
from ...config_manager import ConfigManager

logger = logging.getLogger(__name__)


class GroupFilter:
    """Handles group-based filtering of statistics data."""
    
    def __init__(self, config_manager: ConfigManager, data_fetcher=None):
        """
        Initialize group filter.
        
        Args:
            config_manager: Configuration manager instance
            data_fetcher: Data fetcher instance for database access
        """
        self.config_manager = config_manager
        self.data_fetcher = data_fetcher
    
    def apply_filters(self, raw_data: Dict[str, Any], monitoring_group: str, user_group: str) -> Dict[str, Any]:
        """
        Apply monitoring group and user group filters to raw data.
        
        Args:
            raw_data: Raw statistics data
            monitoring_group: Monitoring group name
            user_group: User group name
            
        Returns:
            Filtered statistics data
        """
        # Combined filtering - use detailed data
        if monitoring_group != "all" and user_group != "all":
            return self._apply_combined_filters(raw_data, monitoring_group, user_group)
        elif monitoring_group != "all":
            return self._apply_monitoring_group_filter(raw_data, monitoring_group, user_group)
        elif user_group != "all":
            return self._apply_user_group_filter(raw_data, monitoring_group, user_group)
        else:
            # No filters - return as is
            return raw_data
    
    def _apply_combined_filters(self, raw_data: Dict[str, Any], monitoring_group: str, user_group: str) -> Dict[str, Any]:
        """Apply combined monitoring group + user group filters."""
        try:
            daily_stats = raw_data["daily_stats"]
            
            # Get allowed chat and user IDs
            allowed_chat_ids = self._get_allowed_chat_ids(monitoring_group)
            allowed_user_ids = self._get_allowed_user_ids(user_group)
            
            logger.info(f"Allowed chat IDs: {allowed_chat_ids}")
            logger.info(f"Allowed user IDs: {allowed_user_ids}")
            
            # Use detailed filtering for proper intersection of user+chat filters
            if allowed_chat_ids and allowed_user_ids:
                logger.info(f"Using detailed filtering: {len(allowed_chat_ids)} chats, {len(allowed_user_ids)} users")
                return self._apply_detailed_combined_filters(daily_stats, allowed_chat_ids, allowed_user_ids, user_group)
            
            # Fallback to simple filtering if no detailed filtering possible
            filtered_user_stats = self._filter_users_by_ids(raw_data["user_stats"], allowed_user_ids)
            filtered_chat_stats = self._filter_chats_by_ids(raw_data["chat_stats"], allowed_chat_ids)
            
            # Apply user group name resolution
            if user_group != "all":
                filtered_user_stats = self._filter_users_by_user_group(filtered_user_stats, user_group)
            
            return {
                "daily_stats": daily_stats,
                "user_stats": filtered_user_stats,
                "chat_stats": filtered_chat_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to apply combined filters: {e}")
            # Fallback to legacy filtering
            return self._apply_filters_legacy(raw_data, monitoring_group, user_group)
    
    def _apply_detailed_combined_filters(self, daily_stats: Dict[str, Any], allowed_chat_ids: set, 
                                       allowed_user_ids: set, user_group: str) -> Dict[str, Any]:
        """Apply filters using detailed daily_user_chat_stats table."""
        try:
            # Import here to avoid circular imports
            from ...database.statistics_repository import StatisticsRepository
            
            # Get detailed statistics from daily_user_chat_stats
            date_str = daily_stats["date"]
            monitoring_groups_hash = daily_stats["monitoring_groups_hash"]
            
            # Use the data_fetcher's database for detailed queries
            if self.data_fetcher and hasattr(self.data_fetcher, 'database'):
                repo = StatisticsRepository(self.data_fetcher.database)
            else:
                # Fallback: try to get database from other sources
                from ...database import DatabaseManager
                db_manager = DatabaseManager()
                repo = StatisticsRepository(db_manager)
            
            # Get filtered data from detailed table
            # Convert empty sets to None for the database query
            chat_ids_param = allowed_chat_ids if allowed_chat_ids else None
            user_ids_param = allowed_user_ids if allowed_user_ids else None
            
            filtered_user_tuples = repo.get_filtered_user_statistics_from_details(
                date_str, monitoring_groups_hash, chat_ids_param, user_ids_param
            )
            
            filtered_chat_tuples = repo.get_filtered_chat_statistics_from_details(
                date_str, monitoring_groups_hash, chat_ids_param, user_ids_param
            )
            
            # Convert tuples to statistics objects
            from .data_converter import DataConverter
            converter = DataConverter()
            
            filtered_user_stats = converter.tuples_to_user_statistics(filtered_user_tuples)
            filtered_chat_stats = converter.tuples_to_chat_statistics(filtered_chat_tuples)
            
            # Apply user group name resolution
            if user_group != "all":
                filtered_user_stats = self._filter_users_by_user_group(filtered_user_stats, user_group)
            
            # Calculate total messages from filtered data
            total_messages = sum(user.messages for user in filtered_user_stats)
            
            # Update daily stats with filtered total
            updated_daily_stats = daily_stats.copy()
            updated_daily_stats["total_messages"] = total_messages
            
            return {
                "daily_stats": updated_daily_stats,
                "user_stats": filtered_user_stats,
                "chat_stats": filtered_chat_stats
            }
            
        except Exception as e:
            logger.error(f"Detailed filtering failed: {e}")
            # Fallback to simple filtering
            return {
                "daily_stats": daily_stats,
                "user_stats": [],
                "chat_stats": []
            }
    
    def _apply_monitoring_group_filter(self, raw_data: Dict[str, Any], monitoring_group: str, user_group: str) -> Dict[str, Any]:
        """Apply monitoring group filter only."""
        daily_stats = raw_data["daily_stats"]
        allowed_chat_ids = self._get_allowed_chat_ids(monitoring_group)
        
        if not allowed_chat_ids:
            # No filtering needed
            return raw_data
        
        # Use detailed filtering for proper chat-based user filtering
        try:
            return self._apply_detailed_combined_filters(daily_stats, allowed_chat_ids, set(), user_group)
        except Exception as e:
            logger.error(f"Detailed monitoring group filtering failed: {e}")
            # Fallback to simple filtering
            filtered_chat_stats = self._filter_chats_by_ids(raw_data["chat_stats"], allowed_chat_ids)
            return {
                "daily_stats": raw_data["daily_stats"],
                "user_stats": raw_data["user_stats"],  # Keep all users in fallback
                "chat_stats": filtered_chat_stats
            }
    
    def _apply_user_group_filter(self, raw_data: Dict[str, Any], monitoring_group: str, user_group: str) -> Dict[str, Any]:
        """Apply user group filter only."""
        daily_stats = raw_data["daily_stats"]
        allowed_user_ids = self._get_allowed_user_ids(user_group)
        
        if not allowed_user_ids:
            # No filtering needed
            return raw_data
        
        # Use detailed filtering for proper user-based filtering with total recalculation
        try:
            return self._apply_detailed_combined_filters(daily_stats, set(), allowed_user_ids, user_group)
        except Exception as e:
            logger.error(f"Detailed user group filtering failed: {e}")
            # Fallback to simple filtering
            filtered_user_stats = self._filter_users_by_ids(raw_data["user_stats"], allowed_user_ids)
            filtered_user_stats = self._filter_users_by_user_group(filtered_user_stats, user_group)
            
            # Recalculate total messages from filtered users
            total_messages = sum(user.messages for user in filtered_user_stats)
            updated_daily_stats = daily_stats.copy()
            updated_daily_stats["total_messages"] = total_messages
            
            return {
                "daily_stats": updated_daily_stats,
                "user_stats": filtered_user_stats,
                "chat_stats": raw_data["chat_stats"]  # Keep all chats
            }
    
    def _apply_filters_legacy(self, raw_data: Dict[str, Any], monitoring_group: str, user_group: str) -> Dict[str, Any]:
        """Legacy filtering approach for fallback."""
        user_stats = raw_data["user_stats"]
        chat_stats = raw_data["chat_stats"]
        
        # Apply monitoring group filter
        if monitoring_group != "all":
            chat_stats = self._filter_chats_by_monitoring_group(chat_stats, monitoring_group)
        
        # Apply user group filter
        if user_group != "all":
            user_stats = self._filter_users_by_user_group(user_stats, user_group)
        
        return {
            "daily_stats": raw_data["daily_stats"],
            "user_stats": user_stats,
            "chat_stats": chat_stats
        }
    
    def _get_allowed_chat_ids(self, monitoring_group: str) -> Set[int]:
        """Get set of allowed chat IDs for monitoring group."""
        try:
            monitoring_groups = self.config_manager.get_monitoring_groups()
            if monitoring_group in monitoring_groups:
                group_config = monitoring_groups[monitoring_group]
                # Extract chat IDs from configuration
                if "chats" in group_config:
                    chat_ids = set()
                    for chat_id_str, chat_name in group_config["chats"].items():
                        try:
                            full_chat_id = int(chat_id_str)
                            # Convert full Telegram chat ID to database storage format
                            # Supergroups: -1001234567890 -> 1234567890 (remove -100 prefix)
                            # Regular groups: -1234567890 -> 1234567890 (remove - prefix)
                            if full_chat_id < -1000000000000:  # Supergroup
                                db_chat_id = abs(full_chat_id) - 1000000000000
                            elif full_chat_id < 0:  # Regular group  
                                db_chat_id = abs(full_chat_id)
                            else:  # Already positive
                                db_chat_id = full_chat_id
                            chat_ids.add(db_chat_id)
                            logger.debug(f"Converted chat ID {full_chat_id} -> {db_chat_id}")
                        except ValueError:
                            logger.warning(f"Invalid chat ID format: {chat_id_str}")
                    return chat_ids
                elif "chat_ids" in group_config:  # Alternative format
                    chat_ids = set()
                    for chat_id_str, chat_name in group_config["chat_ids"].items():
                        try:
                            full_chat_id = int(chat_id_str)
                            # Convert full Telegram chat ID to database storage format
                            if full_chat_id < -1000000000000:  # Supergroup
                                db_chat_id = abs(full_chat_id) - 1000000000000
                            elif full_chat_id < 0:  # Regular group  
                                db_chat_id = abs(full_chat_id)
                            else:  # Already positive
                                db_chat_id = full_chat_id
                            chat_ids.add(db_chat_id)
                            logger.debug(f"Converted chat ID {full_chat_id} -> {db_chat_id}")
                        except ValueError:
                            logger.warning(f"Invalid chat ID format: {chat_id_str}")
                    return chat_ids
            return set()
        except Exception as e:
            logger.error(f"Error getting allowed chat IDs: {e}")
            return set()
    
    def _get_allowed_user_ids(self, user_group: str) -> Set[int]:
        """Get set of allowed user IDs for user group."""
        try:
            user_groups = self.config_manager.get_user_groups()
            if user_group in user_groups:
                group_config = user_groups[user_group]
                # Extract user IDs from configuration
                if "users" in group_config:
                    user_ids = set()
                    for user_id, user_name in group_config["users"].items():
                        try:
                            user_ids.add(int(user_id))
                        except ValueError:
                            logger.warning(f"Invalid user ID format: {user_id}")
                    return user_ids
            return set()
        except Exception as e:
            logger.error(f"Error getting allowed user IDs: {e}")
            return set()
    
    def _filter_chats_by_ids(self, chat_stats: List[ChatStatistics], allowed_chat_ids: Set[int]) -> List[ChatStatistics]:
        """Filter chat statistics by allowed chat IDs."""
        if not allowed_chat_ids:
            return chat_stats
        return [chat for chat in chat_stats if chat.chat_id in allowed_chat_ids]
    
    def _filter_users_by_ids(self, user_stats: List[UserStatistics], allowed_user_ids: Set[int]) -> List[UserStatistics]:
        """Filter user statistics by allowed user IDs."""
        if not allowed_user_ids:
            return user_stats
        return [user for user in user_stats if user.user_id in allowed_user_ids]
    
    def _filter_chats_by_monitoring_group(self, chat_stats: List[ChatStatistics], monitoring_group: str) -> List[ChatStatistics]:
        """Filter chats by monitoring group configuration."""
        allowed_chat_ids = self._get_allowed_chat_ids(monitoring_group)
        return self._filter_chats_by_ids(chat_stats, allowed_chat_ids)
    
    def _filter_users_by_user_group(self, user_stats: List[UserStatistics], user_group: str) -> List[UserStatistics]:
        """Filter and rename users by user group configuration."""
        try:
            user_groups = self.config_manager.get_user_groups()
            if user_group not in user_groups:
                return user_stats
            
            group_config = user_groups[user_group]
            user_mapping = {}
            
            # Build user ID to display name mapping
            if "users" in group_config:
                for user_id, user_name in group_config["users"].items():
                    try:
                        user_mapping[int(user_id)] = user_name
                    except ValueError:
                        logger.warning(f"Invalid user ID format: {user_id}")
            
            # Filter and rename users
            filtered_users = []
            for user in user_stats:
                if user.user_id in user_mapping:
                    # Create new user stat with display name
                    filtered_users.append(UserStatistics(
                        user_id=user.user_id,
                        name=user_mapping[user.user_id],
                        messages=user.messages,
                        percentage=user.percentage
                    ))
            
            return filtered_users
            
        except Exception as e:
            logger.error(f"Error filtering users by user group: {e}")
            return user_stats
    
    def _convert_chat_ids(self, chat_id_strings: List[str]) -> Set[int]:
        """Convert chat ID strings to integers."""
        chat_ids = set()
        for chat_id_str in chat_id_strings:
            try:
                # Handle negative chat IDs (groups/supergroups)
                chat_id = int(chat_id_str)
                chat_ids.add(chat_id)
            except ValueError:
                logger.warning(f"Invalid chat ID format: {chat_id_str}")
        return chat_ids 