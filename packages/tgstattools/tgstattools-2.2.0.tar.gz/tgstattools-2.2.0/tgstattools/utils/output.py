"""
Output formatting utilities for TgStatTools.

This module provides colored console output and formatting functions.
"""

import json
from typing import List, Dict, Any, Optional
from colorama import Fore, Style, init

# Initialize colorama for Windows compatibility
init(autoreset=True)


def success(message: str) -> None:
    """Print success message in green."""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")


def error(message: str) -> None:
    """Print error message in red."""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")


def warning(message: str) -> None:
    """Print warning message in yellow."""
    print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")


def info(message: str) -> None:
    """Print info message in blue."""
    print(f"{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")


def print_table(data: Dict[str, Any], headers: Optional[List[str]] = None) -> None:
    """Print data as a simple table."""
    if headers is None:
        headers = ["Key", "Value"]
    
    # Calculate column widths
    key_width = max(len(str(k)) for k in data.keys()) if data else 10
    value_width = max(len(str(v)) for v in data.values()) if data else 10
    
    # Ensure minimum widths
    key_width = max(key_width, len(headers[0]))
    value_width = max(value_width, len(headers[1]))
    
    # Print header
    print(f"{headers[0]:<{key_width}} | {headers[1]:<{value_width}}")
    print("-" * (key_width + value_width + 3))
    
    # Print data
    for key, value in data.items():
        print(f"{str(key):<{key_width}} | {str(value):<{value_width}}")


def print_json(data: Any, indent: int = 2) -> None:
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


def print_separator(char: str = "=", length: int = 50) -> None:
    """Print a separator line."""
    print(char * length)


def print_header(title: str, char: str = "=") -> None:
    """Print a formatted header."""
    print_separator(char)
    print(f" {title} ")
    print_separator(char) 