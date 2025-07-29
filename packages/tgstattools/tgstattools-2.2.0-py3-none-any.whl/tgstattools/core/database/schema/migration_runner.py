"""
Database migration utilities.

This module handles database schema migrations and version management.
Single Responsibility: Managing database schema migrations.
"""

import logging
from typing import Dict, Any, List
from ..connection import DatabaseConnection

logger = logging.getLogger(__name__)


class MigrationRunner:
    """Handles database schema migrations."""
    
    def __init__(self, connection: DatabaseConnection):
        """
        Initialize migration runner.
        
        Args:
            connection: Database connection instance
        """
        self.connection = connection
    
    def apply_migrations(self) -> Dict[str, Any]:
        """Apply pending migrations."""
        result = {
            "success": True,
            "applied_migrations": [],
            "errors": []
        }
        
        try:
            current_version = self._get_current_version()
            available_migrations = self._get_available_migrations()
            
            # Filter migrations that need to be applied
            pending_migrations = [
                migration for migration in available_migrations
                if migration["version"] > current_version
            ]
            
            if not pending_migrations:
                logger.info("No pending migrations to apply")
                return result
            
            # Apply migrations in order
            for migration in sorted(pending_migrations, key=lambda x: x["version"]):
                try:
                    self._apply_migration(migration)
                    result["applied_migrations"].append(migration["version"])
                    logger.info(f"Applied migration {migration['version']}: {migration['description']}")
                except Exception as e:
                    error_msg = f"Failed to apply migration {migration['version']}: {e}"
                    result["errors"].append(error_msg)
                    result["success"] = False
                    logger.error(error_msg)
                    break  # Stop on first error
            
        except Exception as e:
            result["success"] = False
            result["errors"].append(f"Migration process failed: {e}")
            logger.exception("Migration process failed")
        
        return result
    
    def _get_current_version(self) -> int:
        """Get current schema version."""
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if migrations table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='schema_migrations'
                """)
                
                if not cursor.fetchone():
                    return 0  # No migrations table, version 0
                
                # Get latest version
                cursor.execute("SELECT MAX(version) FROM schema_migrations")
                result = cursor.fetchone()
                return result[0] if result and result[0] else 0
                
        except Exception as e:
            logger.error(f"Error getting current version: {e}")
            return 0
    
    def _get_available_migrations(self) -> List[Dict[str, Any]]:
        """Get list of available migrations."""
        # In a real system, this would read from migration files
        # For now, we define migrations programmatically
        return [
            {
                "version": 1,
                "description": "Initial schema creation",
                "sql": []  # Handled by SchemaCreator
            },
            {
                "version": 2,
                "description": "Add user-chat detailed statistics",
                "sql": [
                    """
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
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_daily_user_chat_combined 
                    ON daily_user_chat_stats(date, monitoring_groups_hash, user_id, chat_id)
                    """
                ]
            }
        ]
    
    def _apply_migration(self, migration: Dict[str, Any]) -> None:
        """Apply a single migration."""
        with self.connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Execute migration SQL
            for sql_statement in migration["sql"]:
                if sql_statement.strip():
                    cursor.execute(sql_statement)
            
            # Record migration as applied
            cursor.execute("""
                INSERT INTO schema_migrations (version, description)
                VALUES (?, ?)
            """, (migration["version"], migration["description"]))
            
            conn.commit()
    
    def rollback_migration(self, target_version: int) -> Dict[str, Any]:
        """
        Rollback to a specific schema version.
        
        Args:
            target_version: Version to rollback to
            
        Returns:
            Dictionary with rollback results
        """
        result = {
            "success": True,
            "rolled_back_migrations": [],
            "errors": []
        }
        
        try:
            current_version = self._get_current_version()
            
            if target_version >= current_version:
                logger.info(f"Already at or below target version {target_version}")
                return result
            
            # For SQLite, rollbacks are complex since we can't easily drop columns
            # This is a simplified implementation
            logger.warning("Migration rollback is not fully implemented for SQLite")
            result["errors"].append("Rollback not fully supported")
            result["success"] = False
            
        except Exception as e:
            result["success"] = False
            result["errors"].append(f"Rollback failed: {e}")
            logger.exception("Migration rollback failed")
        
        return result
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history."""
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT version, applied_at, description
                    FROM schema_migrations
                    ORDER BY version
                """)
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        "version": row[0],
                        "applied_at": row[1],
                        "description": row[2]
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Error getting migration history: {e}")
            return [] 