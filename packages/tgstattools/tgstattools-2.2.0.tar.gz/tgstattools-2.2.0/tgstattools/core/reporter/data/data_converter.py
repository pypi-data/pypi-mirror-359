"""
Data conversion utilities.

This module handles type conversions and data transformations.
Single Responsibility: Converting data types and formats.
"""

import logging
from typing import Dict, Any, List
from ...template_processor.data_models import StatisticsData, UserStatistics, ChatStatistics
from ...timezone_utils import convert_utc_to_local_date

logger = logging.getLogger(__name__)


class DataConverter:
    """Handles data type conversions and transformations."""
    
    @staticmethod
    def create_statistics_data(filtered_data: Dict[str, Any], target_date, 
                              monitoring_group: str, reporting_group: str = None) -> StatisticsData:
        """
        Convert filtered data to StatisticsData object.
        
        Args:
            filtered_data: Filtered statistics data
            target_date: Target date
            monitoring_group: Monitoring group name
            reporting_group: Reporting group name (optional)
            
        Returns:
            StatisticsData object
        """
        daily_stats = filtered_data["daily_stats"]
        user_stats = filtered_data["user_stats"]
        chat_stats = filtered_data["chat_stats"]
        
        # Recalculate percentages
        total_messages = sum(user.messages for user in user_stats)
        
        if total_messages > 0:
            for user in user_stats:
                user.percentage = (user.messages / total_messages) * 100
            
            for chat in chat_stats:
                chat.percentage = (chat.messages / total_messages) * 100
        
        # Format date with timezone
        formatted_date = DataConverter._format_date_with_timezone(target_date, reporting_group)
        
        return StatisticsData(
            date=formatted_date,
            total_messages=total_messages,
            users=user_stats,
            chats=chat_stats,
            monitoring_groups_used=[monitoring_group],
            collection_completed_at=formatted_date,
            reporting_group=reporting_group
        )
    
    @staticmethod
    def create_empty_statistics(target_date, monitoring_group: str, reporting_group: str = None) -> StatisticsData:
        """
        Create empty StatisticsData object.
        
        Args:
            target_date: Target date
            monitoring_group: Monitoring group name
            reporting_group: Reporting group name (optional)
            
        Returns:
            Empty StatisticsData object
        """
        formatted_date = DataConverter._format_date_with_timezone(target_date, reporting_group)
        
        return StatisticsData(
            date=formatted_date,
            total_messages=0,
            users=[],
            chats=[],
            monitoring_groups_used=[monitoring_group],
            collection_completed_at=formatted_date,
            reporting_group=reporting_group
        )
    
    @staticmethod
    def tuples_to_user_statistics(tuples_data: List[tuple]) -> List[UserStatistics]:
        """
        Convert tuple data to UserStatistics objects.
        
        Args:
            tuples_data: List of tuples with user data
            
        Returns:
            List of UserStatistics objects
        """
        user_stats = []
        for row in tuples_data:
            user_stats.append(UserStatistics(
                user_id=row[0],
                name=row[1] or f"User_{row[0]}",
                messages=row[2],
                percentage=0  # Will be recalculated
            ))
        return user_stats
    
    @staticmethod
    def tuples_to_chat_statistics(tuples_data: List[tuple]) -> List[ChatStatistics]:
        """
        Convert tuple data to ChatStatistics objects.
        
        Args:
            tuples_data: List of tuples with chat data
            
        Returns:
            List of ChatStatistics objects
        """
        chat_stats = []
        for row in tuples_data:
            chat_stats.append(ChatStatistics(
                chat_id=row[0],
                title=row[1] or f"Chat_{row[0]}",
                messages=row[2],
                percentage=0  # Will be recalculated
            ))
        return chat_stats
    
    @staticmethod
    def _format_date_with_timezone(target_date, reporting_group: str = None) -> str:
        """
        Format date with timezone conversion.
        
        Args:
            target_date: Target date
            reporting_group: Reporting group name for timezone
            
        Returns:
            Formatted date string
        """
        try:
            # Convert UTC date to local timezone for display
            if reporting_group:
                # In v2.2, timezone conversion is simplified
                # Just use convert_utc_to_local_date utility
                return convert_utc_to_local_date(target_date)
            else:
                return str(target_date)
        except Exception as e:
            logger.warning(f"Date formatting failed: {e}")
            return str(target_date) 