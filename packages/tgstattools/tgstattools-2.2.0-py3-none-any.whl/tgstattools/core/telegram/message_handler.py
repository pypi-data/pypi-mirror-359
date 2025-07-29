"""
Message handling functionality for Telegram client.

This module provides:
- Message sending operations
- Message retrieval and iteration
- Message formatting and processing
- Error handling for message operations
"""

import logging
from typing import Dict, Any, List, Optional, AsyncGenerator

logger = logging.getLogger(__name__)

# Check if Telethon is available
try:
    from telethon.errors import RPCError
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    class RPCError(Exception): pass


class TelegramClientError(Exception):
    """Telegram client related errors."""
    pass


class AuthenticationError(Exception):
    """Authentication related errors."""
    pass


class MessageHandler:
    """Handles message operations for Telegram client."""
    
    def __init__(self, session_manager):
        """Initialize with session manager."""
        self.session_manager = session_manager
    
    async def send_message(self, chat_id: int, message: str) -> Optional[int]:
        """Send message to chat and return message ID."""
        try:
            if not await self.session_manager.is_authenticated():
                raise AuthenticationError("Not authenticated")
                
            entity = await self.session_manager.client.get_entity(chat_id)
            # Check if message contains HTML tags and set parse_mode accordingly
            parse_mode = 'html' if ('<' in message and '>' in message) else None
            sent_message = await self.session_manager.client.send_message(entity, message, parse_mode=parse_mode)
            
            return sent_message.id
            
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            raise TelegramClientError(f"Send message failed: {e}")
    
    async def get_messages(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages from chat."""
        try:
            if not await self.session_manager.is_authenticated():
                raise AuthenticationError("Not authenticated")
                
            entity = await self.session_manager.client.get_entity(chat_id)
            messages = await self.session_manager.client.get_messages(entity, limit=limit)
            
            result = []
            for msg in messages:
                result.append(self._format_message(msg))
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to get messages from {chat_id}: {e}")
            return []
    
    async def get_messages_raw(self, entity, limit: int = 100, offset_date=None, reverse: bool = False):
        """Get raw messages for statistics collection."""
        try:
            if not await self.session_manager.is_authenticated():
                raise AuthenticationError("Not authenticated")
                
            return await self.session_manager.client.get_messages(
                entity, 
                limit=limit, 
                offset_date=offset_date, 
                reverse=reverse
            )
            
        except Exception as e:
            logger.error(f"Failed to get raw messages: {e}")
            return []
    
    async def iter_messages(self, entity, limit: int = None, offset_date=None, reverse: bool = False) -> AsyncGenerator[Any, None]:
        """Iterate over messages for compatibility with StatisticsCollector."""
        try:
            if not await self.session_manager.is_authenticated():
                raise AuthenticationError("Not authenticated")
                
            async for message in self.session_manager.client.iter_messages(
                entity, 
                limit=limit, 
                offset_date=offset_date, 
                reverse=reverse
            ):
                yield message
                
        except Exception as e:
            logger.error(f"Failed to iterate messages: {e}")
            return
    
    def _format_message(self, msg) -> Dict[str, Any]:
        """Format message to consistent structure."""
        return {
            'id': msg.id,
            'text': msg.text or '',
            'sender_id': msg.sender_id,
            'date': msg.date,
            'is_reply': msg.is_reply,
            'media': msg.media is not None
        } 