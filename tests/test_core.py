"""Core automated tests for password hashing and request status transition rules."""
import pytest

from db.security import hash_password, verify_password
from services.requests import ALLOWED, change_status, create_request
from views.my_requests import available_actions


def test_password_hash_differs_from_plain_text():
    raw = "CampusSecret@123"
    stored = hash_password(raw)
    assert stored != raw
    assert stored.startswith("pbkdf2_sha256$")


def test_password_hash_salting():
    raw = "CampusSecret@123"
    hash1 = hash_password(raw)
    hash2 = hash_password(raw)
    # Different random salts mean hashes are never identical
    assert hash1 != hash2
    assert verify_password(raw, hash1)
    assert verify_password(raw, hash2)


def test_password_verify_succeeds_and_fails_appropriately():
    password = "CorrectHorseBatteryStaple@2026"
    stored = hash_password(password)
    assert verify_password(password, stored) is True
    assert verify_password("WrongPassword@2026", stored) is False
    assert verify_password("", stored) is False
    assert verify_password(password, "invalid_hash_string") is False


def test_allowed_status_transitions_map():
    # pending -> accepted, rejected, cancelled
    assert ALLOWED["pending"] == {"accepted", "rejected", "cancelled"}
    # accepted -> awaiting confirmation or cancelled
    assert ALLOWED["accepted"] == {"awaiting_confirmation", "cancelled"}
    assert ALLOWED["awaiting_confirmation"] == {"completed"}
    # Terminal states
    assert ALLOWED["completed"] == set()
    assert ALLOWED["rejected"] == set()
    assert ALLOWED["cancelled"] == set()


def test_completion_actions_are_role_specific():
    provider_accepted = available_actions("accepted", is_provider=True)
    learner_accepted = available_actions("accepted", is_provider=False)
    learner_awaiting = available_actions("awaiting_confirmation", is_provider=False)
    provider_awaiting = available_actions("awaiting_confirmation", is_provider=True)

    assert ("✅ Mark Completed", "awaiting_confirmation") in provider_accepted
    assert all(action[0] != "✅ Mark Completed" for action in learner_accepted)
    assert learner_awaiting == [("✅ Confirm Completion", "completed")]
    assert provider_awaiting == []


def test_invalid_transition_from_pending_to_completed_rejected():
    # Directly attempting to complete a pending request (ID 1 in seed data)
    from db.database import get_connection

    conn = get_connection()
    try:
        row = conn.execute("SELECT provider_id FROM requests WHERE id = 1").fetchone()
        provider_id = row["provider_id"]
    finally:
        conn.close()

    ok, msg = change_status(request_id=1, actor_id=provider_id, new_status="completed")
    assert ok is False
    assert "Cannot change a pending request to completed" in msg


def test_unauthorized_actor_cannot_change_status():
    # Actor 9999 is neither learner nor provider
    ok, msg = change_status(request_id=1, actor_id=9999, new_status="accepted")
    assert ok is False
    assert "permission" in msg.lower()


def test_duplicate_open_request_is_blocked():
    # Seed request 1 is from learner (Rahul) to provider (Asha) for Python
    # Attempting to create another request for same learner, provider, and skill:
    from db.database import get_connection

    conn = get_connection()
    try:
        row = conn.execute("SELECT learner_id, provider_id, skill_id FROM requests WHERE id = 1").fetchone()
        learner_id = row["learner_id"]
        provider_id = row["provider_id"]
        skill_id = row["skill_id"]
    finally:
        conn.close()

    ok, msg = create_request(learner_id, provider_id, skill_id, "Another duplicate request")
    assert ok is False
    assert "already have an open request" in msg.lower()


def test_terminal_states_cannot_change():
    from db.database import get_connection

    conn = get_connection()
    try:
        # Find a rejected or completed request from seed
        row = conn.execute("SELECT id, provider_id FROM requests WHERE status IN ('completed', 'rejected') LIMIT 1").fetchone()
        req_id = row["id"]
        provider_id = row["provider_id"]
    finally:
        conn.close()

    ok, msg = change_status(request_id=req_id, actor_id=provider_id, new_status="accepted")
    assert ok is False
    assert "final and cannot be changed" in msg.lower()
