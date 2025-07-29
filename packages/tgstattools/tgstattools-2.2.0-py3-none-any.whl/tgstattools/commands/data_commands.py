"""
Data viewing commands: view-data with various period options.

These commands handle data visualization and analysis from the database.
"""

import argparse
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.data_viewer import DataViewer, DataViewError
    from ..core.template_processor import TemplateProcessor


def register_commands(subparsers: Any) -> None:
    """Register data viewing commands."""
    
    # View data command with subcommands for different periods
    view_parser = subparsers.add_parser(
        "view-data",
        help="View collected statistics",
        description="Display statistics for various time periods"
    )
    
    view_subparsers = view_parser.add_subparsers(
        dest="period",
        help="Time period for data viewing",
        metavar="<period>"
    )
    
    # Previous day
    prev_day_parser = view_subparsers.add_parser(
        "previous-day",
        help="View previous day statistics"
    )
    _add_common_view_args(prev_day_parser)
    
    # Specific date
    date_parser = view_subparsers.add_parser(
        "date",
        help="View statistics for specific date (YYYY-MM-DD)"
    )
    date_parser.add_argument(
        "date",
        help="Date in YYYY-MM-DD format"
    )
    _add_common_view_args(date_parser)
    
    # Period shortcuts
    for period in ["previous-week", "previous-month", "previous-quarter", 
                   "previous-semiannual", "previous-annual"]:
        period_parser = view_subparsers.add_parser(
            period,
            help=f"View {period.replace('-', ' ')} statistics"
        )
        _add_common_view_args(period_parser)


