"""Tests for progress-related API endpoints and session-based submit_score."""

from flask import url_for

from server.models import User
from server import progress_store as ps


def test_progress_endpoints_require_auth(client):
    # GET requires auth
    resp = client.get("/api/progress")
    assert resp.status_code == 401
    # POST requires auth
    resp = client.post("/api/progress", json={"max_unlocked_level": 3})
    assert resp.status_code == 401


def test_progress_get_and_set(client, db, monkeypatch, tmp_path):
    # Isolate progress file
    monkeypatch.setattr(ps, "PROGRESS_FILE", str(tmp_path / "user_progress.json"))

    # Create user and login via form to establish session
    user = User(username="tester")
    user.set_password("pw")
    db.session.add(user)
    db.session.commit()

    client.post(url_for("auth.login"), data={"username": "tester", "password": "pw"})

    # Initially default 1
    r = client.get("/api/progress")
    assert r.status_code == 200
    assert r.get_json()["max_unlocked_level"] == 1

    # Set to 4
    r = client.post("/api/progress", json={"max_unlocked_level": 4})
    assert r.status_code == 200
    assert r.get_json()["max_unlocked_level"] == 4

    # Get again -> 4
    r = client.get("/api/progress")
    assert r.status_code == 200
    assert r.get_json()["max_unlocked_level"] == 4


def test_progress_post_validation(client, db):
    # Login user
    user = User(username="valuser")
    user.set_password("pw")
    db.session.add(user)
    db.session.commit()
    client.post(url_for("auth.login"), data={"username": "valuser", "password": "pw"})

    # Non-JSON
    r = client.post("/api/progress", data="not json")
    assert r.status_code == 415
    # Invalid value
    r = client.post("/api/progress", json={"max_unlocked_level": "bad"})
    assert r.status_code == 400


def test_submit_score_session_auth(client, db):
    # Create user and login; submit without user_id uses current_user
    user = User(username="sessuser")
    user.set_password("pw")
    db.session.add(user)
    db.session.commit()

    client.post(url_for("auth.login"), data={"username": "sessuser", "password": "pw"})
    r = client.post("/api/submit_score", json={"score": 1234, "level": 2})
    # 201 Created
    assert r.status_code == 201

