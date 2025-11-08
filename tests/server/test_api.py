"""Tests for the API blueprint.

This module contains tests for the API endpoints, including
login, logout, and score submission functionality.
"""

import json

from plane_war_server.data.models import Score, User


def test_api_login_success(client, db):
    """Test successful API login."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Act
    response = client.post(
        "/api/login",
        json={"username": "testuser", "password": "password123"},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 200
    assert data["success"] is True
    assert data["message"] == "Login successful"
    assert data["user_id"] == user.id
    assert data["username"] == "testuser"


def test_api_login_invalid_credentials(client, db):
    """Test API login with invalid credentials."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Act
    response = client.post(
        "/api/login",
        json={"username": "testuser", "password": "wrongpassword"},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 401
    assert data["success"] is False
    assert data["message"] == "Invalid credentials"


def test_api_login_nonexistent_user(client, db):
    """Test API login with nonexistent user."""
    # Arrange & Act
    response = client.post(
        "/api/login",
        json={"username": "nonexistent", "password": "password123"},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 401
    assert data["success"] is False
    assert data["message"] == "Invalid credentials"


def test_api_login_missing_username(client, db):
    """Test API login with missing username."""
    # Arrange & Act
    response = client.post(
        "/api/login",
        json={"password": "password123"},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 400
    assert data["success"] is False
    assert data["message"] == "Username and password required"


def test_api_login_missing_password(client, db):
    """Test API login with missing password."""
    # Arrange & Act
    response = client.post(
        "/api/login",
        json={"username": "testuser"},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 400
    assert data["success"] is False
    assert data["message"] == "Username and password required"


def test_api_login_not_json(client, db):
    """Test API login with non-JSON request."""
    # Arrange & Act
    response = client.post(
        "/api/login",
        data={"username": "testuser", "password": "password123"},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 415
    assert data["success"] is False
    assert data["message"] == "Request must be JSON"


def test_api_logout(client, db):
    """Test API logout."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Login first
    client.post(
        "/api/login",
        json={"username": "testuser", "password": "password123"},
    )

    # Act
    response = client.post("/api/logout")
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 200
    assert data["success"] is True
    assert data["message"] == "Logout successful"


def test_api_submit_score_success(client, db):
    """Test successful score submission."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Act
    response = client.post(
        "/api/submit_score",
        json={"user_id": user.id, "score": 1000, "level": 1},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 201
    assert data["success"] is True
    assert "Score submitted successfully for level 1" in data["message"]

    # Verify score was saved
    score = Score.query.filter_by(user_id=user.id, level=1).first()
    assert score is not None
    assert score.score_value == 1000


def test_api_submit_score_missing_user_id(client, db):
    """Test score submission with missing user_id."""
    # Arrange & Act
    response = client.post(
        "/api/submit_score",
        json={"score": 1000, "level": 1},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 400
    assert data["success"] is False
    assert data["message"] == "Missing user_id, score, or level"


def test_api_submit_score_missing_score(client, db):
    """Test score submission with missing score."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Act
    response = client.post(
        "/api/submit_score",
        json={"user_id": user.id, "level": 1},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 400
    assert data["success"] is False
    assert data["message"] == "Missing user_id, score, or level"


def test_api_submit_score_missing_level(client, db):
    """Test score submission with missing level."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Act
    response = client.post(
        "/api/submit_score",
        json={"user_id": user.id, "score": 1000},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 400
    assert data["success"] is False
    assert data["message"] == "Missing user_id, score, or level"


def test_api_submit_score_invalid_user_id_type(client, db):
    """Test score submission with invalid user_id type."""
    # Arrange & Act
    response = client.post(
        "/api/submit_score",
        json={"user_id": "invalid", "score": 1000, "level": 1},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 400
    assert data["success"] is False
    assert data["message"] == "Invalid data types for user_id, score, or level"


def test_api_submit_score_invalid_score_type(client, db):
    """Test score submission with invalid score type."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Act
    response = client.post(
        "/api/submit_score",
        json={"user_id": user.id, "score": "invalid", "level": 1},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 400
    assert data["success"] is False
    assert data["message"] == "Invalid data types for user_id, score, or level"


def test_api_submit_score_invalid_level_type(client, db):
    """Test score submission with invalid level type."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Act
    response = client.post(
        "/api/submit_score",
        json={"user_id": user.id, "score": 1000, "level": "invalid"},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 400
    assert data["success"] is False
    assert data["message"] == "Invalid data types for user_id, score, or level"


def test_api_submit_score_nonexistent_user(client, db):
    """Test score submission for nonexistent user."""
    # Arrange & Act
    response = client.post(
        "/api/submit_score",
        json={"user_id": 99999, "score": 1000, "level": 1},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 404
    assert data["success"] is False
    assert data["message"] == "User specified by user_id not found"


def test_api_submit_score_not_json(client, db):
    """Test score submission with non-JSON request."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Act
    response = client.post(
        "/api/submit_score",
        data={"user_id": user.id, "score": 1000, "level": 1},
    )
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 415
    assert data["success"] is False
    assert data["message"] == "Request must be JSON"


def test_api_submit_multiple_scores(client, db):
    """Test submitting multiple scores for the same user."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Act
    response1 = client.post(
        "/api/submit_score",
        json={"user_id": user.id, "score": 1000, "level": 1},
    )
    response2 = client.post(
        "/api/submit_score",
        json={"user_id": user.id, "score": 1500, "level": 1},
    )
    response3 = client.post(
        "/api/submit_score",
        json={"user_id": user.id, "score": 2000, "level": 2},
    )

    # Assert
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response3.status_code == 201

    # Verify all scores were saved
    scores = Score.query.filter_by(user_id=user.id).all()
    assert len(scores) == 3
