"""Session slot publishing, booking, and management business logic (no Streamlit code)."""
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Tuple, Optional

from db.database import get_connection
from services.auth import is_active_user

IST = ZoneInfo("Asia/Kolkata")


def publish_slot(provider_id: int, start_time: str, end_time: str) -> Tuple[bool, str]:
    """Provider publishes a time window for accepted requests."""
    start_time = (start_time or "").strip()
    end_time = (end_time or "").strip()

    if not start_time or not end_time:
        return False, "Please specify both start and end times."

    try:
        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    except ValueError:
        return False, "Start time must be formatted as 'YYYY-MM-DD HH:MM'."
    try:
        end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
    except ValueError:
        return False, "End time must be formatted as 'YYYY-MM-DD HH:MM'."

    if start_dt.strftime("%Y-%m-%d %H:%M") != start_time:
        return False, "Start time must be formatted as 'YYYY-MM-DD HH:MM'."
    if end_dt.strftime("%Y-%m-%d %H:%M") != end_time:
        return False, "End time must be formatted as 'YYYY-MM-DD HH:MM'."

    if end_time <= start_time:
        return False, "End time must be after start time."

    if start_dt.replace(tzinfo=IST) <= datetime.now(IST):
        return False, "Start time must be in the future."

    conn = get_connection()
    try:
        with conn:
            provider = conn.execute(
                "SELECT 1 FROM users WHERE id = ? AND role = 'student' AND is_active = 1",
                (provider_id,),
            ).fetchone()
            if not provider:
                return False, "Active student provider not found."

            conn.execute(
                "INSERT INTO slots (provider_id, start_time, end_time) VALUES (?, ?, ?)",
                (provider_id, start_time, end_time),
            )
        return True, "Slot published successfully."
    except sqlite3.Error as e:
        return False, f"Failed to publish slot: {str(e)}"
    finally:
        conn.close()


