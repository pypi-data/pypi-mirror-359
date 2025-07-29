"""
Data query engine for retrieving statistics from the database.

This module provides:
- Database query operations for statistics
- Single day and date range queries
- Data aggregation and processing
- Monitoring group resolution
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional

from .period_manager import PeriodRange
from ..template_processor import StatisticsData

logger = logging.getLogger(__name__)


class DataQueryEngine:
    """Handles database queries and data retrieval operations."""
    
    def __init__(self, database_manager=None, config_manager=None):
        """Initialize data query engine."""
        self.database_manager = database_manager
        self.config_manager = config_manager
    
    async def get_statistics_for_period(self, 
                                       period_range: PeriodRange,
                                       monitoring_group: str = "all") -> Dict[str, Any]:
        """Get raw statistics data for specified period."""
        logger.debug(f"Getting statistics for period: {period_range.description}")
        
        if not self.database_manager:
            # For testing purposes, return mock data
            logger.warning("Database manager not configured, using mock data")
            return await self._get_mock_query_data(period_range, monitoring_group)
        
        try:
            # Calculate monitoring groups hash
            monitoring_groups_hash = await self._resolve_monitoring_groups_hash(monitoring_group)
            
            # Query data from database
            if period_range.start_date == period_range.end_date:
                # Single day query
                raw_data = await self._query_single_day(
                    period_range.start_date, 
                    monitoring_groups_hash
                )
            else:
                # Multi-day aggregation
                raw_data = await self._query_date_range(
                    period_range.start_date,
                    period_range.end_date,
                    monitoring_groups_hash
                )
            
            return raw_data
            
        except Exception as e:
            logger.error(f"Failed to get statistics for period {period_range.description}: {e}")
            raise
    
    async def get_statistics_breakdown(self,
                                     period_range: PeriodRange,
                                     monitoring_group: str = "all") -> List[Dict[str, Any]]:
        """Get day-by-day breakdown for a period."""
        logger.debug(f"Getting statistics breakdown for period: {period_range.description}")
        
        breakdown_data = []
        current_date = period_range.start_date
        
        while current_date <= period_range.end_date:
            single_day_range = PeriodRange(
                start_date=current_date,
                end_date=current_date,
                period_type="single-day",
                description=str(current_date)
            )
            
            try:
                day_data = await self.get_statistics_for_period(
                    single_day_range, 
                    monitoring_group
                )
                breakdown_data.append(day_data)
            except Exception as e:
                logger.warning(f"Failed to get data for {current_date}: {e}")
                # Create empty data for missing days
                empty_data = {
                    'total_messages': 0,
                    'users': [],
                    'chats': [],
                    'monitoring_groups_used': [],
                    'collection_completed_at': ''
                }
                breakdown_data.append(empty_data)
            
            current_date += timedelta(days=1)
        
        logger.debug(f"Generated breakdown with {len(breakdown_data)} day entries")
        return breakdown_data
    
    async def check_data_availability(self, period_range: PeriodRange, monitoring_group: str = "all") -> Dict[str, Any]:
        """Check what data is available for the specified period."""
        logger.debug(f"Checking data availability for period: {period_range.description}")
        
        # Placeholder implementation
        return {
            "period": period_range.description,
            "start_date": str(period_range.start_date),
            "end_date": str(period_range.end_date),
            "monitoring_group": monitoring_group,
            "available_days": (period_range.end_date - period_range.start_date).days + 1,
            "missing_days": 0,
            "last_update": datetime.now().isoformat()
        }
    
    async def _resolve_monitoring_groups_hash(self, monitoring_group: str) -> str:
        """Resolve monitoring group to hash."""
        if not self.config_manager:
            return "default_hash"
        
        # Placeholder - would calculate actual hash based on group configuration
        if monitoring_group == "all":
            group_names = ["all"]
        else:
            group_names = [monitoring_group]
        
        return self.config_manager.calculate_monitoring_groups_hash(group_names)
    
    async def _query_single_day(self, target_date: date, monitoring_groups_hash: str) -> Dict[str, Any]:
        """Query statistics for a single day."""
        logger.debug(f"Querying single day: {target_date}")
        
        if not self.database_manager:
            return await self._get_mock_single_day_data(target_date)
        
        try:
            # Query database for specific date and monitoring group hash
            daily_stats = self.database_manager.get_daily_statistics(target_date, monitoring_groups_hash)
            
            if not daily_stats:
                # Try to find data for this date with any monitoring group hash
                with self.database_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT ds.*, 
                               (SELECT GROUP_CONCAT(DISTINCT user_name) FROM daily_user_stats dus 
                                WHERE dus.date = ds.date AND dus.daily_stats_id = ds.id) as user_names,
                               (SELECT GROUP_CONCAT(DISTINCT chat_title) FROM daily_chat_stats dcs 
                                WHERE dcs.date = ds.date AND dcs.daily_stats_id = ds.id) as chat_titles
                        FROM daily_statistics ds 
                        WHERE ds.date = ? 
                        ORDER BY ds.total_messages DESC 
                        LIMIT 1
                    """, (target_date.isoformat(),))
                    
                    result = cursor.fetchone()
                    if result:
                        daily_stats = {
                            'date': result[1],
                            'monitoring_groups_hash': result[2],
                            'total_messages': result[3],
                            'collection_completed_at': result[5],
                            'status': result[6],
                            'monitoring_groups_used': eval(result[9]) if result[9] else []
                        }
                    else:
                        return await self._get_mock_single_day_data(target_date)
            
            # Get user and chat statistics for this date
            with self.database_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get user statistics
                cursor.execute("""
                    SELECT user_id, user_name, messages, percentage 
                    FROM daily_user_stats 
                    WHERE date = ? 
                    ORDER BY messages DESC
                """, (target_date.isoformat(),))
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'user_id': row[0],
                        'name': row[1] or f"User_{row[0]}",
                        'messages': row[2],
                        'percentage': row[3]
                    })
                
                # Get chat statistics
                cursor.execute("""
                    SELECT chat_id, chat_title, messages, percentage 
                    FROM daily_chat_stats 
                    WHERE date = ? 
                    ORDER BY messages DESC
                """, (target_date.isoformat(),))
                
                chats = []
                for row in cursor.fetchall():
                    chats.append({
                        'chat_id': row[0],
                        'title': row[1] or f"Chat_{row[0]}",
                        'messages': row[2],
                        'percentage': row[3]
                    })
            
            return {
                'total_messages': daily_stats.get('total_messages', 0),
                'users': users,
                'chats': chats,
                'monitoring_groups_used': daily_stats.get('monitoring_groups_used', []),
                'collection_completed_at': daily_stats.get('collection_completed_at', ''),
                'date': str(target_date)
            }
            
        except Exception as e:
            logger.error(f"Database query failed for {target_date}: {e}")
            return await self._get_mock_single_day_data(target_date)
    
    async def _query_date_range(self, start_date: date, end_date: date, monitoring_groups_hash: str) -> Dict[str, Any]:
        """Query and aggregate statistics for a date range."""
        logger.debug(f"Querying date range: {start_date} to {end_date}")
        
        if not self.database_manager:
            return await self._get_mock_range_data(start_date, end_date)
        
        try:
            # Aggregate data across the date range
            with self.database_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get total messages for the range
                cursor.execute("""
                    SELECT COALESCE(SUM(total_messages), 0) as total_messages,
                           MAX(collection_completed_at) as latest_collection
                    FROM daily_statistics 
                    WHERE date BETWEEN ? AND ?
                """, (start_date.isoformat(), end_date.isoformat()))
                
                result = cursor.fetchone()
                total_messages = result[0] if result else 0
                latest_collection = result[1] if result else ''
                
                # Get aggregated user statistics for the range
                cursor.execute("""
                    SELECT user_id, user_name, 
                           SUM(messages) as total_messages,
                           ROUND(SUM(messages) * 100.0 / ?, 2) as percentage
                    FROM daily_user_stats 
                    WHERE date BETWEEN ? AND ?
                    GROUP BY user_id, user_name
                    HAVING SUM(messages) > 0
                    ORDER BY total_messages DESC
                """, (max(total_messages, 1), start_date.isoformat(), end_date.isoformat()))
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'user_id': row[0],
                        'name': row[1] or f"User_{row[0]}",
                        'messages': row[2],
                        'percentage': row[3]
                    })
                
                # Get aggregated chat statistics for the range
                cursor.execute("""
                    SELECT chat_id, chat_title, 
                           SUM(messages) as total_messages,
                           ROUND(SUM(messages) * 100.0 / ?, 2) as percentage
                    FROM daily_chat_stats 
                    WHERE date BETWEEN ? AND ?
                    GROUP BY chat_id, chat_title
                    HAVING SUM(messages) > 0
                    ORDER BY total_messages DESC
                """, (max(total_messages, 1), start_date.isoformat(), end_date.isoformat()))
                
                chats = []
                for row in cursor.fetchall():
                    chats.append({
                        'chat_id': row[0],
                        'title': row[1] or f"Chat_{row[0]}",
                        'messages': row[2],
                        'percentage': row[3]
                    })
                
                # Get monitoring groups used in this range
                cursor.execute("""
                    SELECT DISTINCT monitoring_groups_used
                    FROM daily_statistics 
                    WHERE date BETWEEN ? AND ?
                    AND monitoring_groups_used IS NOT NULL
                """, (start_date.isoformat(), end_date.isoformat()))
                
                monitoring_groups_used = []
                for row in cursor.fetchall():
                    if row[0]:
                        try:
                            groups = eval(row[0]) if isinstance(row[0], str) else row[0]
                            if isinstance(groups, list):
                                monitoring_groups_used.extend(groups)
                        except:
                            pass
                
                # Remove duplicates and sort
                monitoring_groups_used = sorted(list(set(monitoring_groups_used)))
                
                return {
                    'total_messages': total_messages,
                    'users': users,
                    'chats': chats,
                    'monitoring_groups_used': monitoring_groups_used,
                    'collection_completed_at': latest_collection,
                    'date_range': f"{start_date} to {end_date}"
                }
                
        except Exception as e:
            logger.error(f"Database range query failed for {start_date} to {end_date}: {e}")
            return await self._get_mock_range_data(start_date, end_date)
    
    async def _get_mock_query_data(self, period_range: PeriodRange, monitoring_group: str) -> Dict[str, Any]:
        """Generate mock query data for testing."""
        logger.debug(f"Generating mock query data for {period_range.description}")
        
        if period_range.start_date == period_range.end_date:
            return await self._get_mock_single_day_data(period_range.start_date)
        else:
            return await self._get_mock_range_data(period_range.start_date, period_range.end_date)
    
    async def _get_mock_single_day_data(self, target_date: date) -> Dict[str, Any]:
        """Return empty data - should use real database queries."""
        return {
            'total_messages': 0,
            'users': [],
            'chats': [],
            'monitoring_groups_used': [],
            'collection_completed_at': None,
            'note': 'No mock data - use real database or perform collection first'
        }
    
    async def _get_mock_range_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Return empty data - should use real database queries."""
        return {
            'total_messages': 0,
            'users': [],
            'chats': [],
            'monitoring_groups_used': [],
            'collection_completed_at': None,
            'note': 'No mock data - use real database or perform collection first'
        } 