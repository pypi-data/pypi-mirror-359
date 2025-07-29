"""
Output formatting utilities for session commands.

This module handles all output formatting operations.
Single Responsibility: Formatting and displaying session-related information.
"""

from typing import Dict, Any
from ...utils.output import success, info, print_table


class OutputFormatter:
    """Handles output formatting for session operations."""
    
    @staticmethod
    def print_session_help() -> None:
        """Print session commands help information."""
        print("""
TgStatTools - Session Management Commands

Available commands:
  generate-session    Generate new Telegram session (interactive)
  test-connection     Test current Telegram connection
  
Environment variables required:
  TELEGRAM_API_ID     Your Telegram API ID
  TELEGRAM_API_HASH   Your Telegram API hash

Get your API credentials at: https://my.telegram.org/apps
""")
    
    @staticmethod
    def print_session_info(session_name: str, session_dir: str, user: Dict[str, Any], 
                          test_result: Dict[str, Any]) -> None:
        """Print detailed session information after successful creation."""
        success(f"🎉 Session generation complete! Found {test_result['stats']['total_chats']} accessible chats")
        
        print("\n📋 Session Information:")
        session_info = {
            "Session Name": session_name,
            "Session File": f"{session_dir}/{session_name}.session",
            "User ID": str(user['id']),
            "Name": f"{user['first_name']} {user.get('last_name', '')}".strip(),
            "Username": f"@{user.get('username', 'N/A')}",
            "Phone": user.get('phone', 'N/A'),
            "Premium": "Yes" if user.get('is_premium') else "No",
            "Total Chats": str(test_result['stats']['total_chats']),
            "Groups": str(test_result['stats']['groups']),
            "Channels": str(test_result['stats']['channels']),
            "Supergroups": str(test_result['stats']['supergroups']),
            "Users": str(test_result['stats']['users'])
        }
        print_table(session_info, headers=["Property", "Value"])
    
    @staticmethod
    def print_connection_test_results(test_result: Dict[str, Any]) -> None:
        """Print connection test results."""
        if test_result['success']:
            success("✅ Connection test successful!")
            
            stats = test_result['stats']
            print(f"\n📊 Chat Statistics:")
            print(f"  Total accessible chats: {stats['total_chats']}")
            print(f"  Groups: {stats['groups']}")
            print(f"  Channels: {stats['channels']}")
            print(f"  Supergroups: {stats['supergroups']}")
            print(f"  Users: {stats['users']}")
            
            if test_result.get('chats'):
                print(f"\n💬 Sample chats (showing first {len(test_result['chats'])}):")
                for chat in test_result['chats']:
                    chat_type = chat.get('type', 'Unknown')
                    member_count = f" ({chat['members_count']} members)" if chat.get('members_count') else ""
                    print(f"  • {chat['title']} [{chat_type}]{member_count}")
        else:
            print(f"❌ Connection test failed: {test_result.get('error', 'Unknown error')}")
    
    @staticmethod
    def print_user_authentication_success(user: Dict[str, Any]) -> None:
        """Print user authentication success message."""
        success(f"✅ Successfully authenticated as {user['first_name']} (@{user.get('username', 'N/A')})")
    
    @staticmethod
    def print_existing_session_info(user_info: Dict[str, Any]) -> None:
        """Print information about existing session."""
        success(f"Session already exists and authenticated as {user_info['first_name']} (@{user_info.get('username', 'N/A')})") 