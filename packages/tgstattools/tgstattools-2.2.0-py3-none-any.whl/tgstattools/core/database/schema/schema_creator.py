"""
Database schema creation utilities.

This module handles creating database tables and initial structure.
Single Responsibility: Creating database schema and tables.
"""

import logging
from typing import Dict, Any
from ..connection import DatabaseConnection

logger = logging.getLogger(__name__)


class SchemaCreator:
    """Handles database schema creation."""
    
    def __init__(self, connection: DatabaseConnection):
        """
        Initialize schema creator.
        
        Args:
            connection: Database connection instance
        """
        self.connection = connection
    
    def create_schema(self) -> None:
        """Create database schema with all required tables."""
        with self.connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create all tables
            self._create_migrations_table(cursor)
            self._create_statistics_tables(cursor)
            self._create_cache_tables(cursor)
            
            # Create indexes
            from .index_manager import IndexManager
            index_manager = IndexManager(self.connection)
            index_manager.create_all_indexes()
            
            # Insert initial migration record
            cursor.execute("""
                INSERT OR IGNORE INTO schema_migrations (version, description)
                VALUES (1, 'Initial schema creation with user-chat details')
            """)
            
            conn.commit()
            logger.info("Database schema created successfully")
    
    def _create_migrations_table(self, cursor) -> None:
        """Create schema migrations table."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                description TEXT NOT NULL
            )
        """)
    
    def _create_statistics_tables(self, cursor) -> None:
        """Create statistics-related tables."""
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
        
        # User statistics table (aggregated)
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
        
        # Chat statistics table (aggregated)
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
        
        # User-Chat detailed statistics table
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
    
    def _create_cache_tables(self, cursor) -> None:
        """Create cache-related tables."""
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
    
    def create_table_if_not_exists(self, table_name: str, table_sql: str) -> bool:
        """
        Create a specific table if it doesn't exist.
        
        Args:
            table_name: Name of the table
            table_sql: SQL statement to create the table
            
        Returns:
            True if table was created, False if it already existed
        """
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table_name,))
                
                if cursor.fetchone():
                    return False  # Table already exists
                
                # Create table
                cursor.execute(table_sql)
                conn.commit()
                
                logger.info(f"Created table: {table_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating table {table_name}: {e}")
            raise 