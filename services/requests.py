"""Skill request creation and status lifecycle business logic (no Streamlit code)."""
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Tuple, Optional

from db.database import get_connection
from services.auth import is_active_user

IST = ZoneInfo("Asia/Kolkata")

ALLOWED = {
    "pending":   {"accepted", "rejected", "cancelled"},
    "accepted":  {"awaiting_confirmation", "cancelled"},
    "awaiting_confirmation": {"completed"},
    "rejected":  set(),
    "completed": set(),
    "cancelled": set(),
}


def create_request(
    learner_id: int, provider_id: int, skill_id: int, message: str
) -> Tuple[bool, str]:
    """Create a new learning request from learner to provider."""
    if learner_id == provider_id:
        return False, "You cannot request your own skill."

    clean_msg = (message or "").strip()
    if not clean_msg:
        return False, "Please add a message explaining what you would like to learn."

    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        with conn:
            learner = conn.execute(
                "SELECT 1 FROM users WHERE id = ? AND role = 'student' AND is_active = 1",
                (learner_id,),
            ).fetchone()
            if not learner:
                return False, "Your student account is not available."

            listing = conn.execute(
                """
                SELECT 1
                FROM user_skills us
                JOIN users provider ON provider.id = us.user_id
                WHERE us.user_id = ? AND us.skill_id = ?
                  AND us.kind = 'teach' AND us.is_hidden = 0
                  AND provider.role = 'student' AND provider.is_active = 1
                """,
                (provider_id, skill_id),
            ).fetchone()
            if not listing:
                return False, "This skill listing is no longer available."

            # Block duplicate open requests for the same skill and student
            existing = conn.execute(
                """
                SELECT id, status FROM requests
                WHERE learner_id = ? AND provider_id = ? AND skill_id = ?
                  AND status IN ('pending', 'accepted', 'awaiting_confirmation')
                """,
                (learner_id, provider_id, skill_id),
            ).fetchone()

            if existing:
                return (
                    False,
                    f"You already have an open request ({existing['status']}) for this skill with this student.",
                )

            conn.execute(
                """
                INSERT INTO requests (learner_id, provider_id, skill_id, message, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'pending', ?, ?)
                """,
                (learner_id, provider_id, skill_id, clean_msg, now_str, now_str),
            )
        return True, "Request sent."
    finally:
        conn.close()


def fetch_requests(user_id: int, as_provider: bool) -> List[Dict[str, Any]]:
    """Fetch incoming (as_provider=True) or sent (as_provider=False) requests."""
    col = "r.provider_id" if as_provider else "r.learner_id"
    conn = get_connection()
    try:
        rows = conn.execute(
            f"""
            SELECT r.id, r.learner_id, r.provider_id, r.skill_id,
                   r.status, r.message, r.created_at, r.updated_at,
                   EXISTS (
                       SELECT 1 FROM reports rp
                       WHERE rp.request_id = r.id
                   ) AS issue_reported,
                   s.name AS skill, s.category,
                   l.name AS learner, l.department AS learner_dept,
                   p.name AS provider, p.department AS provider_dept
            FROM requests r
            JOIN skills s ON s.id = r.skill_id
            JOIN users l ON l.id = r.learner_id
            JOIN users p ON p.id = r.provider_id
            WHERE {col} = ?
            ORDER BY r.created_at DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def count_incoming_pending(user_id: int) -> int:
    """Return the number of incoming pending requests for this provider."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM requests WHERE provider_id = ? AND status = 'pending'",
            (user_id,),
        ).fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def change_status(request_id: int, actor_id: int, new_status: str) -> Tuple[bool, str]:
    """Execute validated status transition on a request.

    Rejects invalid transitions with clear error messages.
    """
    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        with conn:
            row = conn.execute(
                "SELECT status, learner_id, provider_id FROM requests WHERE id = ?",
                (request_id,),
            ).fetchone()

            if row is None:
                return False, "Request not found."

            current = row["status"]
            learner_id = row["learner_id"]
            provider_id = row["provider_id"]

            if actor_id not in (learner_id, provider_id):
                return False, "You do not have permission to modify this request."

            if not is_active_user(conn, actor_id, "student"):
                return False, "Your student account is not active."

            # Terminal states
            if current in ("completed", "rejected", "cancelled"):
                return False, f"Requests marked as {current} are final and cannot be changed."

            # Allowed transitions
            allowed_next = ALLOWED.get(current, set())
            if new_status not in allowed_next:
                return False, f"Cannot change a {current} request to {new_status}."

            # Role permissions
            if current == "pending":
                if new_status in ("accepted", "rejected") and actor_id != provider_id:
                    return False, "Only the skill provider can accept or reject."
                # Both learner and provider can cancel pending
            elif current == "accepted" and new_status == "awaiting_confirmation":
                if actor_id != provider_id:
                    return False, "Only the skill provider can request completion confirmation."
            elif current == "awaiting_confirmation" and new_status == "completed":
                if actor_id != learner_id:
                    return False, "Only the learner can confirm completion."

            # Update request
            conn.execute(
                "UPDATE requests SET status = ?, updated_at = ? WHERE id = ?",
                (new_status, now_str, request_id),
            )

            # If request is completed or cancelled, sync associated scheduled session if any
            if new_status in ("completed", "cancelled"):
                conn.execute(
                    "UPDATE sessions SET status = ? WHERE request_id = ? AND status = 'scheduled'",
                    (new_status, request_id),
                )

        return True, f"Request {new_status}."
    finally:
        conn.close()


def get_request_by_id(request_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve full details of a specific request."""
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT r.*, s.name AS skill, s.category,
                   l.name AS learner, l.department AS learner_dept,
                   p.name AS provider, p.department AS provider_dept
            FROM requests r
            JOIN skills s ON s.id = r.skill_id
            JOIN users l ON l.id = r.learner_id
            JOIN users p ON p.id = r.provider_id
            WHERE r.id = ?
            """,
            (request_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
