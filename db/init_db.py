import sqlite3
from pathlib import Path
from config import DB_PATH

SCHEMA_FILE = Path(__file__).with_name("schema.sql")


def _migrate_request_status(conn):
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'requests'"
    ).fetchone()
    if row is None or "'awaiting_confirmation'" in row[0]:
        return

    sequence = conn.execute(
        "SELECT seq FROM sqlite_sequence WHERE name = 'requests'"
    ).fetchone()
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute(
            """
            CREATE TABLE requests_migrated (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                learner_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                provider_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                skill_id    INTEGER NOT NULL REFERENCES skills(id),
                message     TEXT NOT NULL DEFAULT '',
                status      TEXT NOT NULL DEFAULT 'pending'
                            CHECK (status IN (
                                'pending', 'accepted', 'awaiting_confirmation',
                                'rejected', 'completed', 'cancelled'
                            )),
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
                CHECK (learner_id <> provider_id)
            )
            """
        )
        conn.execute(
            """
            INSERT INTO requests_migrated
                (id, learner_id, provider_id, skill_id, message, status, created_at, updated_at)
            SELECT id, learner_id, provider_id, skill_id, message, status, created_at, updated_at
            FROM requests
            """
        )
        conn.execute("DROP TABLE requests")
        conn.execute("ALTER TABLE requests_migrated RENAME TO requests")
        conn.execute(
            "CREATE INDEX idx_requests_provider ON requests(provider_id, status)"
        )
        conn.execute(
            "CREATE INDEX idx_requests_learner ON requests(learner_id, status)"
        )
        if sequence is not None:
            updated = conn.execute(
                "UPDATE sqlite_sequence SET seq = ? WHERE name = 'requests'",
                (sequence[0],),
            )
            if updated.rowcount == 0:
                conn.execute(
                    "INSERT INTO sqlite_sequence (name, seq) VALUES ('requests', ?)",
                    (sequence[0],),
                )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON")


def _migrate_report_request_link(conn):
    columns = {
        row[1] for row in conn.execute("PRAGMA table_info(reports)").fetchall()
    }
    if "request_id" not in columns:
        conn.execute(
            "ALTER TABLE reports ADD COLUMN request_id INTEGER "
            "REFERENCES requests(id) ON DELETE CASCADE"
        )
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_reports_request_issue "
        "ON reports(request_id) WHERE request_id IS NOT NULL"
    )


def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
        _migrate_request_status(conn)
        _migrate_report_request_link(conn)
        conn.commit()
        violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise sqlite3.IntegrityError(f"Foreign key violations after migration: {violations}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
