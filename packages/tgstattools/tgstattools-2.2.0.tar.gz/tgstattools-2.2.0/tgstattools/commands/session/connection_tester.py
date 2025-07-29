"""
Connection testing utilities.

This module handles Telegram connection testing and chat discovery.
Single Responsibility: Testing connection and gathering chat statistics.
"""

import logging
from typing import Dict, Any, List
from ...core.telegram import TelegramClientWrapper

logger = logging.getLogger(__name__)


class ConnectionTester:
    """Handles Telegram connection testing and chat discovery."""
    
    @staticmethod
    async def perform_connection_test(client: TelegramClientWrapper, 
                                    limit: int = 50, 
                                    list_chats: bool = False) -> Dict[str, Any]:
        """
        Perform comprehensive connection test.
        
        Args:
            client: Telegram client wrapper
            limit: Maximum number of chats to retrieve
            list_chats: Whether to include chat list in results
            
        Returns:
            Dictionary with test results and statistics
        """
        result = {
            "success": False,
            "error": None,
            "stats": {
                "total_chats": 0,
                "groups": 0,
                "channels": 0,
                "supergroups": 0,
                "users": 0
            },
            "chats": []
        }
        
        try:
            # Test basic connection
            if not await client.is_authenticated():
                result["error"] = "Client is not authenticated"
                return result
            
            # Get user info to verify connection
            user_info = await client.get_me()
            if not user_info:
                result["error"] = "Could not retrieve user information"
                return result
            
            # Get chats with limit
            chats = await client.get_chats(limit=limit)
            
            if not chats:
                result["error"] = "No chats found or accessible"
                return result
            
            # Process chat statistics
            stats = ConnectionTester._calculate_chat_statistics(chats)
            result["stats"] = stats
            
            # Include chat list if requested
            if list_chats:
                result["chats"] = ConnectionTester._format_chat_list(chats)
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.exception("Connection test failed")
            result["error"] = str(e)
            return result
    
    @staticmethod
    def _calculate_chat_statistics(chats: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Calculate statistics from chat list.
        
        Args:
            chats: List of chat dictionaries
            
        Returns:
            Dictionary with chat type statistics
        """
        stats = {
            "total_chats": len(chats),
            "groups": 0,
            "channels": 0,
            "supergroups": 0,
            "users": 0
        }
        
        for chat in chats:
            chat_type = chat.get('type', '').lower()
            
            if chat_type == 'group':
                stats["groups"] += 1
            elif chat_type == 'channel':
                stats["channels"] += 1
            elif chat_type == 'supergroup':
                stats["supergroups"] += 1
            elif chat_type == 'user':
                stats["users"] += 1
        
        return stats
    
    @staticmethod
    def _format_chat_list(chats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format chat list for display.
        
        Args:
            chats: Raw chat list
            
        Returns:
            Formatted chat list with essential information
        """
        formatted_chats = []
        
        for chat in chats:
            formatted_chat = {
                "id": chat.get('id'),
                "title": chat.get('title', 'Unknown'),
                "type": chat.get('type', 'Unknown'),
                "members_count": chat.get('members_count')
            }
            
            # Add username for users
            if chat.get('type') == 'user' and chat.get('username'):
                formatted_chat["username"] = chat.get('username')
            
            formatted_chats.append(formatted_chat)
        
        return formatted_chats
    
    @staticmethod
    async def quick_connection_check(client: TelegramClientWrapper) -> bool:
        """
        Quick connection check without detailed statistics.
        
        Args:
            client: Telegram client wrapper
            
        Returns:
            True if connection is working, False otherwise
        """
        try:
            if not await client.is_authenticated():
                return False
            
            user_info = await client.get_me()
            return user_info is not None
            
        except Exception as e:
            logger.debug(f"Quick connection check failed: {e}")
            return False 