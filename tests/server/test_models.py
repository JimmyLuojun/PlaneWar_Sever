"""Tests for database models.

This module contains tests for the User and Score models, including
password hashing, relationships, and data validation.
"""

from datetime import datetime

from plane_war_server.data.models import Score, User, load_user


def test_user_creation(db):
    """Test creating a new user."""
    # Arrange & Act
    user = User(username="testuser")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    # Assert
    assert user.id is not None
    assert user.username == "testuser"
    assert user.password_hash is not None
    assert user.password_hash != "password123"


def test_user_set_password(db):
    """Test password hashing."""
    # Arrange
    user = User(username="testuser")

    # Act
    user.set_password("mypassword")

    # Assert
    assert user.password_hash is not None
    assert user.password_hash != "mypassword"
    assert len(user.password_hash) > 0


def test_user_check_password(db):
    """Test password verification."""
    # Arrange
    user = User(username="testuser")
    user.set_password("correctpassword")
    db.session.add(user)
    db.session.commit()

    # Act & Assert
    assert user.check_password("correctpassword") is True
    assert user.check_password("wrongpassword") is False


def test_user_repr(db):
    """Test user string representation."""
    # Arrange
    user = User(username="testuserrepr")
    user.set_password("password")

    # Act
    db.session.add(user)
    db.session.commit()

    # Assert
    assert repr(user) == "<User testuserrepr>"


def test_score_creation(db):
    """Test creating a new score."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    # Act
    score = Score(user_id=user.id, score_value=1000, level=1)
    db.session.add(score)
    db.session.commit()

    # Assert
    assert score.id is not None
    assert score.user_id == user.id
    assert score.score_value == 1000
    assert score.level == 1
    assert isinstance(score.timestamp, datetime)


def test_score_repr(db):
    """Test score string representation."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    score = Score(user_id=user.id, score_value=1000, level=1)
    db.session.add(score)
    db.session.commit()

    # Act
    repr_string = repr(score)

    # Assert
    assert f"<Score 1000 by UserID {user.id} on Level 1" in repr_string


def test_user_score_relationship(db):
    """Test the relationship between User and Score."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    # Act
    score1 = Score(user_id=user.id, score_value=1000, level=1)
    score2 = Score(user_id=user.id, score_value=2000, level=2)
    db.session.add_all([score1, score2])
    db.session.commit()

    # Assert
    assert user.scores.count() == 2
    assert score1.player.username == "testuser"
    assert score2.player.username == "testuser"


def test_user_cascade_delete(db):
    """Test that deleting a user also deletes their scores."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    score1 = Score(user_id=user.id, score_value=1000, level=1)
    score2 = Score(user_id=user.id, score_value=2000, level=2)
    db.session.add_all([score1, score2])
    db.session.commit()

    user_id = user.id

    # Act
    db.session.delete(user)
    db.session.commit()

    # Assert
    assert User.query.get(user_id) is None
    assert Score.query.filter_by(user_id=user_id).count() == 0


def test_load_user_valid_id(app, db):
    """Test loading a user with a valid ID."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()
    user_id = user.id

    # Act
    with app.app_context():
        loaded_user = load_user(user_id)

    # Assert
    assert loaded_user is not None
    assert loaded_user.id == user_id
    assert loaded_user.username == "testuser"


def test_load_user_invalid_id(app, db):
    """Test loading a user with an invalid ID."""
    # Arrange & Act
    with app.app_context():
        loaded_user = load_user(99999)

    # Assert
    assert loaded_user is None


def test_load_user_invalid_type(app, db):
    """Test loading a user with an invalid ID type."""
    # Arrange & Act
    with app.app_context():
        loaded_user = load_user("invalid")

    # Assert
    assert loaded_user is None


def test_multiple_scores_for_same_level(db):
    """Test that a user can have multiple scores for the same level."""
    # Arrange
    user = User(username="testuser")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()

    # Act
    score1 = Score(user_id=user.id, score_value=1000, level=1)
    score2 = Score(user_id=user.id, score_value=1500, level=1)
    score3 = Score(user_id=user.id, score_value=800, level=1)
    db.session.add_all([score1, score2, score3])
    db.session.commit()

    # Assert
    level_1_scores = Score.query.filter_by(user_id=user.id, level=1).all()
    assert len(level_1_scores) == 3
    assert {s.score_value for s in level_1_scores} == {1000, 1500, 800}
