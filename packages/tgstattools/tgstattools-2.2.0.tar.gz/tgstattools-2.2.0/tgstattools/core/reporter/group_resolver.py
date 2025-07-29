"""
Reporting group resolution and chat discovery for TgStatTools.

This module handles resolving reporting group configurations to
specific chat IDs and managing auto-discovery functionality.
"""

import logging
from typing import List, Set
from ..config_manager import ConfigManager

logger = logging.getLogger(__name__)


class ReportDeliveryError(Exception):
    """Report delivery related errors."""
    pass


class GroupResolver:
    """Handles reporting group resolution and chat discovery."""
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize group resolver."""
        self.config_manager = config_manager
        
    async def resolve_reporting_group(self, group_name: str) -> List[int]:
        """Resolve reporting group to list of chat IDs."""
        logger.debug(f"Resolving reporting group: {group_name}")
        
        try:
            config = self.config_manager.load_reporting_group(group_name)
            
            # Check if this is an auto-discovery group
            if self.config_manager.is_auto_discovery_group(config):
                return await self.discover_all_reporting_chats()
            else:
                # Use explicitly defined chat IDs
                chat_ids = config.get("chat_ids", {})
                return list(chat_ids.keys())
                
        except Exception as e:
            logger.error(f"Failed to resolve reporting group '{group_name}': {e}")
            raise ReportDeliveryError(f"Cannot resolve reporting group '{group_name}': {e}")
    
    async def discover_all_reporting_chats(self) -> List[int]:
        """Discover all chats from all reporting groups."""
        logger.debug("Discovering all reporting chats from all groups")
        
        all_chat_ids: Set[int] = set()
        
        try:
            groups = self.config_manager.list_groups("reporting")["reporting"]
            
            for group_name in groups:
                if group_name == "all":  # Skip the auto-discovery group itself
                    continue
                    
                try:
                    config = self.config_manager.load_reporting_group(group_name)
                    # Only process non-auto-discovery groups
                    if not self.config_manager.is_auto_discovery_group(config):
                        chat_ids = config.get("chat_ids", {})
                        all_chat_ids.update(chat_ids.keys())
                        logger.debug(f"Added {len(chat_ids)} chats from group '{group_name}'")
                except Exception as e:
                    logger.warning(f"Failed to load reporting group '{group_name}': {e}")
            
            result = list(all_chat_ids)
            logger.debug(f"Discovered {len(result)} unique reporting chats")
            return result
            
        except Exception as e:
            logger.error(f"Failed to discover reporting chats: {e}")
            raise ReportDeliveryError(f"Cannot discover reporting chats: {e}") 