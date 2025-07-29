"""
Percentage calculation utilities for statistics data.

This module provides centralized percentage calculation logic
to avoid code duplication across different components.
"""

import logging
from typing import List
from .data_models import UserStatistics, ChatStatistics

logger = logging.getLogger(__name__)


class PercentageCalculator:
    """Utility class for percentage calculations."""
    
    @staticmethod
    def recalculate_user_percentages(user_stats: List[UserStatistics]) -> List[UserStatistics]:
        """Recalculate user percentages based on current message totals."""
        total_messages = sum(user.messages for user in user_stats)
        
        if total_messages == 0:
            return user_stats
        
        return [
            UserStatistics(
                user_id=user.user_id,
                name=user.name,
                messages=user.messages,
                percentage=(user.messages / total_messages) * 100
            )
            for user in user_stats
        ]
    
    @staticmethod
    def recalculate_chat_percentages(chat_stats: List[ChatStatistics]) -> List[ChatStatistics]:
        """Recalculate chat percentages based on current message totals."""
        total_messages = sum(chat.messages for chat in chat_stats)
        
        if total_messages == 0:
            return chat_stats
        
        return [
            ChatStatistics(
                chat_id=chat.chat_id,
                title=chat.title,
                messages=chat.messages,
                percentage=(chat.messages / total_messages) * 100
            )
            for chat in chat_stats
        ]
    
    @staticmethod
    def get_total_user_messages(user_stats: List[UserStatistics]) -> int:
        """Get total messages from user statistics."""
        return sum(user.messages for user in user_stats)
    
    @staticmethod
    def get_total_chat_messages(chat_stats: List[ChatStatistics]) -> int:
        """Get total messages from chat statistics."""
        return sum(chat.messages for chat in chat_stats) 