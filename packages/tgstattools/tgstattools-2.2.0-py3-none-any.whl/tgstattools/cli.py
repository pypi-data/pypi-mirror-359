"""
Main CLI interface for TgStatTools v2.0.

This module provides the console script entry point and command routing system.
All commands are organized into separate modules following single responsibility principle.
"""

import argparse
import sys
from typing import List, Optional

try:
    import colorama
    colorama.init(autoreset=True)
    from colorama import Fore, Style
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    
    # Fallback when colorama is not available
    class _Fore:
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        CYAN = ""
        WHITE = ""
    
    class _Style:
        BRIGHT = ""
        RESET_ALL = ""
    
    Fore = _Fore()
    Style = _Style()

from . import __version__
from .commands import (
    session_commands,
    database_commands,
    data_commands,
    config_commands,
    simple_commands,
)


def colored_print(message: str, color: str = "", style: str = "") -> None:
    """Print colored message if colors are available."""
    if COLORS_AVAILABLE:
        print(f"{color}{style}{message}{Style.RESET_ALL}")
    else:
        print(message)


def print_success(message: str) -> None:
    """Print success message in green."""
    colored_print(f"✓ {message}", Fore.GREEN, Style.BRIGHT)


def print_error(message: str) -> None:
    """Print error message in red."""
    colored_print(f"✗ {message}", Fore.RED, Style.BRIGHT)


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    colored_print(f"⚠ {message}", Fore.YELLOW, Style.BRIGHT)


def print_info(message: str) -> None:
    """Print info message in cyan."""
    colored_print(f"ℹ {message}", Fore.CYAN)


def create_main_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="tgstattools",
        description="TgStatTools v2.2 - Telegram chat statistics collection and reporting CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Session setup (2 commands)
  tgstattools generate-session         # Setup Telegram session
  tgstattools test-connection          # Test Telegram connection
  
  # Database operations (2 commands)
  tgstattools backup-db                # Create database backup
  tgstattools restore-db backup.db     # Restore from backup
  
  # Data collection and viewing (2 commands)
  tgstattools collect-previous-day     # Collect previous day stats
  tgstattools view-data previous-day   # View collected statistics
  tgstattools view-data previous-month --send-to testReportChats  # Send monthly report
  
  # Configuration (1 command)
  tgstattools validate-config          # Validate configurations
  
TOTAL: 7 essential commands only - simplified architecture

For detailed help on any command:
  tgstattools <command> --help
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"TgStatTools v{__version__}"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="<command>"
    )
    
    # Register essential command modules only
    session_commands.register_commands(subparsers)
    database_commands.register_commands(subparsers)
    data_commands.register_commands(subparsers)
    config_commands.register_commands(subparsers)
    simple_commands.register_simple_commands(subparsers)
    
    return parser


def handle_command(args: argparse.Namespace) -> int:
    """Route command to appropriate handler and return exit code."""
    try:
        # Map commands to their handlers - minimal set only
        command_handlers = {
            # Session management (2 commands)
            "generate-session": session_commands.handle_generate_session,
            "test-connection": session_commands.handle_test_connection,
            
            # Database operations (2 commands)
            "backup-db": database_commands.handle_backup_db,
            "restore-db": database_commands.handle_restore_db,
            
            # Data viewing and collection (2 commands)
            "view-data": data_commands.handle_view_data,
            "collect-previous-day": simple_commands.handle_collect_previous_day,
            
            # Configuration management (1 command)
            "validate-config": config_commands.handle_validate_config,
        }
        
        if args.command in command_handlers:
            return command_handlers[args.command](args)
        else:
            print_error(f"Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print_warning("Operation interrupted by user")
        return 130
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = create_main_parser()
    
    # Parse arguments
    if argv is None:
        argv = sys.argv[1:]
    
    if not argv:
        parser.print_help()
        return 0
    
    args = parser.parse_args(argv)
    
    if args.command is None:
        parser.print_help()
        return 0
    
    return handle_command(args)


if __name__ == "__main__":
    sys.exit(main()) 