# filepath: c:\Gabriel\Bots\Ignis\database.py
import aiosqlite

async def initialize_db():
    async with aiosqlite.connect("ignis.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                points INTEGER DEFAULT 0,
                rank TEXT DEFAULT 'Inductii',
                progress INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect("ignis.db") as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def create_user(user_id):
    async with aiosqlite.connect("ignis.db") as db:
        await db.execute("INSERT INTO users (user_id, points, rank) VALUES (?, 0, 'Novato')", (user_id,))
        await db.commit()

async def update_points(user_id, points):
    async with aiosqlite.connect("ignis.db") as db:
        await db.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points, user_id))
        await db.commit()