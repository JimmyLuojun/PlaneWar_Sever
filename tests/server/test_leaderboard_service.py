"""Tests for the leaderboard service.

This module contains tests for the leaderboard business logic,
including overall leaderboard, level-specific leaderboards, and
distinct level retrieval.
"""

from datetime import datetime, timedelta

from server.leaderboard_service import (
    get_distinct_levels,
    get_leaderboard_by_level,
    get_overall_leaderboard,
)
from server.models import Score, User


def test_get_leaderboard_by_level_empty(db):
    """Test getting leaderboard for a level with no scores."""
    # Arrange & Act
    leaderboard = get_leaderboard_by_level(1)

    # Assert
    assert leaderboard == []


def test_get_leaderboard_by_level_single_user(db):
    """Test getting leaderboard for a level with one user."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    score = Score(user_id=user.id, score_value=1000, level=1)
    db.session.add(score)
    db.session.commit()

    # Act
    leaderboard = get_leaderboard_by_level(1)

    # Assert
    assert len(leaderboard) == 1
    assert leaderboard[0]["rank"] == 1
    assert leaderboard[0]["username"] == "testuser"
    assert leaderboard[0]["score"] == 1000
    assert leaderboard[0]["timestamp"] is not None


def test_get_leaderboard_by_level_multiple_users(db):
    """Test getting leaderboard for a level with multiple users."""
    # Arrange
    user1 = User(username="user1")
    user1.set_password("password")
    user2 = User(username="user2")
    user2.set_password("password")
    user3 = User(username="user3")
    user3.set_password("password")
    db.session.add_all([user1, user2, user3])
    db.session.commit()

    score1 = Score(user_id=user1.id, score_value=1000, level=1)
    score2 = Score(user_id=user2.id, score_value=2000, level=1)
    score3 = Score(user_id=user3.id, score_value=1500, level=1)
    db.session.add_all([score1, score2, score3])
    db.session.commit()

    # Act
    leaderboard = get_leaderboard_by_level(1)

    # Assert
    assert len(leaderboard) == 3
    assert leaderboard[0]["username"] == "user2"
    assert leaderboard[0]["score"] == 2000
    assert leaderboard[1]["username"] == "user3"
    assert leaderboard[1]["score"] == 1500
    assert leaderboard[2]["username"] == "user1"
    assert leaderboard[2]["score"] == 1000


def test_get_leaderboard_by_level_uses_highest_score(db):
    """Test that leaderboard uses the highest score for each user."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    score1 = Score(user_id=user.id, score_value=1000, level=1)
    score2 = Score(user_id=user.id, score_value=2000, level=1)
    score3 = Score(user_id=user.id, score_value=1500, level=1)
    db.session.add_all([score1, score2, score3])
    db.session.commit()

    # Act
    leaderboard = get_leaderboard_by_level(1)

    # Assert
    assert len(leaderboard) == 1
    assert leaderboard[0]["score"] == 2000


def test_get_leaderboard_by_level_tie_breaking(db):
    """Test tie-breaking by earliest timestamp."""
    # Arrange
    user1 = User(username="user1")
    user1.set_password("password")
    user2 = User(username="user2")
    user2.set_password("password")
    db.session.add_all([user1, user2])
    db.session.commit()

    # User1 achieved score 1000 first
    now = datetime.utcnow()
    score1 = Score(
        user_id=user1.id, score_value=1000, level=1, timestamp=now - timedelta(hours=2)
    )
    # User2 achieved score 1000 later
    score2 = Score(
        user_id=user2.id, score_value=1000, level=1, timestamp=now - timedelta(hours=1)
    )
    db.session.add_all([score1, score2])
    db.session.commit()

    # Act
    leaderboard = get_leaderboard_by_level(1)

    # Assert
    assert len(leaderboard) == 2
    assert leaderboard[0]["username"] == "user1"  # Earlier timestamp
    assert leaderboard[1]["username"] == "user2"


def test_get_leaderboard_by_level_different_levels(db):
    """Test that leaderboard only shows scores for the specified level."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    score1 = Score(user_id=user.id, score_value=1000, level=1)
    score2 = Score(user_id=user.id, score_value=2000, level=2)
    db.session.add_all([score1, score2])
    db.session.commit()

    # Act
    leaderboard_level1 = get_leaderboard_by_level(1)
    leaderboard_level2 = get_leaderboard_by_level(2)

    # Assert
    assert len(leaderboard_level1) == 1
    assert leaderboard_level1[0]["score"] == 1000
    assert len(leaderboard_level2) == 1
    assert leaderboard_level2[0]["score"] == 2000


def test_get_overall_leaderboard_empty(db):
    """Test getting overall leaderboard with no scores."""
    # Arrange & Act
    leaderboard = get_overall_leaderboard()

    # Assert
    assert leaderboard == []


def test_get_overall_leaderboard_single_user_single_level(db):
    """Test overall leaderboard with one user and one level."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    score = Score(user_id=user.id, score_value=1000, level=1)
    db.session.add(score)
    db.session.commit()

    # Act
    leaderboard = get_overall_leaderboard()

    # Assert
    assert len(leaderboard) == 1
    assert leaderboard[0]["rank"] == 1
    assert leaderboard[0]["username"] == "testuser"
    assert leaderboard[0]["score"] == 1000


def test_get_overall_leaderboard_single_user_multiple_levels(db):
    """Test overall leaderboard with one user across multiple levels."""
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

    # Act
    leaderboard = get_overall_leaderboard()

    # Assert
    assert len(leaderboard) == 1
    assert leaderboard[0]["score"] == 4500  # Sum of all levels


