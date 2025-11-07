"""
Database Optimization Script - Analyze and optimize database performance.
"""

import asyncio
import aiomysql
from utils.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from utils.database import get_pool
from utils.logger import get_logger

logger = get_logger(__name__)


async def analyze_slow_queries():
    """Analyze slow queries and suggest indexes"""
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # Check if slow query log is enabled
            await cursor.execute("SHOW VARIABLES LIKE 'slow_query_log'")
            slow_log_enabled = await cursor.fetchone()
            
            if slow_log_enabled and slow_log_enabled.get("Value") == "ON":
                logger.info("Slow query log is enabled")
            else:
                logger.warning("Slow query log is not enabled. Enable it for better analysis.")
            
            # Analyze table indexes
            await cursor.execute("SHOW TABLES")
            tables = await cursor.fetchall()
            
            suggestions = []
            for table in tables:
                table_name = list(table.values())[0]
                
                # Get table info
                await cursor.execute(f"SHOW INDEX FROM {table_name}")
                indexes = await cursor.fetchall()
                
                # Get table structure
                await cursor.execute(f"DESCRIBE {table_name}")
                columns = await cursor.fetchall()
                
                # Check for missing indexes on foreign keys and frequently queried columns
                indexed_columns = {idx.get("Column_name") for idx in indexes}
                
                for col in columns:
                    col_name = col.get("Field")
                    col_key = col.get("Key")
                    
                    # Suggest index for columns used in WHERE clauses frequently
                    if col_key == "" and col_name not in indexed_columns:
                        if col_name in ["user_id", "rank", "path", "exp", "points", "created_at", "updated_at"]:
                            suggestions.append({
                                "table": table_name,
                                "column": col_name,
                                "reason": f"Column '{col_name}' is frequently queried but not indexed"
                            })
            
            return suggestions


async def create_suggested_indexes(suggestions: list):
    """Create indexes based on suggestions"""
    pool = get_pool()
    
    created = 0
    for suggestion in suggestions:
        try:
            table = suggestion["table"]
            column = suggestion["column"]
            index_name = f"idx_{table}_{column}"
            
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column})"
                    )
                    await conn.commit()
            
            logger.info(f"Created index {index_name} on {table}({column})")
            created += 1
        except Exception as e:
            logger.error(f"Failed to create index for {table}.{column}: {e}")
    
    return created


async def optimize_tables():
    """Optimize database tables"""
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SHOW TABLES")
            tables = await cursor.fetchall()
            
            optimized = 0
            for table in tables:
                table_name = list(table.values())[0]
                try:
                    await cursor.execute(f"OPTIMIZE TABLE {table_name}")
                    result = await cursor.fetchone()
                    logger.info(f"Optimized table {table_name}: {result}")
                    optimized += 1
                except Exception as e:
                    logger.error(f"Failed to optimize table {table_name}: {e}")
            
            return optimized


async def main():
    """Main optimization function"""
    logger.info("Starting database optimization...")
    
    # Analyze slow queries
    suggestions = await analyze_slow_queries()
    if suggestions:
        logger.info(f"Found {len(suggestions)} optimization suggestions")
        for suggestion in suggestions:
            logger.info(f"  - {suggestion['table']}.{suggestion['column']}: {suggestion['reason']}")
        
        # Ask for confirmation before creating indexes
        # In production, you might want to review these first
        # created = await create_suggested_indexes(suggestions)
        # logger.info(f"Created {created} indexes")
    else:
        logger.info("No optimization suggestions found")
    
    # Optimize tables
    optimized = await optimize_tables()
    logger.info(f"Optimized {optimized} tables")
    
    logger.info("Database optimization complete")


if __name__ == "__main__":
    from utils.database import initialize_db
    asyncio.run(initialize_db())
    asyncio.run(main())

