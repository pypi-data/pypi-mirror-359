"""
Database schema management module.

This module provides schema-related functionality with proper separation of concerns:
- Schema creator for database table creation
- Schema validator for structure validation
- Migration runner for schema migrations
- DB statistics for database metrics
- Index manager for performance optimization
"""

from .schema_creator import SchemaCreator
from .schema_validator import SchemaValidator
from .migration_runner import MigrationRunner
from .db_statistics import DbStatistics
from .index_manager import IndexManager

__all__ = [
    'SchemaCreator',
    'SchemaValidator',
    'MigrationRunner',
    'DbStatistics',
    'IndexManager'
] 