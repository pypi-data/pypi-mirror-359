"""
Data error handling utilities.

This module handles error processing and recovery for data operations.
Single Responsibility: Managing errors and providing fallback mechanisms.
"""

import logging
from typing import Dict, Any, Optional, Callable
from ...template_processor.data_models import StatisticsData
from .data_converter import DataConverter

logger = logging.getLogger(__name__)


class DataErrorHandler:
    """Handles errors in data retrieval and processing operations."""
    
    @staticmethod
    def handle_retrieval_error(error: Exception, target_date, monitoring_group: str, 
                              reporting_group: str = None) -> StatisticsData:
        """
        Handle data retrieval errors and return empty statistics.
        
        Args:
            error: The exception that occurred
            target_date: Target date for statistics
            monitoring_group: Monitoring group name
            reporting_group: Reporting group name (optional)
            
        Returns:
            Empty StatisticsData object
        """
        logger.error(f"Data retrieval error for {target_date}: {error}")
        return DataConverter.create_empty_statistics(target_date, monitoring_group, reporting_group)
    
    @staticmethod
    def handle_filtering_error(error: Exception, raw_data: Dict[str, Any], 
                              monitoring_group: str, user_group: str) -> Dict[str, Any]:
        """
        Handle filtering errors and return unfiltered data.
        
        Args:
            error: The exception that occurred
            raw_data: Raw statistics data
            monitoring_group: Monitoring group name
            user_group: User group name
            
        Returns:
            Raw data without filtering
        """
        logger.error(f"Filtering error for {monitoring_group}/{user_group}: {error}")
        logger.warning("Returning unfiltered data as fallback")
        return raw_data
    
    @staticmethod
    def handle_conversion_error(error: Exception, target_date, monitoring_group: str,
                               reporting_group: str = None) -> StatisticsData:
        """
        Handle data conversion errors and return empty statistics.
        
        Args:
            error: The exception that occurred
            target_date: Target date for statistics
            monitoring_group: Monitoring group name
            reporting_group: Reporting group name (optional)
            
        Returns:
            Empty StatisticsData object
        """
        logger.error(f"Data conversion error for {target_date}: {error}")
        return DataConverter.create_empty_statistics(target_date, monitoring_group, reporting_group)
    
    @staticmethod
    def safe_execute(operation: Callable, fallback_value: Any = None, 
                    error_message: str = "Operation failed") -> Any:
        """
        Safely execute an operation with error handling.
        
        Args:
            operation: Function to execute
            fallback_value: Value to return on error
            error_message: Custom error message
            
        Returns:
            Operation result or fallback value
        """
        try:
            return operation()
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return fallback_value
    
    @staticmethod
    def validate_data_integrity(data: Dict[str, Any]) -> bool:
        """
        Validate data integrity and structure.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        try:
            if not isinstance(data, dict):
                logger.error("Data is not a dictionary")
                return False
            
            required_keys = ["daily_stats", "user_stats", "chat_stats"]
            for key in required_keys:
                if key not in data:
                    logger.error(f"Missing required key: {key}")
                    return False
            
            # Validate daily_stats structure
            daily_stats = data["daily_stats"]
            if not isinstance(daily_stats, dict):
                logger.error("daily_stats is not a dictionary")
                return False
            
            # Validate user_stats structure
            user_stats = data["user_stats"]
            if not isinstance(user_stats, list):
                logger.error("user_stats is not a list")
                return False
            
            # Validate chat_stats structure
            chat_stats = data["chat_stats"]
            if not isinstance(chat_stats, list):
                logger.error("chat_stats is not a list")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Data validation error: {e}")
            return False
    
    @staticmethod
    def log_operation_metrics(operation_name: str, success: bool, 
                             execution_time: float = None, record_count: int = None):
        """
        Log operation metrics for monitoring and debugging.
        
        Args:
            operation_name: Name of the operation
            success: Whether operation was successful
            execution_time: Execution time in seconds (optional)
            record_count: Number of records processed (optional)
        """
        status = "SUCCESS" if success else "FAILED"
        message = f"Operation {operation_name}: {status}"
        
        if execution_time is not None:
            message += f" (took {execution_time:.3f}s)"
        
        if record_count is not None:
            message += f" (processed {record_count} records)"
        
        if success:
            logger.info(message)
        else:
            logger.error(message) 