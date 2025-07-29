"""
Database schema validation utilities.

This module handles validating database structure and integrity.
Single Responsibility: Validating database schema and structure.
"""

import logging
from typing import Dict, Any, Set
from ..connection import DatabaseConnection

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Handles database schema validation."""
    
    def __init__(self, connection: DatabaseConnection):
        """
        Initialize schema validator.
        
        Args:
            connection: Database connection instance
        """
        self.connection = connection
    
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
                
                # Get existing tables
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                existing_tables = {row[0] for row in cursor.fetchall()}
                
                # Check for missing tables
                missing_tables = expected_tables - existing_tables
                if missing_tables:
                    validation["valid"] = False
                    validation["errors"].append(f"Missing tables: {missing_tables}")
                
                # Check for unexpected tables
                unexpected_tables = existing_tables - expected_tables
                if unexpected_tables:
                    validation["warnings"].append(f"Unexpected tables: {unexpected_tables}")
                
                # Get table counts
                for table in existing_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        validation["table_counts"][table] = count
                    except Exception as e:
                        validation["warnings"].append(f"Could not count {table}: {e}")
                
                # Validate table structures
                structure_validation = self._validate_table_structures()
                validation.update(structure_validation)
                
        except Exception as e:
            validation["valid"] = False
            validation["errors"].append(f"Schema validation error: {e}")
            logger.exception("Schema validation failed")
        
        return validation
    
    def _validate_table_structures(self) -> Dict[str, Any]:
        """Validate individual table structures."""
        validation = {
            "structure_errors": [],
            "structure_warnings": []
        }
        
        table_schemas = self._get_expected_table_schemas()
        
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                for table_name, expected_columns in table_schemas.items():
                    try:
                        # Get actual table schema
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        actual_columns = {row[1]: row[2] for row in cursor.fetchall()}
                        
                        # Check for missing columns
                        missing_columns = set(expected_columns.keys()) - set(actual_columns.keys())
                        if missing_columns:
                            validation["structure_errors"].append(
                                f"Table {table_name} missing columns: {missing_columns}"
                            )
                        
                        # Check for type mismatches
                        for col_name, expected_type in expected_columns.items():
                            if col_name in actual_columns:
                                actual_type = actual_columns[col_name].upper()
                                expected_type = expected_type.upper()
                                if actual_type != expected_type:
                                    validation["structure_warnings"].append(
                                        f"Table {table_name} column {col_name}: "
                                        f"expected {expected_type}, got {actual_type}"
                                    )
                    
                    except Exception as e:
                        validation["structure_errors"].append(
                            f"Could not validate table {table_name}: {e}"
                        )
        
        except Exception as e:
            validation["structure_errors"].append(f"Structure validation error: {e}")
        
        return validation
    
    def _get_expected_table_schemas(self) -> Dict[str, Dict[str, str]]:
        """Get expected table schemas for validation."""
        return {
            "daily_statistics": {
                "id": "INTEGER",
                "date": "DATE",
                "monitoring_groups_hash": "TEXT",
                "total_messages": "INTEGER",
                "collection_started_at": "TIMESTAMP",
                "collection_completed_at": "TIMESTAMP",
                "collection_status": "TEXT",
                "errors_count": "INTEGER",
                "media_groups_processed": "INTEGER",
                "monitoring_groups_used": "TEXT"
            },
            "daily_user_stats": {
                "id": "INTEGER",
                "daily_stats_id": "INTEGER",
                "date": "DATE",
                "monitoring_groups_hash": "TEXT",
                "user_id": "INTEGER",
                "user_name": "TEXT",
                "messages": "INTEGER",
                "percentage": "REAL"
            },
            "daily_chat_stats": {
                "id": "INTEGER",
                "daily_stats_id": "INTEGER",
                "date": "DATE",
                "monitoring_groups_hash": "TEXT",
                "chat_id": "INTEGER",
                "chat_title": "TEXT",
                "messages": "INTEGER",
                "percentage": "REAL"
            },
            "daily_user_chat_stats": {
                "id": "INTEGER",
                "daily_stats_id": "INTEGER",
                "date": "DATE",
                "monitoring_groups_hash": "TEXT",
                "user_id": "INTEGER",
                "chat_id": "INTEGER",
                "messages": "INTEGER",
                "percentage": "REAL"
            }
        }
    
    def get_schema_version(self) -> int:
        """Get current schema version."""
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(version) FROM schema_migrations")
                result = cursor.fetchone()
                return result[0] if result and result[0] else 0
        except Exception:
            return 0
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if a specific table exists."""
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table_name,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking table {table_name}: {e}")
            return False 