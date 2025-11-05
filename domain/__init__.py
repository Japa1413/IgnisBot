"""
Domain layer - Protocols and domain models.

This module contains Protocols (structural types) that define
contracts for services and repositories, enabling better type
safety and testability without full Hexagonal Architecture overhead.
"""

from domain.protocols import (
    UserRepositoryProtocol,
    AuditRepositoryProtocol,
    ConsentRepositoryProtocol,
    CacheServiceProtocol,
    ConsentServiceProtocol,
    EventDispatcherProtocol,
    XPRepositoryProtocol,
    ProgressionRepositoryProtocol,
)

__all__ = [
    "UserRepositoryProtocol",
    "AuditRepositoryProtocol",
    "ConsentRepositoryProtocol",
    "CacheServiceProtocol",
    "ConsentServiceProtocol",
    "EventDispatcherProtocol",
    "XPRepositoryProtocol",
    "ProgressionRepositoryProtocol",
]

