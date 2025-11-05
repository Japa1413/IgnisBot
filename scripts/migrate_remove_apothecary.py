"""
Migration script to remove apothecary path and migrate users
"""
import asyncio
import sys
sys.path.insert(0, '.')

from utils.database import get_pool, initialize_db
from utils.logger import get_logger

logger = get_logger(__name__)

async def migrate():
    """Remove apothecary path and migrate users to legionary"""
    try:
        pool = get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Find users with apothecary path
                await cursor.execute("""
                    SELECT user_id, `rank`, exp, points
                    FROM users
                    WHERE path = 'apothecary'
                """)
                apothecary_users = await cursor.fetchall()
                
                if apothecary_users:
                    logger.info(f"Found {len(apothecary_users)} users with apothecary path")
                    
                    # Migrate to legionary path
                    await cursor.execute("""
                        UPDATE users
                        SET path = 'legionary'
                        WHERE path = 'apothecary'
                    """)
                    
                    migrated = cursor.rowcount
                    logger.info(f"✅ Migrated {migrated} users from 'apothecary' to 'legionary' path")
                    
                    # Log details for each migrated user
                    for user in apothecary_users:
                        user_id, rank, exp, points = user
                        logger.info(f"  - User {user_id}: rank='{rank}', exp={exp}, points={points} -> path='legionary'")
                else:
                    logger.info("No users found with apothecary path")
                
                logger.info("✅ Migration completed successfully!")
                
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        raise

async def main():
    await initialize_db()
    await migrate()

if __name__ == "__main__":
    asyncio.run(main())

