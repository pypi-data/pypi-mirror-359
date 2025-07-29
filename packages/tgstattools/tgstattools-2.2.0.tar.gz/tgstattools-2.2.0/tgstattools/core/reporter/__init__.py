"""
Report generation and delivery system for TgStatTools.

This module provides a unified interface for report generation and delivery,
delegating to specialized components for different responsibilities.
"""

import logging
from typing import Dict, Any, Optional
from ..config_manager import ConfigManager
from ..template_processor import TemplateProcessor, StatisticsData
from ..telegram_client import TelegramClient
from .group_resolver import GroupResolver, ReportDeliveryError
from .delivery_manager import DeliveryManager  
from .report_generator import ReportGenerator

logger = logging.getLogger(__name__)

# Export main classes and exceptions
__all__ = [
    'Reporter', 'ReportDeliveryError',
    'GroupResolver', 'DeliveryManager', 'ReportGenerator'
]


class Reporter:
    """Unified interface for report generation and delivery."""
    
    def __init__(self, 
                 config_manager: Optional[ConfigManager] = None,
                 template_processor: Optional[TemplateProcessor] = None,
                 telegram_client: Optional[TelegramClient] = None):
        """Initialize reporter with specialized components."""
        self.config_manager = config_manager or ConfigManager()
        self.template_processor = template_processor or TemplateProcessor(self.config_manager)
        self.telegram_client = telegram_client
        
        # Initialize specialized components
        self.group_resolver = GroupResolver(self.config_manager)
        self.delivery_manager = DeliveryManager(self.template_processor, self.telegram_client)
        self.report_generator = ReportGenerator(self.template_processor)
        
    async def generate_and_send_report(self, 
                                     data: StatisticsData,
                                     template_name: str,
                                     reporting_group: str,
                                     output_format: str = "text",
                                     user_group: str = None,
                                     monitoring_group: str = None) -> Dict[str, Any]:
        """Generate and send report to specified reporting group."""
        logger.info(f"Generating report for {data.date} using template '{template_name}'")
        
        try:
            # Generate formatted report
            formatted_report = self.report_generator.generate_report(data, template_name, output_format, user_group, monitoring_group)
            
            # Get target chats for delivery
            target_chats = await self.group_resolver.resolve_reporting_group(reporting_group)
            
            # Send report to all target chats
            delivery_results = await self.delivery_manager.deliver_report(formatted_report, target_chats)
            
            # Compile results
            result = {
                "success": True,
                "report_length": len(formatted_report),
                "target_chats_count": len(target_chats),
                "successful_deliveries": sum(1 for r in delivery_results.values() if r["success"]),
                "failed_deliveries": sum(1 for r in delivery_results.values() if not r["success"]),
                "delivery_details": delivery_results,
                "template_used": template_name,
                "format": output_format
            }
            
            if result["failed_deliveries"] > 0:
                logger.warning(f"Report delivery partially failed: {result['failed_deliveries']}/{len(target_chats)} failed")
            else:
                logger.info(f"Report delivered successfully to {len(target_chats)} chats")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate and send report: {e}")
            return {
                "success": False,
                "error": str(e),
                "template_used": template_name,
                "format": output_format
            }
    
    def generate_report_preview(self, data: StatisticsData, template_name: str, output_format: str = "text",
                               user_group: str = None, monitoring_group: str = None) -> str:
        """Generate report preview without sending."""
        return self.report_generator.generate_report_preview(data, template_name, output_format, user_group, monitoring_group)
    
    async def test_delivery_connectivity(self, reporting_group: str) -> Dict[str, Any]:
        """Test connectivity to all chats in reporting group."""
        logger.info(f"Testing delivery connectivity for reporting group: {reporting_group}")
        
        try:
            target_chats = await self.group_resolver.resolve_reporting_group(reporting_group)
            return await self.delivery_manager.test_delivery_connectivity(target_chats)
            
        except Exception as e:
            logger.error(f"Failed to test delivery connectivity: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """Validate template configuration."""
        return self.report_generator.validate_template(template_name)
    
    async def send_test_message(self, chat_id: int, message: str = None) -> Dict[str, Any]:
        """Send test message to specific chat."""
        test_message = self.report_generator.generate_test_message(message)
        return await self.delivery_manager.send_test_message(chat_id, test_message) 