"""
Event handlers for IgnisBot events.
"""

from .audit_handler import setup_audit_handler
from .cache_handler import setup_cache_handler

__all__ = [
    'setup_audit_handler',
    'setup_cache_handler',
]

