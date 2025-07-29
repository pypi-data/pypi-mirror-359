"""
Statistics data repository.

This module handles CRUD operations for statistics data including
daily statistics, user stats, and chat stats.
"""

import json
import logging
from typing import Dict, Any, Optional
from .connection import DatabaseConnection


logger = logging.getLogger(__name__)


class StatisticsRepository:
    """Repository for statistics data operations."""
    
    def __init__(self, connection: DatabaseConnection):
        """Initialize statistics repository with database connection."""
        self.connection = connection
    
    def insert_daily_statistics(self, date, monitoring_groups_hash, total_messages, 
                               collection_started_at, collection_completed_at=None,
                               collection_status="in_progress", errors_count=0,
                               media_groups_processed=0, monitoring_groups_used=None) -> int:
        """Insert daily statistics record and return the ID."""
        query = """
            INSERT INTO daily_statistics 
            (date, monitoring_groups_hash, total_messages, collection_started_at,
             collection_completed_at, collection_status, errors_count, 
             media_groups_processed, monitoring_groups_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        # Convert monitoring_groups_used to JSON if it's a list
        if isinstance(monitoring_groups_used, list):
            monitoring_groups_used = json.dumps(monitoring_groups_used)
        
        params = (date, monitoring_groups_hash, total_messages, collection_started_at,
                 collection_completed_at, collection_status, errors_count,
                 media_groups_processed, monitoring_groups_used)
        
        return self.connection.execute_insert(query, params)
    
    def upsert_daily_statistics(self, date, monitoring_groups_hash, total_messages,
                               collection_started_at, collection_completed_at=None,
                               collection_status="in_progress", errors_count=0,
                               media_groups_processed=0, monitoring_groups_used=None) -> int:
        """Insert or update daily statistics (for current-day actualization)."""
        existing = self.get_daily_statistics(date, monitoring_groups_hash)
        
        if existing:
            # Update existing record
            if isinstance(monitoring_groups_used, list):
                monitoring_groups_used = json.dumps(monitoring_groups_used)
            
            query = """
                UPDATE daily_statistics 
                SET total_messages = ?, collection_started_at = ?,
                    collection_completed_at = ?, collection_status = ?,
                    errors_count = ?, media_groups_processed = ?,
                    monitoring_groups_used = ?
                WHERE date = ? AND monitoring_groups_hash = ?
            """
            params = (total_messages, collection_started_at, collection_completed_at,
                     collection_status, errors_count, media_groups_processed,
                     monitoring_groups_used, date, monitoring_groups_hash)
            self.connection.execute_update(query, params)
            return existing["id"]
        else:
            # Insert new record
            return self.insert_daily_statistics(
                date, monitoring_groups_hash, total_messages, collection_started_at,
                collection_completed_at, collection_status, errors_count,
                media_groups_processed, monitoring_groups_used
            )
    
    def get_daily_statistics(self, date, monitoring_groups_hash: str) -> Optional[Dict[str, Any]]:
        """Get daily statistics for a specific date and groups hash."""
        query = """
            SELECT * FROM daily_statistics 
            WHERE date = ? AND monitoring_groups_hash = ?
        """
        results = self.connection.execute_query(query, (date, monitoring_groups_hash))
        
        if results:
            row = results[0]
            return dict(row)
        return None
    
    def collection_exists(self, date, monitoring_groups_hash: str) -> bool:
        """Check if collection exists for date and groups hash."""
        stats = self.get_daily_statistics(date, monitoring_groups_hash)
        return stats is not None
    
    def complete_collection(self, stats_id: int, errors_count: int, 
                           media_groups_processed: int) -> None:
        """Mark collection as completed."""
        query = """
            UPDATE daily_statistics 
            SET collection_status = 'completed',
                collection_completed_at = datetime('now'),
                errors_count = ?,
                media_groups_processed = ?
            WHERE id = ?
        """
        self.connection.execute_update(query, (errors_count, media_groups_processed, stats_id))
    
    def insert_daily_user_stats(self, daily_stats_id: int, date, monitoring_groups_hash: str,
                               user_id: int, user_name: str, messages: int, percentage: float) -> None:
        """Insert user statistics record."""
        query = """
            INSERT OR REPLACE INTO daily_user_stats
            (daily_stats_id, date, monitoring_groups_hash, user_id, user_name, messages, percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (daily_stats_id, date, monitoring_groups_hash, user_id, user_name, messages, percentage)
        self.connection.execute_update(query, params)
    
    def insert_daily_chat_stats(self, daily_stats_id: int, date, monitoring_groups_hash: str,
                               chat_id: int, chat_title: str, messages: int, percentage: float) -> None:
        """Insert chat statistics record."""
        query = """
            INSERT OR REPLACE INTO daily_chat_stats
            (daily_stats_id, date, monitoring_groups_hash, chat_id, chat_title, messages, percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (daily_stats_id, date, monitoring_groups_hash, chat_id, chat_title, messages, percentage)
        self.connection.execute_update(query, params)
    
    def insert_user_stats(self, stats_id: int, date, monitoring_groups_hash: str, 
                         user_stats) -> None:
        """Insert user statistics for a collection (batch operation)."""
        query = """
            INSERT INTO daily_user_stats 
            (daily_stats_id, date, monitoring_groups_hash, user_id, user_name, messages, percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        with self.connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Handle both dict and list formats
            if isinstance(user_stats, dict):
                for user_id, data in user_stats.items():
                    params = (stats_id, date, monitoring_groups_hash, user_id,
                             data["name"], data["messages"], data["percentage"])
                    cursor.execute(query, params)
            elif isinstance(user_stats, list):
                for user_data in user_stats:
                    if isinstance(user_data, tuple) and len(user_data) == 4:
                        user_id, name, messages, percentage = user_data
                        params = (stats_id, date, monitoring_groups_hash, user_id,
                                 name, messages, percentage)
                        cursor.execute(query, params)
            
            conn.commit()
    
    def insert_chat_stats(self, stats_id: int, date, monitoring_groups_hash: str,
                         chat_stats) -> None:
        """Insert chat statistics for a collection (batch operation)."""
        query = """
            INSERT INTO daily_chat_stats
            (daily_stats_id, date, monitoring_groups_hash, chat_id, chat_title, messages, percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        with self.connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Handle both dict and list formats
            if isinstance(chat_stats, dict):
                for chat_id, data in chat_stats.items():
                    params = (stats_id, date, monitoring_groups_hash, chat_id,
                             data["title"], data["messages"], data["percentage"])
                    cursor.execute(query, params)
            elif isinstance(chat_stats, list):
                for chat_data in chat_stats:
                    if isinstance(chat_data, tuple) and len(chat_data) == 4:
                        chat_id, title, messages, percentage = chat_data
                        params = (stats_id, date, monitoring_groups_hash, chat_id,
                                 title, messages, percentage)
                        cursor.execute(query, params)
            
            conn.commit()
    
    def get_user_statistics(self, date, monitoring_groups_hash: str) -> list:
        """Get user statistics for a specific date and monitoring groups hash."""
        query = """
            SELECT user_id, user_name, messages, percentage 
            FROM daily_user_stats 
            WHERE date = ? AND monitoring_groups_hash = ?
            ORDER BY messages DESC
        """
        return self.connection.execute_query(query, (date, monitoring_groups_hash))
    
    def get_chat_statistics(self, date, monitoring_groups_hash: str) -> list:
        """Get chat statistics for a specific date and monitoring groups hash."""
        query = """
            SELECT chat_id, chat_title, messages, percentage 
            FROM daily_chat_stats 
            WHERE date = ? AND monitoring_groups_hash = ?
            ORDER BY messages DESC
        """
        return self.connection.execute_query(query, (date, monitoring_groups_hash))
    
    def delete_user_stats_for_collection(self, daily_stats_id: int) -> int:
        """Delete user statistics for a specific collection (for re-collection)."""
        query = "DELETE FROM daily_user_stats WHERE daily_stats_id = ?"
        return self.connection.execute_update(query, (daily_stats_id,))
    
    def delete_chat_stats_for_collection(self, daily_stats_id: int) -> int:
        """Delete chat statistics for a specific collection (for re-collection)."""
        query = "DELETE FROM daily_chat_stats WHERE daily_stats_id = ?"
        return self.connection.execute_update(query, (daily_stats_id,))
    
    def insert_daily_user_chat_stats(self, daily_stats_id: int, date, monitoring_groups_hash: str,
                                    user_chat_stats: dict) -> None:
        """Insert detailed user-chat statistics records."""
        query = """
            INSERT OR REPLACE INTO daily_user_chat_stats
            (daily_stats_id, date, monitoring_groups_hash, user_id, chat_id, messages, percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        with self.connection.get_connection() as conn:
            cursor = conn.cursor()
            
            for (user_id, chat_id), messages in user_chat_stats.items():
                # percentage will be calculated later, set to 0 for now
                params = (daily_stats_id, date, monitoring_groups_hash, user_id, chat_id, messages, 0.0)
                cursor.execute(query, params)
            
            conn.commit()

    def get_user_chat_statistics(self, date, monitoring_groups_hash: str) -> list:
        """Get detailed user-chat statistics for a specific date and monitoring groups hash."""
        query = """
            SELECT user_id, chat_id, messages, percentage 
            FROM daily_user_chat_stats 
            WHERE date = ? AND monitoring_groups_hash = ?
            ORDER BY messages DESC
        """
        return self.connection.execute_query(query, (date, monitoring_groups_hash))

    def get_filtered_user_statistics_from_details(self, date: str, monitoring_groups_hash: str, 
                                                 chat_ids: set = None, user_ids: set = None) -> list:
        """Get aggregated user statistics from detailed data with filtering."""
        base_query = """
            SELECT uc.user_id, u.user_name, SUM(uc.messages) as total_messages
            FROM daily_user_chat_stats uc
            LEFT JOIN daily_user_stats u ON u.user_id = uc.user_id AND u.date = uc.date AND u.monitoring_groups_hash = uc.monitoring_groups_hash
            WHERE uc.date = ? AND uc.monitoring_groups_hash = ?
        """
        
        params = [date, monitoring_groups_hash]
        conditions = []
        
        if chat_ids:
            placeholders = ','.join(['?' for _ in chat_ids])
            conditions.append(f"uc.chat_id IN ({placeholders})")
            params.extend(chat_ids)
        
        if user_ids:
            placeholders = ','.join(['?' for _ in user_ids])
            conditions.append(f"uc.user_id IN ({placeholders})")
            params.extend(user_ids)
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += " GROUP BY uc.user_id, u.user_name ORDER BY total_messages DESC"
        
        return self.connection.execute_query(base_query, params)

    def get_filtered_chat_statistics_from_details(self, date: str, monitoring_groups_hash: str,
                                                 chat_ids: set = None, user_ids: set = None) -> list:
        """Get aggregated chat statistics from detailed data with filtering."""
        base_query = """
            SELECT uc.chat_id, c.chat_title, SUM(uc.messages) as total_messages
            FROM daily_user_chat_stats uc
            LEFT JOIN daily_chat_stats c ON c.chat_id = uc.chat_id AND c.date = uc.date AND c.monitoring_groups_hash = uc.monitoring_groups_hash
            WHERE uc.date = ? AND uc.monitoring_groups_hash = ?
        """
        
        params = [date, monitoring_groups_hash]
        conditions = []
        
        if chat_ids:
            placeholders = ','.join(['?' for _ in chat_ids])
            conditions.append(f"uc.chat_id IN ({placeholders})")
            params.extend(chat_ids)
        
        if user_ids:
            placeholders = ','.join(['?' for _ in user_ids])
            conditions.append(f"uc.user_id IN ({placeholders})")
            params.extend(user_ids)
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += " GROUP BY uc.chat_id, c.chat_title ORDER BY total_messages DESC"
        
        return self.connection.execute_query(base_query, params)

    def delete_user_chat_stats_for_collection(self, daily_stats_id: int) -> int:
        """Delete detailed user-chat statistics for a specific collection (for re-collection)."""
        query = "DELETE FROM daily_user_chat_stats WHERE daily_stats_id = ?"
        return self.connection.execute_update(query, (daily_stats_id,)) 