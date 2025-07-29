"""
CLI handlers for session commands.

This module handles command-line interface for session management.
Single Responsibility: Processing CLI commands and coordinating services.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any
from ...utils.output import info, warning, error, success
from ...core.config_manager import get_env_value
from ...core.telegram import create_client, TELETHON_AVAILABLE
from .session_auth_service import SessionAuthService
from .connection_tester import ConnectionTester
from .session_validator import SessionValidator
from .output_formatter import OutputFormatter

logger = logging.getLogger(__name__)


def register_commands(subparsers) -> None:
    """Register session-related commands."""
    # Generate session command
    generate_parser = subparsers.add_parser(
        'generate-session',
        help='Generate new Telegram session (interactive)'
    )
    generate_parser.add_argument(
        '--session-name',
        default='tgstattools_session',
        help='Name for the session file (default: tgstattools_session)'
    )
    generate_parser.set_defaults(func=handle_generate_session)
    
    # Test connection command
    test_parser = subparsers.add_parser(
        'test-connection',
        help='Test current Telegram connection'
    )
    test_parser.add_argument(
        '--session-name',
        default='tgstattools_session',
        help='Session name to test (default: tgstattools_session)'
    )
    test_parser.add_argument(
        '--list-chats',
        action='store_true',
        help='List accessible chats during test'
    )
    test_parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum number of chats to check (default: 50)'
    )
    test_parser.set_defaults(func=handle_test_connection)


def handle_generate_session(args) -> int:
    """
    Handle generate-session command.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code
    """
    if not TELETHON_AVAILABLE:
        error("Telethon not installed. Install with: pip install telethon")
        return 1
    
    try:
        return asyncio.run(_generate_session_async(args))
    except KeyboardInterrupt:
        warning("\nSession generation cancelled by user")
        return 1
    except Exception as e:
        error(f"Session generation failed: {e}")
        logger.exception("Session generation error")
        return 1


def handle_test_connection(args) -> int:
    """
    Handle test-connection command.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code
    """
    if not TELETHON_AVAILABLE:
        error("Telethon not installed. Install with: pip install telethon")
        return 1
    
    try:
        return asyncio.run(_test_connection_async(args))
    except KeyboardInterrupt:
        warning("\nConnection test cancelled by user")
        return 1
    except Exception as e:
        error(f"Connection test failed: {e}")
        logger.exception("Connection test error")
        return 1


async def _generate_session_async(args) -> int:
    """Generate session asynchronously."""
    info("🔐 Starting Telegram session generation...")
    
    # Load environment variables
    api_credentials = _load_api_credentials()
    if not api_credentials:
        return 1
    
    # Session configuration
    session_name = getattr(args, 'session_name', 'tgstattools_session')
    session_dir = Path("data/sessions")
    
    info(f"Session will be saved as: {session_dir / session_name}.session")
    
    # Create authentication service
    auth_service = SessionAuthService(
        api_credentials['api_id'], 
        api_credentials['api_hash']
    )
    
    # Create session
    result = await auth_service.create_new_session(session_name, str(session_dir))
    
    if result["success"]:
        # Print session information
        output_formatter = OutputFormatter()
        output_formatter.print_session_info(
            session_name, 
            str(session_dir), 
            result["user"], 
            result["test_result"]
        )
        return 0
    else:
        error(f"Session generation failed: {result['error']}")
        return 1


async def _test_connection_async(args) -> int:
    """Test connection asynchronously."""
    info("🔍 Testing Telegram connection...")
    
    # Load environment variables
    api_credentials = _load_api_credentials()
    if not api_credentials:
        return 1
    
    # Session configuration
    session_name = getattr(args, 'session_name', 'tgstattools_session')
    session_dir = Path("data/sessions")
    limit = getattr(args, 'limit', 50)
    list_chats = getattr(args, 'list_chats', False)
    
    # Validate session exists
    if not SessionValidator.is_session_valid(session_name, str(session_dir)):
        error(f"Session '{session_name}' not found or invalid")
        error("Run 'generate-session' first to create a session")
        return 1
    
    # Create client and test connection
    client = create_client(
        api_credentials['api_id'], 
        api_credentials['api_hash'], 
        session_name, 
        str(session_dir)
    )
    
    try:
        await client.connect()
        
        if not await client.is_authenticated():
            error("Session is not authenticated")
            error("Run 'generate-session' to create a new authenticated session")
            return 1
        
        # Perform connection test
        test_result = await ConnectionTester.perform_connection_test(
            client, 
            limit=limit, 
            list_chats=list_chats
        )
        
        # Display results
        output_formatter = OutputFormatter()
        output_formatter.print_connection_test_results(test_result)
        
        return 0 if test_result["success"] else 1
        
    finally:
        await client.disconnect()


def _load_api_credentials() -> dict:
    """Load API credentials from environment."""
    # Load environment variables from .env file
    from dotenv import load_dotenv
    env_file = Path("config/.env")
    if env_file.exists():
        load_dotenv(env_file)
    
    # Get API credentials
    api_id = get_env_value('TELEGRAM_API_ID')
    api_hash = get_env_value('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        error("Telegram API credentials not found in environment")
        print("\nTo get your API credentials:")
        print("1. Go to https://my.telegram.org/apps")
        print("2. Create a new application")
        print("3. Add TELEGRAM_API_ID and TELEGRAM_API_HASH to your .env file")
        return None
    
    return {
        'api_id': api_id,
        'api_hash': api_hash
    } 