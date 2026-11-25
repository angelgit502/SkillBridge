from db.database import get_connection

conn = get_connection()
tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()
print([row[0] for row in tables])
conn.close()
