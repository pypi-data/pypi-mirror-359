"""
Database schema management.

This module handles database schema creation, validation, and migrations.
"""

import logging
from typing import Dict, Any, Set
from .connection import DatabaseConnection


logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages database schema creation, validation, and migrations."""
    
    def __init__(self, connection: DatabaseConnection):
        """Initialize schema manager with database connection."""
        self.connection = connection
    
    def initialize_schema(self) -> None:
        """Initialize database and create schema if needed."""
        # For in-memory databases or new files, always create schema
        if str(self.connection.db_path) == ":memory:" or not self.connection.db_path.exists():
            logger.info(f"Creating new database: {self.connection.db_path}")
            self.create_schema()
        else:
            logger.debug(f"Using existing database: {self.connection.db_path}")
            # Validate existing schema and create if needed
            validation = self.validate_schema()
            if not validation["valid"]:
                logger.info("Database schema invalid, recreating...")
                self.create_schema()
        
        logger.info("Database schema initialized successfully")
    
    def create_schema(self) -> None:
        """Create database schema with all required tables."""
        with self.connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Schema migrations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    description TEXT NOT NULL
                )
            """)
            
            # Main daily statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    monitoring_groups_hash TEXT NOT NULL,
                    total_messages INTEGER NOT NULL,
                    collection_started_at TIMESTAMP NOT NULL,
                    collection_completed_at TIMESTAMP,
                    collection_status TEXT NOT NULL DEFAULT 'in_progress' 
                        CHECK (collection_status IN ('in_progress', 'completed', 'failed')),
                    errors_count INTEGER DEFAULT 0,
                    media_groups_processed INTEGER DEFAULT 0,
                    monitoring_groups_used TEXT,
                    UNIQUE(date, monitoring_groups_hash)
                )
            """)
            
            # User statistics table (aggregated - for compatibility)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_user_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    daily_stats_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    monitoring_groups_hash TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    messages INTEGER NOT NULL,
                    percentage REAL NOT NULL,
                    UNIQUE(date, monitoring_groups_hash, user_id),
                    FOREIGN KEY (daily_stats_id) REFERENCES daily_statistics(id)
                )
            """)
            
            # Chat statistics table (aggregated - for compatibility)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_chat_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    daily_stats_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    monitoring_groups_hash TEXT NOT NULL,
                    chat_id INTEGER NOT NULL,
                    chat_title TEXT NOT NULL,
                    messages INTEGER NOT NULL,
                    percentage REAL NOT NULL,
                    UNIQUE(date, monitoring_groups_hash, chat_id),
                    FOREIGN KEY (daily_stats_id) REFERENCES daily_statistics(id)
                )
            """)
            
            # НОВАЯ ТАБЛИЦА: User-Chat detailed statistics (решает проблему фильтрации)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_user_chat_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    daily_stats_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    monitoring_groups_hash TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    messages INTEGER NOT NULL,
                    percentage REAL NOT NULL DEFAULT 0,
                    UNIQUE(date, monitoring_groups_hash, user_id, chat_id),
                    FOREIGN KEY (daily_stats_id) REFERENCES daily_statistics(id)
                )
            """)
            
            # User cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_cache (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT,
                    username TEXT,
                    last_seen TIMESTAMP,
                    cached_at TIMESTAMP NOT NULL
                )
            """)
            
            # Chat cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_cache (
                    chat_id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    type TEXT,
                    members_count INTEGER,
                    accessible BOOLEAN NOT NULL,
                    cached_at TIMESTAMP NOT NULL
                )
            """)
            
            # Create indexes for performance
            self._create_indexes(cursor)
            
            # Insert initial migration record
            cursor.execute("""
                INSERT OR IGNORE INTO schema_migrations (version, description)
                VALUES (1, 'Initial schema creation with user-chat details')
            """)
            
            conn.commit()
            logger.info("Database schema created successfully")
    
    def _create_indexes(self, cursor) -> None:
        """Create performance indexes."""
        indexes = [
            """CREATE INDEX IF NOT EXISTS idx_daily_user_stats_date_hash_user 
               ON daily_user_stats(date, monitoring_groups_hash, user_id)""",
            
            """CREATE INDEX IF NOT EXISTS idx_daily_chat_stats_date_hash_chat 
               ON daily_chat_stats(date, monitoring_groups_hash, chat_id)""",
            
            # КРИТИЧЕСКИЕ ИНДЕКСЫ для новой таблицы daily_user_chat_stats
            """CREATE INDEX IF NOT EXISTS idx_daily_user_chat_date 
               ON daily_user_chat_stats(date, monitoring_groups_hash)""",
            
            """CREATE INDEX IF NOT EXISTS idx_daily_user_chat_user 
               ON daily_user_chat_stats(user_id, date)""",
            
            """CREATE INDEX IF NOT EXISTS idx_daily_user_chat_chat 
               ON daily_user_chat_stats(chat_id, date)""",
            
            """CREATE INDEX IF NOT EXISTS idx_daily_user_chat_combined 
               ON daily_user_chat_stats(date, monitoring_groups_hash, user_id, chat_id)""",
            
            """CREATE INDEX IF NOT EXISTS idx_user_cache_last_seen 
               ON user_cache(last_seen)""",
            
            """CREATE INDEX IF NOT EXISTS idx_chat_cache_accessible 
               ON chat_cache(accessible, cached_at)""",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def validate_schema(self) -> Dict[str, Any]:
        """Validate database schema and return validation results."""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "table_counts": {}
        }
        
        expected_tables = {
            "schema_migrations",
            "daily_statistics", 
            "daily_user_stats",
            "daily_chat_stats",
            "daily_user_chat_stats",
            "user_cache",
            "chat_cache"
        }
        
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if all expected tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = {row[0] for row in cursor.fetchall()}
                
                # Check for missing tables
                missing_tables = expected_tables - existing_tables
                for table in missing_tables:
                    validation["valid"] = False
                    validation["errors"].append(f"Missing table: {table}")
                
                # Get row counts for existing expected tables
                for table in expected_tables.intersection(existing_tables):
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    validation["table_counts"][table] = cursor.fetchone()[0]
                
                # Check for orphaned tables
                unexpected_tables = existing_tables - expected_tables
                for table in unexpected_tables:
                    if not table.startswith("sqlite_"):
                        validation["warnings"].append(f"Unexpected table: {table}")
                        
        except Exception as e:
            validation["valid"] = False
            validation["errors"].append(f"Schema validation failed: {e}")
        
        return validation
    
    def get_schema_version(self) -> int:
        """Get current schema version."""
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(version) FROM schema_migrations")
                result = cursor.fetchone()
                return result[0] if result and result[0] is not None else 0
        except Exception:
            return 0
    
    def validate_database(self) -> Dict[str, Any]:
        """Validate database integrity and return results."""
        return self.validate_schema()
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get summary statistics from database."""
        summary = {
            "collections": {},
            "users": {},
            "chats": {},
            "cache": {},
            "date_range": {}
        }
        
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Collection statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN collection_status = 'completed' THEN 1 END) as completed,
                        COUNT(CASE WHEN collection_status = 'failed' THEN 1 END) as failed,
                        SUM(total_messages) as total_messages,
                        MIN(date) as earliest_date,
                        MAX(date) as latest_date
                    FROM daily_statistics
                """)
                row = cursor.fetchone()
                if row:
                    summary["collections"] = dict(row)
                
                # User statistics
                cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT user_id) as unique_users,
                        SUM(messages) as total_messages
                    FROM daily_user_stats
                """)
                row = cursor.fetchone()
                if row:
                    summary["users"] = dict(row)
                
                # Chat statistics
                cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT chat_id) as unique_chats,
                        SUM(messages) as total_messages
                    FROM daily_chat_stats
                """)
                row = cursor.fetchone()
                if row:
                    summary["chats"] = dict(row)
                
                # Cache statistics
                cursor.execute("SELECT COUNT(*) FROM user_cache")
                summary["cache"]["users_cached"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM chat_cache")
                summary["cache"]["chats_cached"] = cursor.fetchone()[0]
                
        except Exception as e:
            logger.error(f"Error getting statistics summary: {e}")
            summary["error"] = str(e)
        
        return summary
    
    def apply_migrations(self) -> Dict[str, Any]:
        """Apply pending database migrations."""
        result = {
            "applied_migrations": [],
            "errors": [],
            "current_version": self.get_schema_version()
        }
        
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                current_version = self.get_schema_version()
                
                # Migration 2: Add daily_user_chat_stats table
                if current_version < 2:
                    logger.info("Applying migration 2: Add daily_user_chat_stats table")
                    
                    # Create new table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS daily_user_chat_stats (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            daily_stats_id INTEGER NOT NULL,
                            date DATE NOT NULL,
                            monitoring_groups_hash TEXT NOT NULL,
                            user_id INTEGER NOT NULL,
                            chat_id INTEGER NOT NULL,
                            messages INTEGER NOT NULL,
                            percentage REAL NOT NULL DEFAULT 0,
                            UNIQUE(date, monitoring_groups_hash, user_id, chat_id),
                            FOREIGN KEY (daily_stats_id) REFERENCES daily_statistics(id)
                        )
                    """)
                    
                    # Create indexes
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_daily_user_chat_date 
                        ON daily_user_chat_stats(date, monitoring_groups_hash)
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_daily_user_chat_user 
                        ON daily_user_chat_stats(user_id, date)
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_daily_user_chat_chat 
                        ON daily_user_chat_stats(chat_id, date)
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_daily_user_chat_combined 
                        ON daily_user_chat_stats(date, monitoring_groups_hash, user_id, chat_id)
                    """)
                    
                    # Record migration
                    cursor.execute("""
                        INSERT INTO schema_migrations (version, description)
                        VALUES (2, 'Add daily_user_chat_stats table for detailed filtering')
                    """)
                    
                    result["applied_migrations"].append("v2: Add daily_user_chat_stats table")
                    logger.info("Migration 2 applied successfully")
                
                conn.commit()
                result["current_version"] = 2
                
        except Exception as e:
            result["errors"].append(f"Migration failed: {e}")
            logger.error(f"Migration failed: {e}")
        
        return result 