"""Skill catalog, search, and listings business logic (no Streamlit code)."""
from typing import List, Dict, Any, Optional, Tuple

from config import DEPARTMENTS
from db.database import get_connection
from services.auth import is_active_user


def search_listings(
    query: str = "",
    department: Optional[str] = None,
    category: Optional[str] = None,
    exclude_user: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Return teaching listings (one row per student-skill pair), with filters applied.

    Only active students and non-hidden listings are shown.
    """
    sql = """
        SELECT us.skill_id, s.name AS skill, s.category,
               u.id AS provider_id, u.name AS provider, u.department, u.bio,
               ROUND(AVG(f.rating), 1) AS avg_rating,
               COUNT(f.id) AS review_count
        FROM user_skills us
        JOIN skills s ON s.id = us.skill_id
        JOIN users u ON u.id = us.user_id
        LEFT JOIN requests r ON r.provider_id = u.id AND r.skill_id = s.id
        LEFT JOIN sessions sess ON sess.request_id = r.id AND sess.status = 'completed'
        LEFT JOIN feedback f ON f.session_id = sess.id
        WHERE us.kind = 'teach' AND us.is_hidden = 0
          AND u.is_active = 1 AND u.role = 'student'
    """
    params: List[Any] = []

    if query and query.strip():
        sql += " AND s.name LIKE ?"
        params.append(f"%{query.strip()}%")

    if department and department != "All":
        sql += " AND u.department = ?"
        params.append(department)

    if category and category != "All":
        sql += " AND s.category = ?"
        params.append(category)

    if exclude_user is not None:
        sql += " AND u.id <> ?"
        params.append(exclude_user)

    sql += " GROUP BY us.skill_id, us.user_id ORDER BY s.name, u.name"

    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()


def get_departments() -> List[str]:
    """Return list of departments."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT DISTINCT department FROM users WHERE role = 'student' ORDER BY department"
        ).fetchall()
        db_depts = [r[0] for r in rows if r[0]]
        return sorted(list(set(db_depts + DEPARTMENTS)))
    finally:
        conn.close()


def get_categories() -> List[str]:
    """Return list of distinct skill categories."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT DISTINCT category FROM skills ORDER BY category").fetchall()
        return [r[0] for r in rows if r[0]]
    finally:
        conn.close()


def get_all_skills() -> List[Dict[str, Any]]:
    """Return all skills ordered by name."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT id, name, category FROM skills ORDER BY name").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_or_get_skill(
    name: str, category: str = "Other", actor_id: Optional[int] = None
) -> Tuple[Optional[int], str]:
    """Find an existing skill or insert a new one."""
    clean_name = (name or "").strip()
    clean_cat = (category or "").strip() or "Other"

    if not clean_name:
        return None, "Skill name cannot be empty."
    if actor_id is None:
        return None, "An active account is required to manage the skill catalog."

    conn = get_connection()
    try:
        with conn:
            if not is_active_user(conn, actor_id):
                return None, "An active account is required to manage the skill catalog."

            existing = conn.execute(
                "SELECT id FROM skills WHERE name = ? COLLATE NOCASE", (clean_name,)
            ).fetchone()
            if existing:
                return existing["id"], "Skill exists."

            cur = conn.execute(
                "INSERT INTO skills (name, category) VALUES (?, ?)",
                (clean_name, clean_cat),
            )
            return cur.lastrowid, "Skill added."
    finally:
        conn.close()


def get_popular_skills(limit: int = 5) -> List[Dict[str, Any]]:
    """Return top popular skills based on request volume and teaching listings."""
    conn = get_connection()
    try:
        sql = """
            SELECT s.id, s.name, s.category,
                   COUNT(DISTINCT r.id) AS request_count,
                   COUNT(DISTINCT us.user_id) AS teacher_count
            FROM skills s
            LEFT JOIN requests r ON r.skill_id = s.id
            LEFT JOIN user_skills us ON us.skill_id = s.id AND us.kind = 'teach' AND us.is_hidden = 0
            GROUP BY s.id, s.name, s.category
            ORDER BY request_count DESC, teacher_count DESC
            LIMIT ?
        """
        rows = conn.execute(sql, (limit,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

