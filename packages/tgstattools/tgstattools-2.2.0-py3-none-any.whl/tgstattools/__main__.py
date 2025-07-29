"""
Module execution entry point for TgStatTools.

This allows running the package as a module:
    python -m tgstattools <command> [options]
"""

from .cli import main

if __name__ == "__main__":
    main() 