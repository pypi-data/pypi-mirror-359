"""
Authentication management functionality for Telegram client.

This module provides:
- Phone number authentication
- Code verification
- Two-factor authentication (2FA) support
- User information retrieval
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Check if Telethon is available
try:
    from telethon.errors import (
        SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError,
        PhoneNumberInvalidError, FloodWaitError
    )
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    # Define dummy classes to prevent import errors
    class SessionPasswordNeededError(Exception): pass
    class PhoneCodeInvalidError(Exception): pass
    class PhoneCodeExpiredError(Exception): pass
    class PhoneNumberInvalidError(Exception): pass
    class FloodWaitError(Exception): pass


class AuthenticationError(Exception):
    """Authentication related errors."""
    pass


class RateLimitError(Exception):
    """Rate limit related errors."""
    pass


class AuthManager:
    """Manages Telegram authentication operations."""
    
    def __init__(self, session_manager):
        """Initialize with session manager."""
        self.session_manager = session_manager
        self._auth_data = {}
    
    async def authenticate_with_phone(self, phone: str) -> Dict[str, Any]:
        """Start phone authentication process."""
        try:
            await self.session_manager.ensure_connected()
                
            # Clean phone number
            phone = phone.strip().replace(' ', '').replace('-', '')
            if not phone.startswith('+'):
                phone = '+' + phone
                
            result = await self.session_manager.client.send_code_request(phone)
            
            # Store auth data for verification
            self._auth_data = {
                'phone': phone,
                'phone_code_hash': result.phone_code_hash
            }
            
            return {
                "status": "code_sent",
                "message": f"Verification code sent to {phone}",
                "phone_code_hash": result.phone_code_hash
            }
            
        except PhoneNumberInvalidError:
            raise AuthenticationError("Invalid phone number format")
        except FloodWaitError as e:
            raise RateLimitError(f"Rate limit exceeded. Try again in {e.seconds} seconds")
        except Exception as e:
            logger.error(f"Phone authentication failed: {e}")
            raise AuthenticationError(f"Failed to send code: {e}")
    
    async def verify_code(self, phone: str, phone_code_hash: str, code: str) -> Dict[str, Any]:
        """Verify authentication code."""
        try:
            # Clean code
            code = code.strip().replace(' ', '').replace('-', '')
            
            try:
                user = await self.session_manager.client.sign_in(
                    phone=phone,
                    code=code,
                    phone_code_hash=phone_code_hash
                )
                
                return {
                    "status": "authenticated",
                    "message": "Successfully authenticated",
                    "user": self._format_user_info(user)
                }
                
            except SessionPasswordNeededError:
                return {
                    "status": "password_required",
                    "message": "Two-factor authentication enabled. Password required."
                }
                
        except PhoneCodeInvalidError:
            raise AuthenticationError("Invalid verification code")
        except PhoneCodeExpiredError:
            raise AuthenticationError("Verification code expired")
        except Exception as e:
            logger.error(f"Code verification failed: {e}")
            raise AuthenticationError(f"Verification failed: {e}")
    
    async def verify_password(self, password: str) -> Dict[str, Any]:
        """Verify 2FA password."""
        try:
            user = await self.session_manager.client.sign_in(password=password)
            
            return {
                "status": "authenticated",
                "message": "Successfully authenticated with password",
                "user": self._format_user_info(user)
            }
            
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            raise AuthenticationError(f"Password verification failed: {e}")
    
    async def get_me(self) -> Optional[Dict[str, Any]]:
        """Get current user information."""
        try:
            if not await self.session_manager.is_authenticated():
                return None
                
            me = await self.session_manager.client.get_me()
            if not me:
                return None
                
            return self._format_user_info(me)
            
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None
    
    def _format_user_info(self, user) -> Dict[str, Any]:
        """Format user information to consistent structure."""
        return {
            'id': user.id,
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'username': user.username,
            'phone': user.phone,
            'is_premium': getattr(user, 'premium', False),
            'is_verified': getattr(user, 'verified', False)
        } 