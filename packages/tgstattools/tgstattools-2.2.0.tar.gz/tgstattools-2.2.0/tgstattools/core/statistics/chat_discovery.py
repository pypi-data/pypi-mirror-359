"""
Chat discovery module for TgStatTools.

This module handles automatic discovery of accessible Telegram chats
based on configured filters and permissions.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ChatDiscovery:
    """Handles automatic discovery of accessible chats."""
    
    def __init__(self, telegram_client):
        """Initialize chat discovery with Telegram client."""
        self.telegram_client = telegram_client
        self.logger = logging.getLogger(__name__)
    
    async def discover_chats(self, group_config: Dict[str, Any]) -> Dict[int, str]:
        """
        Discover chats using auto-discovery logic.
        
        Args:
            group_config: Configuration with filters for chat discovery
            
        Returns:
            Dictionary mapping chat IDs to chat titles
        """
        chats = {}
        filters = group_config.get("filters", {})
        
        try:
            # Get all dialogs from Telegram
            self.logger.info("Starting chat auto-discovery...")
            
            async for dialog in self.telegram_client.iter_dialogs():
                chat = dialog.entity
                
                # Apply filters
                if filters.get("exclude_private", True) and self._is_private_chat(chat):
                    continue
                
                if filters.get("exclude_channels", False) and self._is_channel(chat):
                    continue
                
                min_members = filters.get("min_members", 1)
                if not self._meets_member_requirement(chat, min_members):
                    continue
                
                # Check if we can read messages
                if await self._verify_chat_access(chat):
                    # Get appropriate title based on chat type
                    chat_title = self._get_chat_title(chat)
                    chats[chat.id] = chat_title
        
        except Exception as e:
            self.logger.error(f"Error during chat discovery: {e}")
        
        self.logger.info(f"Discovered {len(chats)} accessible chats")
        return chats
    
    def _is_private_chat(self, chat) -> bool:
        """Check if chat is a private conversation."""
        return hasattr(chat, 'is_user') and chat.is_user
    
    def _is_channel(self, chat) -> bool:
        """Check if chat is a broadcast channel."""
        return hasattr(chat, 'is_channel') and chat.is_channel
    
    def _meets_member_requirement(self, chat, min_members: int) -> bool:
        """Check if chat meets minimum member requirement."""
        if hasattr(chat, 'participants_count'):
            return chat.participants_count >= min_members
        return True  # Default to True if we can't determine member count
    
    def _get_chat_title(self, chat) -> str:
        """Get appropriate title for chat based on its type."""
        if hasattr(chat, 'title') and chat.title:
            # Group or channel with title
            return chat.title
        elif hasattr(chat, 'first_name'):
            # User/private chat
            full_name = chat.first_name or ""
            if hasattr(chat, 'last_name') and chat.last_name:
                full_name += f" {chat.last_name}"
            if hasattr(chat, 'username') and chat.username:
                full_name += f" (@{chat.username})"
            return full_name or f"User {chat.id}"
        else:
            # Fallback
            return f"Chat {chat.id}"
    
    async def _verify_chat_access(self, chat) -> bool:
        """Verify that we can read messages from the chat."""
        try:
            # Try to get latest message to verify access
            async for _ in self.telegram_client.iter_messages(chat, limit=1):
                return True
        except Exception:
            # Skip chats we can't access
            return False
        return False 