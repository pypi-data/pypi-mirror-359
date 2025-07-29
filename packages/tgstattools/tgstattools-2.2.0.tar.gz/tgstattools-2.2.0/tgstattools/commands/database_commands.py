"""
Database operation commands: backup-db, restore-db, migrate-db, validate-db.

These commands handle database backup, restore, migration and validation operations.
"""

import argparse
from typing import Any
import shutil
from datetime import datetime
from pathlib import Path
import gzip
import sqlite3
from ..core.database import Database


def register_commands(subparsers: Any) -> None:
    """Register database operation commands."""
    
    # Backup database command
    backup_parser = subparsers.add_parser(
        "backup-db",
        help="Create database backup",
        description="Create a backup of the statistics database"
    )
    backup_parser.add_argument(
        "path",
        nargs="?",
        help="Backup file path (default: data/backups/)"
    )
    backup_parser.add_argument(
        "--compress",
        action="store_true",
        help="Compress backup file"
    )
    
    # Restore database command
    restore_parser = subparsers.add_parser(
        "restore-db",
        help="Restore database from backup",
        description="Restore database from a backup file"
    )
    restore_parser.add_argument(
        "backup_path",
        help="Path to backup file"
    )
    restore_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing database without confirmation"
    )
    
    # Removed validate-db and migrate-schema commands - not needed after restore-db


def handle_backup_db(args: argparse.Namespace) -> int:
    """Handle database backup command."""
    try:
        print("Creating database backup...")
        
        # Initialize database
        db = Database()
        db_path = db.get_database_path()
        
        if not Path(db_path).exists():
            print("❌ Database file not found")
            return 1
        
        # Create backup directory if needed
        backup_dir = Path("data/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"statistics_{timestamp}.db"
        
        if args.path:
            backup_path = Path(args.path)
            if backup_path.is_dir():
                backup_path = backup_path / backup_filename
        else:
            backup_path = backup_dir / backup_filename
        
        # Create backup
        print(f"Backing up to: {backup_path}")
        
        if args.compress:
            backup_path = Path(str(backup_path) + ".gz")
            with open(db_path, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print("✅ Compressed backup created successfully")
        else:
            shutil.copy2(db_path, backup_path)
            print("✅ Backup created successfully")
        
        return 0
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return 1


def handle_restore_db(args: argparse.Namespace) -> int:
    """Handle database restore command."""
    try:
        print(f"Restoring database from: {args.backup_path}")
        
        backup_path = Path(args.backup_path)
        if not backup_path.exists():
            print("❌ Backup file not found")
            return 1
        
        # Initialize database
        db = Database()
        db_path = db.get_database_path()
        
        # Check if database exists
        if Path(db_path).exists() and not args.force:
            print("❌ Database already exists. Use --force to overwrite")
            return 1
        
        # Create database directory if needed
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Restore backup
        if str(backup_path).endswith('.gz'):
            with gzip.open(backup_path, 'rb') as f_in:
                with open(db_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy2(backup_path, db_path)
        
        print("✅ Database restored successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return 1


def handle_migrate_db(args: argparse.Namespace) -> int:
    """Handle database migration command."""
    try:
        print("Checking database migrations...")
        
        # Initialize database
        db = Database()
        
        # Get current schema version
        with db.get_connection() as conn:
            try:
                version = conn.execute("SELECT version FROM schema_migrations").fetchone()
                current_version = version[0] if version else 0
            except sqlite3.OperationalError:
                current_version = 0
        
        print(f"Current schema version: {current_version}")
        
        # Define migrations (in production this would be loaded from files)
        migrations = [
            {
                "version": 1,
                "description": "Initial schema",
                "sql": """
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version INTEGER PRIMARY KEY,
                        description TEXT NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS daily_statistics (
                        date TEXT PRIMARY KEY,
                        monitoring_groups_hash TEXT NOT NULL,
                        total_messages INTEGER NOT NULL DEFAULT 0,
                        total_users INTEGER NOT NULL DEFAULT 0,
                        total_chats INTEGER NOT NULL DEFAULT 0,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE TABLE IF NOT EXISTS daily_chat_stats (
                        date TEXT NOT NULL,
                        monitoring_groups_hash TEXT NOT NULL,
                        chat_id INTEGER NOT NULL,
                        chat_title TEXT NOT NULL,
                        messages INTEGER NOT NULL DEFAULT 0,
                        percentage REAL NOT NULL DEFAULT 0,
                        PRIMARY KEY (date, monitoring_groups_hash, chat_id)
                    );
                    CREATE TABLE IF NOT EXISTS daily_user_stats (
                        date TEXT NOT NULL,
                        monitoring_groups_hash TEXT NOT NULL,
                        user_id INTEGER NOT NULL,
                        user_name TEXT NOT NULL,
                        messages INTEGER NOT NULL DEFAULT 0,
                        percentage REAL NOT NULL DEFAULT 0,
                        PRIMARY KEY (date, monitoring_groups_hash, user_id)
                    );
                    CREATE TABLE IF NOT EXISTS user_cache (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        is_bot BOOLEAN NOT NULL DEFAULT 0,
                        last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE TABLE IF NOT EXISTS chat_cache (
                        chat_id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        type TEXT NOT NULL,
                        member_count INTEGER,
                        last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                    INSERT OR REPLACE INTO schema_migrations (version, description) VALUES (1, 'Initial schema');
                """
            }
        ]
        
        # Find pending migrations
        pending = [m for m in migrations if m["version"] > current_version]
        
        if not pending:
            print("✅ Database schema is up to date")
            return 0
        
        print(f"Found {len(pending)} pending migrations:")
        for migration in pending:
            print(f"  • Version {migration['version']}: {migration['description']}")
        
        if args.dry_run:
            print("\nDry run completed. Use without --dry-run to apply migrations")
            return 0
        
        # Apply migrations
        print("\nApplying migrations...")
        with db.get_connection() as conn:
            for migration in pending:
                print(f"  • Applying version {migration['version']}...")
                conn.executescript(migration["sql"])
                conn.commit()
        
        print("✅ All migrations applied successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return 1


# Removed validate-db and migrate-schema handlers - not needed 