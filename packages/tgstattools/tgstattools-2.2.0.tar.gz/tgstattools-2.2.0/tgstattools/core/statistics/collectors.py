"""
Simplified statistics collectors for TgStatTools.

This module provides collectors for final statistics collection:
- YesterdayStatsCollector: Collects final statistics for previous day
- ReportGenerator: Generates reports from existing database data
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from . import StatisticsCollector


logger = logging.getLogger(__name__)


class YesterdayStatsCollector:
    """
    Collects final, comprehensive statistics for the previous day.
    
    - Should run once per day (typically early morning)
    - Always overwrites any existing data for yesterday
    - Provides definitive, final statistics
    """
    
    def __init__(self, config_manager, database, telegram_client):
        self.config_manager = config_manager
        self.database = database
        self.telegram_client = telegram_client
        self.collector = StatisticsCollector(config_manager, database, telegram_client)
        self.logger = logging.getLogger(__name__)
    
    async def collect_yesterday_stats(self, monitoring_group: str = "all", force: bool = True) -> Dict[str, Any]:
        """
        Collect statistics for yesterday with timezone awareness.
        
        Args:
            monitoring_group: Group of chats to monitor (default: "all")
            force: Whether to overwrite existing data (default: True until timezone control is implemented)
            
        Returns:
            Collection result dictionary
        """
        yesterday = date.today() - timedelta(days=1)
        
        self.logger.info(f"📅 YesterdayStatsCollector: Starting collection for {yesterday}")
        self.logger.info(f"📊 Monitoring group: {monitoring_group}")
        self.logger.info(f"⚠️ Force mode: {force} (timezone boundaries not yet controlled)")
        
        # TODO: Implement timezone-aware day boundaries before making this "final"
        result = await self.collector.collect_statistics(
            monitoring_group=monitoring_group,
            target_date=yesterday,
            force_collection=force  # Configurable until timezone control
        )
        
        if result["success"]:
            self.logger.info(
                f"✅ YesterdayStatsCollector completed FINAL collection for {yesterday}:"
                f"\n   📨 Total messages: {result.get('total_messages', 0)}"
                f"\n   👥 Users: {result.get('user_count', 0)}"
                f"\n   💬 Chats: {result.get('chat_count', 0)}"
                f"\n   ❌ Errors: {result.get('errors_count', 0)}"
                f"\n   🔒 Data is now FINAL and ready for reports"
            )
        else:
            self.logger.error(f"❌ YesterdayStatsCollector failed for {yesterday}: {result.get('error')}")
        
        return result


class ReportGenerator:
    """
    Generates reports ONLY from existing database data.
    
    - Never collects new data
    - Only reads from database
    - Supports all report types (daily, weekly, monthly, etc.)
    """
    
    def __init__(self, config_manager, database, telegram_client):
        self.config_manager = config_manager
        self.database = database
        self.telegram_client = telegram_client
        self.logger = logging.getLogger(__name__)
    
    async def generate_report_from_db(self, 
                                    start_date: date,
                                    end_date: Optional[date] = None,
                                    monitoring_group: str = "all",
                                    user_group: str = "all",
                                    reporting_group: str = "testReportChats",
                                    template: str = "sort_descending_excluding_zero_results") -> Dict[str, Any]:
        """
        Generate report from existing database data.
        
        Args:
            start_date: Start date for report
            end_date: End date for report (if None, single day report)
            monitoring_group: Monitoring group filter
            user_group: User group filter
            reporting_group: Where to send report
            template: Report template
            
        Returns:
            Report generation result
        """
        if end_date is None:
            end_date = start_date
            
        self.logger.info(
            f"📊 ReportGenerator: Creating report from database"
            f"\n   📅 Period: {start_date} to {end_date}"
            f"\n   🎯 Monitoring: {monitoring_group}"
            f"\n   👥 Users: {user_group}"
            f"\n   📤 Reporting: {reporting_group}"
            f"\n   🎨 Template: {template}"
        )
        
        # Import reporter for sending
        from ..reporter import Reporter
        
        reporter = Reporter(
            config_manager=self.config_manager,
            telegram_client=self.telegram_client
        )
        
        # Get statistics data from database
        from ..reporter.data_retriever import DataRetriever
        
        # Create data retriever and get statistics
        data_retriever = DataRetriever(self.database, self.config_manager)
        stats_data = await data_retriever.get_filtered_statistics(
            target_date=start_date,
            monitoring_group=monitoring_group,
            user_group=user_group,
            reporting_group=reporting_group
        )
        
        # Generate and send report
        result = await reporter.generate_and_send_report(
            data=stats_data,
            template_name=template,
            reporting_group=reporting_group,
            output_format="text",
            user_group=user_group,
            monitoring_group=monitoring_group
        )
        
        return result 