def get_provider_available_slots(
    provider_id: int, future_only: bool = False
) -> List[Dict[str, Any]]:
    """Get slots published by provider that are not yet booked in any active session."""
    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M")
    conn = get_connection()
    try:
        time_filter = "AND s.start_time > ?" if future_only else ""
        params = (provider_id, now_str) if future_only else (provider_id,)
        rows = conn.execute(
            f"""
            SELECT s.id, s.provider_id, s.start_time, s.end_time
            FROM slots s
            LEFT JOIN sessions sess ON sess.slot_id = s.id
            JOIN users provider ON provider.id = s.provider_id
            WHERE s.provider_id = ? AND sess.id IS NULL
              AND provider.role = 'student' AND provider.is_active = 1
              {time_filter}
            ORDER BY s.start_time ASC
            """,
            params,
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_slot(slot_id: int, provider_id: int) -> Tuple[bool, str]:
    """Delete an unbooked slot."""
    conn = get_connection()
    try:
        with conn:
            if not is_active_user(conn, provider_id, "student"):
                return False, "Your student account is not active."

            booked = conn.execute(
                "SELECT 1 FROM sessions WHERE slot_id = ?", (slot_id,)
            ).fetchone()
            if booked:
                return False, "Cannot delete a slot that has already been booked."

            cur = conn.execute(
                "DELETE FROM slots WHERE id = ? AND provider_id = ?",
                (slot_id, provider_id),
            )
            if cur.rowcount == 0:
                return False, "Slot not found or unauthorized."
        return True, "Slot deleted."
    finally:
        conn.close()


def book_slot_for_request(
    request_id: int, slot_id: int, learner_id: int
) -> Tuple[bool, str]:
    """Book a slot and create the session in one atomic transaction."""
    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        with conn:
            # Validate request
            req = conn.execute(
                "SELECT id, learner_id, provider_id, status FROM requests WHERE id = ?",
                (request_id,),
            ).fetchone()

            if not req:
                return False, "Request not found."

            if req["status"] != "accepted":
                return False, f"Cannot schedule session for request with status '{req['status']}'."

            if req["learner_id"] != learner_id:
                return False, "Only the learner who made the request can book this session."

            if not is_active_user(conn, learner_id, "student"):
                return False, "Your student account is not active."

            if not is_active_user(conn, req["provider_id"], "student"):
                return False, "The skill provider's account is not active."

            # Ensure request does not already have an active/scheduled session
            existing_sess = conn.execute(
                "SELECT id, status FROM sessions WHERE request_id = ?", (request_id,)
            ).fetchone()
            if existing_sess:
                return (
                    False,
                    f"This request already has an associated session ({existing_sess['status']}).",
                )

            # Validate slot
            slot = conn.execute(
                "SELECT id, provider_id, start_time FROM slots WHERE id = ?", (slot_id,)
            ).fetchone()
            if not slot:
                return False, "Selected slot does not exist."

            if slot["provider_id"] != req["provider_id"]:
                return False, "The slot does not belong to the skill provider."

            if slot["start_time"] <= datetime.now(IST).strftime("%Y-%m-%d %H:%M"):
                return False, "Past time slots cannot be booked."

            # Check if slot is already booked
            already_booked = conn.execute(
                "SELECT 1 FROM sessions WHERE slot_id = ?", (slot_id,)
            ).fetchone()
            if already_booked:
                return False, "This slot has already been booked by another student."

            # Atomic session creation
            conn.execute(
                """
                INSERT INTO sessions (request_id, slot_id, status, created_at)
                VALUES (?, ?, 'scheduled', ?)
                """,
                (request_id, slot_id, now_str),
            )

        return True, "Session booked successfully."
    except sqlite3.IntegrityError:
        return False, "Failed to book slot due to a booking conflict."
    finally:
        conn.close()


def change_session_status(
    session_id: int, actor_id: int, new_status: str
) -> Tuple[bool, str]:
    """Cancel a scheduled session; completion is confirmed through request status."""
    if new_status != "cancelled":
        return False, "Session completion must be confirmed through the learning request."

    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        with conn:
            row = conn.execute(
                """
                SELECT s.id, s.status, s.request_id, r.status AS request_status,
                       r.learner_id, r.provider_id
                FROM sessions s
                JOIN requests r ON r.id = s.request_id
                WHERE s.id = ?
                """,
                (session_id,),
            ).fetchone()

            if not row:
                return False, "Session not found."

            if actor_id not in (row["learner_id"], row["provider_id"]):
                return False, "You do not have permission to modify this session."

            if not is_active_user(conn, actor_id, "student"):
                return False, "Your student account is not active."

            if row["request_status"] != "accepted":
                return False, "Only sessions for accepted requests can be cancelled."

            if row["status"] in ("completed", "cancelled"):
                return False, f"Session is already {row['status']}."

            conn.execute(
                "UPDATE sessions SET status = ? WHERE id = ?", (new_status, session_id)
            )

            conn.execute(
                "UPDATE requests SET status = ?, updated_at = ? WHERE id = ?",
                (new_status, now_str, row["request_id"]),
            )

        return True, f"Session marked as {new_status}."
    finally:
        conn.close()


def get_user_sessions(user_id: int, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all sessions for a user (as learner or provider)."""
    sql = """
        SELECT sess.id, sess.request_id, sess.slot_id, sess.status, sess.created_at,
               sl.start_time, sl.end_time,
               sk.name AS skill, sk.category,
               r.status AS request_status,
               l.id AS learner_id, l.name AS learner, l.department AS learner_dept,
               p.id AS provider_id, p.name AS provider, p.department AS provider_dept,
               f.id AS feedback_id, f.rating, f.comment
        FROM sessions sess
        JOIN slots sl ON sl.id = sess.slot_id
        JOIN requests r ON r.id = sess.request_id
        JOIN skills sk ON sk.id = r.skill_id
        JOIN users l ON l.id = r.learner_id
        JOIN users p ON p.id = r.provider_id
        LEFT JOIN feedback f ON f.session_id = sess.id
        WHERE (l.id = ? OR p.id = ?)
    """
    params = [user_id, user_id]

    if status_filter and status_filter != "All":
        sql += " AND sess.status = ?"
        params.append(status_filter.lower())

    sql += " ORDER BY sl.start_time ASC"

    conn = get_connection()
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_next_session(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve the nearest upcoming scheduled session for the user."""
    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M")
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT sess.id, sess.status, sl.start_time, sl.end_time,
                   sk.name AS skill, sk.category,
                   l.id AS learner_id, l.name AS learner, l.department AS learner_dept,
                   p.id AS provider_id, p.name AS provider, p.department AS provider_dept
            FROM sessions sess
            JOIN slots sl ON sl.id = sess.slot_id
            JOIN requests r ON r.id = sess.request_id
            JOIN skills sk ON sk.id = r.skill_id
            JOIN users l ON l.id = r.learner_id
            JOIN users p ON p.id = r.provider_id
            WHERE (l.id = ? OR p.id = ?)
              AND sess.status = 'scheduled'
              AND sl.end_time >= ?
            ORDER BY sl.start_time ASC
            LIMIT 1
            """,
            (user_id, user_id, now_str),
        ).fetchone()

        if row:
            return dict(row)

        return None
    finally:
        conn.close()
