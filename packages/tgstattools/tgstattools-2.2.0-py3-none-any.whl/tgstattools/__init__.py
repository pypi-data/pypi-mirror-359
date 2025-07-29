"""
TgStatTools v2.0 - Advanced Telegram chat statistics collection and reporting daemon.

This package provides a comprehensive solution for collecting, storing, and analyzing
Telegram chat statistics with automated reporting capabilities.
"""

__version__ = "2.2.0"
__author__ = "TgStatTools Team"
__email__ = "team@tgstattools.dev"

# Main exports
from .cli import main

__all__ = ["main", "__version__"] 