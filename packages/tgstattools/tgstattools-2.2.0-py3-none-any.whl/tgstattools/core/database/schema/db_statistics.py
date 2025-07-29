"""
Database statistics utilities.

This module handles collecting and analyzing database statistics and metrics.
Single Responsibility: Gathering database statistics and metrics.
"""

import logging
from typing import Dict, Any, List
from ..connection import DatabaseConnection

logger = logging.getLogger(__name__)


class DbStatistics:
    """Handles database statistics and metrics collection."""
    
    def __init__(self, connection: DatabaseConnection):
        """
        Initialize database statistics collector.
        
        Args:
            connection: Database connection instance
        """
        self.connection = connection
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get comprehensive database statistics summary."""
        summary = {
            "database_info": {},
            "table_stats": {},
            "recent_activity": {},
            "performance_metrics": {}
        }
        
        try:
            summary["database_info"] = self._get_database_info()
            summary["table_stats"] = self._get_table_statistics()
            summary["recent_activity"] = self._get_recent_activity()
            summary["performance_metrics"] = self._get_performance_metrics()
            
        except Exception as e:
            logger.error(f"Error collecting database statistics: {e}")
            summary["error"] = str(e)
        
        return summary
    
    def _get_database_info(self) -> Dict[str, Any]:
        """Get basic database information."""
        info = {}
        
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Database size
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                info["size_bytes"] = page_count * page_size
                info["size_mb"] = round(info["size_bytes"] / (1024 * 1024), 2)
                
                # Schema version
                try:
                    cursor.execute("SELECT MAX(version) FROM schema_migrations")
                    result = cursor.fetchone()
                    info["schema_version"] = result[0] if result and result[0] else 0
                except:
                    info["schema_version"] = 0
                
                # Table count
                cursor.execute("""
                    SELECT COUNT(*) FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                info["table_count"] = cursor.fetchone()[0]
                
                # Index count
                cursor.execute("""
                    SELECT COUNT(*) FROM sqlite_master 
                    WHERE type='index' AND name NOT LIKE 'sqlite_%'
                """)
                info["index_count"] = cursor.fetchone()[0]
                
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            info["error"] = str(e)
        
        return info
    
    def _get_table_statistics(self) -> Dict[str, Any]:
        """Get statistics for each table."""
        table_stats = {}
        
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    try:
                        stats = {}
                        
                        # Row count
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        stats["row_count"] = cursor.fetchone()[0]
                        
                        # Table size estimation
                        cursor.execute(f"PRAGMA table_info({table})")
                        column_count = len(cursor.fetchall())
                        stats["column_count"] = column_count
                        
                        # Estimate size (rough calculation)
                        if stats["row_count"] > 0:
                            estimated_row_size = column_count * 50  # Rough estimate
                            stats["estimated_size_bytes"] = stats["row_count"] * estimated_row_size
                        else:
                            stats["estimated_size_bytes"] = 0
                        
                        table_stats[table] = stats
                        
                    except Exception as e:
                        table_stats[table] = {"error": str(e)}
                        
        except Exception as e:
            logger.error(f"Error getting table statistics: {e}")
            table_stats["error"] = str(e)
        
        return table_stats
    
    def _get_recent_activity(self) -> Dict[str, Any]:
        """Get recent database activity statistics."""
        activity = {}
        
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Recent statistics collections
                try:
                    cursor.execute("""
                        SELECT COUNT(*), MAX(collection_completed_at), MIN(collection_completed_at)
                        FROM daily_statistics 
                        WHERE collection_completed_at IS NOT NULL
                        AND collection_completed_at >= datetime('now', '-30 days')
                    """)
                    result = cursor.fetchone()
                    if result and result[0]:
                        activity["collections_last_30_days"] = result[0]
                        activity["latest_collection"] = result[1]
                        activity["earliest_recent_collection"] = result[2]
                    else:
                        activity["collections_last_30_days"] = 0
                except:
                    activity["collections_last_30_days"] = 0
                
                # Total messages processed
                try:
                    cursor.execute("""
                        SELECT SUM(total_messages), AVG(total_messages)
                        FROM daily_statistics 
                        WHERE collection_status = 'completed'
                    """)
                    result = cursor.fetchone()
                    if result and result[0]:
                        activity["total_messages_processed"] = result[0]
                        activity["average_messages_per_day"] = round(result[1], 2)
                    else:
                        activity["total_messages_processed"] = 0
                        activity["average_messages_per_day"] = 0
                except:
                    activity["total_messages_processed"] = 0
                    activity["average_messages_per_day"] = 0
                
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            activity["error"] = str(e)
        
        return activity
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics."""
        metrics = {}
        
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Cache hit ratio (if available)
                try:
                    cursor.execute("PRAGMA cache_size")
                    metrics["cache_size"] = cursor.fetchone()[0]
                except:
                    metrics["cache_size"] = "unknown"
                
                # Journal mode
                try:
                    cursor.execute("PRAGMA journal_mode")
                    metrics["journal_mode"] = cursor.fetchone()[0]
                except:
                    metrics["journal_mode"] = "unknown"
                
                # Synchronous mode
                try:
                    cursor.execute("PRAGMA synchronous")
                    sync_mode = cursor.fetchone()[0]
                    sync_modes = {0: "OFF", 1: "NORMAL", 2: "FULL", 3: "EXTRA"}
                    metrics["synchronous_mode"] = sync_modes.get(sync_mode, str(sync_mode))
                except:
                    metrics["synchronous_mode"] = "unknown"
                
                # Auto vacuum
                try:
                    cursor.execute("PRAGMA auto_vacuum")
                    auto_vacuum = cursor.fetchone()[0]
                    vacuum_modes = {0: "NONE", 1: "FULL", 2: "INCREMENTAL"}
                    metrics["auto_vacuum"] = vacuum_modes.get(auto_vacuum, str(auto_vacuum))
                except:
                    metrics["auto_vacuum"] = "unknown"
                
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            metrics["error"] = str(e)
        
        return metrics
    
    def get_table_row_count(self, table_name: str) -> int:
        """Get row count for a specific table."""
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting row count for {table_name}: {e}")
            return 0
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get detailed disk usage information."""
        usage = {}
        
        try:
            with self.connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Overall database size
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                usage["total_size_bytes"] = page_count * page_size
                
                # Free pages
                cursor.execute("PRAGMA freelist_count")
                free_pages = cursor.fetchone()[0]
                usage["free_size_bytes"] = free_pages * page_size
                usage["used_size_bytes"] = usage["total_size_bytes"] - usage["free_size_bytes"]
                
                # Usage percentage
                if usage["total_size_bytes"] > 0:
                    usage["usage_percentage"] = round(
                        (usage["used_size_bytes"] / usage["total_size_bytes"]) * 100, 2
                    )
                else:
                    usage["usage_percentage"] = 0
                
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            usage["error"] = str(e)
        
        return usage 