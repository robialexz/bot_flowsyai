import aiosqlite
from .config import DB_FILE, logger

async def setup_database():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, 
            first_name TEXT, 
            last_name TEXT, 
            username TEXT, 
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            target_price REAL NOT NULL,
            direction TEXT NOT NULL, -- 'above' or 'below'
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS celebration_media (
            media_id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_type TEXT NOT NULL, -- 'gif', 'sticker', 'animation'
            file_id TEXT NOT NULL,    -- Telegram file_id
            category TEXT NOT NULL,   -- 'buy', 'price_up', 'milestone'
            message TEXT             -- Optional celebration message
        )""")
        await db.commit()
    logger.info("Database initialized successfully.")

async def update_user_in_db(user):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, first_name, last_name, username) VALUES (?, ?, ?, ?)",
                       (user.id, user.first_name, user.last_name, user.username))
        await db.commit()

async def create_price_alert(user_id: int, symbol: str, target_price: float, direction: str) -> int:
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "INSERT INTO alerts (user_id, symbol, target_price, direction) VALUES (?, ?, ?, ?)",
            (user_id, symbol.upper(), target_price, direction.lower())
        )
        await db.commit()
        return cursor.lastrowid

async def get_user_alerts(user_id: int) -> list:
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT alert_id, symbol, target_price, direction FROM alerts WHERE user_id = ?",
            (user_id,)
        )
        return await cursor.fetchall()

async def delete_alert(alert_id: int, user_id: int) -> bool:
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "DELETE FROM alerts WHERE alert_id = ? AND user_id = ?",
            (alert_id, user_id)
        )
        await db.commit()
        return cursor.rowcount > 0

async def get_all_active_alerts() -> list:
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT a.alert_id, a.user_id, a.symbol, a.target_price, a.direction FROM alerts a JOIN users u ON a.user_id = u.user_id"
        )
        return await cursor.fetchall()

async def add_celebration_media(media_type: str, file_id: str, category: str, message: str = None) -> int:
    """Adaugă un nou media pentru celebrări în baza de date."""
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "INSERT INTO celebration_media (media_type, file_id, category, message) VALUES (?, ?, ?, ?)",
            (media_type, file_id, category, message)
        )
        await db.commit()
        return cursor.lastrowid

async def get_random_celebration_media(category: str) -> tuple:
    """Returnează un media aleatoriu pentru o anumită categorie."""
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT media_type, file_id, message FROM celebration_media WHERE category = ? ORDER BY RANDOM() LIMIT 1",
            (category,)
        )
        return await cursor.fetchone()

async def delete_celebration_media(media_id: int) -> bool:
    """Șterge un media din baza de date."""
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "DELETE FROM celebration_media WHERE media_id = ?",
            (media_id,)
        )
        await db.commit()
        return cursor.rowcount > 0