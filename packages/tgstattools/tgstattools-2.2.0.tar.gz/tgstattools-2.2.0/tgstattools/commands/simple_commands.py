"""
Simplified CLI commands for statistics collection.

This module provides only essential commands:
- collect-previous-day: Collect final statistics for previous day  
- report-in-console: Generate reports in console from existing database data
- report-in-chat-group: Send reports to Telegram chat groups
"""

import argparse
import asyncio
from datetime import datetime, date, timedelta
from typing import Any

from ..core.database import Database
from ..core.config_manager import ConfigManager
from ..core.statistics.collectors import YesterdayStatsCollector, ReportGenerator


def register_simple_commands(subparsers: Any) -> None:
    """Register simplified statistics collection commands."""
    
    # Yesterday collection command
    yesterday_parser = subparsers.add_parser(
        "collect-previous-day", 
        help="Collect final statistics for previous day",
        description="Collect final, definitive statistics for previous day"
    )
    yesterday_parser.add_argument(
        "--monitoring-group",
        default="all",
        help="Monitoring group to collect from (default: all)"
    )
    yesterday_parser.add_argument(
        "--force",
        action="store_true",
        default=True,
        help="Force collection even if data exists (default: True until timezone control)"
    )

    
    # report-in-console and report-in-chat-group commands removed 
    # Use view-data with --send-to parameter instead



def handle_collect_previous_day(args: argparse.Namespace) -> int:
    """Handle collect-previous-day command.""" 
    return asyncio.run(_handle_collect_previous_day_async(args))


async def _handle_collect_previous_day_async(args: argparse.Namespace) -> int:
    """Handle collect-previous-day command asynchronously."""
    try:
        print("📅 Starting PREVIOUS DAY statistics collection...")
        print(f"📊 Monitoring group: {args.monitoring_group}")
        print("🔒 This will create FINAL data for yesterday")
        
        # Initialize components
        config_manager = ConfigManager()
        db_path = config_manager.environment.get_database_path()
        database = Database(db_path)
        
        # Get API credentials
        api_id = config_manager.environment.get_env_value("TELEGRAM_API_ID")
        api_hash = config_manager.environment.get_env_value("TELEGRAM_API_HASH")
        
        if not api_id or not api_hash:
            print("❌ Telegram API credentials not found in environment")
            return 1
        
        from ..core.telegram import create_client
        telegram_client = create_client(api_id, api_hash, "tgstattools_session", "data/sessions")
        
        await telegram_client.connect()
        
        if not await telegram_client.is_authenticated():
            print("❌ Telegram client not authenticated")
            print("Please run 'python -m tgstattools generate-session' first")
            return 1
        
        # Create collector
        collector = YesterdayStatsCollector(config_manager, database, telegram_client)
        
        # Collect yesterday's statistics
        result = await collector.collect_yesterday_stats(
            monitoring_group=args.monitoring_group,
            force=getattr(args, 'force', True)
        )
        
        if result["success"]:
            yesterday = date.today() - timedelta(days=1)
            print(f"\n✅ PREVIOUS DAY collection completed successfully for {yesterday}!")
            print(f"📨 Total messages: {result.get('total_messages', 0)}")
            print(f"👥 Users: {result.get('user_count', 0)}")
            print(f"💬 Chats: {result.get('chat_count', 0)}")
            print(f"❌ Errors: {result.get('errors_count', 0)}")
            print("🔒 Data is now FINAL and ready for reports")
            return 0
        else:
            print(f"\n❌ PREVIOUS DAY collection failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Error during PREVIOUS DAY collection: {e}")
        return 1


# Removed deprecated report functions - use view-data with --send-to instead


 