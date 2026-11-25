"""Authentication and user account management (no Streamlit code)."""
import sqlite3
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, Tuple

from config import DEPARTMENTS
from db.database import get_connection
from db.security import hash_password, verify_password

EMAIL_DOMAIN = "@christuniversity.in"
EMAIL_PATTERN = re.compile(r"^[^@\s]+@christuniversity\.in$", re.IGNORECASE)
IST = ZoneInfo("Asia/Kolkata")


def login(email: str, password: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Authenticate a user by university email and password.

    Returns:
        (user_dict, error_message)
    """
    if not email or not password:
        return None, "Please enter both email and password."

    cleaned_email = email.strip().lower()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ? COLLATE NOCASE", (cleaned_email,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None, "Invalid email or password."

    if not row["is_active"]:
        return None, "Your account has been deactivated. Please contact an administrator."

    if not verify_password(password, row["password_hash"]):
        return None, "Invalid email or password."

    user_dict = {k: row[k] for k in row.keys() if k != "password_hash"}
    return user_dict, "Login successful."


def is_active_user(conn: sqlite3.Connection, user_id: int, role: Optional[str] = None) -> bool:
    """Return whether a user exists, is active, and optionally has the required role."""
    query = "SELECT 1 FROM users WHERE id = ? AND is_active = 1"
    params = [user_id]
    if role is not None:
        query += " AND role = ?"
        params.append(role)
    return conn.execute(query, params).fetchone() is not None


def register(
    name: str,
    email: str,
    department: str,
    password: str,
    confirm_password: Optional[str] = None,
) -> Tuple[bool, str]:
    """Register a new student account."""
    name = (name or "").strip()
    email = (email or "").strip().lower()

    if not name:
        return False, "Please enter your full name."

    if not EMAIL_PATTERN.fullmatch(email):
        return False, f"Email must be a valid CHRIST University email ending in {EMAIL_DOMAIN}."

    if not department or department not in DEPARTMENTS:
        return False, "Please select a valid department."

    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters."

    if confirm_password is not None and password != confirm_password:
        return False, "Passwords do not match."

    created_at = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        with conn:
            existing = conn.execute(
                "SELECT 1 FROM users WHERE email = ? COLLATE NOCASE", (email,)
            ).fetchone()
            if existing:
                return False, "An account with this email already exists."

            conn.execute(
                "INSERT INTO users (name, email, password_hash, department, role, is_active, created_at) "
                "VALUES (?, ?, ?, ?, 'student', 1, ?)",
                (name, email, hash_password(password), department, created_at),
            )
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch user details by ID."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, name, email, department, bio, role, is_active, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
