"""SQLite storage: farmers (preferences + alert subscription) and chat history."""
import sqlite3
from contextlib import contextmanager

from .config import DB_PATH
from .data import DEFAULT_PREFS


@contextmanager
def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init() -> None:
    with conn() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS farmers (
                 phone TEXT PRIMARY KEY, city TEXT, crop TEXT, lang TEXT,
                 subscribed INTEGER NOT NULL DEFAULT 0)"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS messages (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT NOT NULL,
                 role TEXT NOT NULL, content TEXT NOT NULL)"""
        )


def get_farmer(phone: str) -> dict | None:
    with conn() as c:
        row = c.execute("SELECT * FROM farmers WHERE phone = ?", (phone,)).fetchone()
    return dict(row) if row else None


def save_farmer(phone: str, **fields) -> dict:
    """Create or update a farmer. Only the fields you pass are changed."""
    cur = get_farmer(phone) or {"phone": phone, **DEFAULT_PREFS, "subscribed": 0}
    cur.update({k: v for k, v in fields.items() if v is not None})
    with conn() as c:
        c.execute(
            """INSERT INTO farmers (phone, city, crop, lang, subscribed)
               VALUES (:phone, :city, :crop, :lang, :subscribed)
               ON CONFLICT(phone) DO UPDATE SET
                 city = :city, crop = :crop, lang = :lang, subscribed = :subscribed""",
            cur,
        )
    return cur


def list_subscribed() -> list[dict]:
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM farmers WHERE subscribed = 1")]


def add_message(phone: str, role: str, content: str) -> None:
    with conn() as c:
        c.execute("INSERT INTO messages (phone, role, content) VALUES (?, ?, ?)", (phone, role, content))


def recent_messages(phone: str, n: int = 8) -> list[dict]:
    with conn() as c:
        rows = c.execute(
            "SELECT role, content FROM messages WHERE phone = ? ORDER BY id DESC LIMIT ?", (phone, n)
        ).fetchall()
    return [dict(r) for r in reversed(rows)]
