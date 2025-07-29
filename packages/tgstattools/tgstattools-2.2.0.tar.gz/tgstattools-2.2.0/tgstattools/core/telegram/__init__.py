"""
Telegram client wrapper for TgStatTools.

This module provides a high-level interface for Telegram API operations
including message sending, chat access testing, and connection management.

The client is now modularized for better maintainability:
- session_manager: Connection lifecycle and session management
- auth_manager: Authentication and user management
- message_handler: Message operations and iteration
- entity_manager: Entity resolution and chat management
"""

import logging
from typing import Optional, Dict, Any, List

from .session_manager import SessionManager, ConnectionError
from .auth_manager import AuthManager, AuthenticationError, RateLimitError
from .message_handler import MessageHandler, TelegramClientError
from .entity_manager import EntityManager

logger = logging.getLogger(__name__)


class TelegramClientWrapper:
    """Wrapper for Telegram client operations with modular architecture."""
    
    def __init__(self, api_id: str, api_hash: str, session_name: str, session_dir: str):
        """Initialize wrapper with modular components."""
        # Initialize core session manager
        self.session_manager = SessionManager(api_id, api_hash, session_name, session_dir)
        
        # Initialize specialized managers
        self.auth_manager = AuthManager(self.session_manager)
        self.message_handler = MessageHandler(self.session_manager)
        self.entity_manager = EntityManager(self.session_manager)
        
        # Store configuration for statistics
        self.session_name = session_name
        self.api_id = int(api_id)
    
    # Connection Management (delegate to SessionManager)
    async def connect(self):
        """Connect to Telegram."""
        await self.session_manager.connect()
    
    async def disconnect(self):
        """Disconnect from Telegram."""
        await self.session_manager.disconnect()
    
    async def is_authenticated(self) -> bool:
        """Check if authenticated."""
        return await self.session_manager.is_authenticated()
    
    # Authentication (delegate to AuthManager)
    async def get_me(self) -> Optional[Dict[str, Any]]:
        """Get current user info."""
        return await self.auth_manager.get_me()
    
    async def authenticate_with_phone(self, phone: str) -> Dict[str, Any]:
        """Start phone authentication."""
        return await self.auth_manager.authenticate_with_phone(phone)
    
    async def verify_code(self, phone: str, phone_code_hash: str, code: str) -> Dict[str, Any]:
        """Verify authentication code."""
        return await self.auth_manager.verify_code(phone, phone_code_hash, code)
    
    async def verify_password(self, password: str) -> Dict[str, Any]:
        """Verify 2FA password."""
        return await self.auth_manager.verify_password(password)
    
    # Message Operations (delegate to MessageHandler)
    async def send_message(self, chat_id: int, message: str) -> Optional[int]:
        """Send message to chat and return message ID."""
        return await self.message_handler.send_message(chat_id, message)
    
    async def get_messages(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages from chat."""
        return await self.message_handler.get_messages(chat_id, limit)
    
    async def get_messages_raw(self, entity, limit: int = 100, offset_date=None, reverse: bool = False):
        """Get raw messages for statistics collection."""
        return await self.message_handler.get_messages_raw(entity, limit, offset_date, reverse)
    
    async def iter_messages(self, entity, limit: int = None, offset_date=None, reverse: bool = False):
        """Iterate over messages for compatibility with StatisticsCollector."""
        async for message in self.message_handler.iter_messages(entity, limit, offset_date, reverse):
            yield message
    
    # Entity Operations (delegate to EntityManager)
    async def get_entity(self, entity_id):
        """Get entity by ID for compatibility with StatisticsCollector."""
        return await self.entity_manager.get_entity(entity_id)
    
    async def resolve_chat_entity(self, chat_id: int, chat_title: str = None):
        """Resolve chat entity by ID or title."""
        return await self.entity_manager.resolve_chat_entity(chat_id, chat_title)
    
    async def get_chat_info(self, chat_id: int, chat_title: str = None) -> Optional[Dict[str, Any]]:
        """Get chat information."""
        return await self.entity_manager.get_chat_info(chat_id, chat_title)
    
    async def test_chat_access(self, chat_id: int) -> bool:
        """Test if we can access the specified chat."""
        return await self.entity_manager.test_chat_access(chat_id)
    
    async def get_dialogs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of user dialogs."""
        return await self.entity_manager.get_dialogs(limit)
    
    async def get_chats(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of chats (alias for get_dialogs for backward compatibility)."""
        return await self.entity_manager.get_dialogs(limit)
    
    async def iter_dialogs(self, limit: int = None):
        """Iterate over dialogs for compatibility with StatisticsCollector."""
        async for dialog in self.entity_manager.iter_dialogs(limit):
            yield dialog
    
    # Utility Methods
    def get_statistics(self) -> Dict[str, Any]:
        """Get client statistics."""
        session_stats = self.session_manager.get_statistics()
        return {
            **session_stats,
            'modular_architecture': True,
            'components': ['session_manager', 'auth_manager', 'message_handler', 'entity_manager']
        }


# Factory function for backward compatibility
def create_client(api_id: str, api_hash: str, session_name: str, session_dir: str) -> TelegramClientWrapper:
    """Create Telegram client wrapper."""
    return TelegramClientWrapper(api_id, api_hash, session_name, session_dir)


# Legacy class for compatibility (delegates to new architecture)
class TelegramClientLegacy:
    """Legacy wrapper for backward compatibility."""
    
    def __init__(self, api_id: str, api_hash: str, session_name: str = "tgstattools"):
        """Initialize Telegram client."""
        self.wrapper = TelegramClientWrapper(api_id, api_hash, session_name, "data/sessions")
        
    async def connect(self) -> None:
        """Connect to Telegram API."""
        await self.wrapper.connect()
        
    async def disconnect(self) -> None:
        """Disconnect from Telegram API."""
        await self.wrapper.disconnect()
    
    async def send_message(self, chat_id: int, message: str) -> int:
        """Send message to chat and return message ID."""
        result = await self.wrapper.send_message(chat_id, message)
        if result is None:
            raise TelegramClientError("Failed to send message")
        return result
    
    async def test_chat_access(self, chat_id: int) -> bool:
        """Test if we can access the specified chat."""
        return await self.wrapper.test_chat_access(chat_id)
    
    async def get_chat_info(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get information about a chat."""
        return await self.wrapper.get_chat_info(chat_id)
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Telegram API."""
        try:
            if not await self.wrapper.is_authenticated():
                return {
                    "success": False,
                    "error": "Not authenticated"
                }
            
            # Test getting user info
            user = await self.wrapper.get_me()
            if not user:
                return {
                    "success": False,
                    "error": "Failed to get user info"
                }
            
            return {
                "success": True,
                "connected": True,
                "user": user
            }
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Import TELETHON_AVAILABLE for backward compatibility
from .session_manager import TELETHON_AVAILABLE

# Backward compatibility exports
__all__ = [
    'TelegramClientWrapper',
    'TelegramClientLegacy', 
    'SessionManager',
    'AuthManager',
    'TELETHON_AVAILABLE', 
    'MessageHandler',
    'EntityManager',
    'create_client',
    # Exceptions
    'TelegramClientError',
    'AuthenticationError',
    'RateLimitError', 
    'ConnectionError'
]

# Alias for backward compatibility
TelegramClient = TelegramClientWrapper 