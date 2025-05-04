# tests/server/test_models.py # Corrected path comment
import pytest
from server.app import create_app # Adjust import based on your app factory location
from server.extensions import db
from server.models import User, Score
# --- MODIFIED IMPORT ---
from datetime import datetime, timedelta, UTC # Import UTC

# --- Fixture for Test App Context and Database ---
@pytest.fixture(scope='function')
def test_app_db():
    """Fixture to create app context and in-memory database for each test function."""
    # Use an in-memory SQLite database for testing
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False, # Disable CSRF for simpler form testing if needed
        "LOGIN_DISABLED": False, # Keep login enabled unless specifically testing without it
        "SECRET_KEY": "test-secret-key", # Required for session management
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    # Assumes create_app accepts config_override
    app = create_app(config_override=test_config)

    with app.app_context():
        db.create_all() # Create tables based on models
        yield app, db    # Provide the app and db object to the test
        db.session.remove() # Clean up session
        db.drop_all()     # Drop all tables after the test

# --- User Model Tests ---

def test_user_creation(test_app_db):
    """Test creating a new User."""
    app, db = test_app_db
    username = "testuser"
    password = "password123"
    user = User(username=username)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    retrieved_user = User.query.filter_by(username=username).first()
    assert retrieved_user is not None
    assert retrieved_user.username == username
    assert retrieved_user.id is not None
    assert retrieved_user.password_hash != password # Ensure password is hashed
    assert retrieved_user.check_password(password) # Check password verification
    assert not retrieved_user.check_password("wrongpassword")

def test_user_repr(test_app_db):
    """Test the __repr__ method of the User model."""
    app, db = test_app_db
    user = User(username="repr_user")
    user.set_password("pw")
    db.session.add(user)
    db.session.commit()
    assert repr(user) == '<User repr_user>'

# --- Score Model Tests ---

def test_score_creation(test_app_db):
    """Test creating a new Score and its relationship with User."""
    app, db = test_app_db
    # Create a user first
    user = User(username="scorer")
    user.set_password("pass")
    db.session.add(user)
    db.session.commit() # Commit user to get an ID

    score_val = 100
    level_val = 1
    # Create score associated with the user
    # Assumes Score model now takes 'level' correctly
    score = Score(user_id=user.id, score_value=score_val, level=level_val)
    db.session.add(score)
    db.session.commit()

    retrieved_score = Score.query.filter_by(user_id=user.id).first()
    assert retrieved_score is not None
    assert retrieved_score.score_value == score_val
    assert retrieved_score.level == level_val # Check level
    assert retrieved_score.user_id == user.id
    assert retrieved_score.timestamp is not None
    assert isinstance(retrieved_score.timestamp, datetime)

    # Test relationship access
    assert retrieved_score.player == user
    # Check relationship using lazy='dynamic' query object
    assert user.scores.count() == 1
    assert user.scores.first() == retrieved_score

def test_score_repr(test_app_db):
    """Test the __repr__ method of the Score model."""
    app, db = test_app_db
    user = User(username="score_repr_user")
    user.set_password("pw")
    db.session.add(user)
    db.session.commit()

    # Assumes Score model takes 'level'
    score = Score(user_id=user.id, score_value=55, level=2)
    db.session.add(score)
    db.session.commit()
    # The timestamp part might vary slightly, so check the beginning part
    # Ensure repr matches the updated format in models.py
    assert repr(score).startswith(f'<Score 55 by UserID {user.id} on Level 2 at ')

def test_score_timestamp_default(test_app_db):
    """Test that the timestamp defaults correctly and use timezone-aware comparison."""
    app, db = test_app_db
    user = User(username="timeuser")
    user.set_password("pw")
    db.session.add(user)
    db.session.commit()

    # Assumes Score model takes 'level'
    score = Score(user_id=user.id, score_value=10, level=1)
    db.session.add(score)
    db.session.commit()

    # --- USE RECOMMENDED METHOD FOR UTC TIME ---
    now_utc = datetime.now(UTC) # Get current timezone-aware UTC time

    # Assert timestamp is close to now (within a reasonable delta like 10 seconds)
    # Ensure the score timestamp is timezone-aware if possible, or compare naive times carefully
    # If score.timestamp is naive (depends on DB driver/SQLAlchemy config), make 'now' naive for comparison:
    # now_naive = datetime.now(UTC).replace(tzinfo=None)
    # assert now_naive - score.timestamp < timedelta(seconds=10)

    # Assuming score.timestamp is timezone-aware (best practice with default=datetime.utcnow replacement):
    assert score.timestamp.tzinfo is not None or db.engine.dialect.name == 'sqlite', "Timestamp should be timezone-aware (except maybe basic SQLite)"
    # Compare aware time directly if possible, otherwise compare naive versions
    if score.timestamp.tzinfo:
         assert now_utc - score.timestamp < timedelta(seconds=10)
    else: # Fallback for naive comparison (less ideal)
         now_naive = now_utc.replace(tzinfo=None)
         score_naive = score.timestamp # Already naive
         assert now_naive - score_naive < timedelta(seconds=10)


def test_user_score_cascade_delete(test_app_db):
    """Test that deleting a User cascades to delete their Scores."""
    app, db = test_app_db
    user = User(username="deleteuser")
    user.set_password("pw")
    db.session.add(user)
    db.session.commit()

    # Assumes Score model takes 'level'
    score1 = Score(user_id=user.id, score_value=100, level=1)
    score2 = Score(user_id=user.id, score_value=200, level=2)
    db.session.add_all([score1, score2])
    db.session.commit()

    assert Score.query.count() == 2

    # Delete the user
    db.session.delete(user)
    db.session.commit()

    # Assert scores associated with the user are also deleted
    assert User.query.filter_by(username="deleteuser").first() is None
    assert Score.query.count() == 0 # Verify cascade delete worked
