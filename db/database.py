"""Database connection and initialization helpers."""
import sqlite3
from pathlib import Path
from threading import Lock

from config import DB_PATH

_INITIALIZED_PATHS: set[str] = set()
_INITIALIZATION_LOCK = Lock()


def ensure_db():
    """Ensure the database and schema are ready without inserting sample records."""
    with _INITIALIZATION_LOCK:
        if DB_PATH in _INITIALIZED_PATHS and Path(DB_PATH).exists():
            return

        from db.init_db import init_db
        init_db()
        _INITIALIZED_PATHS.add(DB_PATH)


def get_connection():
    """Return an open SQLite connection with foreign keys enabled and Row factory."""
    ensure_db()
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
