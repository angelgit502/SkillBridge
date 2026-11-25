"""Feedback, ratings, and student report handling business logic (no Streamlit code)."""
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Tuple, Optional

from db.database import get_connection
from services.auth import is_active_user

IST = ZoneInfo("Asia/Kolkata")


def submit_feedback(
    session_id: int, learner_id: int, rating: int, comment: str
) -> Tuple[bool, str]:
    """Learner submits 1-5 star rating and comment for a completed session."""
    if not (1 <= rating <= 5):
        return False, "Rating must be between 1 and 5."

    clean_comment = (comment or "").strip()
    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        with conn:
            # Validate session and learner identity
            row = conn.execute(
                """
                SELECT s.id, s.status, r.learner_id, r.status AS request_status
                FROM sessions s
                JOIN requests r ON r.id = s.request_id
                WHERE s.id = ?
                """,
                (session_id,),
            ).fetchone()

            if not row:
                return False, "Session not found."

            if row["learner_id"] != learner_id:
                return False, "Only the learner who attended this session can submit feedback."

            if not is_active_user(conn, learner_id, "student"):
                return False, "Your student account is not active."

            if row["status"] != "completed":
                return False, "Feedback can only be submitted for completed sessions."

            if row["request_status"] != "completed":
                return False, "Feedback is available only after the learner confirms completion."

            # Check if feedback already submitted
            existing = conn.execute(
                "SELECT 1 FROM feedback WHERE session_id = ?", (session_id,)
            ).fetchone()
            if existing:
                return False, "Feedback has already been submitted for this session."

            conn.execute(
                """
                INSERT INTO feedback (session_id, rating, comment, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, rating, clean_comment, now_str),
            )
        return True, "Feedback submitted successfully."
    except sqlite3.IntegrityError:
        return False, "Feedback has already been recorded for this session."
    finally:
        conn.close()


def get_unreviewed_sessions(learner_id: int) -> List[Dict[str, Any]]:
    """Get completed sessions attended by the learner that have no feedback yet."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT s.id, s.created_at, sl.start_time, sl.end_time,
                   sk.name AS skill, p.name AS provider
            FROM sessions s
            JOIN requests r ON r.id = s.request_id
            JOIN skills sk ON sk.id = r.skill_id
            JOIN users p ON p.id = r.provider_id
            JOIN slots sl ON sl.id = s.slot_id
            LEFT JOIN feedback f ON f.session_id = s.id
            WHERE r.learner_id = ? AND r.status = 'completed'
              AND s.status = 'completed' AND f.id IS NULL
            ORDER BY sl.start_time DESC
            """,
            (learner_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_feedback_given(learner_id: int) -> List[Dict[str, Any]]:
    """Fetch all feedback submitted by the learner."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT f.id, f.rating, f.comment, f.created_at,
                   sk.name AS skill, p.name AS provider
            FROM feedback f
            JOIN sessions s ON s.id = f.session_id
            JOIN requests r ON r.id = s.request_id
            JOIN skills sk ON sk.id = r.skill_id
            JOIN users p ON p.id = r.provider_id
            WHERE r.learner_id = ?
            ORDER BY f.created_at DESC
            """,
            (learner_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_feedback_received(provider_id: int) -> List[Dict[str, Any]]:
    """Fetch all feedback received by the provider for teaching."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT f.id, f.rating, f.comment, f.created_at,
                   sk.name AS skill, l.name AS learner
            FROM feedback f
            JOIN sessions s ON s.id = f.session_id
            JOIN requests r ON r.id = s.request_id
            JOIN skills sk ON sk.id = r.skill_id
            JOIN users l ON l.id = r.learner_id
            WHERE r.provider_id = ?
            ORDER BY f.created_at DESC
            """,
            (provider_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create_report(
    reporter_id: int,
    target_type: str,
    reason: str,
    target_user_id: Optional[int] = None,
    target_skill_id: Optional[int] = None,
) -> Tuple[bool, str]:
    """Any student can report a user or skill listing with a reason."""
    clean_reason = (reason or "").strip()
    if not clean_reason:
        return False, "Please provide a reason for the report."

    if target_type not in ("user", "skill_listing"):
        return False, "Invalid report target type."

    if target_type == "user":
        if target_user_id is None or target_skill_id is not None:
            return False, "Select a valid student to report."
    elif target_skill_id is None:
        return False, "Select a skill listing to report."

    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        with conn:
            if not is_active_user(conn, reporter_id, "student"):
                return False, "Only active students may submit reports."

            if target_type == "user":
                target = conn.execute(
                    "SELECT 1 FROM users WHERE id = ? AND role = 'student'",
                    (target_user_id,),
                ).fetchone()
            else:
                target = conn.execute(
                    "SELECT 1 FROM skills WHERE id = ?", (target_skill_id,)
                ).fetchone()
                if target and target_user_id is not None:
                    target = conn.execute(
                        """
                        SELECT 1
                        FROM user_skills
                        WHERE user_id = ? AND skill_id = ?
                          AND kind = 'teach' AND is_hidden = 0
                        """,
                        (target_user_id, target_skill_id),
                    ).fetchone()

            if not target:
                return False, "The selected report target is no longer available."

            conn.execute(
                """
                INSERT INTO reports (reporter_id, target_type, target_user_id, target_skill_id, reason, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'open', ?)
                """,
                (reporter_id, target_type, target_user_id, target_skill_id, clean_reason, now_str),
            )
        return True, "Report submitted to administrators."
    except sqlite3.IntegrityError:
        return False, "The selected report target is no longer available."
    finally:
        conn.close()


def report_request_issue(
    request_id: int, learner_id: int, reason: str
) -> Tuple[bool, str]:
    """Report an issue with an awaiting-confirmation request to the admin queue."""
    clean_reason = (reason or "").strip()
    if not clean_reason:
        return False, "Please describe the issue."

    conn = get_connection()
    try:
        with conn:
            request = conn.execute(
                """
                SELECT learner_id, provider_id, status
                FROM requests
                WHERE id = ?
                """,
                (request_id,),
            ).fetchone()
            if not request:
                return False, "Learning request not found."
            if request["learner_id"] != learner_id:
                return False, "Only the learner who made the request can report an issue."
            if not is_active_user(conn, learner_id, "student"):
                return False, "Your student account is not active."
            if request["status"] != "awaiting_confirmation":
                return False, "Issues can only be reported while awaiting learner confirmation."

            try:
                conn.execute(
                    """
                    INSERT INTO reports
                        (reporter_id, target_type, target_user_id, request_id,
                         reason, status, created_at)
                    VALUES (?, 'user', ?, ?, ?, 'open', ?)
                    """,
                    (
                        learner_id,
                        request["provider_id"],
                        request_id,
                        clean_reason,
                        datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
            except sqlite3.IntegrityError:
                return False, "An issue has already been reported for this request."
        return True, "Issue reported to administrators. The request remains awaiting confirmation."
    finally:
        conn.close()
