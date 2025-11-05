"""
Event type definitions for IgnisBot event system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PointsChangedEvent:
    """Event fired when user points are changed"""
    user_id: int
    before: int
    after: int
    delta: int
    reason: str
    performed_by: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    command: str = ""  # Command that triggered the change (e.g., "/add", "/vc_log")


@dataclass
class UserCreatedEvent:
    """Event fired when a new user is created"""
    user_id: int
    timestamp: datetime = field(default_factory=datetime.utcnow)

