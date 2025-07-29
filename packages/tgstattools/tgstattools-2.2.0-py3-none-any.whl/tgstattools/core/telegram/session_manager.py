"""
Session management functionality for Telegram client.

This module provides:
- Connection lifecycle management
- Session persistence and handling
- Connection state tracking
- Error handling for connection issues
"""

import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Check if Telethon is available
try:
    from telethon import TelegramClient as TelethonClient
    from telethon.sessions import StringSession
    from telethon.errors import RPCError, FloodWaitError, AuthKeyUnregisteredError
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    # Define dummy classes to prevent import errors
    class TelethonClient: pass
    class StringSession: pass
    class RPCError(Exception): pass
    class FloodWaitError(Exception): pass
    class AuthKeyUnregisteredError(Exception): pass


class ConnectionError(Exception):
    """Connection related errors."""
    pass


class SessionManager:
    """Manages Telegram session lifecycle and connections."""
    
    def __init__(self, api_id: str, api_hash: str, session_name: str, session_dir: str):
        """Initialize session manager."""
        if not TELETHON_AVAILABLE:
            raise ConnectionError("Telethon not available. Install with: pip install telethon")
            
        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.session_name = session_name
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Use file session for persistence
        session_file = self.session_dir / f"{session_name}.session"
        self._client = TelethonClient(str(session_file), self.api_id, self.api_hash)
        self._connected = False
        
    @property
    def client(self) -> TelethonClient:
        """Get underlying Telethon client."""
        return self._client
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected and self._client.is_connected()
    
    async def connect(self) -> None:
        """Connect to Telegram."""
        try:
            if not self._client.is_connected():
                await self._client.connect()
                self._connected = True
                logger.info("Connected to Telegram")
            else:
                logger.debug("Already connected to Telegram")
        except Exception as e:
            logger.error(f"Failed to connect to Telegram: {e}")
            raise ConnectionError(f"Connection failed: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from Telegram."""
        try:
            if self._client.is_connected():
                await self._client.disconnect()
                logger.info("Disconnected from Telegram")
            self._connected = False
        except Exception as e:
            logger.warning(f"Error during disconnect: {e}")
    
    async def ensure_connected(self) -> None:
        """Ensure connection is established."""
        if not self.is_connected:
            await self.connect()
    
    async def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        try:
            if not self.is_connected:
                return False
            return await self._client.is_user_authorized()
        except Exception as e:
            logger.warning(f"Authentication check failed: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """Get session statistics."""
        return {
            'connected': self.is_connected,
            'session_name': self.session_name,
            'api_id': self.api_id,
            'session_dir': str(self.session_dir)
        } 