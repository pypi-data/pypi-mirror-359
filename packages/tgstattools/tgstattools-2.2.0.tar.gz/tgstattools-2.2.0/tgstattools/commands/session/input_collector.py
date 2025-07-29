"""
User input collection utilities.

This module handles all user input operations for session management.
Single Responsibility: Collecting and validating user input.
"""

import re
from typing import Optional
from ...utils.output import info, warning, error


class InputCollector:
    """Handles user input collection for session operations."""
    
    @staticmethod
    def get_phone_number() -> str:
        """Get phone number from user input with validation."""
        while True:
            phone = input("\n📞 Enter your phone number (with country code, e.g., +1234567890): ").strip()
            
            if not phone:
                warning("Phone number cannot be empty")
                continue
                
            # Basic phone number validation
            if not re.match(r'^\+?[1-9]\d{1,14}$', phone):
                warning("Invalid phone number format. Use international format (e.g., +1234567890)")
                continue
                
            # Ensure it starts with +
            if not phone.startswith('+'):
                phone = '+' + phone
                
            return phone
    
    @staticmethod
    def get_verification_code() -> str:
        """Get verification code from user input."""
        while True:
            code = input("\n🔢 Enter the verification code you received: ").strip()
            
            if not code:
                warning("Verification code cannot be empty")
                continue
                
            # Basic code validation (usually 5-6 digits)
            if not re.match(r'^\d{4,6}$', code):
                warning("Verification code should be 4-6 digits")
                continue
                
            return code
    
    @staticmethod
    def get_2fa_password() -> str:
        """Get 2FA password from user input."""
        import getpass
        
        while True:
            password = getpass.getpass("\n🔐 Enter your 2FA password: ").strip()
            
            if not password:
                warning("2FA password cannot be empty")
                continue
                
            return password
    
    @staticmethod
    def confirm(message: str) -> bool:
        """Get confirmation from user."""
        while True:
            response = input(f"\n❓ {message} [y/N]: ").strip().lower()
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                warning("Please enter 'y' for yes or 'n' for no")
                continue 