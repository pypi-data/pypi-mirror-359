"""
Database connection management.

This module provides basic SQLite database connection operations 
with connection pooling and configuration.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager


logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Base database connection manager with optimized SQLite settings."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection manager."""
        self.db_path = Path(db_path or "data/statistics.db")
        
        # For file databases, create parent directory
        if str(self.db_path) != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Enable WAL mode and other optimizations
        self._connection_config = {
            "check_same_thread": False,
            "timeout": 30.0,
        }
        
        # For in-memory databases, maintain persistent connection
        self._persistent_conn = None
        if str(self.db_path) == ":memory:":
            self._persistent_conn = self._create_connection()
        
        logger.debug(f"Database connection initialized: {self.db_path}")
    
    def _create_connection(self):
        """Create a new database connection with optimizations."""
        conn = sqlite3.connect(str(self.db_path), **self._connection_config)
        
        # Enable foreign keys and optimize settings
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = 10000")
        conn.execute("PRAGMA temp_store = MEMORY")
        
        # Row factory for easier data access
        conn.row_factory = sqlite3.Row
        
        return conn
    
    def get_database_path(self) -> str:
        """Get the absolute path to the database file."""
        if str(self.db_path) == ":memory:":
            return ":memory:"
        return str(self.db_path.absolute())
    
    def close(self) -> None:
        """Close database connections."""
        if self._persistent_conn:
            self._persistent_conn.close()
            self._persistent_conn = None
        logger.debug("Database connections closed")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling and optimization."""
        # For in-memory databases, use persistent connection
        if self._persistent_conn:
            try:
                yield self._persistent_conn
            except sqlite3.Error as e:
                self._persistent_conn.rollback()
                logger.error(f"Database error: {e}")
                raise
            return
        
        # For file databases, use context-managed connections
        conn = None
        try:
            conn = self._create_connection()
            yield conn
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[sqlite3.Row]:
        """Execute SELECT query and return results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute UPDATE/INSERT/DELETE query and return affected rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute INSERT query and return last row ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.lastrowid
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database file information."""
        info = {
            "path": str(self.db_path),
            "exists": self.db_path.exists() if str(self.db_path) != ":memory:" else True,
            "size_bytes": 0,
            "tables": [],
            "indexes": []
        }
        
        # For file databases, get file size
        if str(self.db_path) != ":memory:" and self.db_path.exists():
            info["size_bytes"] = self.db_path.stat().st_size
        
        # Always try to get table and index information
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get table names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                info["tables"] = [row[0] for row in cursor.fetchall()]
                
                # Get index names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
                info["indexes"] = [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            info["error"] = str(e)
        
        return info 