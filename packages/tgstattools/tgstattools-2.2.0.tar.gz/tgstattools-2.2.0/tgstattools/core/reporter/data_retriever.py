"""
Data retrieval and filtering for report generation (Refactored).

This module handles retrieving statistics data from the database
and applying user/monitoring group filters with proper separation of concerns.

REFACTORED: This module now uses modular architecture following SRP principles:
- DataFetcher: Database operations
- GroupFilter: Group-based filtering  
- DataConverter: Type conversions and formatting
- DataErrorHandler: Error management

Single Responsibility: Coordinating data retrieval operations using specialized services.
"""

import logging
import time
from typing import Optional
from ..template_processor.data_models import StatisticsData
from ..config_manager import ConfigManager
from ..user_utils import UserNameResolver
from .data import DataFetcher, GroupFilter, DataConverter, DataErrorHandler

logger = logging.getLogger(__name__)


class DataRetriever:
    """Handles data retrieval and filtering for reports using modular architecture."""
    
    def __init__(self, database, config_manager: Optional[ConfigManager] = None):
        """Initialize data retriever with modular components."""
        self.database = database
        self.config_manager = config_manager or ConfigManager()
        self.name_resolver = UserNameResolver(self.config_manager)
        
        # Initialize specialized components
        self.data_fetcher = DataFetcher(database)
        self.group_filter = GroupFilter(self.config_manager, self.data_fetcher)
        self.data_converter = DataConverter()
        self.error_handler = DataErrorHandler()
    
    async def get_filtered_statistics(self, target_date, monitoring_group: str = "all", 
                                    user_group: str = "all", reporting_group: str = None) -> StatisticsData:
        """
        Get statistics data with applied filters and timezone conversion.
        
        This method coordinates the entire data retrieval process using specialized services.
        """
        start_time = time.time()
        
        try:
            # Step 1: Fetch raw data from database
            raw_data = await self.data_fetcher.get_raw_statistics(target_date)
            
            if not raw_data:
                self.error_handler.log_operation_metrics(
                    "get_filtered_statistics", False, time.time() - start_time
                )
                return self.data_converter.create_empty_statistics(target_date, monitoring_group, reporting_group)
            
            # Step 2: Validate data integrity
            if not self.error_handler.validate_data_integrity(raw_data):
                return self.error_handler.handle_retrieval_error(
                    Exception("Data integrity validation failed"), 
                    target_date, monitoring_group, reporting_group
                )
            
            # Step 3: Apply group-based filtering
            try:
                filtered_data = self.group_filter.apply_filters(raw_data, monitoring_group, user_group)
            except Exception as e:
                filtered_data = self.error_handler.handle_filtering_error(e, raw_data, monitoring_group, user_group)
            
            # Step 4: Convert to final format with percentage recalculation
            try:
                result = self.data_converter.create_statistics_data(
                    filtered_data, target_date, monitoring_group, reporting_group
                )
            except Exception as e:
                return self.error_handler.handle_conversion_error(e, target_date, monitoring_group, reporting_group)
            
            # Log success metrics
            total_messages = result.total_messages
            execution_time = time.time() - start_time
            self.error_handler.log_operation_metrics(
                "get_filtered_statistics", True, execution_time, total_messages
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.error_handler.log_operation_metrics(
                "get_filtered_statistics", False, execution_time
            )
            return self.error_handler.handle_retrieval_error(e, target_date, monitoring_group, reporting_group) 