"""
Message formatting for template processing.

This module handles formatting filtered statistics data into
text and JSON formats according to template specifications.
"""

import json
import logging
from typing import Dict, Any, List
from .data_models import StatisticsData

logger = logging.getLogger(__name__)


class MessageFormatter:
    """Handles formatting statistics data into various output formats."""
    
    def format_statistics(self, data: StatisticsData, template: Dict[str, Any], 
                         user_group: str = None, monitoring_group: str = None) -> str:
        """Format statistics data using specified template."""
        logger.debug(f"Formatting statistics data as text")
        
        formatting = template['formatting']
        options = template['options']
        
        # Start building the message
        output = []
        
        # Header
        output.append(formatting['header'].format(date=data.date))
        
        # Total messages
        output.append(formatting['total'].format(total_messages=data.total_messages))
        
        # User group header (if template supports it)
        if 'user_group_header' in formatting and user_group:
            output.append(formatting['user_group_header'].format(user_group=user_group))
        
        # Users section
        if data.users:
            output.append(formatting['user_section_header'])
            
            for user in data.users:
                if options['show_percentages']:
                    # Process percentage formatting
                    percentage = user.percentage
                    if options['round_percentages']:
                        percentage = round(percentage, options['round_percentages'])
                    
                    line = formatting['user_line'].format(
                        name=user.name,
                        messages=user.messages,
                        percentage=percentage
                    )
                else:
                    # Format without percentage
                    line = formatting['user_line'].format(
                        name=user.name,
                        messages=user.messages,
                        percentage=0  # Fallback, template should handle this
                    )
                
                output.append(line)
        
        # Chats section
        if data.chats:
            # Use provided monitoring_group or fallback to data
            mg_name = monitoring_group or (data.monitoring_groups_used[0] if data.monitoring_groups_used else "All")
            if mg_name == "all":
                mg_name = "All"
            
            output.append(formatting['chat_section_header'].format(monitoring_group=mg_name))
            
            for chat in data.chats:
                if options['show_percentages']:
                    # Process percentage formatting
                    percentage = chat.percentage
                    if options['round_percentages']:
                        percentage = round(percentage, options['round_percentages'])
                    
                    line = formatting['chat_line'].format(
                        title=chat.title,
                        messages=chat.messages,
                        percentage=percentage
                    )
                else:
                    # Format without percentage
                    line = formatting['chat_line'].format(
                        title=chat.title,
                        messages=chat.messages,
                        percentage=0  # Fallback, template should handle this
                    )
                
                output.append(line)
        
        # Join all parts
        result = ''.join(output)
        
        # Check message length limits for Telegram
        if options.get('telegram_formatting', True):
            max_length = options.get('max_message_length', 4096)
            if len(result) > max_length:
                logger.warning(f"Formatted message length ({len(result)}) exceeds limit ({max_length})")
                # For now, just truncate - could implement smart splitting later
                result = result[:max_length-3] + "..."
        
        return result
    
    def format_as_json(self, data: StatisticsData, template_name: str) -> str:
        """Format statistics data as JSON."""
        logger.debug(f"Formatting statistics data as JSON")
        
        # Convert to JSON-serializable format
        json_data = {
            "date": data.date,
            "total_messages": data.total_messages,
            "collection_completed_at": data.collection_completed_at,
            "monitoring_groups_used": data.monitoring_groups_used,
            "template_used": template_name,
            "users": [
                {
                    "user_id": user.user_id,
                    "name": user.name,
                    "messages": user.messages,
                    "percentage": round(user.percentage, 2)
                }
                for user in data.users
            ],
            "chats": [
                {
                    "chat_id": chat.chat_id,
                    "title": chat.title,
                    "messages": chat.messages,
                    "percentage": round(chat.percentage, 2)
                }
                for chat in data.chats
            ]
        }
        
        return json.dumps(json_data, indent=2, ensure_ascii=False)
    
    def split_long_message(self, message: str, max_length: int = 4096) -> List[str]:
        """Split long message into chunks for Telegram."""
        if len(message) <= max_length:
            return [message]
        
        chunks = []
        lines = message.split('\n')
        current_chunk = ""
        
        for line in lines:
            # If adding this line would exceed the limit
            if len(current_chunk + line + '\n') > max_length:
                if current_chunk:
                    chunks.append(current_chunk.rstrip())
                    current_chunk = line + '\n'
                else:
                    # Single line is too long, force split
                    chunks.append(line[:max_length-3] + "...")
                    current_chunk = ""
            else:
                current_chunk += line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk.rstrip())
        
        return chunks 