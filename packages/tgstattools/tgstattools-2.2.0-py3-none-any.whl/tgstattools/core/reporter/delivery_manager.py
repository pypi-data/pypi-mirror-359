"""
Report delivery management for TgStatTools.

This module handles the actual delivery of formatted reports to
Telegram chats, including message chunking and retry logic.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from ..template_processor import TemplateProcessor
from ..telegram_client import TelegramClient

logger = logging.getLogger(__name__)


class ReportDeliveryError(Exception):
    """Report delivery related errors."""
    pass


class DeliveryManager:
    """Handles report delivery to Telegram chats."""
    
    def __init__(self, 
                 template_processor: TemplateProcessor,
                 telegram_client: Optional[TelegramClient] = None):
        """Initialize delivery manager."""
        self.template_processor = template_processor
        self.telegram_client = telegram_client
        
    async def deliver_report(self, report_content: str, target_chat_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """Deliver report to list of chat IDs."""
        if not self.telegram_client:
            raise ReportDeliveryError("Telegram client not configured")
        
        logger.debug(f"Delivering report to {len(target_chat_ids)} chats")
        
        delivery_results = {}
        
        # Split long messages if needed
        message_chunks = self.template_processor.split_long_message(report_content)
        logger.debug(f"Report split into {len(message_chunks)} chunks")
        
        for chat_id in target_chat_ids:
            logger.debug(f"Sending report to chat {chat_id}")
            
            try:
                # Send all chunks for this chat
                chunk_results = []
                for i, chunk in enumerate(message_chunks):
                    try:
                        message_id = await self._send_message(chat_id, chunk)
                        chunk_results.append({
                            "chunk": i + 1,
                            "success": True,
                            "message_id": message_id
                        })
                        
                        # Small delay between chunks to avoid rate limiting
                        if len(message_chunks) > 1 and i < len(message_chunks) - 1:
                            await asyncio.sleep(0.5)
                            
                    except Exception as e:
                        logger.error(f"Failed to send chunk {i+1} to chat {chat_id}: {e}")
                        chunk_results.append({
                            "chunk": i + 1,
                            "success": False,
                            "error": str(e)
                        })
                
                # Determine overall success for this chat
                successful_chunks = sum(1 for r in chunk_results if r["success"])
                overall_success = successful_chunks == len(message_chunks)
                
                delivery_results[chat_id] = {
                    "success": overall_success,
                    "chunks_sent": successful_chunks,
                    "total_chunks": len(message_chunks),
                    "chunk_details": chunk_results
                }
                
                if overall_success:
                    logger.debug(f"Successfully delivered report to chat {chat_id}")
                else:
                    logger.warning(f"Partial delivery to chat {chat_id}: {successful_chunks}/{len(message_chunks)} chunks sent")
                
            except Exception as e:
                logger.error(f"Failed to deliver report to chat {chat_id}: {e}")
                delivery_results[chat_id] = {
                    "success": False,
                    "error": str(e),
                    "chunks_sent": 0,
                    "total_chunks": len(message_chunks)
                }
        
        return delivery_results
    
    async def _send_message(self, chat_id: int, message: str, retry_count: int = 3) -> int:
        """Send single message to chat with retry logic."""
        last_error = None
        
        for attempt in range(retry_count):
            try:
                # Use telegram client to send message
                message_id = await self.telegram_client.send_message(chat_id, message)
                return message_id
                
            except Exception as e:
                last_error = e
                logger.warning(f"Send attempt {attempt + 1} failed for chat {chat_id}: {e}")
                
                if attempt < retry_count - 1:
                    # Exponential backoff
                    delay = 2 ** attempt
                    logger.debug(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
        
        # All attempts failed
        raise ReportDeliveryError(f"Failed to send message after {retry_count} attempts: {last_error}")
    
    async def test_delivery_connectivity(self, target_chat_ids: List[int]) -> Dict[str, Any]:
        """Test connectivity to all target chats."""
        logger.debug(f"Testing delivery connectivity to {len(target_chat_ids)} chats")
        
        if not self.telegram_client:
            return {"success": False, "error": "Telegram client not configured"}
        
        try:
            connectivity_results = {}
            accessible_count = 0
            
            for chat_id in target_chat_ids:
                try:
                    # Test if we can access the chat
                    is_accessible = await self.telegram_client.test_chat_access(chat_id)
                    connectivity_results[chat_id] = {
                        "accessible": is_accessible,
                        "error": None if is_accessible else "Chat not accessible"
                    }
                    
                    if is_accessible:
                        accessible_count += 1
                        
                except Exception as e:
                    connectivity_results[chat_id] = {
                        "accessible": False,
                        "error": str(e)
                    }
            
            return {
                "success": True,
                "total_chats": len(target_chat_ids),
                "accessible_chats": accessible_count,
                "inaccessible_chats": len(target_chat_ids) - accessible_count,
                "chat_details": connectivity_results
            }
            
        except Exception as e:
            logger.error(f"Failed to test delivery connectivity: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_test_message(self, chat_id: int, message: str) -> Dict[str, Any]:
        """Send test message to specific chat."""
        if not self.telegram_client:
            return {"success": False, "error": "Telegram client not configured"}
        
        try:
            message_id = await self._send_message(chat_id, message)
            return {
                "success": True,
                "chat_id": chat_id,
                "message_id": message_id,
                "message_length": len(message)
            }
        except Exception as e:
            logger.error(f"Failed to send test message to chat {chat_id}: {e}")
            return {
                "success": False,
                "chat_id": chat_id,
                "error": str(e)
            } 