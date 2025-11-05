"""
Base Repository with common functionality for all repositories.
"""

from __future__ import annotations

from typing import Optional
import aiomysql
from utils.database import get_pool
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseRepository:
    """Base class for all repositories with common database operations"""
    
    def __init__(self):
        self._pool: Optional[aiomysql.Pool] = None
    
    @property
    def pool(self) -> aiomysql.Pool:
        """Get database connection pool"""
        if self._pool is None:
            self._pool = get_pool()
        return self._pool
    
    async def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = False,
        as_dict: bool = False
    ):
        """
        Execute a SQL query with optional result fetching.
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch_one: Return single row
            fetch_all: Return all rows
            as_dict: Use DictCursor for dict results
        
        Returns:
            Query result(s) or None
        """
        pool = self.pool
        cursor_type = aiomysql.DictCursor if as_dict else aiomysql.Cursor
        
        async with pool.acquire() as conn:
            async with conn.cursor(cursor_type) as cursor:
                await cursor.execute(query, params or ())
                
                if fetch_one:
                    return await cursor.fetchone()
                elif fetch_all:
                    return await cursor.fetchall()
                else:
                    return cursor.rowcount
