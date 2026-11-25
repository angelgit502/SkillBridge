import pytest

import db.database as database
import db.init_db as init_db
from db.seed import seed


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    db_path = str(tmp_path / "skillbridge-test.db")
    monkeypatch.setattr(database, "DB_PATH", db_path)
    monkeypatch.setattr(init_db, "DB_PATH", db_path)

    init_db.init_db()
    conn = database.get_connection()
    try:
        with conn:
            seed(conn)
    finally:
        conn.close()
