"""Admin moderation and account management business logic (no Streamlit code)."""
from typing import List, Dict, Any, Optional, Tuple

from db.database import get_connection
from services.auth import is_active_user


def open_reports() -> List[Dict[str, Any]]:
    """Return all open reports in descending order of creation."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT rp.id, rp.target_type, rp.reason, rp.target_user_id, rp.target_skill_id,
                   rp.request_id, issue_skill.name AS request_skill, rp.created_at,
                   reporter.name AS reporter,
                   COALESCE(tu.name, sk.name) AS target
            FROM reports rp
            JOIN users reporter ON reporter.id = rp.reporter_id
            LEFT JOIN users tu ON tu.id = rp.target_user_id
            LEFT JOIN skills sk ON sk.id = rp.target_skill_id
            LEFT JOIN requests issue_request ON issue_request.id = rp.request_id
            LEFT JOIN skills issue_skill ON issue_skill.id = issue_request.skill_id
            WHERE rp.status = 'open'
            ORDER BY rp.created_at DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def resolve_report(
    report_id: int, actor_id: int, deactivate_user_id: Optional[int] = None
) -> Tuple[bool, str]:
    """Mark a report resolved and optionally deactivate the offending user."""
    conn = get_connection()
    try:
        with conn:
            if not is_active_user(conn, actor_id, "admin"):
                return False, "An active administrator account is required."

            report = conn.execute(
                "SELECT 1 FROM reports WHERE id = ? AND status = 'open'",
                (report_id,),
            ).fetchone()
            if not report:
                return False, "Open report not found."

            if deactivate_user_id is not None:
                target = conn.execute(
                    "SELECT 1 FROM users WHERE id = ? AND role = 'student'",
                    (deactivate_user_id,),
                ).fetchone()
                if not target:
                    return False, "Student account not found."

            updated = conn.execute(
                "UPDATE reports SET status = 'resolved' WHERE id = ? AND status = 'open'",
                (report_id,),
            )
            if updated.rowcount == 0:
                return False, "Open report not found."

            if deactivate_user_id is not None:
                conn.execute(
                    "UPDATE users SET is_active = 0 WHERE id = ? AND role = 'student'",
                    (deactivate_user_id,),
                )
        return True, "Report resolved."
    finally:
        conn.close()


def get_all_students() -> List[Dict[str, Any]]:
    """Return all registered students."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, name, email, department, bio, is_active, created_at
            FROM users
            WHERE role = 'student'
            ORDER BY name ASC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def toggle_user_active(actor_id: int, user_id: int, new_status: int) -> Tuple[bool, str]:
    """Activate or deactivate a student account."""
    if new_status not in (0, 1):
        return False, "Account status must be active (1) or inactive (0)."

    conn = get_connection()
    try:
        with conn:
            if not is_active_user(conn, actor_id, "admin"):
                return False, "An active administrator account is required."

            updated = conn.execute(
                "UPDATE users SET is_active = ? WHERE id = ? AND role = 'student'",
                (new_status, user_id),
            )
            if updated.rowcount == 0:
                return False, "Student account not found."
        status_label = "activated" if new_status else "deactivated"
        return True, f"Account {status_label}."
    finally:
        conn.close()
