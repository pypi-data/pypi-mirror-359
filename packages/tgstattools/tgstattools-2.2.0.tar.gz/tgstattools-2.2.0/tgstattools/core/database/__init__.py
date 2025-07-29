"""
Database package for TgStatTools.

This package provides database operations divided by responsibility:
- DatabaseConnection: Base connection management
- SchemaManager: Schema creation and validation  
- StatisticsRepository: Statistics data operations
- CacheService: User and chat caching
- Database: Backward-compatible unified interface
"""

from .connection import DatabaseConnection
from .schema_manager import SchemaManager
from .statistics_repository import StatisticsRepository
from .cache_service import CacheService
from typing import Dict, Any


class Database:
    """
    Unified database interface for backward compatibility.
    
    This class aggregates all database services into a single interface
    to maintain compatibility with existing code while benefiting from
    the new modular architecture.
    """
    
    def __init__(self, db_path: str = None):
        """Initialize database with all services."""
        # Core connection
        self.connection = DatabaseConnection(db_path)
        
        # Service components
        self.schema = SchemaManager(self.connection)
        self.stats = StatisticsRepository(self.connection)
        self.cache = CacheService(self.connection)
        
        # Initialize schema
        self.schema.initialize_schema()
    
    # === Connection and basic operations ===
    def get_connection(self):
        """Get database connection context manager."""
        return self.connection.get_connection()
    
    def get_database_path(self) -> str:
        """Get database file path."""
        return self.connection.get_database_path()
    
    def close(self) -> None:
        """Close database connections."""
        return self.connection.close()
    
    def initialize(self) -> None:
        """Initialize database schema."""
        return self.schema.initialize_schema()
    
    def execute_query(self, query: str, params=None):
        """Execute SELECT query."""
        return self.connection.execute_query(query, params)
    
    def execute_update(self, query: str, params=None) -> int:
        """Execute UPDATE/INSERT/DELETE query."""
        return self.connection.execute_update(query, params)
    
    # === Schema operations ===
    def validate_schema(self):
        """Validate database schema."""
        return self.schema.validate_schema()
    
    def validate_database(self):
        """Validate database integrity."""
        return self.schema.validate_database()
    
    def get_schema_version(self) -> int:
        """Get schema version."""
        return self.schema.get_schema_version()
    
    def get_database_info(self):
        """Get database information."""
        return self.connection.get_database_info()
    
    def get_statistics_summary(self):
        """Get statistics summary."""
        return self.schema.get_statistics_summary()
    
    # === Statistics operations ===
    def insert_daily_statistics(self, date, monitoring_groups_hash, total_messages, 
                               collection_started_at, collection_completed_at=None,
                               collection_status="in_progress", errors_count=0,
                               media_groups_processed=0, monitoring_groups_used=None) -> int:
        """Insert daily statistics record."""
        return self.stats.insert_daily_statistics(
            date, monitoring_groups_hash, total_messages, collection_started_at,
            collection_completed_at, collection_status, errors_count,
            media_groups_processed, monitoring_groups_used
        )
    
    def upsert_daily_statistics(self, date, monitoring_groups_hash, total_messages,
                               collection_started_at, collection_completed_at=None,
                               collection_status="in_progress", errors_count=0,
                               media_groups_processed=0, monitoring_groups_used=None) -> int:
        """Insert or update daily statistics."""
        return self.stats.upsert_daily_statistics(
            date, monitoring_groups_hash, total_messages, collection_started_at,
            collection_completed_at, collection_status, errors_count,
            media_groups_processed, monitoring_groups_used
        )
    
    def get_daily_statistics(self, date, monitoring_groups_hash: str):
        """Get daily statistics."""
        return self.stats.get_daily_statistics(date, monitoring_groups_hash)
    
    def collection_exists(self, date, monitoring_groups_hash: str) -> bool:
        """Check if collection exists."""
        return self.stats.collection_exists(date, monitoring_groups_hash)
    
    def complete_collection(self, stats_id: int, errors_count: int, 
                           media_groups_processed: int) -> None:
        """Mark collection as completed."""
        return self.stats.complete_collection(stats_id, errors_count, media_groups_processed)
    
    def insert_daily_user_stats(self, daily_stats_id: int, date, monitoring_groups_hash: str,
                               user_id: int, user_name: str, messages: int, percentage: float) -> None:
        """Insert user statistics record."""
        return self.stats.insert_daily_user_stats(
            daily_stats_id, date, monitoring_groups_hash, user_id, user_name, messages, percentage
        )
    
    def insert_daily_chat_stats(self, daily_stats_id: int, date, monitoring_groups_hash: str,
                               chat_id: int, chat_title: str, messages: int, percentage: float) -> None:
        """Insert chat statistics record."""
        return self.stats.insert_daily_chat_stats(
            daily_stats_id, date, monitoring_groups_hash, chat_id, chat_title, messages, percentage
        )
    
    def insert_user_stats(self, stats_id: int, date, monitoring_groups_hash: str, 
                         user_stats) -> None:
        """Insert user statistics (batch)."""
        return self.stats.insert_user_stats(stats_id, date, monitoring_groups_hash, user_stats)
    
    def insert_chat_stats(self, stats_id: int, date, monitoring_groups_hash: str,
                         chat_stats) -> None:
        """Insert chat statistics (batch)."""
        return self.stats.insert_chat_stats(stats_id, date, monitoring_groups_hash, chat_stats)
    
    def delete_user_stats_for_collection(self, daily_stats_id: int) -> int:
        """Delete user statistics for a specific collection (for re-collection)."""
        return self.stats.delete_user_stats_for_collection(daily_stats_id)
    
    def delete_chat_stats_for_collection(self, daily_stats_id: int) -> int:
        """Delete chat statistics for a specific collection (for re-collection)."""
        return self.stats.delete_chat_stats_for_collection(daily_stats_id)
    
    def insert_daily_user_chat_stats(self, daily_stats_id: int, date, monitoring_groups_hash: str,
                                    user_chat_stats: dict) -> None:
        """Insert detailed user-chat statistics."""
        return self.stats.insert_daily_user_chat_stats(
            daily_stats_id, date, monitoring_groups_hash, user_chat_stats
        )

    def get_user_chat_statistics(self, date, monitoring_groups_hash: str) -> list:
        """Get detailed user-chat statistics."""
        return self.stats.get_user_chat_statistics(date, monitoring_groups_hash)

    def get_filtered_user_statistics_from_details(self, date: str, monitoring_groups_hash: str,
                                                 chat_ids: set = None, user_ids: set = None) -> list:
        """Get filtered user statistics from detailed data."""
        return self.stats.get_filtered_user_statistics_from_details(
            date, monitoring_groups_hash, chat_ids, user_ids
        )

    def get_filtered_chat_statistics_from_details(self, date: str, monitoring_groups_hash: str,
                                                 chat_ids: set = None, user_ids: set = None) -> list:
        """Get filtered chat statistics from detailed data."""
        return self.stats.get_filtered_chat_statistics_from_details(
            date, monitoring_groups_hash, chat_ids, user_ids
        )

    def delete_user_chat_stats_for_collection(self, daily_stats_id: int) -> int:
        """Delete detailed user-chat statistics for re-collection."""
        return self.stats.delete_user_chat_stats_for_collection(daily_stats_id)
    
    # === Cache operations ===
    def update_user_cache(self, user_id: int, user_data) -> None:
        """Update user cache."""
        return self.cache.update_user_cache(user_id, user_data)
    
    def get_user_from_cache(self, user_id: int):
        """Get user from cache."""
        return self.cache.get_user_from_cache(user_id)
    
    def update_chat_cache(self, chat_id: int, chat_data) -> None:
        """Update chat cache."""
        return self.cache.update_chat_cache(chat_id, chat_data)
    
    def get_chat_from_cache(self, chat_id: int):
        """Get chat from cache."""
        return self.cache.get_chat_from_cache(chat_id)
    
    def cleanup_old_cache(self, days_old: int = 30) -> int:
        """Clean up old cache entries."""
        return self.cache.cleanup_old_cache(days_old)

    def apply_migrations(self) -> Dict[str, Any]:
        """Apply pending database migrations."""
        return self.schema.apply_migrations()


# Factory function for creating database instances
def create_database(db_path: str = None) -> Database:
    """Create a new database instance with all services."""
    return Database(db_path)


# Export classes for direct use if needed
__all__ = [
    'Database',
    'DatabaseConnection', 
    'SchemaManager',
    'StatisticsRepository',
    'CacheService',
    'create_database'
] 