def _add_common_view_args(parser: argparse.ArgumentParser) -> None:
    """Add common arguments for view commands."""
    parser.add_argument(
        "template",
        nargs="?",
        default="sort_descending_excluding_zero_results",
        help="Display template (default: sort_descending_excluding_zero_results)"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    # Group filtering options (integrated from removed report-in-console)
    parser.add_argument(
        "--monitoring-group",
        default="all",
        help="Monitoring group filter (default: all)"
    )
    parser.add_argument(
        "--user-group",
        default="all", 
        help="User group filter (default: all)"
    )
    parser.add_argument(
        "--reporting-group",
        help="Reporting group (for filtering configuration)"
    )
    # NEW: Send report to chat groups
    parser.add_argument(
        "--send-to",
        help="Send report to specified reporting group instead of displaying in console"
    )


def handle_view_data(args: argparse.Namespace) -> int:
    """Handle data viewing command."""
    import asyncio
    from ..core.data_viewer import DataViewer, DataViewError
    from ..core.template_processor import TemplateProcessor
    from ..core.config_manager import ConfigManager
    
    print(f"📊 Viewing data for period: {args.period}")
    
    try:
        # Initialize components
        from ..core.config_manager import ConfigManager
        from ..core.template_processor import TemplateProcessor
        from ..core.data_viewer import DataViewer
        from ..core.database import Database
        
        config_manager = ConfigManager()
        database = Database()
        template_processor = TemplateProcessor(config_manager)
        data_viewer = DataViewer(database_manager=database, config_manager=config_manager)
        
        # Run async data viewing
        return asyncio.run(_view_data_async(args, data_viewer, template_processor, config_manager))
        
    except Exception as e:
        print(f"❌ Error viewing data: {e}")
        return 1


async def _view_data_async(args: argparse.Namespace, data_viewer: "DataViewer", template_processor: "TemplateProcessor", config_manager) -> int:
    """Handle data viewing asynchronously."""
    try:
        # Determine period range
        if args.period == "date":
            target_date = data_viewer.parse_date_string(args.date)
            period_range = data_viewer.calculate_custom_range(target_date, target_date)
        else:
            period_range = data_viewer.calculate_period_range(args.period)
        
        print(f"📅 Period: {period_range.description}")
        
        # Get template and format
        template_name = getattr(args, 'template', 'sort_descending_excluding_zero_results')
        output_format = getattr(args, 'format', 'text')
        
        print(f"🎨 Template: {template_name}")
        print(f"📄 Format: {output_format}")
        
        # Get filtering parameters
        monitoring_group = getattr(args, 'monitoring_group', 'all')
        user_group = getattr(args, 'user_group', 'all')
        reporting_group = getattr(args, 'reporting_group', None)
        send_to = getattr(args, 'send_to', None)
        
        print(f"🎯 Monitoring group: {monitoring_group}")
        print(f"👥 User group: {user_group}")
        if send_to:
            print(f"📤 Sending to: {send_to}")
        
        # Check if we need to send to chats instead of displaying
        if send_to:
            # Use same logic as report-in-chat-group for sending reports
            from ..core.config_manager import ConfigManager
            from ..core.database import Database
            from ..core.reporter.data_retriever import DataRetriever
            from ..core.reporter import Reporter
            from ..core.telegram import create_client
            
            config_manager = ConfigManager()
            db_path = config_manager.environment.get_database_path()
            database = Database(db_path)
            
            # Get API credentials
            api_id = config_manager.environment.get_env_value("TELEGRAM_API_ID")
            api_hash = config_manager.environment.get_env_value("TELEGRAM_API_HASH")
            
            if not api_id or not api_hash:
                print("❌ Telegram API credentials not found in environment")
                return 1
            
            telegram_client = create_client(api_id, api_hash, "tgstattools_session", "data/sessions")
            
            await telegram_client.connect()
            
            if not await telegram_client.is_authenticated():
                print("❌ Telegram client not authenticated")
                return 1
            
            # Get filtered statistics data using DataRetriever for multi-day periods
            data_retriever = DataRetriever(database, config_manager)
            
            # All periods now use single-day logic (since we removed range commands)
            stats_data = await data_retriever.get_filtered_statistics(
                target_date=period_range.start_date,
                monitoring_group=monitoring_group,
                user_group=user_group,
                reporting_group=reporting_group
            )
            
            # Generate and send report
            reporter = Reporter(config_manager, None, telegram_client)
            
            result = await reporter.generate_and_send_report(
                data=stats_data,
                template_name=template_name,
                reporting_group=send_to,
                output_format="text",
                user_group=user_group,
                monitoring_group=monitoring_group
            )
            
            if result.get("success", False):
                print(f"\n✅ Report sent successfully!")
                print(f"📊 Total messages: {stats_data.total_messages}")
                print(f"👥 Users: {len(stats_data.users)}")
                print(f"💬 Chats: {len(stats_data.chats)}")
                print(f"📤 Delivered to: {result.get('successful_deliveries', 0)}/{result.get('target_chats_count', 0)} chats")
                if result.get('failed_deliveries', 0) > 0:
                    print(f"⚠️ Failed deliveries: {result.get('failed_deliveries', 0)}")
                return 0
            else:
                print(f"\n❌ Report sending failed: {result.get('error', 'Unknown error')}")
                return 1
        else:
            # Display in console - use same filtering logic as send-to
            from ..core.reporter.data_retriever import DataRetriever
            from ..core.database import Database
            
            # Initialize database for data retriever
            db_path = config_manager.environment.get_database_path()
            retriever_database = Database(db_path)
            data_retriever = DataRetriever(retriever_database, config_manager)
            
            # All periods now use single-day logic with proper filtering
            stats_data = await data_retriever.get_filtered_statistics(
                target_date=period_range.start_date,
                monitoring_group=monitoring_group,
                user_group=user_group,
                reporting_group=reporting_group
            )
            
            # Format output
            if output_format == "json":
                formatted_output = template_processor.format_as_json(stats_data, template_name)
            else:
                formatted_output = template_processor.format_statistics(stats_data, template_name)
            
            print("\n" + "="*50)
            print(formatted_output)
            print("="*50)
            
            print(f"\n✅ Data viewing completed successfully")
            return 0
        
    except Exception as e:
        # Import DataViewError inside the function to avoid import issues
        from ..core.data_viewer import DataViewError
        if isinstance(e, DataViewError):
            print(f"❌ Data viewing error: {e}")
        else:
            print(f"❌ Unexpected error: {e}")
        return 1 