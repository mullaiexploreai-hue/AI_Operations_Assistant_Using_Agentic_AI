"""SQLite connections for the local IT knowledge and ticket tools."""
import sqlite3
from pathlib import Path

from config import DB_PATH


def get_read_only_connection() -> sqlite3.Connection:
    ensure_initialized()
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def get_admin_connection() -> sqlite3.Connection:
    """Read-write connection — only db/init_db.py should use this."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_initialized() -> None:
    """Bootstrap the database on first use so a student who skips the
    manual `python -m db.init_db` step doesn't just hit a crash. The
    explicit script is still the documented, primary way to (re)seed."""
    if not Path(DB_PATH).exists():
        from db.init_db import build_database

        build_database()
