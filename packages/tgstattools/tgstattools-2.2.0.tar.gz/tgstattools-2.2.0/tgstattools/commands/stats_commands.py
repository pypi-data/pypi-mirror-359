"""
Statistics and analysis commands: show-stats.

These commands handle system statistics and performance analysis.
"""

import argparse
import json
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..core.database import Database
from ..core.config_manager import ConfigManager


def register_commands(subparsers: Any) -> None:
    """Register statistics and analysis commands."""
    
    # Show statistics command
    stats_parser = subparsers.add_parser(
        "show-stats",
        help="Show system statistics",
        description="Display database and collection statistics with optional detailed breakdown"
    )
    stats_parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed breakdown by users and chats"
    )
    stats_parser.add_argument(
        "--export",
        help="Export statistics to file (.json or .csv format determined by extension)"
    )
    stats_parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of recent days to analyze (default: 30)"
    )
    stats_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (text for console, json for machine reading)"
    )


def show_stats(args: argparse.Namespace) -> int:
    """Show statistics command entry point."""
    return handle_show_stats(args)


def handle_show_stats(args: argparse.Namespace) -> int:
    """Handle show statistics command."""
    try:
        print("📊 Collecting system statistics...")
        
        # Initialize components (skip ConfigManager for Phase 8 testing)
        database = Database()
        
        # Collect basic statistics
        basic_stats = _collect_basic_statistics(database)
        
        # Collect timeline statistics
        timeline_stats = _collect_timeline_statistics(database, args.days)
        
        # Collect detailed statistics if requested
        detailed_stats = None
        if args.detailed:
            detailed_stats = _collect_detailed_statistics(database, args.days)
        
        # Compile complete statistics
        complete_stats = {
            "generated_at": datetime.now().isoformat(),
            "analysis_period_days": args.days,
            "basic": basic_stats,
            "timeline": timeline_stats,
            "detailed": detailed_stats
        }
        
        # Handle export if requested
        if args.export:
            success = _export_statistics(complete_stats, args.export)
            if not success:
                return 1
        
        # Display statistics
        if args.format == "json":
            print(json.dumps(complete_stats, indent=2, ensure_ascii=False))
        else:
            _display_text_statistics(complete_stats, args.detailed)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error collecting statistics: {e}")
        return 1


