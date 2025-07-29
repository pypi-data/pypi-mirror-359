"""
Report generation and template validation for TgStatTools.

This module handles generating formatted reports from statistics data
and validating template configurations.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from ..template_processor import TemplateProcessor, StatisticsData

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Handles report generation and template validation."""
    
    def __init__(self, template_processor: TemplateProcessor):
        """Initialize report generator."""
        self.template_processor = template_processor
        
    def generate_report(self, data: StatisticsData, template_name: str, output_format: str = "text", 
                       user_group: str = None, monitoring_group: str = None) -> str:
        """Generate formatted report from statistics data."""
        logger.debug(f"Generating report for {data.date} using template '{template_name}' in {output_format} format")
        
        try:
            if output_format == "json":
                return self.template_processor.format_as_json(data, template_name)
            else:
                return self.template_processor.format_statistics(data, template_name, user_group, monitoring_group)
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise
    
    def generate_report_preview(self, data: StatisticsData, template_name: str, output_format: str = "text",
                               user_group: str = None, monitoring_group: str = None) -> str:
        """Generate report preview without sending."""
        logger.debug(f"Generating report preview for {data.date} using template '{template_name}'")
        
        try:
            if output_format == "json":
                return self.template_processor.format_as_json(data, template_name)
            else:
                return self.template_processor.format_statistics(data, template_name, user_group, monitoring_group)
        except Exception as e:
            logger.error(f"Failed to generate report preview: {e}")
            raise
    
    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """Validate template configuration."""
        try:
            template = self.template_processor.load_template(template_name)
            return {
                "valid": True,
                "template_name": template_name,
                "sections": list(template.keys())
            }
        except Exception as e:
            return {
                "valid": False,
                "template_name": template_name,
                "error": str(e)
            }
    
    def generate_test_message(self, message: str = None) -> str:
        """Generate test message for delivery testing."""
        return message or f"🧪 TgStatTools test message - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" 