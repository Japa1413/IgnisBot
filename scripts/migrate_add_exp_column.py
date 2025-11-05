"""
Migration script to add exp and path columns to users table
"""
import asyncio
import sys
sys.path.insert(0, '.')

import aiomysql
from utils.database import get_pool
from utils.logger import get_logger

logger = get_logger(__name__)

async def migrate():
    """Add exp and path columns if they don't exist"""
    try:
        pool = get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Check if exp column exists
                await cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'users'
                    AND COLUMN_NAME = 'exp'
                """)
                result = await cursor.fetchone()
                exp_exists = result[0] > 0 if result else False
                
                # Add exp column if it doesn't exist
                if not exp_exists:
                    logger.info("Adding 'exp' column to users table...")
                    await cursor.execute("""
                        ALTER TABLE users 
                        ADD COLUMN exp INT DEFAULT 0 AFTER points
                    """)
                    logger.info("✅ Column 'exp' added successfully")
                else:
                    logger.info("Column 'exp' already exists")
                
                # Check if path column exists
                await cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'users'
                    AND COLUMN_NAME = 'path'
                """)
                result = await cursor.fetchone()
                path_exists = result[0] > 0 if result else False
                
                # Add path column if it doesn't exist
                if not path_exists:
                    logger.info("Adding 'path' column to users table...")
                    await cursor.execute("""
                        ALTER TABLE users 
                        ADD COLUMN path VARCHAR(50) DEFAULT 'pre_induction' AFTER exp
                    """)
                    logger.info("✅ Column 'path' added successfully")
                else:
                    logger.info("Column 'path' already exists")
                
                # Update existing rows: set exp = points (for backward compatibility)
                logger.info("Updating existing rows: exp = points...")
                await cursor.execute("""
                    UPDATE users 
                    SET exp = COALESCE(points, 0) 
                    WHERE exp IS NULL OR exp = 0 OR exp != points
                """)
                updated = cursor.rowcount
                logger.info(f"✅ Updated {updated} rows")
                
                # Add indexes if they don't exist
                try:
                    await cursor.execute("""
                        SELECT COUNT(*) as count
                        FROM information_schema.statistics 
                        WHERE table_schema = DATABASE() 
                        AND table_name = 'users' 
                        AND index_name = 'idx_exp'
                    """)
                    result = await cursor.fetchone()
                    idx_exp_exists = result[0] > 0 if result else False
                    
                    if not idx_exp_exists:
                        await cursor.execute("CREATE INDEX idx_exp ON users(exp DESC)")
                        logger.info("✅ Index idx_exp created")
                    else:
                        logger.info("Index idx_exp already exists")
                except Exception as e:
                    logger.warning(f"Could not create idx_exp index: {e}")
                
                try:
                    await cursor.execute("""
                        SELECT COUNT(*) as count
                        FROM information_schema.statistics 
                        WHERE table_schema = DATABASE() 
                        AND table_name = 'users' 
                        AND index_name = 'idx_rank'
                    """)
                    result = await cursor.fetchone()
                    idx_rank_exists = result[0] > 0 if result else False
                    
                    if not idx_rank_exists:
                        await cursor.execute("CREATE INDEX idx_rank ON users(`rank`)")
                        logger.info("✅ Index idx_rank created")
                    else:
                        logger.info("Index idx_rank already exists")
                except Exception as e:
                    logger.warning(f"Could not create idx_rank index: {e}")
                
                logger.info("✅ Migration completed successfully!")
                
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        raise

async def main():
    from utils.database import initialize_db
    await initialize_db()
    await migrate()

if __name__ == "__main__":
    asyncio.run(main())

