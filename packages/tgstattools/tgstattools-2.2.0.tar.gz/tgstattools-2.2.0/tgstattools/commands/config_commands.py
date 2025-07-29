"""
Configuration management commands: init-config, validate-config, list-groups.

These commands handle configuration initialization, validation and group management.
"""

import argparse
from typing import Any


def register_commands(subparsers: Any) -> None:
    """Register configuration management commands."""
    
    # Removed init-config command - configurations should work automatically
    
    # Validate configuration command
    validate_parser = subparsers.add_parser(
        "validate-config",
        help="Validate configuration files",
        description="Check configuration syntax and consistency"
    )
    validate_parser.add_argument(
        "--fix-errors",
        action="store_true",
        help="Attempt to fix detected errors"
    )
    
    # list-groups command removed - functionality integrated into validate-config


# Removed init-config handler - configurations should work automatically


def handle_validate_config(args: argparse.Namespace) -> int:
    """Handle configuration validation command."""
    try:
        from ..core.config_manager import ConfigManager
        
        print("🔍 Validating configuration files...")
        if args.fix_errors:
            print("🔧 Auto-fix mode enabled")
        
        config_manager = ConfigManager()
        errors = config_manager.validate_all_configs()
        
        if not errors:
            print("✅ All configuration files are valid!")
            return 0
        else:
            print(f"❌ Found {len(errors)} configuration errors:")
            for error in errors:
                print(f"  • {error}")
            return 1
            
    except Exception as e:
        print(f"❌ Error validating configuration: {e}")
        return 1


def handle_list_groups(args: argparse.Namespace) -> int:
    """Handle list groups command."""
    try:
        from ..core.config_manager import ConfigManager
        
        print(f"📋 Listing groups of type: {args.type}")
        
        config_manager = ConfigManager()
        groups = config_manager.list_groups(args.type if args.type != "all" else None)
        
        if not any(groups.values()):
            print("📭 No configuration groups found. Run 'tgstattools init-config' to create examples.")
            return 0
        
        for group_type, group_list in groups.items():
            if group_list:
                print(f"\n📂 {group_type.replace('_', ' ').title()}:")
                for group_name in group_list:
                    print(f"  • {group_name}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error listing groups: {e}")
        return 1 