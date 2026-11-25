"""Sample data seeding helpers."""
"""Fill skillbridge.db with sample data for testing and the demo.

Run from the project root:
    python -m db.seed            # adds data if the database is empty
    python -m db.seed --reset    # clears all data, then seeds again
"""
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from db.database import get_connection
from db.security import hash_password

# Students share one demo password, so you can always log in during the demo.
DEMO_PASSWORD = "Demo@1234"
ADMIN_EMAIL = "admin@christuniversity.in"
ADMIN_PASSWORD = os.environ.get("SKILLBRIDGE_ADMIN_PASSWORD", "Admin@1234")

SKILLS = [
    ("Python", "Programming"),
    ("Java", "Programming"),
    ("Graphic Design", "Design"),
    ("Figma", "Design"),
    ("Public Speaking", "Soft Skills"),
    ("Excel", "Productivity"),
    ("Guitar", "Music"),
    ("Machine Learning", "Data"),
    ("Data Visualization", "Data"),
]

# (name, email, department, bio)
STUDENTS = [
    ("Asha Menon", "asha.menon@christuniversity.in", "Computer Science",
     "Enjoys teaching Python and basic data structures."),
    ("Rahul Verma", "rahul.verma@christuniversity.in", "Commerce",
     "Learning Python for finance analytics."),
    ("Meera Thomas", "meera.thomas@christuniversity.in", "Design",
     "Graphic designer who likes Figma."),
    ("Arjun Nair", "arjun.nair@christuniversity.in", "Computer Science",
     "Public speaking coach and club debater."),
    ("Priya Kapoor", "priya.kapoor@christuniversity.in", "Psychology",
     "Wants to learn graphic design. Plays guitar on weekends."),
]

# (email, skill name, kind) where kind is 'teach' or 'learn'
USER_SKILLS = [
    ("asha.menon@christuniversity.in", "Python", "teach"),
    ("asha.menon@christuniversity.in", "Figma", "learn"),
    ("rahul.verma@christuniversity.in", "Excel", "teach"),
    ("rahul.verma@christuniversity.in", "Python", "learn"),
    ("meera.thomas@christuniversity.in", "Graphic Design", "teach"),
    ("meera.thomas@christuniversity.in", "Figma", "teach"),
    ("meera.thomas@christuniversity.in", "Public Speaking", "learn"),
    ("arjun.nair@christuniversity.in", "Public Speaking", "teach"),
    ("arjun.nair@christuniversity.in", "Python", "learn"),
    ("priya.kapoor@christuniversity.in", "Guitar", "teach"),
    ("priya.kapoor@christuniversity.in", "Graphic Design", "learn"),
]

def reset(conn):
    # Delete children first so the order doesn't matter with foreign keys.
    for table in ["feedback", "sessions", "slots", "reports",
                  "requests", "user_skills", "skills", "users"]:
        conn.execute(f"DELETE FROM {table}")
    conn.execute("DELETE FROM sqlite_sequence")

def seed(conn):
    ist = ZoneInfo("Asia/Kolkata")
    now = datetime.now(ist)
    accepted_start = (now + timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)
    accepted_end = accepted_start + timedelta(hours=1)
    completed_start = (now - timedelta(days=7)).replace(hour=14, minute=0, second=0, microsecond=0)
    completed_end = completed_start + timedelta(hours=1)

    # Admin and students
    user_ids = {}
    conn.execute(
        "INSERT INTO users (name, email, password_hash, department, bio, role) "
        "VALUES (?, ?, ?, ?, ?, 'admin')",
        ("Skillbridge Admin", ADMIN_EMAIL, hash_password(ADMIN_PASSWORD),
         "Administration", "Platform administrator"),
    )
    for name, email, dept, bio in STUDENTS:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, department, bio) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, email, hash_password(DEMO_PASSWORD), dept, bio),
        )
        user_ids[email] = cur.lastrowid

    # Skills
    conn.executemany("INSERT INTO skills (name, category) VALUES (?, ?)", SKILLS)
    skill_ids = {row["name"]: row["id"]
                 for row in conn.execute("SELECT id, name FROM skills")}

    # Which skills each student teaches or wants to learn
    for email, skill, kind in USER_SKILLS:
        conn.execute(
            "INSERT INTO user_skills (user_id, skill_id, kind) VALUES (?, ?, ?)",
            (user_ids[email], skill_ids[skill], kind),
        )

    # Requests (learner, provider, skill, message, status)
    def add_request(learner, provider, skill, message, status):
        cur = conn.execute(
            "INSERT INTO requests (learner_id, provider_id, skill_id, message, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_ids[learner], user_ids[provider], skill_ids[skill], message, status),
        )
        return cur.lastrowid

    def add_slot(provider, start, end):
        cur = conn.execute(
            "INSERT INTO slots (provider_id, start_time, end_time) VALUES (?, ?, ?)",
            (user_ids[provider], start, end),
        )
        return cur.lastrowid

    def add_session(request_id, slot_id, status):
        cur = conn.execute(
            "INSERT INTO sessions (request_id, slot_id, status) VALUES (?, ?, ?)",
            (request_id, slot_id, status),
        )
        return cur.lastrowid

    # 1. Pending request, nothing scheduled yet
    add_request("rahul.verma@christuniversity.in", "asha.menon@christuniversity.in",
                "Python", "Need Python basics for my finance dashboard project.",
                "pending")

    # 2. Accepted request with a scheduled session in the future
    req = add_request("arjun.nair@christuniversity.in", "asha.menon@christuniversity.in",
                      "Python", "Can we cover loops and functions?", "accepted")
    slot = add_slot("asha.menon@christuniversity.in",
                    accepted_start.strftime("%Y-%m-%d %H:%M"),
                    accepted_end.strftime("%Y-%m-%d %H:%M"))
    add_session(req, slot, "scheduled")

    # 3. Completed session with feedback
    req = add_request("priya.kapoor@christuniversity.in", "meera.thomas@christuniversity.in",
                      "Graphic Design", "Want to learn poster design basics.", "completed")
    slot = add_slot("meera.thomas@christuniversity.in",
                    completed_start.strftime("%Y-%m-%d %H:%M"),
                    completed_end.strftime("%Y-%m-%d %H:%M"))
    session_id = add_session(req, slot, "completed")
    conn.execute(
        "INSERT INTO feedback (session_id, rating, comment) VALUES (?, ?, ?)",
        (session_id, 5, "Clear explanations and useful exercises."),
    )

    # 4. Rejected request
    add_request("meera.thomas@christuniversity.in", "arjun.nair@christuniversity.in",
                "Public Speaking", "Would like tips for presentations.", "rejected")

    # 5. One open report against a skill listing
    conn.execute(
        "INSERT INTO reports (reporter_id, target_type, target_skill_id, reason) "
        "VALUES (?, 'skill_listing', ?, ?)",
        (user_ids["priya.kapoor@christuniversity.in"], skill_ids["Guitar"],
         "Listing has no description of the lessons offered."),
    )

def seed_if_empty():
    """Load the demo dataset only when the database has no users."""
    conn = get_connection()
    try:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
            return False
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
                seed(conn)
                return True
        return False
    finally:
        conn.close()

def main():
    conn = get_connection()
    try:
        with conn:  # commits on success, rolls back on error
            if "--reset" in sys.argv:
                reset(conn)
            elif conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
                print("Database already has data. Run with --reset to rebuild it.")
                return
            seed(conn)
        print("Sample data loaded.")
        print(f"Admin login:   {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"Student login: any student email / {DEMO_PASSWORD}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()