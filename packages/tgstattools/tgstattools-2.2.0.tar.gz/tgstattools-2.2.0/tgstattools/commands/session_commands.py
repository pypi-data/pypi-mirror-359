"""
Session management commands.

This module provides commands for managing Telegram sessions,
including session generation and connection testing.

REFACTORED: This module now uses the new modular structure following SRP principles.
All functionality has been split into separate modules with single responsibilities:

- session/cli_handlers.py: CLI command processing
- session/session_auth_service.py: Authentication logic
- session/connection_tester.py: Connection testing
- session/session_validator.py: Session validation  
- session/input_collector.py: User input handling
- session/output_formatter.py: Output formatting

This follows the Single Responsibility Principle where each module has one reason to change.
"""

import logging
from .session import register_commands, handle_generate_session, handle_test_connection
from .session.session_validator import SessionValidator
from .session.output_formatter import OutputFormatter

logger = logging.getLogger(__name__)

# Re-export main functions for backward compatibility
__all__ = [
    'register_commands',
    'handle_generate_session', 
    'handle_test_connection',
    'SessionValidator',
    'OutputFormatter'
]

# Legacy function for backward compatibility
def print_session_help():
    """Print session management help (legacy compatibility)."""
    OutputFormatter.print_session_help()

# Legacy functions for backward compatibility
def validate_session_file(session_path):
    """Validate session file (legacy compatibility)."""
    return SessionValidator.validate_session_file(session_path)

def get_session_info(session_name="tgstattools_session", session_dir="data/sessions"):
    """Get session info (legacy compatibility).""" 
    return SessionValidator.get_session_info(session_name, session_dir) 