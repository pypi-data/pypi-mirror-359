"""
Chat statistics collection module for TgStatTools.

This module handles collecting message statistics from individual Telegram chats,
with specialized logic for different chat types and media group deduplication.
"""

import logging
from typing import Dict, Any, Set
from datetime import datetime, date, timedelta
from telethon.tl.types import Channel
from telethon.errors import ChatAdminRequiredError, ChannelPrivateError

logger = logging.getLogger(__name__)


class ChatCollector:
    """Collects statistics from individual Telegram chats."""
    
    def __init__(self, telegram_client):
        """Initialize chat collector with Telegram client."""
        self.telegram_client = telegram_client
        self.logger = logging.getLogger(__name__)
    
    async def collect_chat_statistics(self, chat_id: int, chat_title: str, 
                                     target_date: date) -> Dict[str, Any]:
        """
        Collect statistics from a single chat.
        
        Args:
            chat_id: ID of the chat to collect statistics from
            chat_title: Title of the chat for logging
            target_date: Date to collect statistics for
            
        Returns:
            Dictionary containing:
                - users: Dict mapping user IDs to message counts
                - message_count: Total number of messages
                - media_groups: Number of media groups processed
                - success: Whether collection was successful
                - chat_type: Type of the chat (regular, channel, megagroup)
        """
        user_messages = {}
        message_count = 0
        media_groups_seen = set()
        chat_type = "unknown"
        
        # Calculate date range for the target date
        start_date = datetime.combine(target_date, datetime.min.time())
        end_date = datetime.combine(target_date, datetime.max.time())
        
        self.logger.info(f"Starting collection from chat {chat_id} ({chat_title}) for {target_date}")
        
        try:
            # Get entity and determine chat type
            entity = await self._get_chat_entity(chat_id, chat_title)
            chat_type = self._determine_chat_type(entity, chat_title)
            
            # Collect messages based on chat type
            messages = await self._collect_messages_by_type(entity, chat_type, chat_title, 
                                                          start_date, end_date)
            
            # Process messages for statistics
            user_messages, message_count, media_groups_seen = self._process_messages(
                messages, start_date, end_date
            )
            
            self.logger.info(
                f"Successfully collected from {chat_title}:"
                f"\n - Chat type: {chat_type}"
                f"\n - Total messages: {message_count}"
                f"\n - Unique users: {len(user_messages)}"
                f"\n - Media groups: {len(media_groups_seen)}"
            )
            
            return {
                "users": user_messages,
                "message_count": message_count,
                "media_groups": len(media_groups_seen),
                "success": True,
                "chat_type": chat_type
            }
            
        except Exception as e:
            self.logger.error(
                f"Failed to collect from {chat_title}:"
                f"\n - Error type: {type(e).__name__}"
                f"\n - Error message: {str(e)}"
            )
            return {
                "users": {},
                "message_count": 0,
                "media_groups": 0,
                "success": False,
                "chat_type": chat_type,
                "error": str(e)
            }
    
    async def _get_chat_entity(self, chat_id: int, chat_title: str):
        """Get chat entity with proper error handling."""
        try:
            entity = await self.telegram_client.get_entity(chat_id)
            self.logger.info(
                f"Successfully got entity for {chat_title}:"
                f"\n - Type: {type(entity)}"
                f"\n - ID: {entity.id}"
                f"\n - Access Hash: {getattr(entity, 'access_hash', 'N/A')}"
            )
            return entity
        except ValueError as e:
            self.logger.error(f"Invalid chat ID format for {chat_title}: {e}")
            raise
        except (ChatAdminRequiredError, ChannelPrivateError) as e:
            self.logger.error(f"Access error for {chat_title}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get entity for {chat_title}: {e}")
            raise
    
    def _determine_chat_type(self, entity, chat_title: str) -> str:
        """Determine the type of chat based on entity."""
        if isinstance(entity, Channel):
            if entity.megagroup:
                self.logger.info(f"Entity {chat_title} is a megagroup (supergroup)")
                return "megagroup"
            else:
                self.logger.info(f"Entity {chat_title} is a broadcast channel")
                return "channel"
        else:
            self.logger.info(f"Entity {chat_title} is a regular chat")
            return "chat"
    
    async def _collect_messages_by_type(self, entity, chat_type: str, chat_title: str,
                                       start_date: datetime, end_date: datetime) -> list:
        """Collect messages using appropriate method based on chat type."""
        if chat_type == "megagroup":
            return await self._collect_megagroup_messages(entity, chat_title, start_date, end_date)
        else:
            return await self._collect_standard_messages(entity, chat_title, end_date)
    
    async def _collect_megagroup_messages(self, entity, chat_title: str, 
                                         start_date: datetime, end_date: datetime) -> list:
        """Collect messages from megagroup with specialized logic."""
        try:
            messages = []
            
            # ИСПРАВЛЕНО: Правильная логика сбора сообщений
            # Начинаем со следующего дня после целевой даты и идем назад
            next_day = datetime.combine(end_date.date(), datetime.min.time()) + timedelta(days=1)
            
            async for message in self.telegram_client.iter_messages(
                entity,
                offset_date=next_day,  # Начинаем со следующего дня
                reverse=False,  # Идем от новых к старым (НЕ reverse!)
                limit=None  # No limit for megagroups
            ):
                message_date = message.date.replace(tzinfo=None)
                
                # Если сообщение старше начала целевого дня - прекращаем поиск
                if message_date < start_date:
                    break
                    
                # Если сообщение в пределах целевого дня - добавляем
                if start_date <= message_date <= end_date:
                    messages.append(message)
                    
                    # Log progress every 100 messages
                    if len(messages) % 100 == 0:
                        self.logger.debug(f"Collected {len(messages)} messages from {chat_title} for {end_date.date()}")
            
            self.logger.info(f"Collected {len(messages)} messages from megagroup {chat_title} for {end_date.date()}")
            return messages
            
        except Exception as e:
            self.logger.error(f"Error fetching messages from megagroup {chat_title}: {e}")
            raise
    
    async def _collect_standard_messages(self, entity, chat_title: str, end_date: datetime) -> list:
        """Collect messages from regular chat or channel."""
        
        # ИСПРАВЛЕНО: Увеличиваем лимит для лучшего покрытия
        # И начинаем со следующего дня для правильной фильтрации
        next_day = datetime.combine(end_date.date(), datetime.min.time()) + timedelta(days=1)
        
        messages = await self.telegram_client.get_messages_raw(
            entity,
            limit=1000,  # Увеличиваем лимит для лучшего покрытия
            offset_date=next_day,  # Начинаем со следующего дня
            reverse=False  # От новых к старым
        )
        
        self.logger.info(f"Retrieved {len(messages)} messages from standard chat {chat_title} for filtering")
        return messages
    
    def _process_messages(self, messages: list, start_date: datetime, end_date: datetime) -> tuple:
        """
        Process messages to extract statistics with media group deduplication.
        
        Returns:
            Tuple of (user_messages, message_count, media_groups_seen)
        """
        user_messages = {}
        message_count = 0
        media_groups_seen = set()
        
        self.logger.info(f"Processing {len(messages)} messages")
        
        for message in messages:
            # Check message date
            message_date = message.date.replace(tzinfo=None)
            if message_date < start_date or message_date > end_date:
                continue
                
            # Skip service messages
            if not message.sender_id:
                continue
                
            # Handle media groups (deduplication)
            if message.grouped_id:
                if message.grouped_id in media_groups_seen:
                    continue  # Skip duplicate from same media group
                media_groups_seen.add(message.grouped_id)
            
            # Update user message count
            if message.sender_id not in user_messages:
                user_messages[message.sender_id] = 0
            user_messages[message.sender_id] += 1
            message_count += 1
        
        return user_messages, message_count, media_groups_seen 