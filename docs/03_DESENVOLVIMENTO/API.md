# 📚 API Documentation - IgnisBot

**Version:** 1.0  
**Last Updated:** 2025-11-07

---

## Overview

IgnisBot is a Discord bot with gamification, event management, and Roblox integration. This document describes the internal APIs and services.

---

## Services

### PointsService

**Location:** `services/points_service.py`

Manages user points and transactions.

#### Methods

##### `add_points(user_id, amount, reason, performed_by)`
Add points to a user.

**Parameters:**
- `user_id` (int): Discord user ID
- `amount` (int): Points to add (positive)
- `reason` (str): Reason for adding points
- `performed_by` (int): Discord user ID who performed the action

**Returns:** `Transaction` object with before/after points

**Raises:** `ValueError` if user not found or consent not given

##### `remove_points(user_id, amount, reason, performed_by)`
Remove points from a user.

**Parameters:**
- `user_id` (int): Discord user ID
- `amount` (int): Points to remove (positive)
- `reason` (str): Reason for removing points
- `performed_by` (int): Discord user ID who performed the action

**Returns:** `Transaction` object with before/after points

**Raises:** `ValueError` if user not found or insufficient points

---

### BloxlinkService

**Location:** `services/bloxlink_service.py`

Handles integration with Bloxlink API for Roblox data.

#### Methods

##### `get_roblox_user(discord_id, guild_id=None)`
Get Roblox user data from Bloxlink.

**Parameters:**
- `discord_id` (int): Discord user ID
- `guild_id` (int, optional): Discord guild ID

**Returns:** Dict with:
- `username`: Roblox username (not display name)
- `id`: Roblox user ID
- `avatar_url`: Roblox avatar URL
- `verified`: Boolean
- `verified_at`: Timestamp

**Returns:** `None` if user not found or not verified

**Features:**
- Circuit breaker protection
- Retry with exponential backoff
- Automatic fallback

##### `get_roblox_user_by_username(username)`
Get Roblox user data by username.

**Parameters:**
- `username` (str): Roblox username

**Returns:** Dict with user data or `None` if not found

---

### CacheService

**Location:** `services/cache_service.py`

Manages in-memory cache for user data.

#### Methods

##### `get_user(user_id)`
Get user data from cache or database.

**Parameters:**
- `user_id` (int): Discord user ID

**Returns:** User data dict or `None`

##### `set_user(user_id, data)`
Store user data in cache.

**Parameters:**
- `user_id` (int): Discord user ID
- `data` (dict): User data

---

## Utilities

### Health Check

**Location:** `utils/health_check.py`

Monitor bot health and system status.

#### `HealthCheck` Class

##### `check_database()`
Check database connection health.

**Returns:** Dict with status, latency, and pool info

##### `check_cache()`
Check cache system health.

**Returns:** Dict with cache statistics

##### `check_integrations()`
Check external integrations (Bloxlink, Roblox API).

**Returns:** Dict with integration status

##### `get_full_health_report()`
Get complete health report.

**Returns:** Complete health status dict

---

### Retry Logic

**Location:** `utils/retry.py`

Retry with exponential backoff and circuit breaker.

#### `retry_with_backoff(func, max_retries=3, ...)`
Retry function with exponential backoff.

**Parameters:**
- `func`: Async function to retry
- `max_retries`: Maximum retry attempts
- `initial_delay`: Initial delay in seconds
- `max_delay`: Maximum delay in seconds
- `exponential_base`: Base for exponential backoff

**Returns:** Function result

**Raises:** Last exception if all retries fail

#### `CircuitBreaker` Class

Circuit breaker pattern for failing services.

**States:**
- `CLOSED`: Normal operation
- `OPEN`: Failing, reject requests
- `HALF_OPEN`: Testing recovery

---

## Commands

### `/health`

Check bot health and system status.

**Permissions:** Everyone

**Response:** Embed with:
- Database status
- Cache status
- Integration status
- Command latency

---

## Error Handling

All services use structured error handling:

- `ValueError`: Business logic errors (user not found, validation, etc.)
- `RuntimeError`: System errors (database not initialized, etc.)
- `Exception`: Unexpected errors

---

## Rate Limiting

Currently not implemented. Planned for future versions.

---

## Authentication

Commands use Discord's built-in authentication. Admin commands require:
- `manage_messages` permission OR
- `administrator` permission OR
- Server owner

---

**For more information, see the main README.md**

