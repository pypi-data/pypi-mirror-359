"""
Manual operation commands.

Minimal module for backward compatibility.
"""

import argparse
from typing import Any


def register_commands(subparsers: Any) -> None:
    """Register manual operation commands."""
    pass  # No commands left to register


def handle_generate_report(args: argparse.Namespace) -> int:
    """Handle generate-report command (simplified without scheduler)."""
    print("❌ The generate-report command has been removed.")
    print("Please use the direct send-report command instead:")
    print("  python -m tgstattools send-report --date YYYY-MM-DD --monitoring-group GROUP --reporting-group GROUP")
    return 1


async def _get_statistics_data_from_db(database, target_date, monitoring_groups_hash, monitoring_group, user_group="all", config_manager=None, reporting_group=None):
    """Get statistics data from database for reporting with filtering."""
    from ..core.reporter.data_retriever import DataRetriever
    
    # Use the new DataRetriever class for clean separation of concerns
    data_retriever = DataRetriever(database, config_manager)
    return await data_retriever.get_filtered_statistics(target_date, monitoring_group, user_group, reporting_group)


 