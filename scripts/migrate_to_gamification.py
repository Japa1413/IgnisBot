"""
Migration script: Migrate existing user data to new gamification system.

Converts existing points to initial XP (1:1 ratio) and calculates initial level.
"""

from __future__ import annotations

import asyncio
import aiomysql
from utils.database import get_pool
from services.level_service import level_from_xp
from utils.logger import get_logger

logger = get_logger(__name__)


async def migrate_user_data():
    """
    Migrate existing user points to new XP/progression system.
    
    Strategy:
    1. Get all users with their current points
    2. Convert points to initial XP (1:1)
    3. Calculate initial level from XP
    4. Create progression entries
    5. Preserve existing rank (will be recalculated later)
    """
    try:
        pool = get_pool()
    except RuntimeError:
        logger.error("Database pool not initialized")
        return
    
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # Get all users
            await cursor.execute(
                "SELECT user_id, points, `rank` FROM users"
            )
            users = await cursor.fetchall()
            
            logger.info(f"Found {len(users)} users to migrate")
            
            migrated = 0
            errors = 0
            
            for user in users:
                user_id = user["user_id"]
                current_points = int(user.get("points", 0))
                current_rank = user.get("rank", "Civitas aspirant")
                
                try:
                    # Convert points to XP (1:1 ratio)
                    initial_xp = current_points
                    
                    # Calculate initial level
                    level, _, _ = level_from_xp(initial_xp)
                    
                    # Create or update progression entry
                    await cursor.execute(
                        """
                        INSERT INTO user_progression (user_id, total_xp, current_level)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            total_xp = VALUES(total_xp),
                            current_level = VALUES(current_level)
                        """,
                        (user_id, initial_xp, level)
                    )
                    
                    # Create initial XP event (legacy migration)
                    await cursor.execute(
                        """
                        INSERT INTO xp_events (user_id, xp_amount, source, details)
                        VALUES (%s, %s, 'migration', %s)
                        """,
                        (
                            user_id,
                            initial_xp,
                            f'{{"legacy_points": {current_points}, "migrated_at": NOW()}}'
                        )
                    )
                    
                    migrated += 1
                    
                    if migrated % 100 == 0:
                        logger.info(f"Migrated {migrated}/{len(users)} users...")
                
                except Exception as e:
                    errors += 1
                    logger.error(f"Error migrating user {user_id}: {e}")
                    continue
            
            await conn.commit()
            
            logger.info(
                f"Migration complete: {migrated} migrated, {errors} errors"
            )


if __name__ == "__main__":
    asyncio.run(migrate_user_data())

