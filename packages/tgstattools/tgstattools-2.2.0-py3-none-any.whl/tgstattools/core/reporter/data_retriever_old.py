"""
Data retrieval and filtering for report generation.

This module handles retrieving statistics data from the database
and applying user/monitoring group filters with proper percentage recalculation.
"""

import logging
from datetime import datetime
from typing import Optional, Set
from ..template_processor.data_models import StatisticsData, UserStatistics, ChatStatistics
from ..config_manager import ConfigManager
from ..user_utils import UserNameResolver
from ..timezone_utils import convert_utc_to_local_date

logger = logging.getLogger(__name__)


class DataRetriever:
    """Handles data retrieval and filtering for reports."""
    
    def __init__(self, database, config_manager: Optional[ConfigManager] = None):
        """Initialize data retriever."""
        self.database = database
        self.config_manager = config_manager or ConfigManager()
        self.name_resolver = UserNameResolver(self.config_manager)
    
    async def get_filtered_statistics(self, target_date, monitoring_group: str = "all", 
                                    user_group: str = "all", reporting_group: str = None) -> StatisticsData:
        """Get statistics data with applied filters and timezone conversion."""
        try:
            # Always get data from "all" group (base collection)
            raw_data = await self._get_raw_statistics(target_date)
            
            if not raw_data:
                return self._create_empty_statistics(target_date, monitoring_group, reporting_group)
            
            # Apply filtering
            filtered_data = self._apply_filters(raw_data, monitoring_group, user_group)
            
            # Recalculate percentages
            return self._recalculate_percentages(filtered_data, target_date, monitoring_group, reporting_group)
            
        except Exception as e:
            logger.error(f"Error retrieving filtered statistics: {e}")
            return self._create_empty_statistics(target_date, monitoring_group, reporting_group)
    
    async def _get_raw_statistics(self, target_date) -> Optional[dict]:
        """Get raw statistics data from database - try different monitoring group hashes."""
        from ..statistics.utils import StatisticsUtils
        
        utils = StatisticsUtils(None, self.database)
        
        # Try to find data with different monitoring group hashes
        # First try "all" (preferred)
        all_groups_hash = utils.calculate_monitoring_groups_hash(["all"])
        daily_stats = self.database.get_daily_statistics(target_date, all_groups_hash)
        
        if not daily_stats:
            # If no "all" data found, try to find ANY data for this date
            results = self.database.execute_query(
                'SELECT * FROM daily_statistics WHERE date = ? ORDER BY collection_completed_at DESC LIMIT 1',
                (str(target_date),)
            )
            if results:
                daily_stats = {
                    "id": results[0][0],
                    "date": results[0][1],
                    "monitoring_groups_hash": results[0][2],
                    "total_messages": results[0][3],
                    "collection_started_at": results[0][4],
                    "collection_completed_at": results[0][5],
                    "collection_status": results[0][6],
                    "errors_count": results[0][7],
                    "media_groups_processed": results[0][8],
                    "monitoring_groups_used": results[0][9]
                }
        
        if not daily_stats:
            return None
        
        # Get user and chat statistics
        user_stats, chat_stats = self._fetch_statistics_from_db(daily_stats["id"])
        
        return {
            "daily_stats": daily_stats,
            "user_stats": user_stats,
            "chat_stats": chat_stats
        }
    
    def _fetch_statistics_from_db(self, daily_stats_id: int) -> tuple:
        """Fetch user and chat statistics from database."""
        user_stats = []
        chat_stats = []
        
        with self.database.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get user stats
            cursor.execute("""
                SELECT user_id, user_name, messages, percentage
                FROM daily_user_stats 
                WHERE daily_stats_id = ?
                ORDER BY messages DESC
            """, (daily_stats_id,))
            
            for row in cursor.fetchall():
                user_stats.append(UserStatistics(
                    user_id=row[0],
                    name=row[1],
                    messages=row[2],
                    percentage=row[3]
                ))
            
            # Get chat stats
            cursor.execute("""
                SELECT chat_id, chat_title, messages, percentage
                FROM daily_chat_stats 
                WHERE daily_stats_id = ?
                ORDER BY messages DESC
            """, (daily_stats_id,))
            
            for row in cursor.fetchall():
                chat_stats.append(ChatStatistics(
                    chat_id=row[0],
                    title=row[1],
                    messages=row[2],
                    percentage=row[3]
                ))
        
        return user_stats, chat_stats
    
    def _apply_filters(self, raw_data: dict, monitoring_group: str, user_group: str) -> dict:
        """Apply monitoring group and user group filters using detailed data."""
        # ИСПРАВЛЕНИЕ: Если есть комбинированная фильтрация - используем детализированные данные
        if monitoring_group != "all" and user_group != "all":
            return self._apply_combined_filters(raw_data, monitoring_group, user_group)
        elif monitoring_group != "all":
            return self._apply_monitoring_group_filter(raw_data, monitoring_group, user_group)
        elif user_group != "all":
            return self._apply_user_group_filter(raw_data, monitoring_group, user_group)
        else:
            # Без фильтров - возвращаем как есть
            return raw_data
    
    def _apply_combined_filters(self, raw_data: dict, monitoring_group: str, user_group: str) -> dict:
        """Apply combined monitoring group + user group filters using detailed data."""
        try:
            daily_stats = raw_data["daily_stats"]
            daily_stats_id = daily_stats["id"]
            date_str = daily_stats["date"]
            monitoring_groups_hash = daily_stats["monitoring_groups_hash"]
            
            # Получить ID разрешенных чатов
            allowed_chat_ids = self._get_allowed_chat_ids(monitoring_group)
            
            # Получить ID разрешенных пользователей  
            allowed_user_ids = self._get_allowed_user_ids(user_group)
            
            # Получить отфильтрованные данные из детализированной таблицы
            filtered_user_data = self.database.get_filtered_user_statistics_from_details(
                date_str, monitoring_groups_hash, allowed_chat_ids, allowed_user_ids
            )
            
            filtered_chat_data = self.database.get_filtered_chat_statistics_from_details(
                date_str, monitoring_groups_hash, allowed_chat_ids, allowed_user_ids
            )
            
            # Преобразовать в правильный формат
            user_stats = []
            for row in filtered_user_data:
                user_stats.append(UserStatistics(
                    user_id=row[0],
                    name=row[1] or f"User_{row[0]}",
                    messages=row[2],
                    percentage=0  # Будет пересчитано
                ))
            
            # ИСПРАВЛЕНИЕ: Применить переименование пользователей из user_group конфигурации
            if user_group != "all":
                user_stats = self._filter_users_by_user_group(user_stats, user_group)
            
            chat_stats = []
            for row in filtered_chat_data:
                chat_stats.append(ChatStatistics(
                    chat_id=row[0],
                    title=row[1] or f"Chat_{row[0]}",
                    messages=row[2],
                    percentage=0  # Будет пересчитано
                ))
            
            return {
                "daily_stats": daily_stats,
                "user_stats": user_stats,
                "chat_stats": chat_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to apply combined filters: {e}")
            # Fallback к старой логике
            return self._apply_filters_legacy(raw_data, monitoring_group, user_group)
    
    def _apply_monitoring_group_filter(self, raw_data: dict, monitoring_group: str, user_group: str) -> dict:
        """Apply only monitoring group filter using detailed data."""
        try:
            daily_stats = raw_data["daily_stats"]
            date_str = daily_stats["date"]
            monitoring_groups_hash = daily_stats["monitoring_groups_hash"]
            
            # Получить ID разрешенных чатов
            allowed_chat_ids = self._get_allowed_chat_ids(monitoring_group)
            
            # Получить отфильтрованные данные из детализированной таблицы
            filtered_user_data = self.database.get_filtered_user_statistics_from_details(
                date_str, monitoring_groups_hash, allowed_chat_ids, None
            )
            
            filtered_chat_data = self.database.get_filtered_chat_statistics_from_details(
                date_str, monitoring_groups_hash, allowed_chat_ids, None
            )
            
            # Преобразовать в правильный формат
            user_stats = []
            for row in filtered_user_data:
                user_stats.append(UserStatistics(
                    user_id=row[0],
                    name=row[1] or f"User_{row[0]}",
                    messages=row[2],
                    percentage=0  # Будет пересчитано
                ))
            
            # ИСПРАВЛЕНИЕ: Применить переименование пользователей из user_group конфигурации (если задана)
            if user_group != "all":
                user_stats = self._filter_users_by_user_group(user_stats, user_group)
            
            chat_stats = []
            for row in filtered_chat_data:
                chat_stats.append(ChatStatistics(
                    chat_id=row[0],
                    title=row[1] or f"Chat_{row[0]}",
                    messages=row[2],
                    percentage=0  # Будет пересчитано
                ))
            
            return {
                "daily_stats": daily_stats,
                "user_stats": user_stats,
                "chat_stats": chat_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to apply monitoring group filter: {e}")
            # Fallback к старой логике
            return self._apply_filters_legacy(raw_data, monitoring_group, user_group)
    
    def _apply_user_group_filter(self, raw_data: dict, monitoring_group: str, user_group: str) -> dict:
        """Apply only user group filter."""
        user_stats = raw_data["user_stats"]
        chat_stats = raw_data["chat_stats"]
        
        # Filter users by user group - можно использовать старую логику
        user_stats = self._filter_users_by_user_group(user_stats, user_group)
        
        return {
            "daily_stats": raw_data["daily_stats"],
            "user_stats": user_stats,
            "chat_stats": chat_stats
        }
    
    def _apply_filters_legacy(self, raw_data: dict, monitoring_group: str, user_group: str) -> dict:
        """Legacy filter logic for backward compatibility."""
        user_stats = raw_data["user_stats"]
        chat_stats = raw_data["chat_stats"]
        
        # Filter chats by monitoring group
        if monitoring_group != "all":
            chat_stats = self._filter_chats_by_monitoring_group(chat_stats, monitoring_group)
        
        # Filter users by user group
        if user_group != "all":
            user_stats = self._filter_users_by_user_group(user_stats, user_group)
        
        return {
            "daily_stats": raw_data["daily_stats"],
            "user_stats": user_stats,
            "chat_stats": chat_stats
        }
    
    def _get_allowed_chat_ids(self, monitoring_group: str) -> set:
        """Get set of allowed chat IDs for monitoring group."""
        try:
            monitoring_group_config = self.config_manager.load_monitoring_group(monitoring_group)
            chats_config = monitoring_group_config.get('chat_ids', monitoring_group_config.get('chats', {}))
            return self._convert_chat_ids(chats_config.keys())
        except Exception as e:
            logger.warning(f"Failed to get allowed chat IDs for '{monitoring_group}': {e}")
            return set()
    
    def _get_allowed_user_ids(self, user_group: str) -> set:
        """Get set of allowed user IDs for user group."""
        try:
            user_group_config = self.config_manager.load_user_group(user_group)
            
            if user_group_config.get("auto_discovery", False):
                # Для auto-discovery групп возвращаем None - без ограничений
                return None
            
            # Для явных групп извлекаем user_ids
            users_config = user_group_config.get('user_ids', user_group_config.get('users', {}))
            if isinstance(users_config, dict):
                return set(int(uid) for uid in users_config.keys())
            else:
                return set()
                
        except Exception as e:
            logger.warning(f"Failed to get allowed user IDs for '{user_group}': {e}")
            return set()
    
    def _filter_chats_by_monitoring_group(self, chat_stats: list, monitoring_group: str) -> list:
        """Filter chats by monitoring group configuration."""
        try:
            monitoring_group_config = self.config_manager.load_monitoring_group(monitoring_group)
            chats_config = monitoring_group_config.get('chat_ids', monitoring_group_config.get('chats', {}))
            
            allowed_chat_ids = self._convert_chat_ids(chats_config.keys())
            
            return [chat for chat in chat_stats if chat.chat_id in allowed_chat_ids]
            
        except Exception as e:
            logger.warning(f"Failed to filter chats by monitoring group '{monitoring_group}': {e}")
            return chat_stats
    
    def _filter_users_by_user_group(self, user_stats: list, user_group: str) -> list:
        """Filter users by user group configuration using centralized name resolver."""
        return self.name_resolver.filter_and_map_users_by_group(user_stats, user_group)
    

    
    def _convert_chat_ids(self, chat_id_strings: list) -> Set[int]:
        """Convert chat ID strings to proper integer format."""
        allowed_chat_ids = set()
        
        for chat_id_str in chat_id_strings:
            chat_id = int(chat_id_str)
            if chat_id_str.startswith("-100"):
                # Remove -100 prefix for supergroups
                positive_id = abs(chat_id) - 1000000000000
                allowed_chat_ids.add(positive_id)
            else:
                allowed_chat_ids.add(abs(chat_id))
        
        return allowed_chat_ids
    
    def _recalculate_percentages(self, filtered_data: dict, target_date, monitoring_group: str, reporting_group: str = None) -> StatisticsData:
        """Recalculate percentages based on filtered data."""
        from ..template_processor.percentage_calculator import PercentageCalculator
        
        user_stats = filtered_data["user_stats"]
        chat_stats = filtered_data["chat_stats"]
        
        # Recalculate percentages using centralized utility
        recalculated_users = PercentageCalculator.recalculate_user_percentages(user_stats)
        recalculated_chats = PercentageCalculator.recalculate_chat_percentages(chat_stats)
        
        # Get total messages from recalculated users
        total_user_messages = PercentageCalculator.get_total_user_messages(recalculated_users)
        
        # Format date with timezone conversion if reporting_group is provided
        formatted_date = self._format_date_with_timezone(target_date, reporting_group)
        
        return StatisticsData(
            date=formatted_date,
            total_messages=total_user_messages,
            users=recalculated_users,
            chats=recalculated_chats,
            monitoring_groups_used=[monitoring_group],
            collection_completed_at=filtered_data["daily_stats"].get("collection_completed_at") or datetime.now().isoformat(),
            reporting_group=reporting_group
        )
    

    
    def _format_date_with_timezone(self, target_date, reporting_group: str = None) -> str:
        """Format date with timezone conversion based on reporting_group configuration."""
        try:
            if reporting_group:
                # Get timezone from reporting_group configuration
                reporting_config = self.config_manager.load_reporting_group(reporting_group)
                timezone = reporting_config.get("content_settings", {}).get("timezone", "UTC")
                date_format = reporting_config.get("content_settings", {}).get("date_format", "%d-%m-%Y")
                
                # Convert UTC date to reporting_group timezone
                converted_date = convert_utc_to_local_date(target_date, timezone)
                return converted_date.strftime(date_format)
            else:
                # Fallback to default format
                return target_date.strftime('%d-%m-%Y')
                
        except Exception as e:
            logger.warning(f"Failed to format date with timezone for reporting_group '{reporting_group}': {e}")
            # Fallback to default format
            return target_date.strftime('%d-%m-%Y')

    def _create_empty_statistics(self, target_date, monitoring_group: str, reporting_group: str = None) -> StatisticsData:
        """Create empty statistics data."""
        formatted_date = self._format_date_with_timezone(target_date, reporting_group)
        
        return StatisticsData(
            date=formatted_date,
            total_messages=0,
            users=[],
            chats=[],
            monitoring_groups_used=[monitoring_group],
            collection_completed_at=datetime.now().isoformat(),
            reporting_group=reporting_group
        ) 