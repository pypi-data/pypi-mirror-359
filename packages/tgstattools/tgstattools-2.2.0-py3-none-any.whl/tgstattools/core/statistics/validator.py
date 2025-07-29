"""
Statistics collection validator.

This module provides validation functionality to detect anomalies
and potential issues in statistics collection results.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)


class CollectionValidator:
    """Validates statistics collection results for anomalies."""
    
    def __init__(self, database):
        """Initialize validator with database connection."""
        self.database = database
        self.logger = logging.getLogger(__name__)
    
    def validate_collection_result(self, collection_result: Dict[str, Any], 
                                  monitoring_group: str, target_date: date) -> Dict[str, Any]:
        """
        Validate collection result for potential issues.
        
        Args:
            collection_result: Result from StatisticsCollector.collect_statistics
            monitoring_group: Name of monitoring group
            target_date: Target collection date
            
        Returns:
            Validation result with warnings and recommendations
        """
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        if not collection_result.get("success"):
            validation["valid"] = False
            validation["errors"].append("Collection failed")
            return validation
        
        # Check for zero messages anomaly
        total_messages = collection_result.get("total_messages", 0)
        chat_count = collection_result.get("chat_count", 0)
        
        if total_messages == 0 and chat_count > 0:
            validation["warnings"].append(
                f"Zero messages collected from {chat_count} chats - potential collection bug"
            )
            validation["recommendations"].append(
                "Check message collection logic and API parameters"
            )
        
        # Check for historical anomalies
        historical_anomalies = self._check_historical_patterns(
            monitoring_group, target_date, total_messages
        )
        validation["warnings"].extend(historical_anomalies)
        
        # Check for reasonable message distribution
        user_count = collection_result.get("user_count", 0)
        if total_messages > 0 and user_count == 0:
            validation["warnings"].append("Messages found but no users recorded")
        
        if total_messages > 100 and user_count < 3:
            validation["warnings"].append(
                f"Unusual user distribution: {total_messages} messages from only {user_count} users"
            )
        
        return validation
    
    def _check_historical_patterns(self, monitoring_group: str, target_date: date, 
                                  current_messages: int) -> List[str]:
        """Check current results against historical patterns."""
        warnings = []
        
        try:
            # Get data from previous 7 days
            historical_data = []
            for i in range(1, 8):
                past_date = target_date - timedelta(days=i)
                
                # Get statistics for this date (simplified - would need proper hash lookup)
                with self.database.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT total_messages 
                        FROM daily_statistics 
                        WHERE date = ? AND collection_status = 'completed'
                    """, (past_date.isoformat(),))
                    
                    result = cursor.fetchone()
                    if result:
                        historical_data.append(result[0])
            
            if historical_data:
                avg_historical = sum(historical_data) / len(historical_data)
                max_historical = max(historical_data)
                
                # Check for significant drops
                if current_messages < avg_historical * 0.1:  # Less than 10% of average
                    warnings.append(
                        f"Significant drop: {current_messages} vs historical average {avg_historical:.0f}"
                    )
                
                # Check for unrealistic spikes
                if current_messages > max_historical * 3:  # More than 3x historical max
                    warnings.append(
                        f"Unusual spike: {current_messages} vs historical max {max_historical}"
                    )
        
        except Exception as e:
            self.logger.warning(f"Could not check historical patterns: {e}")
        
        return warnings
    
    def validate_chat_results(self, chat_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate individual chat collection results."""
        validation = {
            "valid": True,
            "warnings": [],
            "suspicious_chats": []
        }
        
        for chat_result in chat_results:
            chat_id = chat_result.get("chat_id")
            chat_title = chat_result.get("chat_title", f"Chat {chat_id}")
            
            if not chat_result.get("success"):
                validation["warnings"].append(f"Failed to collect from {chat_title}")
                continue
            
            # Check for suspicious patterns
            message_count = chat_result.get("message_count", 0)
            user_count = len(chat_result.get("users", {}))
            
            # Single user domination (>90% of messages)
            if user_count > 1 and message_count > 10:
                users = chat_result.get("users", {})
                max_user_messages = max(users.values()) if users else 0
                if max_user_messages / message_count > 0.9:
                    validation["suspicious_chats"].append({
                        "chat": chat_title,
                        "issue": "Single user dominance",
                        "details": f"{max_user_messages}/{message_count} messages from one user"
                    })
        
        return validation


def create_validator(database) -> CollectionValidator:
    """Create a new collection validator."""
    return CollectionValidator(database) 