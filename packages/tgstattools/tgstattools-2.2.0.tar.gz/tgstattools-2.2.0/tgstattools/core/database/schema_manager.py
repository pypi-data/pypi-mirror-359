"""
Database schema management (Refactored).

This module handles database schema creation, validation, and migrations
with proper separation of concerns.

REFACTORED: This module now uses modular architecture following SRP principles:
- SchemaCreator: Database table creation
- SchemaValidator: Structure validation
- MigrationRunner: Schema migrations
- DbStatistics: Database metrics
- IndexManager: Performance optimization

Single Responsibility: Coordinating schema management operations using specialized services.
"""

import logging
from typing import Dict, Any
from .connection import DatabaseConnection
from .schema import SchemaCreator, SchemaValidator, MigrationRunner, DbStatistics, IndexManager

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages database schema creation, validation, and migrations using modular architecture."""
    
    def __init__(self, connection: DatabaseConnection):
        """Initialize schema manager with modular components."""
        self.connection = connection
        
        # Initialize specialized components
        self.schema_creator = SchemaCreator(connection)
        self.schema_validator = SchemaValidator(connection)
        self.migration_runner = MigrationRunner(connection)
        self.db_statistics = DbStatistics(connection)
        self.index_manager = IndexManager(connection)
    
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
        self.schema_creator.create_schema()
    
    def validate_schema(self) -> Dict[str, Any]:
        """Validate database schema and return validation results."""
        return self.schema_validator.validate_schema()
    
    def get_schema_version(self) -> int:
        """Get current schema version."""
        return self.schema_validator.get_schema_version()
    
    def validate_database(self) -> Dict[str, Any]:
        """Validate database (alias for validate_schema for backward compatibility)."""
        return self.validate_schema()
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get comprehensive database statistics summary."""
        return self.db_statistics.get_statistics_summary()
    
    def apply_migrations(self) -> Dict[str, Any]:
        """Apply pending migrations."""
        return self.migration_runner.apply_migrations()
    
    # Additional convenience methods for backward compatibility
    def check_table_exists(self, table_name: str) -> bool:
        """Check if a specific table exists."""
        return self.schema_validator.check_table_exists(table_name)
    
    def create_table_if_not_exists(self, table_name: str, table_sql: str) -> bool:
        """Create a specific table if it doesn't exist."""
        return self.schema_creator.create_table_if_not_exists(table_name, table_sql)
    
    def get_table_row_count(self, table_name: str) -> int:
        """Get row count for a specific table."""
        return self.db_statistics.get_table_row_count(table_name)
    
    def create_index(self, index_name: str, table_name: str, columns: list, unique: bool = False) -> bool:
        """Create a specific index."""
        return self.index_manager.create_index(index_name, table_name, columns, unique)
    
    def list_indexes(self) -> list:
        """List all indexes in the database."""
        return self.index_manager.list_indexes()
    
    def get_migration_history(self) -> list:
        """Get migration history."""
        return self.migration_runner.get_migration_history()
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get detailed disk usage information."""
        return self.db_statistics.get_disk_usage() 