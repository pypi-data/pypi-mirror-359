"""
Period management functionality for data viewing.

This module provides:
- Period range calculations (day, week, month, quarter, etc.)
- Custom date range validation
- Period type validation
- Date string parsing utilities
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional
from dataclasses import dataclass
from dateutil.relativedelta import relativedelta
import calendar

logger = logging.getLogger(__name__)


class DataViewError(Exception):
    """Data viewing related errors."""
    pass


@dataclass
class PeriodRange:
    """Represents a date range for data querying."""
    start_date: date
    end_date: date
    period_type: str
    description: str


class PeriodManager:
    """Manages period calculations and date range operations."""
    
    VALID_PERIOD_TYPES = {
        "previous-day", "previous-week", "previous-month",
        "previous-quarter", "previous-semiannual", "previous-annual"
    }
    
    def calculate_period_range(self, period_type: str, reference_date: Optional[date] = None) -> PeriodRange:
        """Calculate date range for various period types."""
        if reference_date is None:
            reference_date = date.today()
        
        logger.debug(f"Calculating period range for '{period_type}' from reference date {reference_date}")
        
        if period_type == "previous-day":
            return self._calculate_previous_day(reference_date)
        elif period_type == "previous-week":
            return self._calculate_previous_week(reference_date)
        elif period_type == "previous-month":
            return self._calculate_previous_month(reference_date)
        elif period_type == "previous-quarter":
            return self._calculate_previous_quarter(reference_date)
        elif period_type == "previous-semiannual":
            return self._calculate_previous_semiannual(reference_date)
        elif period_type == "previous-annual":
            return self._calculate_previous_annual(reference_date)
        else:
            raise DataViewError(f"Unknown period type: {period_type}")
    
    def calculate_custom_range(self, start_date: date, end_date: date) -> PeriodRange:
        """Calculate custom date range with validation."""
        if start_date > end_date:
            raise DataViewError(f"Start date ({start_date}) cannot be after end date ({end_date})")
        
        days_count = (end_date - start_date).days + 1
        
        return PeriodRange(
            start_date=start_date,
            end_date=end_date,
            period_type="custom-range",
            description=f"Custom range ({start_date} to {end_date}, {days_count} days)"
        )
    
    def validate_period_type(self, period_type: str) -> bool:
        """Validate if period type is supported."""
        return period_type in self.VALID_PERIOD_TYPES
    
    def parse_date_string(self, date_string: str) -> date:
        """Parse date string in YYYY-MM-DD format."""
        try:
            return datetime.strptime(date_string, "%Y-%m-%d").date()
        except ValueError as e:
            raise DataViewError(f"Invalid date format '{date_string}': expected YYYY-MM-DD")
    
    def _calculate_previous_day(self, reference_date: date) -> PeriodRange:
        """Calculate previous day period."""
        prev_day = reference_date - timedelta(days=1)
        return PeriodRange(
            start_date=prev_day,
            end_date=prev_day,
            period_type="previous-day",
            description=f"Previous day ({prev_day})"
        )
    
    def _calculate_previous_week(self, reference_date: date) -> PeriodRange:
        """Calculate previous week period (Monday to Sunday)."""
        # Find the start of the previous complete week (Monday)
        days_since_monday = reference_date.weekday()
        current_week_start = reference_date - timedelta(days=days_since_monday)
        prev_week_start = current_week_start - timedelta(days=7)
        prev_week_end = prev_week_start + timedelta(days=6)
        
        return PeriodRange(
            start_date=prev_week_start,
            end_date=prev_week_end,
            period_type="previous-week",
            description=f"Previous week ({prev_week_start} to {prev_week_end})"
        )
    
    def _calculate_previous_month(self, reference_date: date) -> PeriodRange:
        """Calculate previous month period."""
        # Find the previous complete month
        if reference_date.month == 1:
            prev_month = 12
            prev_year = reference_date.year - 1
        else:
            prev_month = reference_date.month - 1
            prev_year = reference_date.year
        
        prev_month_start = date(prev_year, prev_month, 1)
        _, last_day = calendar.monthrange(prev_year, prev_month)
        prev_month_end = date(prev_year, prev_month, last_day)
        
        return PeriodRange(
            start_date=prev_month_start,
            end_date=prev_month_end,
            period_type="previous-month",
            description=f"Previous month ({prev_month_start} to {prev_month_end})"
        )
    
    def _calculate_previous_quarter(self, reference_date: date) -> PeriodRange:
        """Calculate previous quarter period."""
        # Find the previous complete quarter
        current_quarter = (reference_date.month - 1) // 3 + 1
        
        if current_quarter == 1:
            prev_quarter = 4
            prev_year = reference_date.year - 1
        else:
            prev_quarter = current_quarter - 1
            prev_year = reference_date.year
        
        # Calculate quarter start month
        quarter_start_month = (prev_quarter - 1) * 3 + 1
        prev_quarter_start = date(prev_year, quarter_start_month, 1)
        
        # Calculate quarter end month and last day
        quarter_end_month = quarter_start_month + 2
        _, last_day = calendar.monthrange(prev_year, quarter_end_month)
        prev_quarter_end = date(prev_year, quarter_end_month, last_day)
        
        return PeriodRange(
            start_date=prev_quarter_start,
            end_date=prev_quarter_end,
            period_type="previous-quarter",
            description=f"Previous quarter Q{prev_quarter} {prev_year} ({prev_quarter_start} to {prev_quarter_end})"
        )
    
    def _calculate_previous_semiannual(self, reference_date: date) -> PeriodRange:
        """Calculate previous half-year period."""
        # Find the previous complete half-year
        current_half = 1 if reference_date.month <= 6 else 2
        
        if current_half == 1:
            prev_half = 2
            prev_year = reference_date.year - 1
            prev_half_start = date(prev_year, 7, 1)
            prev_half_end = date(prev_year, 12, 31)
        else:
            prev_half = 1
            prev_year = reference_date.year
            prev_half_start = date(prev_year, 1, 1)
            prev_half_end = date(prev_year, 6, 30)
        
        return PeriodRange(
            start_date=prev_half_start,
            end_date=prev_half_end,
            period_type="previous-semiannual",
            description=f"Previous half-year H{prev_half} {prev_year} ({prev_half_start} to {prev_half_end})"
        )
    
    def _calculate_previous_annual(self, reference_date: date) -> PeriodRange:
        """Calculate previous year period."""
        # Find the previous complete year
        prev_year = reference_date.year - 1
        prev_year_start = date(prev_year, 1, 1)
        prev_year_end = date(prev_year, 12, 31)
        
        return PeriodRange(
            start_date=prev_year_start,
            end_date=prev_year_end,
            period_type="previous-annual",
            description=f"Previous year {prev_year} ({prev_year_start} to {prev_year_end})"
        ) 