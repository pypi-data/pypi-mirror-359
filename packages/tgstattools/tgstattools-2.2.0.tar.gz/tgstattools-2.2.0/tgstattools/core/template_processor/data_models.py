"""
Data models for template processing system.

This module contains the data structures used to represent
user and chat statistics throughout the template processing pipeline.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class UserStatistics:
    """User statistics data structure."""
    user_id: int
    name: str
    messages: int
    percentage: float


@dataclass
class ChatStatistics:
    """Chat statistics data structure."""
    chat_id: int
    title: str
    messages: int
    percentage: float


@dataclass
class StatisticsData:
    """Complete statistics data structure."""
    date: str
    total_messages: int
    users: List[UserStatistics]
    chats: List[ChatStatistics] 
    monitoring_groups_used: List[str]
    collection_completed_at: str
    reporting_group: str = None 