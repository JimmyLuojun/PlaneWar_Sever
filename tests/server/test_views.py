"""Tests for the views blueprint.

This module contains tests for the web interface routes, including
index, leaderboard, and game pages.
"""

from flask import url_for

from server.models import Score, User


def test_index_redirects_to_login_when_not_authenticated(client, db):
    """Test that index redirects to login for unauthenticated users."""
    # Arrange & Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_index_redirects_to_leaderboard_when_authenticated(client, db):
    """Test that index redirects to leaderboard for authenticated users."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    # Login
    client.post(
        url_for("auth.login"),
        data={"username": "testuser", "password": "password"},
    )

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 302
    assert "/leaderboard" in response.location


def test_leaderboard_requires_login(client, db):
    """Test that leaderboard requires login."""
    # Arrange & Act
    response = client.get("/leaderboard", follow_redirects=False)

    # Assert
    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_leaderboard_overall_empty(client, db):
    """Test overall leaderboard with no scores."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    # Login
    client.post(
        url_for("auth.login"),
        data={"username": "testuser", "password": "password"},
    )

    # Act
    response = client.get("/leaderboard")

    # Assert
    assert response.status_code == 200
    assert b"Overall Leaderboard (Top 0)" in response.data


def test_leaderboard_overall_with_scores(client, db):
    """Test overall leaderboard with scores."""
    # Arrange
    user1 = User(username="user1")
    user1.set_password("password")
    user2 = User(username="user2")
    user2.set_password("password")
    db.session.add_all([user1, user2])
    db.session.commit()

    score1 = Score(user_id=user1.id, score_value=1000, level=1)
    score2 = Score(user_id=user2.id, score_value=1500, level=1)
    score3 = Score(user_id=user1.id, score_value=2000, level=2)
    db.session.add_all([score1, score2, score3])
    db.session.commit()

    # Login
    client.post(
        url_for("auth.login"),
        data={"username": "user1", "password": "password"},
    )

    # Act
    response = client.get("/leaderboard")

    # Assert
    assert response.status_code == 200
    assert b"Overall Leaderboard (Top 2)" in response.data
    assert b"user1" in response.data
    assert b"user2" in response.data


def test_leaderboard_by_level(client, db):
    """Test leaderboard filtered by level."""
    # Arrange
    user1 = User(username="user1")
    user1.set_password("password")
    user2 = User(username="user2")
    user2.set_password("password")
    db.session.add_all([user1, user2])
    db.session.commit()

    score1 = Score(user_id=user1.id, score_value=1000, level=1)
    score2 = Score(user_id=user2.id, score_value=1500, level=1)
    score3 = Score(user_id=user1.id, score_value=2000, level=2)
    db.session.add_all([score1, score2, score3])
    db.session.commit()

    # Login
    client.post(
        url_for("auth.login"),
        data={"username": "user1", "password": "password"},
    )

    # Act
    response = client.get("/leaderboard/level/1")

    # Assert
    assert response.status_code == 200
    assert b"Leaderboard - Level 1 (Top 2)" in response.data
    assert b"user1" in response.data
    assert b"user2" in response.data


def test_leaderboard_nonexistent_level(client, db):
    """Test leaderboard with a nonexistent level."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    # Login
    client.post(
        url_for("auth.login"),
        data={"username": "testuser", "password": "password"},
    )

    # Act
    response = client.get("/leaderboard/level/99", follow_redirects=True)

    # Assert
    assert response.status_code == 200
    assert b"Level 99 does not exist or has no scores." in response.data


def test_leaderboard_shows_available_levels(client, db):
    """Test that leaderboard shows available levels."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    score1 = Score(user_id=user.id, score_value=1000, level=1)
    score2 = Score(user_id=user.id, score_value=1500, level=2)
    score3 = Score(user_id=user.id, score_value=2000, level=3)
    db.session.add_all([score1, score2, score3])
    db.session.commit()

    # Login
    client.post(
        url_for("auth.login"),
        data={"username": "testuser", "password": "password"},
    )

    # Act
    response = client.get("/leaderboard")

    # Assert
    assert response.status_code == 200
    # Check that level links are present (depends on template implementation)
    assert b"Level 1" in response.data or b"level/1" in response.data
    assert b"Level 2" in response.data or b"level/2" in response.data
    assert b"Level 3" in response.data or b"level/3" in response.data


def test_game_page_requires_login(client, db):
    """Test that game page requires login."""
    # Arrange & Act
    response = client.get("/game", follow_redirects=False)

    # Assert
    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_game_page_when_authenticated(client, db):
    """Test game page for authenticated users."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    # Login
    client.post(
        url_for("auth.login"),
        data={"username": "testuser", "password": "password"},
    )

    # Act
    response = client.get("/game")

    # Assert
    assert response.status_code == 200
    assert b"How to Play" in response.data or b"Game" in response.data


def test_leaderboard_ranking_order(client, db):
    """Test that leaderboard shows correct ranking order."""
    # Arrange
    user1 = User(username="topplayer")
    user1.set_password("password")
    user2 = User(username="midplayer")
    user2.set_password("password")
    user3 = User(username="lowplayer")
    user3.set_password("password")
    db.session.add_all([user1, user2, user3])
    db.session.commit()

    # User1 has highest total score
    score1 = Score(user_id=user1.id, score_value=3000, level=1)
    score2 = Score(user_id=user1.id, score_value=3000, level=2)

    # User2 has medium total score
    score3 = Score(user_id=user2.id, score_value=2000, level=1)
    score4 = Score(user_id=user2.id, score_value=2000, level=2)

    # User3 has lowest total score
    score5 = Score(user_id=user3.id, score_value=1000, level=1)
    score6 = Score(user_id=user3.id, score_value=1000, level=2)

    db.session.add_all([score1, score2, score3, score4, score5, score6])
    db.session.commit()

    # Login
    client.post(
        url_for("auth.login"),
        data={"username": "topplayer", "password": "password"},
    )

    # Act
    response = client.get("/leaderboard")
    response_text = response.data.decode("utf-8")

    # Assert
    assert response.status_code == 200

    # Check that topplayer appears before others
    topplayer_pos = response_text.find("topplayer")
    midplayer_pos = response_text.find("midplayer")
    lowplayer_pos = response_text.find("lowplayer")

    assert topplayer_pos != -1
    assert midplayer_pos != -1
    assert lowplayer_pos != -1
    assert topplayer_pos < midplayer_pos < lowplayer_pos
