"""
Event System for IgnisBot

Event-driven architecture for decoupled operations.
"""

from .event_types import PointsChangedEvent, UserCreatedEvent

__all__ = [
    'PointsChangedEvent',
    'UserCreatedEvent',
]

