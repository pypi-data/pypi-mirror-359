"""
Core utilities for TgStatTools.

This module contains shared utility functions used across the project
to avoid code duplication and maintain consistency.
"""

import hashlib
import json
import logging
from typing import List

logger = logging.getLogger(__name__)


def calculate_monitoring_groups_hash(groups: List[str]) -> str:
    """
    Calculate consistent hash for monitoring groups combination.
    
    This ensures that the same combination of monitoring groups
    always produces the same hash, regardless of order.
    
    Args:
        groups: List of monitoring group names
        
    Returns:
        16-character hexadecimal hash string
    """
    sorted_groups = sorted(groups)
    groups_json = json.dumps(sorted_groups)
    return hashlib.sha256(groups_json.encode()).hexdigest()[:16]


def calculate_percentage(part: int, total: int) -> float:
    """
    Calculate percentage with proper handling of edge cases.
    
    Args:
        part: Part value
        total: Total value
        
    Returns:
        Percentage as float (0.0 if total is 0)
    """
    if total <= 0:
        return 0.0
    return round((part / total) * 100, 2)


def format_date_for_display(date_obj, format_str: str = "%d-%m-%Y") -> str:
    """
    Format date object for display in reports.
    
    Args:
        date_obj: Date object to format
        format_str: Format string (default: DD-MM-YYYY)
        
    Returns:
        Formatted date string
    """
    return date_obj.strftime(format_str)


def validate_group_config(group_config: dict, required_type: str = None) -> bool:
    """
    Validate group configuration dictionary.
    
    Args:
        group_config: Configuration dictionary to validate
        required_type: Required group_type value (optional)
        
    Returns:
        True if configuration is valid
    """
    if not isinstance(group_config, dict):
        logger.error("Group config is not a dictionary")
        return False
    
    required_fields = ["group_type", "description"]
    for field in required_fields:
        if field not in group_config:
            logger.error(f"Missing required field: {field}")
            return False
    
    if required_type and group_config["group_type"] != required_type:
        logger.error(f"Invalid group_type: expected {required_type}, got {group_config['group_type']}")
        return False
    
    return True 