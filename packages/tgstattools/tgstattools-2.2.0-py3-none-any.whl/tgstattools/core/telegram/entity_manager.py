"""
Entity management functionality for Telegram client.

This module provides:
- Entity resolution (users, chats, channels)
- Dialog management and iteration
- Chat information retrieval
- Entity type detection and formatting
"""

import logging
from typing import Dict, Any, List, Optional, AsyncGenerator

logger = logging.getLogger(__name__)

# Check if Telethon is available
try:
    from telethon.tl.types import Channel, Chat, User
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    # Define dummy classes to prevent import errors
    class Channel: pass
    class Chat: pass
    class User: pass


class AuthenticationError(Exception):
    """Authentication related errors."""
    pass


class EntityManager:
    """Manages Telegram entities (users, chats, channels)."""
    
    def __init__(self, session_manager):
        """Initialize with session manager."""
        self.session_manager = session_manager
    
    async def get_entity(self, entity_id):
        """Get entity by ID for compatibility with StatisticsCollector."""
        try:
            if not await self.session_manager.is_authenticated():
                raise AuthenticationError("Not authenticated")
                
            return await self.session_manager.client.get_entity(entity_id)
            
        except Exception as e:
            logger.error(f"Failed to get entity {entity_id}: {e}")
            raise
    
    async def resolve_chat_entity(self, chat_id: int, chat_title: str = None):
        """Resolve chat entity by ID or title."""
        try:
            return await self.session_manager.client.get_entity(chat_id)
        except Exception as e:
            if chat_title:
                async for dialog in self.session_manager.client.iter_dialogs():
                    if dialog.name.strip() == chat_title.strip():
                        return dialog.entity
            raise ValueError(f"❌ Не удалось найти чат: {chat_title or chat_id}")
    
    async def get_chat_info(self, chat_id: int, chat_title: str = None) -> Optional[Dict[str, Any]]:
        """Get chat information."""
        try:
            entity = await self.resolve_chat_entity(chat_id, chat_title)
            if not entity:
                return None
                
            return self._format_entity_info(entity)
        except Exception as e:
            logger.error(f"Failed to get chat info: {e}")
            return None
    
    async def test_chat_access(self, chat_id: int) -> bool:
        """Test if we can access the specified chat."""
        try:
            if not await self.session_manager.is_authenticated():
                return False
                
            entity = await self.session_manager.client.get_entity(chat_id)
            return entity is not None
            
        except Exception as e:
            logger.warning(f"Cannot access chat {chat_id}: {e}")
            return False
    
    async def get_dialogs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of user dialogs."""
        try:
            if not await self.session_manager.is_authenticated():
                raise AuthenticationError("Not authenticated")
                
            dialogs = []
            async for dialog in self.session_manager.client.iter_dialogs(limit=limit):
                entity = dialog.entity
                
                dialog_info = self._format_entity_info(entity)
                dialog_info.update({
                    'unread_count': dialog.unread_count,
                    'is_pinned': dialog.pinned
                })
                
                dialogs.append(dialog_info)
                
            return dialogs
            
        except Exception as e:
            logger.error(f"Failed to get dialogs: {e}")
            return []
    
    async def iter_dialogs(self, limit: int = None) -> AsyncGenerator[Any, None]:
        """Iterate over dialogs for compatibility with StatisticsCollector."""
        try:
            if not await self.session_manager.is_authenticated():
                raise AuthenticationError("Not authenticated")
                
            async for dialog in self.session_manager.client.iter_dialogs(limit=limit):
                yield dialog
                
        except Exception as e:
            logger.error(f"Failed to iterate dialogs: {e}")
            return
    
    def _format_entity_info(self, entity) -> Dict[str, Any]:
        """Format entity information to consistent structure."""
        base_info = {
            'id': entity.id,
            'title': self._get_entity_title(entity),
            'type': self._get_entity_type(entity),
            'username': getattr(entity, 'username', None),
            'is_private': isinstance(entity, User),
            'is_channel': isinstance(entity, Channel),
            'is_group': isinstance(entity, Chat)
        }
        
        # Additional info for groups/channels
        if isinstance(entity, (Channel, Chat)):
            base_info.update({
                'participants_count': getattr(entity, 'participants_count', None),
                'is_creator': getattr(entity, 'creator', False),
                'is_megagroup': getattr(entity, 'megagroup', False),
                'is_verified': getattr(entity, 'verified', False),
                'is_scam': getattr(entity, 'scam', False),
                'is_fake': getattr(entity, 'fake', False)
            })
        
        return base_info
    
    def _get_entity_title(self, entity) -> str:
        """Get entity title/name."""
        if hasattr(entity, 'title'):
            return entity.title
        else:
            return f"{entity.first_name or ''} {entity.last_name or ''}".strip()
    
    def _get_entity_type(self, entity) -> str:
        """Get entity type string."""
        if isinstance(entity, User):
            return "user" if not entity.bot else "bot"
        elif isinstance(entity, Channel):
            return "supergroup" if entity.megagroup else "channel"
        elif isinstance(entity, Chat):
            return "group"
        else:
            return "unknown" 