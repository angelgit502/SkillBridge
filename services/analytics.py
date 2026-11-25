"""Dashboard analytics and aggregations business logic (no Streamlit code)."""
import pandas as pd

from db.database import get_connection


def _read(sql: str, params=()) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()


def load_requests(dept: str = "All") -> pd.DataFrame:
    """Load requests, optionally filtered by learner's department."""
    sql = """
        SELECT r.id, r.status, r.created_at,
               s.name AS skill, s.category,
               l.name AS learner, l.department AS learner_dept,
               p.name AS provider, p.department AS provider_dept
        FROM requests r
        JOIN skills s ON s.id = r.skill_id
        JOIN users l ON l.id = r.learner_id
        JOIN users p ON p.id = r.provider_id
    """
    params = []
    if dept != "All":
        sql += " WHERE l.department = ?"
        params.append(dept)

    return _read(sql, params)


def load_students(dept: str = "All") -> pd.DataFrame:
    """Load active students, optionally filtered by department."""
    sql = """
        SELECT id, name, email, department, is_active, created_at
        FROM users
        WHERE role = 'student'
    """
    params = []
    if dept != "All":
        sql += " AND department = ?"
        params.append(dept)

    return _read(sql, params)


def load_ratings(dept: str = "All") -> pd.DataFrame:
    """Load ratings given to providers, optionally filtered by provider's department."""
    sql = """
        SELECT p.name AS provider, p.department AS provider_dept, f.rating, f.comment
        FROM feedback f
        JOIN sessions s ON s.id = f.session_id
        JOIN requests r ON r.id = s.request_id
        JOIN users p ON p.id = r.provider_id
    """
    params = []
    if dept != "All":
        sql += " WHERE p.department = ?"
        params.append(dept)

    return _read(sql, params)


def load_sessions_analytics(dept: str = "All") -> pd.DataFrame:
    """Load session records with participant details."""
    sql = """
        SELECT sess.id, sess.status, sess.created_at,
               sl.start_time, sl.end_time,
               sk.name AS skill, sk.category,
               l.name AS learner, l.department AS learner_dept,
               p.name AS provider, p.department AS provider_dept
        FROM sessions sess
        JOIN slots sl ON sl.id = sess.slot_id
        JOIN requests r ON r.id = sess.request_id
        JOIN skills sk ON sk.id = r.skill_id
        JOIN users l ON l.id = r.learner_id
        JOIN users p ON p.id = r.provider_id
    """
    params = []
    if dept != "All":
        sql += " WHERE l.department = ? OR p.department = ?"
        params.extend([dept, dept])

    return _read(sql, params)


def load_skills_summary() -> pd.DataFrame:
    """Load skill catalog summary with count of teachers and requests."""
    sql = """
        SELECT s.id, s.name AS skill, s.category,
               COUNT(DISTINCT us.user_id) AS teachers_count,
               COUNT(DISTINCT r.id) AS requests_count
        FROM skills s
        LEFT JOIN user_skills us ON us.skill_id = s.id AND us.kind = 'teach' AND us.is_hidden = 0
        LEFT JOIN requests r ON r.skill_id = s.id
        GROUP BY s.id, s.name, s.category
        ORDER BY requests_count DESC, teachers_count DESC
    """
    return _read(sql)


def load_feedback(dept: str = "All") -> pd.DataFrame:
    """Load feedback rows for a provider-department filter."""
    sql = """
        SELECT f.id, f.rating, f.comment, f.created_at,
               sk.name AS skill,
               learner.name AS learner,
               provider.name AS provider,
               provider.department AS provider_dept
        FROM feedback f
        JOIN sessions s ON s.id = f.session_id
        JOIN requests r ON r.id = s.request_id
        JOIN skills sk ON sk.id = r.skill_id
        JOIN users learner ON learner.id = r.learner_id
        JOIN users provider ON provider.id = r.provider_id
    """
    params = []
    if dept != "All":
        sql += " WHERE provider.department = ?"
        params.append(dept)
    return _read(sql, params)

