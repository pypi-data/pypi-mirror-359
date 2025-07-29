"""
Session authentication service.

This module handles Telegram authentication process and session management.
Single Responsibility: Managing authentication flow and session creation.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from ...core.telegram import TelegramClientWrapper, create_client
from ...core.telegram.auth_manager import AuthenticationError, RateLimitError
from ...core.telegram.session_manager import ConnectionError as TelegramConnectionError
from .input_collector import InputCollector
from .output_formatter import OutputFormatter
from .connection_tester import ConnectionTester

logger = logging.getLogger(__name__)


class SessionAuthService:
    """Handles Telegram authentication and session management."""
    
    def __init__(self, api_id: str, api_hash: str):
        """
        Initialize authentication service.
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API hash
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.input_collector = InputCollector()
        self.output_formatter = OutputFormatter()
    
    async def create_new_session(self, session_name: str, session_dir: str) -> Dict[str, Any]:
        """
        Create new Telegram session with authentication.
        
        Args:
            session_name: Name for the session
            session_dir: Directory to store session
            
        Returns:
            Dictionary with creation results
        """
        result = {
            "success": False,
            "error": None,
            "user": None,
            "test_result": None
        }
        
        try:
            # Create session directory
            Path(session_dir).mkdir(parents=True, exist_ok=True)
            
            # Create client
            client = create_client(self.api_id, self.api_hash, session_name, session_dir)
            
            # Connect to Telegram
            await client.connect()
            
            # Check if already authenticated
            if await client.is_authenticated():
                user_info = await client.get_me()
                if user_info:
                    self.output_formatter.print_existing_session_info(user_info)
                    
                    # Ask if user wants to regenerate
                    if not self.input_collector.confirm("Do you want to regenerate the session?"):
                        # Test existing session
                        test_result = await ConnectionTester.perform_connection_test(client, limit=5)
                        result.update({
                            "success": True,
                            "user": user_info,
                            "test_result": test_result
                        })
                        return result
                    
                    # Regenerate session
                    await self._regenerate_session(client, session_name, session_dir)
            
            # Perform authentication
            auth_result = await self._perform_authentication(client)
            if not auth_result["success"]:
                result["error"] = auth_result["error"]
                return result
            
            # Test connection
            test_result = await ConnectionTester.perform_connection_test(client, limit=5)
            
            result.update({
                "success": True,
                "user": auth_result["user"],
                "test_result": test_result
            })
            
            return result
            
        except (AuthenticationError, RateLimitError, TelegramConnectionError) as e:
            result["error"] = str(e)
            return result
        except Exception as e:
            logger.exception("Session creation failed")
            result["error"] = f"Unexpected error: {e}"
            return result
    
    async def _regenerate_session(self, client: TelegramClientWrapper, 
                                 session_name: str, session_dir: str) -> None:
        """Regenerate existing session."""
        # Disconnect to start fresh
        await client.disconnect()
        
        # Remove existing session file
        session_path = Path(session_dir) / f"{session_name}.session"
        if session_path.exists():
            session_path.unlink()
            logger.info("Removed existing session file")
        
        # Reconnect with fresh session
        client = create_client(self.api_id, self.api_hash, session_name, session_dir)
        await client.connect()
    
    async def _perform_authentication(self, client: TelegramClientWrapper) -> Dict[str, Any]:
        """
        Perform the authentication process.
        
        Args:
            client: Telegram client wrapper
            
        Returns:
            Dictionary with authentication results
        """
        result = {
            "success": False,
            "error": None,
            "user": None
        }
        
        try:
            # Get phone number
            phone_number = self.input_collector.get_phone_number()
            
            # Send verification code
            auth_result = await client.authenticate_with_phone(phone_number)
            
            if auth_result['status'] != 'code_sent':
                result["error"] = f"Failed to send code: {auth_result.get('message', 'Unknown error')}"
                return result
            
            # Get verification code
            code = self.input_collector.get_verification_code()
            
            # Verify code
            verify_result = await client.verify_code(
                phone_number, 
                auth_result['phone_code_hash'], 
                code
            )
            
            # Handle 2FA if required
            if verify_result['status'] == 'password_required':
                password = self.input_collector.get_2fa_password()
                verify_result = await client.verify_password(password)
            
            # Check final authentication result
            if verify_result['status'] == 'authenticated':
                user = verify_result['user']
                self.output_formatter.print_user_authentication_success(user)
                
                result.update({
                    "success": True,
                    "user": user
                })
            else:
                result["error"] = f"Authentication failed: {verify_result.get('message', 'Unknown error')}"
            
            return result
            
        except Exception as e:
            logger.exception("Authentication process failed")
            result["error"] = f"Authentication error: {e}"
            return result 