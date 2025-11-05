"""
Repository Layer for IgnisBot

Provides data access abstraction with caching and optimization.
"""

from .base_repository import BaseRepository
from .user_repository import UserRepository
from .audit_repository import AuditRepository
from .consent_repository import ConsentRepository
from .xp_repository import XPRepository
from .progression_repository import ProgressionRepository

__all__ = [
    'BaseRepository',
    'UserRepository',
    'AuditRepository',
    'ConsentRepository',
    'XPRepository',
    'ProgressionRepository',
]
