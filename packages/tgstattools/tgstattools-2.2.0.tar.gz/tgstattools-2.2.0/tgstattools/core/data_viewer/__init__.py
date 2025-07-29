"""
Data viewing and analysis system for TgStatTools.

This module handles querying statistics from the database and preparing
data for display through templates and reports.

The data viewer is now modularized for better maintainability:
- period_manager: Period calculations and date range operations
- data_query_engine: Database queries and data retrieval
- data_processor: Data filtering, transformation and formatting
"""

import logging
from typing import List, Dict, Any, Optional

from .period_manager import PeriodManager, PeriodRange, DataViewError
from .data_query_engine import DataQueryEngine
from .data_processor import DataProcessor
from ..template_processor import StatisticsData
from ..config_manager import ConfigManager

logger = logging.getLogger(__name__)


class DataViewer:
    """Handles data querying and preparation for viewing with modular architecture."""
    
    def __init__(self, database_manager=None, config_manager: Optional[ConfigManager] = None):
        """Initialize data viewer with modular components."""
        # Initialize core managers
        self.period_manager = PeriodManager()
        self.data_query_engine = DataQueryEngine(database_manager, config_manager)
        self.data_processor = DataProcessor(config_manager)
        
        # Store references for backward compatibility
        self.database_manager = database_manager
        self.config_manager = config_manager or ConfigManager()
    
    # Period Management (delegate to PeriodManager)
    def calculate_period_range(self, period_type: str, reference_date: Optional[Any] = None) -> PeriodRange:
        """Calculate date range for various period types."""
        return self.period_manager.calculate_period_range(period_type, reference_date)
    
    def calculate_custom_range(self, start_date: Any, end_date: Any) -> PeriodRange:
        """Calculate custom date range."""
        return self.period_manager.calculate_custom_range(start_date, end_date)
    
    def validate_period_type(self, period_type: str) -> bool:
        """Validate if period type is supported."""
        return self.period_manager.validate_period_type(period_type)
    
    def parse_date_string(self, date_string: str):
        """Parse date string in YYYY-MM-DD format."""
        return self.period_manager.parse_date_string(date_string)
    
    # Data Retrieval and Processing (coordinate between components)
    async def get_statistics_for_period(self, 
                                       period_range: PeriodRange,
                                       monitoring_group: str = "all",
                                       user_group: str = "all") -> StatisticsData:
        """Get statistics data for specified period."""
        logger.debug(f"Getting statistics for period: {period_range.description}")
        
        try:
            # Get raw data from query engine
            raw_data = await self.data_query_engine.get_statistics_for_period(
                period_range, monitoring_group
            )
            
            # Process data through data processor
            statistics_data = await self.data_processor.process_statistics_data(
                raw_data, period_range, user_group
            )
            
            return statistics_data
            
        except Exception as e:
            logger.error(f"Failed to get statistics for period {period_range.description}: {e}")
            # Fallback to mock data for testing
            logger.warning("Falling back to mock data generation")
            return await self.data_processor.generate_mock_statistics_data(
                period_range, monitoring_group, user_group
            )
    
    async def get_statistics_breakdown(self,
                                     period_range: PeriodRange,
                                     monitoring_group: str = "all",
                                     user_group: str = "all") -> List[StatisticsData]:
        """Get day-by-day breakdown for a period."""
        logger.debug(f"Getting statistics breakdown for period: {period_range.description}")
        
        breakdown_data = []
        raw_breakdown = await self.data_query_engine.get_statistics_breakdown(
            period_range, monitoring_group
        )
        
        # Process each day's data
        current_date = period_range.start_date
        for day_raw_data in raw_breakdown:
            single_day_range = PeriodRange(
                start_date=current_date,
                end_date=current_date,
                period_type="single-day",
                description=str(current_date)
            )
            
            try:
                if day_raw_data.get('total_messages', 0) > 0:
                    # Process non-empty data
                    day_statistics = await self.data_processor.process_statistics_data(
                        day_raw_data, single_day_range, user_group
                    )
                else:
                    # Create empty statistics for missing days
                    day_statistics = StatisticsData(
                        date=str(current_date),
                        total_messages=0,
                        users=[],
                        chats=[],
                        monitoring_groups_used=[],
                        collection_completed_at=""
                    )
                
                breakdown_data.append(day_statistics)
                
            except Exception as e:
                logger.warning(f"Failed to process data for {current_date}: {e}")
                # Create empty data for failed processing
                empty_data = StatisticsData(
                    date=str(current_date),
                    total_messages=0,
                    users=[],
                    chats=[],
                    monitoring_groups_used=[],
                    collection_completed_at=""
                )
                breakdown_data.append(empty_data)
            
            # Move to next date (using timedelta import)
            from datetime import timedelta
            current_date += timedelta(days=1)
        
        logger.debug(f"Generated breakdown with {len(breakdown_data)} day entries")
        return breakdown_data
    
    async def check_data_availability(self, period_range: PeriodRange, monitoring_group: str = "all") -> Dict[str, Any]:
        """Check what data is available for the specified period."""
        return await self.data_query_engine.check_data_availability(period_range, monitoring_group)
    
    # Legacy methods for backward compatibility
    async def _get_mock_statistics_data(self, 
                                       period_range: PeriodRange,
                                       monitoring_group: str = "all",
                                       user_group: str = "all") -> StatisticsData:
        """Generate mock statistics data for testing (legacy method)."""
        return await self.data_processor.generate_mock_statistics_data(
            period_range, monitoring_group, user_group
        )


# Factory function for backward compatibility
def create_data_viewer(database_manager=None, config_manager: Optional[ConfigManager] = None) -> DataViewer:
    """Create DataViewer instance."""
    return DataViewer(database_manager, config_manager)


# Backward compatibility exports
__all__ = [
    'DataViewer',
    'PeriodManager',
    'DataQueryEngine', 
    'DataProcessor',
    'PeriodRange',
    'DataViewError',
    'create_data_viewer'
] 