def _collect_basic_statistics(database: Database) -> Dict[str, Any]:
    """Collect basic database and system statistics."""
    stats = {}
    
    try:
        with database.get_connection() as conn:
            cursor = conn.cursor()
            
            # Database file statistics
            db_path = database.db_path
            if os.path.exists(db_path):
                stat_info = os.stat(db_path)
                stats["database"] = {
                    "file_size_mb": round(stat_info.st_size / (1024 * 1024), 2),
                    "last_modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    "path": str(db_path)
                }
            
            # Collection statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_collections,
                    COUNT(CASE WHEN collection_status = 'completed' THEN 1 END) as completed_collections,
                    COUNT(CASE WHEN collection_status = 'in_progress' THEN 1 END) as in_progress_collections,
                    COUNT(CASE WHEN collection_status = 'failed' THEN 1 END) as failed_collections,
                    MIN(date) as earliest_date,
                    MAX(date) as latest_date,
                    SUM(total_messages) as total_messages_collected,
                    AVG(total_messages) as avg_messages_per_day
                FROM daily_statistics
            """)
            collection_data = cursor.fetchone()
            
            stats["collections"] = {
                "total_collection_records": collection_data[0] or 0,
                "completed": collection_data[1] or 0,
                "in_progress": collection_data[2] or 0,
                "failed": collection_data[3] or 0,
                "earliest_date": collection_data[4],
                "latest_date": collection_data[5],
                "total_messages": collection_data[6] or 0,
                "avg_messages_per_day": round(collection_data[7] or 0, 1)
            }
            
            # User statistics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT user_id) as unique_users,
                    SUM(messages) as total_user_messages,
                    AVG(messages) as avg_messages_per_user,
                    MAX(messages) as max_messages_by_user
                FROM daily_user_stats
            """)
            user_data = cursor.fetchone()
            
            stats["users"] = {
                "unique_users": user_data[0] or 0,
                "total_messages": user_data[1] or 0,
                "avg_messages_per_user": round(user_data[2] or 0, 1),
                "max_messages_by_user": user_data[3] or 0
            }
            
            # Chat statistics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT chat_id) as unique_chats,
                    SUM(messages) as total_chat_messages,
                    AVG(messages) as avg_messages_per_chat,
                    MAX(messages) as max_messages_by_chat
                FROM daily_chat_stats
            """)
            chat_data = cursor.fetchone()
            
            stats["chats"] = {
                "unique_chats": chat_data[0] or 0,
                "total_messages": chat_data[1] or 0,
                "avg_messages_per_chat": round(chat_data[2] or 0, 1),
                "max_messages_by_chat": chat_data[3] or 0
            }
            
            # Cache statistics
            cursor.execute("SELECT COUNT(*) FROM user_cache")
            user_cache_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM chat_cache")
            chat_cache_count = cursor.fetchone()[0]
            
            stats["cache"] = {
                "users_cached": user_cache_count,
                "chats_cached": chat_cache_count
            }
            
    except Exception as e:
        stats["error"] = f"Failed to collect basic statistics: {e}"
    
    return stats


def _collect_timeline_statistics(database: Database, days: int) -> Dict[str, Any]:
    """Collect timeline-based statistics for recent days."""
    stats = {}
    
    try:
        with database.get_connection() as conn:
            cursor = conn.cursor()
            
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            # Daily message counts for timeline
            cursor.execute("""
                SELECT 
                    date,
                    SUM(total_messages) as daily_total,
                    COUNT(*) as collections_count
                FROM daily_statistics
                WHERE date BETWEEN ? AND ?
                AND collection_status = 'completed'
                GROUP BY date
                ORDER BY date DESC
                LIMIT ?
            """, (start_date.isoformat(), end_date.isoformat(), days))
            
            daily_data = cursor.fetchall()
            
            stats["period"] = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days_requested": days,
                "days_with_data": len(daily_data)
            }
            
            if daily_data:
                total_messages = sum(row[1] for row in daily_data)
                stats["summary"] = {
                    "total_messages_in_period": total_messages,
                    "avg_messages_per_day": round(total_messages / len(daily_data), 1),
                    "busiest_day": {
                        "date": max(daily_data, key=lambda x: x[1])[0],
                        "messages": max(daily_data, key=lambda x: x[1])[1]
                    },
                    "quietest_day": {
                        "date": min(daily_data, key=lambda x: x[1])[0],
                        "messages": min(daily_data, key=lambda x: x[1])[1]
                    }
                }
                
                stats["daily_breakdown"] = [
                    {
                        "date": row[0],
                        "messages": row[1],
                        "collections": row[2]
                    }
                    for row in daily_data
                ]
            else:
                stats["summary"] = {
                    "total_messages_in_period": 0,
                    "avg_messages_per_day": 0,
                    "note": "No completed collections found in specified period"
                }
                stats["daily_breakdown"] = []
            
    except Exception as e:
        stats["error"] = f"Failed to collect timeline statistics: {e}"
    
    return stats


def _collect_detailed_statistics(database: Database, days: int) -> Dict[str, Any]:
    """Collect detailed statistics by users and chats."""
    stats = {}
    
    try:
        with database.get_connection() as conn:
            cursor = conn.cursor()
            
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            # Top users by message count
            cursor.execute("""
                SELECT 
                    user_name,
                    SUM(messages) as total_messages,
                    COUNT(DISTINCT date) as active_days,
                    AVG(messages) as avg_daily_messages,
                    MAX(messages) as max_daily_messages
                FROM daily_user_stats
                WHERE date BETWEEN ? AND ?
                GROUP BY user_id, user_name
                ORDER BY total_messages DESC
                LIMIT 20
            """, (start_date.isoformat(), end_date.isoformat()))
            
            top_users = [
                {
                    "name": row[0],
                    "total_messages": row[1],
                    "active_days": row[2],
                    "avg_daily_messages": round(row[3], 1),
                    "max_daily_messages": row[4]
                }
                for row in cursor.fetchall()
            ]
            
            # Top chats by message count
            cursor.execute("""
                SELECT 
                    chat_title,
                    SUM(messages) as total_messages,
                    COUNT(DISTINCT date) as active_days,
                    AVG(messages) as avg_daily_messages,
                    MAX(messages) as max_daily_messages
                FROM daily_chat_stats
                WHERE date BETWEEN ? AND ?
                GROUP BY chat_id, chat_title
                ORDER BY total_messages DESC
                LIMIT 20
            """, (start_date.isoformat(), end_date.isoformat()))
            
            top_chats = [
                {
                    "title": row[0],
                    "total_messages": row[1],
                    "active_days": row[2],
                    "avg_daily_messages": round(row[3], 1),
                    "max_daily_messages": row[4]
                }
                for row in cursor.fetchall()
            ]
            
            stats["top_users"] = top_users
            stats["top_chats"] = top_chats
            
    except Exception as e:
        stats["error"] = f"Failed to collect detailed statistics: {e}"
    
    return stats


def _export_statistics(stats: Dict[str, Any], export_path: str) -> bool:
    """Export statistics to file."""
    try:
        path = Path(export_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if path.suffix.lower() == '.json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            print(f"✓ Statistics exported to JSON: {path}")
            
        elif path.suffix.lower() == '.csv':
            _export_to_csv(stats, path)
            print(f"✓ Statistics exported to CSV: {path}")
            
        else:
            print(f"❌ Unsupported export format. Use .json or .csv extension")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False


def _export_to_csv(stats: Dict[str, Any], path: Path) -> None:
    """Export statistics to CSV format."""
    with open(path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['Category', 'Metric', 'Value'])
        
        # Write basic statistics
        if 'basic' in stats:
            basic = stats['basic']
            
            if 'collections' in basic:
                for key, value in basic['collections'].items():
                    writer.writerow(['Collections', key, value])
            
            if 'users' in basic:
                for key, value in basic['users'].items():
                    writer.writerow(['Users', key, value])
            
            if 'chats' in basic:
                for key, value in basic['chats'].items():
                    writer.writerow(['Chats', key, value])
        
        # Write timeline summary
        if 'timeline' in stats and 'summary' in stats['timeline']:
            for key, value in stats['timeline']['summary'].items():
                if isinstance(value, dict):
                    writer.writerow(['Timeline', key, str(value)])
                else:
                    writer.writerow(['Timeline', key, value])


def _display_text_statistics(stats: Dict[str, Any], detailed: bool = False) -> None:
    """Display statistics in human-readable text format."""
    print("\n" + "="*60)
    print("📊 TGSTATTOOLS SYSTEM STATISTICS")
    print("="*60)
    
    # Generated timestamp
    if 'generated_at' in stats:
        print(f"Generated: {stats['generated_at']}")
        print(f"Analysis Period: {stats.get('analysis_period_days', 'N/A')} days")
    print()
    
    # Basic statistics
    if 'basic' in stats:
        basic = stats['basic']
        
        print("📂 DATABASE INFORMATION")
        print("-" * 30)
        if 'database' in basic:
            db = basic['database']
            print(f"  File Size: {db.get('file_size_mb', 'N/A')} MB")
            print(f"  Last Modified: {db.get('last_modified', 'N/A')}")
            print(f"  Path: {db.get('path', 'N/A')}")
        print()
        
        print("📊 COLLECTION SUMMARY")
        print("-" * 30)
        if 'collections' in basic:
            coll = basic['collections']
            print(f"  Total Collections: {coll.get('total_collection_records', 0)}")
            print(f"  ✅ Completed: {coll.get('completed', 0)}")
            print(f"  🔄 In Progress: {coll.get('in_progress', 0)}")
            print(f"  ❌ Failed: {coll.get('failed', 0)}")
            print(f"  Date Range: {coll.get('earliest_date', 'N/A')} to {coll.get('latest_date', 'N/A')}")
            print(f"  Total Messages: {coll.get('total_messages', 0):,}")
            print(f"  Avg Messages/Day: {coll.get('avg_messages_per_day', 0)}")
        print()
        
        print("👥 USER STATISTICS")
        print("-" * 30)
        if 'users' in basic:
            users = basic['users']
            print(f"  Unique Users: {users.get('unique_users', 0)}")
            print(f"  Total Messages: {users.get('total_messages', 0):,}")
            print(f"  Avg Messages/User: {users.get('avg_messages_per_user', 0)}")
            print(f"  Most Active User: {users.get('max_messages_by_user', 0)} messages")
        print()
        
        print("💬 CHAT STATISTICS")
        print("-" * 30)
        if 'chats' in basic:
            chats = basic['chats']
            print(f"  Unique Chats: {chats.get('unique_chats', 0)}")
            print(f"  Total Messages: {chats.get('total_messages', 0):,}")
            print(f"  Avg Messages/Chat: {chats.get('avg_messages_per_chat', 0)}")
            print(f"  Most Active Chat: {chats.get('max_messages_by_chat', 0)} messages")
        print()
    
    # Timeline statistics
    if 'timeline' in stats:
        timeline = stats['timeline']
        
        print("📅 RECENT ACTIVITY")
        print("-" * 30)
        if 'period' in timeline:
            period = timeline['period']
            print(f"  Period: {period.get('start_date')} to {period.get('end_date')}")
            print(f"  Days with Data: {period.get('days_with_data', 0)}/{period.get('days_requested', 0)}")
        
        if 'summary' in timeline:
            summary = timeline['summary']
            print(f"  Total Messages: {summary.get('total_messages_in_period', 0):,}")
            print(f"  Daily Average: {summary.get('avg_messages_per_day', 0)}")
            
            if 'busiest_day' in summary:
                busiest = summary['busiest_day']
                print(f"  Busiest Day: {busiest.get('date')} ({busiest.get('messages', 0):,} messages)")
            
            if 'quietest_day' in summary:
                quietest = summary['quietest_day']
                print(f"  Quietest Day: {quietest.get('date')} ({quietest.get('messages', 0):,} messages)")
        print()
    
    # Detailed statistics
    if detailed and 'detailed' in stats:
        detailed_stats = stats['detailed']
        
        if 'top_users' in detailed_stats and detailed_stats['top_users']:
            print("🏆 TOP USERS (Recent Period)")
            print("-" * 40)
            for i, user in enumerate(detailed_stats['top_users'][:10], 1):
                print(f"  {i:2d}. {user['name']}: {user['total_messages']:,} messages "
                      f"({user['active_days']} days, avg: {user['avg_daily_messages']})")
            print()
        
        if 'top_chats' in detailed_stats and detailed_stats['top_chats']:
            print("🏆 TOP CHATS (Recent Period)")
            print("-" * 40)
            for i, chat in enumerate(detailed_stats['top_chats'][:10], 1):
                print(f"  {i:2d}. {chat['title']}: {chat['total_messages']:,} messages "
                      f"({chat['active_days']} days, avg: {chat['avg_daily_messages']})")
            print()
    
    print("="*60)