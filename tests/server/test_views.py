# tests/server/test_views.py
import pytest
from flask import url_for, session
from server.app import create_app
from server.extensions import db
from server.models import User, Score
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

# --- Fixture for Test App, Client, and Database ---
@pytest.fixture(scope='function')
def view_test_client_db():
    """Fixture for view testing, including login simulation."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False, # Important for login/forms if tested
        "LOGIN_DISABLED": False, # Keep login enabled for view tests
        "SECRET_KEY": "test-secret-key", # Needs to be consistent
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SERVER_NAME": "localhost.test" # Helps url_for generate full URLs if needed
    }
    app = create_app(config_override=test_config)

    with app.app_context():
        db.create_all()

        # Create users
        user_logged_in = User(username="test_viewer")
        user_logged_in.set_password("password")
        user_other = User(username="other_player")
        user_other.set_password("password")
        db.session.add_all([user_logged_in, user_other])
        db.session.commit()

        # Add some scores using timezone-aware datetime
        now_utc = datetime.now(timezone.utc) # Use timezone.utc
        scores = [
            Score(user_id=user_logged_in.id, score_value=100, level=1, timestamp=now_utc - timedelta(hours=1)),
            Score(user_id=user_other.id, score_value=150, level=1, timestamp=now_utc - timedelta(hours=2)),
            Score(user_id=user_logged_in.id, score_value=200, level=2, timestamp=now_utc - timedelta(minutes=30)),
        ]
        db.session.add_all(scores)
        db.session.commit()

        client = app.test_client()
        yield client, app, user_logged_in # Provide client, app, and a user object

        db.session.remove()
        db.drop_all()

# --- Helper Function for Login ---
def login(client, username, password):
    """Helper function to log in a user via the test client."""
    # Assumes you have a '/auth/login' route that handles POST requests
    # Adjust the route and form field names if necessary
    return client.post('/auth/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

# --- Test Index Route ---
def test_index_redirect_anonymous(view_test_client_db):
    """Test '/' redirects to login when anonymous."""
    client, app, _ = view_test_client_db
    with app.app_context():
        response = client.get(url_for('views.index'))
        assert response.status_code == 302  # Redirect
        # Check if the redirect location contains the login URL path
        assert '/auth/login' in response.location

def test_index_redirect_logged_in(view_test_client_db):
    """Test '/' redirects to overall leaderboard when logged in."""
    client, app, user = view_test_client_db
    with app.app_context():
        login(client, user.username, "password")  # Log the user in
        response = client.get(url_for('views.index'))
        assert response.status_code == 302  # Redirect
        # Check if the redirect location contains the leaderboard URL path
        assert '/leaderboard' in response.location

# --- Test Leaderboard Routes ---
def test_leaderboard_anonymous_redirect(view_test_client_db):
    """
    Test: Accessing leaderboard routes when anonymous redirects to login
    with the correct URL-encoded 'next' parameter.
    """
    client, app, _ = view_test_client_db
    with app.app_context():
        login_url = url_for('auth.login', _external=False)
        leaderboard_url = url_for('views.leaderboard', _external=False)
        leaderboard_level1_url = url_for('views.leaderboard', level_num=1, _external=False)

        # Test redirect for overall leaderboard
        response_overall = client.get(leaderboard_url, follow_redirects=False)
        assert response_overall.status_code == 302
        # --- Check against unencoded 'next' parameter using quote --
        expected_overall_next = f"{login_url}?next={quote(leaderboard_url, safe='')}"
        assert response_overall.location == expected_overall_next  # Now match without encoded slashes

        # Test redirect for level-specific leaderboard
        response_level = client.get(leaderboard_level1_url, follow_redirects=False)
        assert response_level.status_code == 302
        # --- Check against unencoded 'next' parameter using quote --
        expected_level1_next = f"{login_url}?next={quote(leaderboard_level1_url, safe='')}"
        assert response_level.location == expected_level1_next  # Now match without encoded slashes

def test_leaderboard_overall_logged_in(view_test_client_db):
    """Test '/leaderboard' (overall) renders correctly when logged in."""
    client, app, user = view_test_client_db
    with app.app_context(): # Ensure url_for works
        login(client, user.username, "password")
        response = client.get(url_for('views.leaderboard'))
        assert response.status_code == 200
        assert b"Overall Leaderboard" in response.data # Check title/heading
        assert b"player" in response.data # Check if usernames are rendered
        assert b"test_viewer" in response.data
        assert b"other_player" in response.data
        assert b"Level 1 Ranking" in response.data # Check dropdown option
        assert b"Level 2 Ranking" in response.data # Check dropdown option

def test_leaderboard_level_1_logged_in(view_test_client_db):
    """Test '/leaderboard/level/1' renders correctly."""
    client, app, user = view_test_client_db
    with app.app_context(): # Ensure url_for works
        login(client, user.username, "password")
        response = client.get(url_for('views.leaderboard', level_num=1))
        assert response.status_code == 200
        assert b"Leaderboard - Level 1" in response.data
        assert b"other_player" in response.data # P2 has higher score on L1
        assert b"test_viewer" in response.data
        # Check ranking order if possible/reliable in test data
        # This might require more specific checks on table row order

def test_leaderboard_invalid_level_redirect(view_test_client_db):
    """Test accessing leaderboard for a non-existent level redirects."""
    client, app, user = view_test_client_db
    with app.app_context():
        login(client, user.username, "password")
        response = client.get(url_for('views.leaderboard', level_num=99))
        assert response.status_code == 302  # Redirects to overall leaderboard
        # Check if the redirect location contains the leaderboard URL path
        assert '/leaderboard' in response.location

# --- Test Game Route ---
def test_game_route_anonymous_redirect(view_test_client_db):
    """
    Test: Accessing '/game' when anonymous redirects to login
    with the correct URL-encoded 'next' parameter.
    """
    client, app, _ = view_test_client_db
    with app.app_context():
        login_url = url_for('auth.login', _external=False)
        game_url = url_for('views.game', _external=False)

        response = client.get(game_url, follow_redirects=False)
        assert response.status_code == 302
        # --- Check against unencoded 'next' parameter using quote --
        expected_next = f"{login_url}?next={quote(game_url, safe='')}"
        assert response.location == expected_next  # Now match without encoded slashes

def test_game_route_logged_in(view_test_client_db):
    """Test '/game' renders correctly when logged in."""
    client, app, user = view_test_client_db
    with app.app_context(): # Ensure url_for works
        login(client, user.username, "password")
        response = client.get(url_for('views.game'))
        assert response.status_code == 200
        assert b"How to Play PlaneWar" in response.data # Check for expected content