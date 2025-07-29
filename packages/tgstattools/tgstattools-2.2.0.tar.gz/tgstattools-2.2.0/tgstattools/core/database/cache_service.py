"""
Cache service for users and chats.

This module handles caching operations for user and chat data
to improve performance and reduce API calls.
"""

import logging
from typing import Dict, Any, Optional
from .connection import DatabaseConnection


logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching user and chat data."""
    
    def __init__(self, connection: DatabaseConnection):
        """Initialize cache service with database connection."""
        self.connection = connection
    
    # User Cache Operations
    def update_user_cache(self, user_id: int, user_data: Dict[str, Any]) -> None:
        """Update user cache with new data."""
        query = """
            INSERT OR REPLACE INTO user_cache
            (user_id, name, username, last_seen, cached_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """
        params = (user_id, user_data.get("name"), user_data.get("username"),
                 user_data.get("last_seen"))
        
        self.connection.execute_update(query, params)
        logger.debug(f"Updated user cache for user {user_id}")
    
    def get_user_from_cache(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from cache."""
        query = "SELECT * FROM user_cache WHERE user_id = ?"
        results = self.connection.execute_query(query, (user_id,))
        
        if results:
            row = results[0]
            return {
                "user_id": row["user_id"],
                "name": row["name"],
                "username": row["username"],
                "last_seen": row["last_seen"],
                "cached_at": row["cached_at"]
            }
        return None
    
    def bulk_update_user_cache(self, users: Dict[int, Dict[str, Any]]) -> int:
        """Bulk update user cache for multiple users."""
        query = """
            INSERT OR REPLACE INTO user_cache
            (user_id, name, username, last_seen, cached_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """
        
        updated_count = 0
        with self.connection.get_connection() as conn:
            cursor = conn.cursor()
            
            for user_id, user_data in users.items():
                params = (user_id, user_data.get("name"), user_data.get("username"),
                         user_data.get("last_seen"))
                cursor.execute(query, params)
                updated_count += 1
            
            conn.commit()
        
        logger.debug(f"Bulk updated {updated_count} users in cache")
        return updated_count
    
    def get_all_cached_users(self) -> Dict[int, Dict[str, Any]]:
        """Get all cached users."""
        query = "SELECT * FROM user_cache ORDER BY cached_at DESC"
        results = self.connection.execute_query(query)
        
        users = {}
        for row in results:
            users[row["user_id"]] = {
                "name": row["name"],
                "username": row["username"],
                "last_seen": row["last_seen"],
                "cached_at": row["cached_at"]
            }
        
        return users
    
    # Chat Cache Operations
    def update_chat_cache(self, chat_id: int, chat_data: Dict[str, Any]) -> None:
        """Update chat cache with new data."""
        query = """
            INSERT OR REPLACE INTO chat_cache
            (chat_id, title, type, members_count, accessible, cached_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """
        params = (chat_id, chat_data.get("title"), chat_data.get("type"),
                 chat_data.get("members_count"), chat_data.get("accessible", True))
        
        self.connection.execute_update(query, params)
        logger.debug(f"Updated chat cache for chat {chat_id}")
    
    def get_chat_from_cache(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get chat data from cache."""
        query = "SELECT * FROM chat_cache WHERE chat_id = ?"
        results = self.connection.execute_query(query, (chat_id,))
        
        if results:
            row = results[0]
            return {
                "chat_id": row["chat_id"],
                "title": row["title"],
                "type": row["type"],
                "members_count": row["members_count"],
                "accessible": row["accessible"],
                "cached_at": row["cached_at"]
            }
        return None
    
    def bulk_update_chat_cache(self, chats: Dict[int, Dict[str, Any]]) -> int:
        """Bulk update chat cache for multiple chats."""
        query = """
            INSERT OR REPLACE INTO chat_cache
            (chat_id, title, type, members_count, accessible, cached_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """
        
        updated_count = 0
        with self.connection.get_connection() as conn:
            cursor = conn.cursor()
            
            for chat_id, chat_data in chats.items():
                params = (chat_id, chat_data.get("title"), chat_data.get("type"),
                         chat_data.get("members_count"), chat_data.get("accessible", True))
                cursor.execute(query, params)
                updated_count += 1
            
            conn.commit()
        
        logger.debug(f"Bulk updated {updated_count} chats in cache")
        return updated_count
    
    def get_all_cached_chats(self) -> Dict[int, Dict[str, Any]]:
        """Get all cached chats."""
        query = "SELECT * FROM chat_cache ORDER BY cached_at DESC"
        results = self.connection.execute_query(query)
        
        chats = {}
        for row in results:
            chats[row["chat_id"]] = {
                "title": row["title"],
                "type": row["type"],
                "members_count": row["members_count"],
                "accessible": row["accessible"],
                "cached_at": row["cached_at"]
            }
        
        return chats
    
    def get_accessible_chats(self) -> Dict[int, Dict[str, Any]]:
        """Get only accessible cached chats."""
        query = "SELECT * FROM chat_cache WHERE accessible = 1 ORDER BY cached_at DESC"
        results = self.connection.execute_query(query)
        
        chats = {}
        for row in results:
            chats[row["chat_id"]] = {
                "title": row["title"],
                "type": row["type"],
                "members_count": row["members_count"],
                "accessible": row["accessible"],
                "cached_at": row["cached_at"]
            }
        
        return chats
    
    # Cache Cleanup Operations
    def cleanup_old_cache(self, days_old: int = 30) -> int:
        """Clean up old cache entries and return number of deleted records."""
        user_query = """
            DELETE FROM user_cache 
            WHERE cached_at < datetime('now', '-{} days')
        """.format(days_old)
        
        deleted_users = self.connection.execute_update(user_query)
        
        chat_query = """
            DELETE FROM chat_cache 
            WHERE cached_at < datetime('now', '-{} days')
        """.format(days_old)
        
        deleted_chats = self.connection.execute_update(chat_query)
        
        total_deleted = deleted_users + deleted_chats
        logger.info(f"Cleaned up {total_deleted} old cache entries (users: {deleted_users}, chats: {deleted_chats})")
        
        return total_deleted
    
    def cleanup_user_cache(self, days_old: int = 30) -> int:
        """Clean up old user cache entries."""
        query = """
            DELETE FROM user_cache 
            WHERE cached_at < datetime('now', '-{} days')
        """.format(days_old)
        
        deleted = self.connection.execute_update(query)
        logger.info(f"Cleaned up {deleted} old user cache entries")
        return deleted
    
    def cleanup_chat_cache(self, days_old: int = 30) -> int:
        """Clean up old chat cache entries."""
        query = """
            DELETE FROM chat_cache 
            WHERE cached_at < datetime('now', '-{} days')
        """.format(days_old)
        
        deleted = self.connection.execute_update(query)
        logger.info(f"Cleaned up {deleted} old chat cache entries")
        return deleted
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "users": {
                "total": 0,
                "with_names": 0,
                "with_usernames": 0
            },
            "chats": {
                "total": 0,
                "accessible": 0,
                "by_type": {}
            }
        }
        
        # User stats
        user_results = self.connection.execute_query("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN name IS NOT NULL AND name != '' THEN 1 END) as with_names,
                COUNT(CASE WHEN username IS NOT NULL AND username != '' THEN 1 END) as with_usernames
            FROM user_cache
        """)
        if user_results:
            row = user_results[0]
            stats["users"] = dict(row)
        
        # Chat stats
        chat_results = self.connection.execute_query("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN accessible = 1 THEN 1 END) as accessible
            FROM chat_cache
        """)
        if chat_results:
            row = chat_results[0]
            stats["chats"]["total"] = row["total"]
            stats["chats"]["accessible"] = row["accessible"]
        
        # Chat types
        type_results = self.connection.execute_query("""
            SELECT type, COUNT(*) as count 
            FROM chat_cache 
            GROUP BY type
        """)
        for row in type_results:
            stats["chats"]["by_type"][row["type"] or "unknown"] = row["count"]
        
        return stats 