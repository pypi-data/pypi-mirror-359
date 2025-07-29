"""
Data fetcher for database operations.

This module handles retrieving statistics data from the database.
Single Responsibility: Fetching raw data from database tables.
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from ...template_processor.data_models import UserStatistics, ChatStatistics

logger = logging.getLogger(__name__)


class DataFetcher:
    """Handles data retrieval from database."""
    
    def __init__(self, database):
        """
        Initialize data fetcher.
        
        Args:
            database: Database connection instance
        """
        self.database = database
    
    async def get_raw_statistics(self, target_date) -> Optional[Dict[str, Any]]:
        """
        Get raw statistics data from database.
        
        Args:
            target_date: Target date for statistics
            
        Returns:
            Dictionary with raw statistics data or None if not found
        """
        try:
            # Try to find data with different monitoring group hashes
            # First try "all" (preferred)
            from ...statistics.utils import StatisticsUtils
            utils = StatisticsUtils(None, self.database)
            
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
            
        except Exception as e:
            logger.error(f"Error fetching raw statistics: {e}")
            return None
    
    def _fetch_statistics_from_db(self, daily_stats_id: int) -> Tuple[List[UserStatistics], List[ChatStatistics]]:
        """
        Fetch user and chat statistics from database.
        
        Args:
            daily_stats_id: ID of daily statistics record
            
        Returns:
            Tuple of (user_stats, chat_stats) lists
        """
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
    
    def get_filtered_user_statistics_from_details(self, date_str: str, monitoring_groups_hash: str, 
                                                 allowed_chat_ids: set, allowed_user_ids: set) -> List[Tuple]:
        """
        Get filtered user statistics from detailed table.
        
        Args:
            date_str: Date string
            monitoring_groups_hash: Hash of monitoring groups
            allowed_chat_ids: Set of allowed chat IDs
            allowed_user_ids: Set of allowed user IDs
            
        Returns:
            List of tuples with user statistics
        """
        return self.database.get_filtered_user_statistics_from_details(
            date_str, monitoring_groups_hash, allowed_chat_ids, allowed_user_ids
        )
    
    def get_filtered_chat_statistics_from_details(self, date_str: str, monitoring_groups_hash: str,
                                                 allowed_chat_ids: set, allowed_user_ids: set) -> List[Tuple]:
        """
        Get filtered chat statistics from detailed table.
        
        Args:
            date_str: Date string
            monitoring_groups_hash: Hash of monitoring groups
            allowed_chat_ids: Set of allowed chat IDs
            allowed_user_ids: Set of allowed user IDs
            
        Returns:
            List of tuples with chat statistics
        """
        return self.database.get_filtered_chat_statistics_from_details(
            date_str, monitoring_groups_hash, allowed_chat_ids, allowed_user_ids
        )
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Any]:
        """
        Execute database query.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Query results
        """
        return self.database.execute_query(query, params) 