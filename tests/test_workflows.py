import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import db.database as database
import db.init_db as init_db
from db.seed import ADMIN_EMAIL, ADMIN_PASSWORD, seed, seed_if_empty
from services.admin import get_all_students, open_reports, resolve_report, toggle_user_active
from services.analytics import (
    load_feedback,
    load_ratings,
    load_requests,
    load_sessions_analytics,
    load_skills_summary,
    load_students,
)
from services.auth import get_user_by_id, login, register
from services.feedback import (
    create_report,
    get_feedback_given,
    get_feedback_received,
    get_unreviewed_sessions,
    report_request_issue,
    submit_feedback,
)
from services.profile import (
    add_user_skill,
    get_user_skills,
    remove_user_skill,
    toggle_skill_hidden,
    update_profile,
)
from services.requests import (
    change_status,
    count_incoming_pending,
    create_request,
    fetch_requests,
    get_request_by_id,
)
from services.sessions import (
    book_slot_for_request,
    change_session_status,
    delete_slot,
    get_next_session,
    get_provider_available_slots,
    get_user_sessions,
    publish_slot,
)
from services.skills import (
    add_or_get_skill,
    get_all_skills,
    get_categories,
    get_departments,
    get_popular_skills,
    search_listings,
)

IST = ZoneInfo("Asia/Kolkata")


def test_new_database_does_not_insert_sample_accounts(tmp_path, monkeypatch):
    db_path = str(tmp_path / "empty.db")
    monkeypatch.setattr(database, "DB_PATH", db_path)
    monkeypatch.setattr(init_db, "DB_PATH", db_path)

    database.ensure_db()
    conn = database.get_connection()
    try:
        assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
    finally:
        conn.close()


def test_login_database_is_seeded_once_for_demo_accounts(tmp_path, monkeypatch):
    db_path = str(tmp_path / "demo.db")
    monkeypatch.setattr(database, "DB_PATH", db_path)
    monkeypatch.setattr(init_db, "DB_PATH", db_path)

    database.ensure_db()
    assert seed_if_empty() is True
    assert seed_if_empty() is False

    for _ in range(10):
        user, message = login("asha.menon@christuniversity.in", "Demo@1234")
        assert user is not None, message


def test_streamlit_login_accepts_valid_credentials_on_first_submit():
    from pathlib import Path
    from streamlit.testing.v1 import AppTest

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=20)
    app.session_state["auth_page"] = "login"
    app.run()
    app.text_input[0].set_value("arjun.nair@christuniversity.in")
    app.text_input[1].set_value("Demo@1234")

    submit = next(button for button in app.button if "Sign In to SkillBridge" in button.label)
    submit.click()
    app.run()

    assert app.session_state["user"]["email"] == "arjun.nair@christuniversity.in"
    assert not app.exception


def test_request_status_migration_preserves_existing_records(tmp_path, monkeypatch):
    db_path = str(tmp_path / "legacy.db")
    monkeypatch.setattr(database, "DB_PATH", db_path)
    monkeypatch.setattr(init_db, "DB_PATH", db_path)

    legacy_schema = init_db.SCHEMA_FILE.read_text(encoding="utf-8")
    legacy_schema = legacy_schema.replace(
        "'pending','accepted','awaiting_confirmation','rejected','completed','cancelled'",
        "'pending','accepted','rejected','completed','cancelled'",
    ).replace(
        "    request_id   INTEGER REFERENCES requests(id) ON DELETE CASCADE,\n",
        "",
    )
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(legacy_schema)
    with conn:
        seed(conn)
    before = {
        table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ("requests", "sessions", "feedback", "reports")
    }
    conn.close()

    init_db.init_db()

    conn = sqlite3.connect(db_path)
    try:
        after = {
            table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("requests", "sessions", "feedback", "reports")
        }
        assert after == before
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        assert "request_id" in {
            row[1] for row in conn.execute("PRAGMA table_info(reports)").fetchall()
        }
        accepted_id = conn.execute(
            "SELECT id FROM requests WHERE status = 'accepted' LIMIT 1"
        ).fetchone()[0]
        conn.execute(
            "UPDATE requests SET status = 'awaiting_confirmation' WHERE id = ?",
            (accepted_id,),
        )
        conn.commit()
        assert conn.execute(
            "SELECT status FROM requests WHERE id = ?", (accepted_id,)
        ).fetchone()[0] == "awaiting_confirmation"
    finally:
        conn.close()


