"""Student profile and personal skills management business logic (no Streamlit code)."""
import sqlite3
from typing import List, Dict, Any, Tuple

from config import DEPARTMENTS
from db.database import get_connection
from services.auth import is_active_user


def update_profile(
    user_id: int, name: str, department: str, bio: str
) -> Tuple[bool, str]:
    """Update user personal profile details."""
    clean_name = (name or "").strip()
    clean_bio = (bio or "").strip()

    if not clean_name:
        return False, "Name cannot be empty."

    if department not in DEPARTMENTS:
        return False, "Please select a valid department."

    conn = get_connection()
    try:
        with conn:
            if not is_active_user(conn, user_id, "student"):
                return False, "Your student account is not active."

            cur = conn.execute(
                "UPDATE users SET name = ?, department = ?, bio = ? WHERE id = ?",
                (clean_name, department, clean_bio, user_id),
            )
            if cur.rowcount == 0:
                return False, "Student account not found."
        return True, "Profile updated successfully."
    finally:
        conn.close()


def get_user_skills(user_id: int, kind: str) -> List[Dict[str, Any]]:
    """Retrieve skills configured for a student as 'teach' or 'learn'."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT us.skill_id, us.kind, us.is_hidden, s.name, s.category
            FROM user_skills us
            JOIN skills s ON s.id = us.skill_id
            WHERE us.user_id = ? AND us.kind = ?
            ORDER BY s.name ASC
            """,
            (user_id, kind),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_user_skill(user_id: int, skill_id: int, kind: str) -> Tuple[bool, str]:
    """Add a skill to teach or learn for a student."""
    if kind not in ("teach", "learn"):
        return False, "Kind must be 'teach' or 'learn'."

    conn = get_connection()
    try:
        with conn:
            if not is_active_user(conn, user_id, "student"):
                return False, "Your student account is not active."

            conn.execute(
                "INSERT INTO user_skills (user_id, skill_id, kind, is_hidden) VALUES (?, ?, ?, 0)",
                (user_id, skill_id, kind),
            )
        return True, f"Skill added to {kind} list."
    except sqlite3.IntegrityError:
        return False, "This skill is already on your list."
    finally:
        conn.close()


def remove_user_skill(user_id: int, skill_id: int, kind: str) -> Tuple[bool, str]:
    """Remove a skill from student's teach or learn list."""
    conn = get_connection()
    try:
        with conn:
            if not is_active_user(conn, user_id, "student"):
                return False, "Your student account is not active."

            cur = conn.execute(
                "DELETE FROM user_skills WHERE user_id = ? AND skill_id = ? AND kind = ?",
                (user_id, skill_id, kind),
            )
            if cur.rowcount == 0:
                return False, "Skill not found on your list."
        return True, f"Skill removed from {kind} list."
    finally:
        conn.close()


def toggle_skill_hidden(
    user_id: int, skill_id: int, is_hidden: bool
) -> Tuple[bool, str]:
    """Hide or reveal a teaching listing in Discover without deleting it."""
    hidden_val = 1 if is_hidden else 0
    conn = get_connection()
    try:
        with conn:
            if not is_active_user(conn, user_id, "student"):
                return False, "Your student account is not active."

            cur = conn.execute(
                "UPDATE user_skills SET is_hidden = ? WHERE user_id = ? AND skill_id = ? AND kind = 'teach'",
                (hidden_val, user_id, skill_id),
            )
            if cur.rowcount == 0:
                return False, "Teaching listing not found."
        state_str = "hidden from Discover" if is_hidden else "visible in Discover"
        return True, f"Listing is now {state_str}."
    finally:
        conn.close()