def test_get_overall_leaderboard_multiple_users(db):
    """Test overall leaderboard with multiple users."""
    # Arrange
    user1 = User(username="user1")
    user1.set_password("password")
    user2 = User(username="user2")
    user2.set_password("password")
    db.session.add_all([user1, user2])
    db.session.commit()

    # User1: 1000 + 1500 = 2500
    score1 = Score(user_id=user1.id, score_value=1000, level=1)
    score2 = Score(user_id=user1.id, score_value=1500, level=2)

    # User2: 2000 + 2000 = 4000
    score3 = Score(user_id=user2.id, score_value=2000, level=1)
    score4 = Score(user_id=user2.id, score_value=2000, level=2)

    db.session.add_all([score1, score2, score3, score4])
    db.session.commit()

    # Act
    leaderboard = get_overall_leaderboard()

    # Assert
    assert len(leaderboard) == 2
    assert leaderboard[0]["username"] == "user2"
    assert leaderboard[0]["score"] == 4000
    assert leaderboard[1]["username"] == "user1"
    assert leaderboard[1]["score"] == 2500


def test_get_overall_leaderboard_uses_highest_score_per_level(db):
    """Test that overall leaderboard uses highest score per level for each user."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    # Multiple scores for level 1, highest is 2000
    score1 = Score(user_id=user.id, score_value=1000, level=1)
    score2 = Score(user_id=user.id, score_value=2000, level=1)
    score3 = Score(user_id=user.id, score_value=1500, level=1)

    # Multiple scores for level 2, highest is 3000
    score4 = Score(user_id=user.id, score_value=2500, level=2)
    score5 = Score(user_id=user.id, score_value=3000, level=2)

    db.session.add_all([score1, score2, score3, score4, score5])
    db.session.commit()

    # Act
    leaderboard = get_overall_leaderboard()

    # Assert
    assert len(leaderboard) == 1
    assert leaderboard[0]["score"] == 5000  # 2000 + 3000


def test_get_overall_leaderboard_tie_breaking(db):
    """Test tie-breaking by earliest timestamp in overall leaderboard."""
    # Arrange
    user1 = User(username="user1")
    user1.set_password("password")
    user2 = User(username="user2")
    user2.set_password("password")
    db.session.add_all([user1, user2])
    db.session.commit()

    now = datetime.utcnow()

    # Both users have same total score (1000)
    # User1 achieved their score first
    score1 = Score(
        user_id=user1.id, score_value=1000, level=1, timestamp=now - timedelta(hours=2)
    )
    # User2 achieved their score later
    score2 = Score(
        user_id=user2.id, score_value=1000, level=1, timestamp=now - timedelta(hours=1)
    )
    db.session.add_all([score1, score2])
    db.session.commit()

    # Act
    leaderboard = get_overall_leaderboard()

    # Assert
    assert len(leaderboard) == 2
    assert leaderboard[0]["username"] == "user1"  # Earlier timestamp
    assert leaderboard[1]["username"] == "user2"


def test_get_distinct_levels_empty(db):
    """Test getting distinct levels with no scores."""
    # Arrange & Act
    levels = get_distinct_levels()

    # Assert
    assert levels == []


def test_get_distinct_levels_single_level(db):
    """Test getting distinct levels with one level."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    score = Score(user_id=user.id, score_value=1000, level=1)
    db.session.add(score)
    db.session.commit()

    # Act
    levels = get_distinct_levels()

    # Assert
    assert levels == [1]


def test_get_distinct_levels_multiple_levels(db):
    """Test getting distinct levels with multiple levels."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    score1 = Score(user_id=user.id, score_value=1000, level=1)
    score2 = Score(user_id=user.id, score_value=1500, level=3)
    score3 = Score(user_id=user.id, score_value=2000, level=2)
    db.session.add_all([score1, score2, score3])
    db.session.commit()

    # Act
    levels = get_distinct_levels()

    # Assert
    assert levels == [1, 2, 3]  # Should be sorted


def test_get_distinct_levels_no_duplicates(db):
    """Test that distinct levels removes duplicates."""
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
    score4 = Score(user_id=user2.id, score_value=2500, level=2)
    db.session.add_all([score1, score2, score3, score4])
    db.session.commit()

    # Act
    levels = get_distinct_levels()

    # Assert
    assert levels == [1, 2]


def test_get_leaderboard_by_level_limit_30(db):
    """Test that leaderboard by level limits to top 30 players."""
    # Arrange
    users = []
    for i in range(35):
        user = User(username=f"user{i}")
        user.set_password("password")
        users.append(user)
        db.session.add(user)
    db.session.commit()

    for i, user in enumerate(users):
        score = Score(user_id=user.id, score_value=1000 + i, level=1)
        db.session.add(score)
    db.session.commit()

    # Act
    leaderboard = get_leaderboard_by_level(1)

    # Assert
    assert len(leaderboard) == 30


def test_get_overall_leaderboard_limit_30(db):
    """Test that overall leaderboard limits to top 30 players."""
    # Arrange
    users = []
    for i in range(35):
        user = User(username=f"user{i}")
        user.set_password("password")
        users.append(user)
        db.session.add(user)
    db.session.commit()

    for i, user in enumerate(users):
        score = Score(user_id=user.id, score_value=1000 + i, level=1)
        db.session.add(score)
    db.session.commit()

    # Act
    leaderboard = get_overall_leaderboard()

    # Assert
    assert len(leaderboard) == 30
