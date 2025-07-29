"""
Simple timezone utilities for reports only.

This module provides minimal timezone functionality following the principle:
"Store UTC, Display Local". All data is collected and stored in UTC,
timezone conversion happens only during report generation.
"""

from datetime import datetime, date, time
from typing import Tuple
import pytz


def convert_utc_to_local_date(utc_date: date, timezone: str = "UTC") -> date:
    """
    Convert UTC date to local date in specified timezone.
    
    Args:
        utc_date: Date in UTC
        timezone: Target timezone (default: UTC)
        
    Returns:
        Date in local timezone
    """
    if timezone == "UTC":
        return utc_date
    
    try:
        tz = pytz.timezone(timezone)
        # Convert UTC date to datetime at midnight
        utc_datetime = datetime.combine(utc_date, time.min)
        utc_datetime = pytz.UTC.localize(utc_datetime)
        
        # Convert to local timezone
        local_datetime = utc_datetime.astimezone(tz)
        return local_datetime.date()
    except Exception:
        # Fallback to UTC if timezone conversion fails
        return utc_date


def get_day_boundaries_utc(local_date: date, timezone: str = "UTC") -> Tuple[datetime, datetime]:
    """
    Get UTC boundaries for a local date in specified timezone.
    
    This is useful for filtering database records by converting
    local day boundaries to UTC for database queries.
    
    Args:
        local_date: Local date
        timezone: Local timezone (default: UTC)
        
    Returns:
        Tuple of (start_utc, end_utc) datetime objects
    """
    if timezone == "UTC":
        # Simple case - no conversion needed
        start_utc = datetime.combine(local_date, time.min).replace(tzinfo=pytz.UTC)
        end_utc = datetime.combine(local_date, time.max).replace(tzinfo=pytz.UTC)
        return (start_utc, end_utc)
    
    try:
        tz = pytz.timezone(timezone)
        
        # Start of day in local timezone
        local_start = tz.localize(datetime.combine(local_date, time.min))
        # End of day in local timezone  
        local_end = tz.localize(datetime.combine(local_date, time.max))
        
        # Convert to UTC
        start_utc = local_start.astimezone(pytz.UTC)
        end_utc = local_end.astimezone(pytz.UTC)
        
        return (start_utc, end_utc)
    except Exception:
        # Fallback to UTC if timezone conversion fails
        start_utc = datetime.combine(local_date, time.min).replace(tzinfo=pytz.UTC)
        end_utc = datetime.combine(local_date, time.max).replace(tzinfo=pytz.UTC)
        return (start_utc, end_utc)


def format_timestamp_for_display(utc_timestamp: datetime, timezone: str = "UTC") -> str:
    """
    Format UTC timestamp for display in specified timezone.
    
    Args:
        utc_timestamp: UTC timestamp
        timezone: Display timezone (default: UTC)
        
    Returns:
        Formatted timestamp string
    """
    if timezone == "UTC":
        return utc_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    try:
        tz = pytz.timezone(timezone)
        # Ensure UTC timezone info
        if utc_timestamp.tzinfo is None:
            utc_timestamp = pytz.UTC.localize(utc_timestamp)
        elif utc_timestamp.tzinfo != pytz.UTC:
            utc_timestamp = utc_timestamp.astimezone(pytz.UTC)
        
        # Convert to local timezone
        local_timestamp = utc_timestamp.astimezone(tz)
        return local_timestamp.strftime(f"%Y-%m-%d %H:%M:%S {timezone}")
    except Exception:
        # Fallback to UTC display
        return utc_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")


def get_available_timezones() -> list:
    """
    Get list of common timezones for user selection.
    
    Returns:
        List of timezone strings
    """
    return [
        "UTC",
        "Europe/Moscow", 
        "Europe/London",
        "Europe/Berlin",
        "US/Eastern",
        "US/Pacific",
        "Asia/Tokyo",
        "Asia/Shanghai",
        "Australia/Sydney"
    ]


def validate_timezone(timezone: str) -> bool:
    """
    Validate if timezone string is valid.
    
    Args:
        timezone: Timezone string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        pytz.timezone(timezone)
        return True
    except pytz.UnknownTimeZoneError:
        return False 