def test_student_and_admin_workflow_persists_across_service_reads():
    email = "workflow.learner@christuniversity.in"
    password = "SkillBridgeTest123!"
    created, message = register(
        "Workflow Learner",
        email,
        "Engineering",
        password,
        password,
    )
    assert created, message

    learner, message = login(email, password)
    assert learner is not None, message
    provider, message = login("asha.menon@christuniversity.in", "Demo@1234")
    assert provider is not None, message
    admin, message = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    assert admin is not None, message

    user_id = learner["id"]
    provider_id = provider["id"]
    python_id = next(skill["id"] for skill in get_all_skills() if skill["name"] == "Python")
    assert "Engineering" in get_departments()
    assert "Programming" in get_categories()
    assert get_popular_skills(limit=3)

    custom_skill_id, message = add_or_get_skill("Workflow Skill", "Academics", actor_id=user_id)
    assert custom_skill_id, message
    duplicate_skill_id, _ = add_or_get_skill("workflow skill", "Other", actor_id=user_id)
    assert duplicate_skill_id == custom_skill_id

    assert add_user_skill(user_id, python_id, "teach")[0]
    assert add_user_skill(user_id, python_id, "learn")[0]
    assert add_user_skill(user_id, custom_skill_id, "learn")[0]
    assert {skill["kind"] for skill in get_user_skills(user_id, "teach")} == {"teach"}
    assert any(
        listing["provider_id"] == user_id
        for listing in search_listings("Python")
    )
    assert toggle_skill_hidden(user_id, python_id, True)[0]
    assert all(
        listing["provider_id"] != user_id
        for listing in search_listings("Python")
    )
    assert toggle_skill_hidden(user_id, python_id, False)[0]

    updated, message = update_profile(user_id, "Updated Learner", "Design", "Learning together.")
    assert updated, message
    saved_profile = get_user_by_id(user_id)
    assert saved_profile["name"] == "Updated Learner"
    assert saved_profile["department"] == "Design"
    assert saved_profile["bio"] == "Learning together."

    created, message = create_request(
        user_id,
        provider_id,
        python_id,
        "I would like help with Python fundamentals.",
    )
    assert created, message
    request = next(
        request for request in fetch_requests(user_id, as_provider=False)
        if request["learner_id"] == user_id
    )
    assert get_request_by_id(request["id"])["status"] == "pending"
    assert count_incoming_pending(provider_id) >= 1
    assert change_status(request["id"], provider_id, "accepted")[0]

    start = (datetime.now(IST) + timedelta(days=14)).replace(
        hour=15, minute=0, second=0, microsecond=0
    )
    start_text = start.strftime("%Y-%m-%d %H:%M")
    end_text = (start + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    assert publish_slot(provider_id, start_text, end_text)[0]
    slot = next(
        slot for slot in get_provider_available_slots(provider_id)
        if slot["start_time"] == start_text
    )
    assert book_slot_for_request(request["id"], slot["id"], user_id)[0]

    learner_sessions = get_user_sessions(user_id)
    session = next(item for item in learner_sessions if item["request_id"] == request["id"])
    assert any(item["request_id"] == request["id"] for item in get_user_sessions(provider_id))
    assert len(get_user_sessions(user_id, status_filter="scheduled")) == 1
    assert get_next_session(user_id)["id"] == session["id"]
    assert all(item["id"] != slot["id"] for item in get_provider_available_slots(provider_id))
    assert change_session_status(session["id"], provider_id, "completed")[0] is False
    assert change_status(request["id"], user_id, "awaiting_confirmation")[0] is False
    assert change_status(request["id"], provider_id, "completed")[0] is False
    assert change_status(request["id"], provider_id, "awaiting_confirmation")[0]
    waiting_request = get_request_by_id(request["id"])
    assert waiting_request["status"] == "awaiting_confirmation"
    assert next(
        item for item in fetch_requests(user_id, as_provider=False)
        if item["id"] == request["id"]
    )["status"] == next(
        item for item in fetch_requests(provider_id, as_provider=True)
        if item["id"] == request["id"]
    )["status"] == "awaiting_confirmation"
    assert change_status(request["id"], provider_id, "awaiting_confirmation")[0] is False
    assert change_status(request["id"], provider_id, "completed")[0] is False
    issue_reported, message = report_request_issue(
        request["id"], user_id, "The session needs follow-up."
    )
    assert issue_reported, message
    assert report_request_issue(
        request["id"], user_id, "Submitting the same issue twice."
    )[0] is False
    assert next(
        item for item in fetch_requests(user_id, as_provider=False)
        if item["id"] == request["id"]
    )["issue_reported"] == 1
    assert submit_feedback(session["id"], user_id, 5, "Not confirmed yet.")[0] is False
    assert change_status(request["id"], provider_id, "completed")[0] is False
    assert change_status(request["id"], user_id, "completed")[0]
    assert get_request_by_id(request["id"])["status"] == "completed"
    assert get_user_sessions(user_id)[0]["request_status"] == "completed"
    assert len(get_user_sessions(user_id, status_filter="completed")) == 1
    assert next(
        item for item in fetch_requests(user_id, as_provider=False)
        if item["id"] == request["id"]
    )["status"] == "completed"

    unreviewed = next(
        item for item in get_unreviewed_sessions(user_id)
        if item["id"] == session["id"]
    )
    assert submit_feedback(unreviewed["id"], user_id, 5, "Clear and helpful.")[0]
    assert any(
        item["provider"] == provider["name"]
        for item in get_feedback_given(user_id)
    )
    assert any(
        item["learner"] == "Updated Learner"
        for item in get_feedback_received(provider_id)
    )

    canceled, message = create_request(
        user_id,
        provider_id,
        python_id,
        "I would like to practice another Python topic.",
    )
    assert canceled, message
    canceled_request = next(
        item for item in fetch_requests(user_id, as_provider=False)
        if item["status"] == "pending"
    )
    assert change_status(canceled_request["id"], provider_id, "accepted")[0]
    cancel_start = (datetime.now(IST) + timedelta(days=16)).replace(
        hour=15, minute=0, second=0, microsecond=0
    )
    cancel_start_text = cancel_start.strftime("%Y-%m-%d %H:%M")
    cancel_end_text = (cancel_start + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    assert publish_slot(provider_id, cancel_start_text, cancel_end_text)[0]
    cancel_slot = next(
        item for item in get_provider_available_slots(provider_id, future_only=True)
        if item["start_time"] == cancel_start_text
    )
    assert book_slot_for_request(canceled_request["id"], cancel_slot["id"], user_id)[0]
    cancel_session = next(
        item for item in get_user_sessions(user_id)
        if item["request_id"] == canceled_request["id"]
    )
    assert change_session_status(cancel_session["id"], user_id, "cancelled")[0]
    assert next(
        item for item in fetch_requests(user_id, as_provider=False)
        if item["id"] == canceled_request["id"]
    )["status"] == "cancelled"

    cleanup_start = (datetime.now(IST) + timedelta(days=20)).replace(
        hour=15, minute=0, second=0, microsecond=0
    )
    cleanup_end = cleanup_start + timedelta(hours=1)
    assert publish_slot(
        provider_id,
        cleanup_start.strftime("%Y-%m-%d %H:%M"),
        cleanup_end.strftime("%Y-%m-%d %H:%M"),
    )[0]
    cleanup_slot = next(
        item for item in get_provider_available_slots(provider_id)
        if item["start_time"] == cleanup_start.strftime("%Y-%m-%d %H:%M")
    )
    assert delete_slot(cleanup_slot["id"], provider_id)[0]
    assert all(
        item["id"] != cleanup_slot["id"]
        for item in get_provider_available_slots(provider_id)
    )

    reported, message = create_report(
        reporter_id=user_id,
        target_type="skill_listing",
        reason="Workflow test report.",
        target_user_id=provider_id,
        target_skill_id=python_id,
    )
    assert reported, message
    report = next(item for item in open_reports() if item["reason"] == "Workflow test report.")
    assert resolve_report(
        report["id"], actor_id=admin["id"], deactivate_user_id=provider_id
    )[0]
    inactive_provider, message = login("asha.menon@christuniversity.in", "Demo@1234")
    assert inactive_provider is None
    assert "deactivated" in message.lower()
    assert toggle_user_active(admin["id"], provider_id, 1)[0]

    assert any(student["id"] == user_id for student in get_all_students())
    assert any(student["id"] == user_id for _, student in load_students("All").iterrows())
    assert not load_requests("All").empty
    assert not load_sessions_analytics("All").empty
    assert not load_feedback("All").empty
    assert not load_ratings("All").empty
    assert not load_skills_summary().empty
    assert remove_user_skill(user_id, python_id, "teach")[0]
    assert remove_user_skill(user_id, python_id, "learn")[0]
    assert remove_user_skill(user_id, custom_skill_id, "learn")[0]
    assert not get_user_skills(user_id, "teach")


def test_deactivated_student_cannot_perform_restricted_actions():
    learner, message = login("priya.kapoor@christuniversity.in", "Demo@1234")
    assert learner is not None, message
    provider, message = login("asha.menon@christuniversity.in", "Demo@1234")
    assert provider is not None, message
    second_provider, message = login("meera.thomas@christuniversity.in", "Demo@1234")
    assert second_provider is not None, message
    admin, message = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    assert admin is not None, message

    skills = {skill["name"]: skill["id"] for skill in get_all_skills()}
    created, message = create_request(
        learner["id"], provider["id"], skills["Python"], "Please help me learn Python."
    )
    assert created, message
    request = next(
        item for item in fetch_requests(learner["id"], as_provider=False)
        if item["status"] == "pending" and item["provider_id"] == provider["id"]
    )
    assert change_status(request["id"], provider["id"], "accepted")[0]

    def future_times(days):
        start = (datetime.now(IST) + timedelta(days=days)).replace(
            hour=15, minute=0, second=0, microsecond=0
        )
        return start.strftime("%Y-%m-%d %H:%M"), (
            start + timedelta(hours=1)
        ).strftime("%Y-%m-%d %H:%M")

    start_text, end_text = future_times(25)
    assert publish_slot(provider["id"], start_text, end_text)[0]
    slot = next(
        item for item in get_provider_available_slots(provider["id"])
        if item["start_time"] == start_text
    )
    assert book_slot_for_request(request["id"], slot["id"], learner["id"])[0]
    session = next(
        item for item in get_user_sessions(learner["id"])
        if item["request_id"] == request["id"]
    )
    assert change_session_status(session["id"], provider["id"], "completed")[0] is False
    assert change_status(request["id"], provider["id"], "awaiting_confirmation")[0]
    assert change_status(request["id"], learner["id"], "completed")[0]

    second_created, message = create_request(
        learner["id"],
        second_provider["id"],
        skills["Graphic Design"],
        "Please help me learn graphic design.",
    )
    assert second_created, message
    pending_second = next(
        item for item in fetch_requests(learner["id"], as_provider=False)
        if item["status"] == "pending" and item["provider_id"] == second_provider["id"]
    )
    assert change_status(pending_second["id"], second_provider["id"], "accepted")[0]
    second_start, second_end = future_times(27)
    assert publish_slot(second_provider["id"], second_start, second_end)[0]
    second_slot = next(
        item for item in get_provider_available_slots(second_provider["id"])
        if item["start_time"] == second_start
    )

    own_start, own_end = future_times(29)
    assert publish_slot(learner["id"], own_start, own_end)[0]
    own_slot = next(
        item for item in get_provider_available_slots(learner["id"])
        if item["start_time"] == own_start
    )
    report_ok, message = create_report(
        reporter_id=learner["id"],
        target_type="skill_listing",
        reason="Test report before deactivation.",
        target_user_id=provider["id"],
        target_skill_id=skills["Python"],
    )
    assert report_ok, message
    report = next(
        item for item in open_reports()
        if item["reason"] == "Test report before deactivation."
    )

    assert toggle_user_active(admin["id"], learner["id"], 0)[0]
    assert get_user_by_id(learner["id"])["is_active"] == 0

    assert create_request(
        learner["id"], provider["id"], skills["Python"], "Another request."
    )[0] is False
    assert create_report(
        learner["id"], "skill_listing", "Inactive reporter.", provider["id"], skills["Python"]
    )[0] is False
    assert book_slot_for_request(pending_second["id"], second_slot["id"], learner["id"])[0] is False
    assert submit_feedback(session["id"], learner["id"], 5, "Good session.")[0] is False
    assert change_status(pending_second["id"], learner["id"], "cancelled")[0] is False
    assert change_session_status(session["id"], learner["id"], "cancelled")[0] is False
    assert publish_slot(learner["id"], *future_times(31))[0] is False
    assert delete_slot(own_slot["id"], learner["id"])[0] is False
    assert update_profile(learner["id"], "Inactive", "Design", "")[0] is False
    assert add_user_skill(learner["id"], skills["Python"], "teach")[0] is False
    assert remove_user_skill(learner["id"], skills["Python"], "learn")[0] is False
    assert toggle_skill_hidden(learner["id"], skills["Excel"], True)[0] is False
    assert add_or_get_skill("Inactive Skill", actor_id=learner["id"])[0] is None
    assert resolve_report(report["id"], actor_id=learner["id"])[0] is False
    assert toggle_user_active(learner["id"], provider["id"], 0)[0] is False


def test_invalid_database_actions_report_failures():
    admin, message = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    assert admin is not None, message

    assert update_profile(99999, "Missing", "Design", "")[0] is False
    assert toggle_skill_hidden(99999, 99999, True)[0] is False
    assert toggle_user_active(admin["id"], 99999, 0)[0] is False
    assert toggle_user_active(admin["id"], 1, 2)[0] is False
    assert resolve_report(99999, actor_id=admin["id"])[0] is False
    assert create_report(1, "skill_listing", "Missing target")[0] is False

    provider, message = login("asha.menon@christuniversity.in", "Demo@1234")
    assert provider is not None, message

    yesterday = (datetime.now(IST) - timedelta(days=1)).replace(
        hour=15, minute=0, second=0, microsecond=0
    )
    yesterday_end = yesterday + timedelta(hours=1)
    assert publish_slot(
        provider["id"],
        yesterday.strftime("%Y-%m-%d %H:%M"),
        yesterday_end.strftime("%Y-%m-%d %H:%M"),
    )[0] is False
    assert publish_slot(provider["id"], "2027-1-2 15:00", "2027-1-2 16:00")[0] is False
