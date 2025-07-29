"""
Database index management utilities.

This module handles creating and managing database indexes for performance.
Single Responsibility: Managing database indexes and performance optimization.
"""

import logging
from typing import List, Dict, Any
from ..connection import DatabaseConnection

logger = logging.getLogger(__name__)


class IndexManager:
    """Handles database index creation and management."""
    
    def __init__(self, connection: DatabaseConnection):
        """
        Initialize index manager.
        
        Args:
            connection: Database connection instance
        """
        self.connection = connection
    
    def create_all_indexes(self) -> None:
        """Create all performance indexes."""
        with self.connection.get_connection() as conn:
            cursor = conn.cursor()
            
            indexes = self._get_index_definitions()
            
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    logger.debug(f"Created index: {index_sql}")
                except Exception as e:
                    logger.warning(f"Failed to create index: {e}")
            
            conn.commit()
            logger.info("Database indexes created successfully")
    
    def _get_index_definitions(self) -> List[str]:
        """Get list of index creation SQL statements."""
        return [
            # Indexes for daily_user_stats
            """CREATE INDEX IF NOT EXISTS idx_daily_user_stats_date_hash_user 
               ON daily_user_stats(date, monitoring_groups_hash, user_id)""",
            
            # Indexes for daily_chat_stats
            """CREATE INDEX IF NOT EXISTS idx_daily_chat_stats_date_hash_chat 
               ON daily_chat_stats(date, monitoring_groups_hash, chat_id)""",
            
            # Critical indexes for daily_user_chat_stats
            """CREATE INDEX IF NOT EXISTS idx_daily_user_chat_date 
               ON daily_user_chat_stats(date, monitoring_groups_hash)""",
            
            """CREATE INDEX IF NOT EXISTS idx_daily_user_chat_user 
               ON daily_user_chat_stats(user_id, date)""",
            
            """CREATE INDEX IF NOT EXISTS idx_daily_user_chat_chat 
               ON daily_user_chat_stats(chat_id, date)""",
            
            """CREATE INDEX IF NOT EXISTS idx_daily_user_chat_combined 
               ON daily_user_chat_stats(date, monitoring_groups_hash, user_id, chat_id)""",
            
            # Cache table indexes
            """CREATE INDEX IF NOT EXISTS idx_user_cache_last_seen 
               ON user_cache(last_seen)""",
            
            """CREATE INDEX IF NOT EXISTS idx_chat_cache_accessible 
               ON chat_cache(accessible, cached_at)""",
        ]
    
    def create_index(self, index_name: str, table_name: str, columns: List[str], 
                    unique: bool = False) -> bool:
        """
        Create a specific index.
        
        Args:
            index_name: Name of the index
            table_name: Table to create index on
            columns: List of column names
            unique: Whether to create unique index
            
        Returns:
            True if index was created, False if it already existed
        """
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if index exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='index' AND name=?
                """, (index_name,))
                
                if cursor.fetchone():
                    return False  # Index already exists
                
                # Build index SQL
                unique_clause = "UNIQUE " if unique else ""
                columns_clause = ", ".join(columns)
                index_sql = f"CREATE {unique_clause}INDEX {index_name} ON {table_name}({columns_clause})"
                
                cursor.execute(index_sql)
                conn.commit()
                
                logger.info(f"Created index: {index_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating index {index_name}: {e}")
            raise
    
    def drop_index(self, index_name: str) -> bool:
        """
        Drop a specific index.
        
        Args:
            index_name: Name of the index to drop
            
        Returns:
            True if index was dropped, False if it didn't exist
        """
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if index exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='index' AND name=?
                """, (index_name,))
                
                if not cursor.fetchone():
                    return False  # Index doesn't exist
                
                cursor.execute(f"DROP INDEX {index_name}")
                conn.commit()
                
                logger.info(f"Dropped index: {index_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error dropping index {index_name}: {e}")
            raise
    
    def list_indexes(self) -> List[Dict[str, Any]]:
        """
        List all indexes in the database.
        
        Returns:
            List of index information dictionaries
        """
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT name, tbl_name, sql 
                    FROM sqlite_master 
                    WHERE type='index' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                
                indexes = []
                for row in cursor.fetchall():
                    indexes.append({
                        'name': row[0],
                        'table': row[1],
                        'sql': row[2]
                    })
                
                return indexes
                
        except Exception as e:
            logger.error(f"Error listing indexes: {e}")
            return []
    
    def analyze_table(self, table_name: str) -> None:
        """
        Analyze table for query optimization.
        
        Args:
            table_name: Name of table to analyze
        """
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"ANALYZE {table_name}")
                conn.commit()
                logger.info(f"Analyzed table: {table_name}")
                
        except Exception as e:
            logger.error(f"Error analyzing table {table_name}: {e}")
            raise 