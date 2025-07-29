"""
Statistics package for TgStatTools.

This package provides modular statistics collection functionality:
- StatisticsCollector: Main unified interface (backward compatible)
- ChatDiscovery: Automatic chat discovery
- ChatCollector: Individual chat statistics collection  
- StatisticsUtils: Utility functions and helpers
- CollectionValidator: Result validation and anomaly detection
"""

import logging
import json
from typing import Dict, List, Any, Optional, Set, Union
from datetime import datetime, date

from .chat_discovery import ChatDiscovery
from .chat_collector import ChatCollector
from .utils import StatisticsUtils
from .validator import CollectionValidator

logger = logging.getLogger(__name__)


class StatisticsCollector:
    """
    Main statistics collector with modular architecture.
    
    This class maintains 100% backward compatibility while leveraging
    the new modular structure for better maintainability and testability.
    """
    
    def __init__(self, config_manager, database, telegram_client):
        """Initialize statistics collector with all services."""
        self.config_manager = config_manager
        self.database = database
        self.telegram_client = telegram_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize modular services
        self.chat_discovery = ChatDiscovery(telegram_client)
        self.chat_collector = ChatCollector(telegram_client)
        self.utils = StatisticsUtils(telegram_client, database)
        self.validator = CollectionValidator(database)
    
    async def collect_statistics(self, monitoring_group: str, target_date: date, force_collection: bool = False) -> Dict[str, Any]:
        """
        Collect statistics for a specific monitoring group and date.
        
        Args:
            monitoring_group: Name of monitoring group configuration
            target_date: Date to collect statistics for
            
        Returns:
            Dictionary with collection results
        """
        try:
            # Load monitoring group configuration
            if monitoring_group == "all":
                # Handle auto-discovery
                group_config = self.config_manager.load_monitoring_group("all")
                chats = await self.chat_discovery.discover_chats(group_config)
            else:
                group_config = self.config_manager.load_monitoring_group(monitoring_group)
                
                # Check if this group uses auto-discovery
                if self.utils.is_auto_discovery_group(group_config):
                    chats = await self.chat_discovery.discover_chats(group_config)
                else:
                    chats = group_config.get("chat_ids", {})
            
            if not chats:
                self.logger.warning(f"No chats found for monitoring group: {monitoring_group}")
                return {"success": False, "error": "No chats to monitor"}
            
            # Calculate monitoring groups hash
            monitoring_groups_hash = self.utils.calculate_monitoring_groups_hash([monitoring_group])
            
            # Check if collection already exists (skip if force_collection is True)
            if not force_collection and self.utils.collection_exists(target_date, monitoring_groups_hash):
                self.logger.info(f"Statistics already collected for {target_date} with hash {monitoring_groups_hash}")
                return {"success": True, "already_collected": True}
            
            # Start collection process
            collection_started = datetime.now()
            self.logger.info(f"Starting statistics collection for {target_date}, {len(chats)} chats")
            
            # Initialize counters
            total_messages = 0
            user_stats = {}  # For compatibility: total per user across all chats
            chat_stats = {}  # For compatibility: total per chat
            user_chat_stats = {}  # NEW: detailed (user_id, chat_id) -> message_count
            errors_count = 0
            media_groups_processed = 0
            
            # Process each chat using modular chat collector
            for chat_id, chat_title in chats.items():
                try:
                    chat_result = await self.chat_collector.collect_chat_statistics(
                        chat_id, chat_title, target_date
                    )
                    
                    if chat_result["success"]:
                        total_messages += chat_result["message_count"]
                        media_groups_processed += chat_result["media_groups"]
                        
                        # ИСПРАВЛЕНИЕ: Сохраняем детализацию ПЕРЕД агрегацией
                        for user_id, count in chat_result["users"].items():
                            # Сохраняем детализированные данные (user_id, chat_id) -> count
                            user_chat_stats[(user_id, chat_id)] = count
                            
                            # Агрегируем для совместимости
                            user_stats[user_id] = user_stats.get(user_id, 0) + count
                        
                        # Store chat statistics (для совместимости)
                        chat_stats[chat_id] = chat_result["message_count"]
                    else:
                        errors_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Error collecting from chat {chat_id} ({chat_title}): {e}")
                    errors_count += 1
                    continue
            
            # Store results in database
            collection_completed = datetime.now()
            
            # Create or update daily statistics record (use upsert for force collection)
            if force_collection:
                daily_stats_id = self.database.upsert_daily_statistics(
                    date=target_date,
                    monitoring_groups_hash=monitoring_groups_hash,
                    total_messages=total_messages,
                    collection_started_at=collection_started,
                    collection_completed_at=collection_completed,
                    collection_status="completed",
                    errors_count=errors_count,
                    media_groups_processed=media_groups_processed,
                    monitoring_groups_used=json.dumps([monitoring_group])
                )
            else:
                daily_stats_id = self.database.insert_daily_statistics(
                    date=target_date,
                    monitoring_groups_hash=monitoring_groups_hash,
                    total_messages=total_messages,
                    collection_started_at=collection_started,
                    collection_completed_at=collection_completed,
                    collection_status="completed",
                    errors_count=errors_count,
                    media_groups_processed=media_groups_processed,
                    monitoring_groups_used=json.dumps([monitoring_group])
                )
            
            # Clear existing statistics if force collection
            if force_collection:
                self.database.delete_user_stats_for_collection(daily_stats_id)
                self.database.delete_chat_stats_for_collection(daily_stats_id)
                self.database.delete_user_chat_stats_for_collection(daily_stats_id)
            
            # Store user statistics with proper name resolution
            for user_id, message_count in user_stats.items():
                user_name = await self.utils.get_user_name(user_id)
                percentage = self.utils.calculate_percentage(message_count, total_messages)
                
                self.database.insert_daily_user_stats(
                    daily_stats_id=daily_stats_id,
                    date=target_date,
                    monitoring_groups_hash=monitoring_groups_hash,
                    user_id=user_id,
                    user_name=user_name,
                    messages=message_count,
                    percentage=percentage
                )
            
            # Store chat statistics (for compatibility)
            for chat_id, message_count in chat_stats.items():
                chat_title = chats.get(chat_id, f"Chat {chat_id}")
                percentage = self.utils.calculate_percentage(message_count, total_messages)
                
                self.database.insert_daily_chat_stats(
                    daily_stats_id=daily_stats_id,
                    date=target_date,
                    monitoring_groups_hash=monitoring_groups_hash,
                    chat_id=chat_id,
                    chat_title=chat_title,
                    messages=message_count,
                    percentage=percentage
                )
            
            # НОВОЕ: Сохранить детализированные данные user-chat
            if user_chat_stats:
                self.logger.info(f"Storing {len(user_chat_stats)} detailed user-chat statistics")
                self.database.insert_daily_user_chat_stats(
                    daily_stats_id=daily_stats_id,
                    date=target_date,
                    monitoring_groups_hash=monitoring_groups_hash,
                    user_chat_stats=user_chat_stats
                )
            
            self.logger.info(
                f"Collection completed: {total_messages} messages, "
                f"{len(user_stats)} users, {len(chat_stats)} chats, "
                f"{errors_count} errors"
            )
            
            # Create result for validation
            result = {
                "success": True,
                "total_messages": total_messages,
                "user_count": len(user_stats),
                "chat_count": len(chat_stats),
                "errors_count": errors_count,
                "media_groups_processed": media_groups_processed
            }
            
            # Validate collection results
            validation = self.validator.validate_collection_result(result, monitoring_group, target_date)
            
            # Log validation warnings
            if validation["warnings"]:
                self.logger.warning("Collection validation warnings:")
                for warning in validation["warnings"]:
                    self.logger.warning(f"  - {warning}")
            
            if validation["recommendations"]:
                self.logger.info("Validation recommendations:")
                for rec in validation["recommendations"]:
                    self.logger.info(f"  - {rec}")
            
            # Add validation info to result
            result["validation"] = validation
            
            return result
            
        except Exception as e:
            self.logger.error(f"Statistics collection failed: {e}")
            return {"success": False, "error": str(e)}
    
    # === Backward compatibility methods ===
    
    async def _discover_chats(self, group_config: Dict[str, Any]) -> Dict[int, str]:
        """Backward compatibility wrapper for chat discovery."""
        return await self.chat_discovery.discover_chats(group_config)
    
    async def _collect_chat_statistics(self, chat_id: int, chat_title: str, 
                                     target_date: date) -> Dict[str, Any]:
        """Backward compatibility wrapper for chat collection."""
        return await self.chat_collector.collect_chat_statistics(chat_id, chat_title, target_date)
    
    async def _get_user_name(self, user_id: int) -> str:
        """Backward compatibility wrapper for user name resolution."""
        return await self.utils.get_user_name(user_id)
    
    def _calculate_monitoring_groups_hash(self, groups: List[str]) -> str:
        """Backward compatibility wrapper for hash calculation."""
        return self.utils.calculate_monitoring_groups_hash(groups)
    
    def _collection_exists(self, target_date: date, monitoring_groups_hash: str) -> bool:
        """Backward compatibility wrapper for collection existence check."""
        return self.utils.collection_exists(target_date, monitoring_groups_hash)


# Export main class for backward compatibility
__all__ = ['StatisticsCollector', 'ChatDiscovery', 'ChatCollector', 'StatisticsUtils'] 