"""
Data filtering and sorting for template processing.

This module handles applying template-defined filters and sorting
rules to statistics data before formatting.
"""

import logging
from typing import Dict, Any, Tuple, List
from .data_models import StatisticsData, UserStatistics, ChatStatistics

logger = logging.getLogger(__name__)


class DataFilter:
    """Handles filtering and sorting of statistics data."""
    
    def filter_and_sort_data(self, data: StatisticsData, template: Dict[str, Any]) -> StatisticsData:
        """Apply template filters and sorting to statistics data."""
        logger.debug(f"Filtering and sorting data with template filters")
        
        filters = template['filters']
        sorting = template['sorting']
        
        # Filter and sort users
        filtered_users = self._filter_users(data.users, filters['users'])
        sorted_users = self._sort_users(filtered_users, sorting['users'])
        
        # Filter and sort chats
        filtered_chats = self._filter_chats(data.chats, filters['chats'])
        sorted_chats = self._sort_chats(filtered_chats, sorting['chats'])
        
        # Recalculate percentages after filtering
        recalculated_users, recalculated_chats = self.recalculate_percentages(sorted_users, sorted_chats)
        
        # Calculate new total messages from filtered data
        filtered_total_messages = sum(user.messages for user in recalculated_users)
        
        # Return filtered data with recalculated percentages
        return StatisticsData(
            date=data.date,
            total_messages=filtered_total_messages,  # Use filtered total
            users=recalculated_users,
            chats=recalculated_chats,
            monitoring_groups_used=data.monitoring_groups_used,
            collection_completed_at=data.collection_completed_at
        )
    
    def _filter_users(self, users: List[UserStatistics], filters: Dict[str, Any]) -> List[UserStatistics]:
        """Filter users based on template rules."""
        filtered_users = []
        
        for user in users:
            # Apply min_messages filter
            if user.messages < filters['min_messages']:
                continue
                
            # Apply zero activity filter
            if not filters['show_zero_activity'] and user.messages == 0:
                continue
                
            filtered_users.append(user)
        
        return filtered_users
    
    def _sort_users(self, users: List[UserStatistics], sort_order: str) -> List[UserStatistics]:
        """Sort users based on template rules."""
        reverse_sort = sort_order == 'desc'
        return sorted(users, key=lambda u: u.messages, reverse=reverse_sort)
    
    def _filter_chats(self, chats: List[ChatStatistics], filters: Dict[str, Any]) -> List[ChatStatistics]:
        """Filter chats based on template rules."""
        filtered_chats = []
        
        for chat in chats:
            # Apply min_messages filter
            if chat.messages < filters['min_messages']:
                continue
                
            # Apply zero activity filter
            if not filters['show_zero_activity'] and chat.messages == 0:
                continue
                
            filtered_chats.append(chat)
        
        return filtered_chats
    
    def _sort_chats(self, chats: List[ChatStatistics], sort_order: str) -> List[ChatStatistics]:
        """Sort chats based on template rules."""
        reverse_sort = sort_order == 'desc'
        return sorted(chats, key=lambda c: c.messages, reverse=reverse_sort)
    
    def recalculate_percentages(self, users: List[UserStatistics], chats: List[ChatStatistics]) -> Tuple[List[UserStatistics], List[ChatStatistics]]:
        """Recalculate percentages after filtering."""
        from .percentage_calculator import PercentageCalculator
        
        recalculated_users = PercentageCalculator.recalculate_user_percentages(users)
        recalculated_chats = PercentageCalculator.recalculate_chat_percentages(chats)
        
        return recalculated_users, recalculated_chats 