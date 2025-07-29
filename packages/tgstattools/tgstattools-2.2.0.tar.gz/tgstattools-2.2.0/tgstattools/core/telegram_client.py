"""
Telegram client wrapper for TgStatTools.

This module now delegates to the modular telegram architecture
for better maintainability while preserving backward compatibility.
"""

# Import everything from modular telegram for backward compatibility
from .telegram import (
    TelegramClientWrapper, TelegramClientLegacy, SessionManager,
    AuthManager, MessageHandler, EntityManager, create_client,
    TelegramClientError, AuthenticationError, RateLimitError, ConnectionError
)

# Import TELETHON_AVAILABLE for backward compatibility
from .telegram.session_manager import TELETHON_AVAILABLE

# Backward compatibility aliases
TelegramClient = TelegramClientWrapper

# Ensure all original classes are available
__all__ = [
    'TelegramClientWrapper',
    'TelegramClientLegacy', 
    'TelegramClient',  # Alias
    'SessionManager',
    'AuthManager',
    'MessageHandler', 
    'EntityManager',
    'create_client',
    'TELETHON_AVAILABLE',  # For backward compatibility
    # Exceptions
    'TelegramClientError',
    'AuthenticationError',
    'RateLimitError',
    'ConnectionError'
] 