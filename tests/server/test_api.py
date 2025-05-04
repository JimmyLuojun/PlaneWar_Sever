# tests/server/test_api.py
import pytest
import json
from server.app import create_app # Adjust import based on your app factory location
from server.extensions import db
from server.models import User, Score

# --- Fixture for Test App, Client, and Database ---
@pytest.fixture(scope='function')
def test_client_db():
    """
    Fixture to create a Flask app instance configured for testing,
    a test client to make requests, and an in-memory database.
    This fixture runs setup before each test function and teardown after.
    """
    # Define configuration overrides for the testing environment
    test_config = {
        "TESTING": True, # Enables testing mode in Flask and extensions
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # Use in-memory SQLite DB
        "WTF_CSRF_ENABLED": False, # Disable CSRF protection for simpler test requests
        # LOGIN_DISABLED: Set based on API auth method.
        # True: If API uses insecure user_id pass-through or tokens managed outside Flask-Login sessions.
        # False: If API relies on Flask-Login session cookies for authentication.
        "LOGIN_DISABLED": True, # Assuming insecure API for now, simplifies testing auth logic directly
        "SECRET_KEY": "test-secret-key", # Required for session cookies, even if login is disabled
        "SQLALCHEMY_TRACK_MODIFICATIONS": False, # Disable noisy modification tracking
        # Add any other necessary test configurations (e.g., mail settings if testing emails)
    }
    # Create the Flask app instance using the factory, passing the test config
    # This assumes create_app now accepts 'config_override'
    app = create_app(config_override=test_config)

    # Establish an application context before interacting with the database or app features
    with app.app_context():
        db.create_all() # Create database tables based on models defined in models.py

        # Optional: Pre-populate the database with a common test user for convenience
        test_user = User(username="api_user")
        test_user.set_password("password") # Set a known password
        db.session.add(test_user)
        db.session.commit() # Commit to save the user and assign an ID

        client = app.test_client() # Create the test client associated with this app instance

        # Yield the test client, db instance, and the test user's ID to the test function
        yield client, db, test_user.id

        # Teardown: Runs after the test function completes
        db.session.remove() # Clean up the database session
        db.drop_all()     # Drop all tables to ensure test isolation

# ============================
# === /api/login Tests ===
# ============================

def test_api_login_success(test_client_db):
    """Test successful API login with correct credentials."""
    client, db, _ = test_client_db # Unpack the fixture results
    # Make a POST request to the login endpoint with valid JSON data
    response = client.post('/api/login', json={ # Ensure URL prefix matches blueprint registration
        'username': 'api_user',
        'password': 'password'
    })
    # Parse the JSON response
    data = response.get_json()
    # Assertions: Check status code and response content
    assert response.status_code == 200 # OK
    assert data['success'] is True
    assert data['message'] == "Login successful"
    assert 'user_id' in data and isinstance(data['user_id'], int)
    assert data['username'] == 'api_user'

def test_api_login_invalid_credentials(test_client_db):
    """Test API login with incorrect password."""
    client, db, _ = test_client_db
    response = client.post('/api/login', json={
        'username': 'api_user',
        'password': 'wrongpassword' # Incorrect password
    })
    data = response.get_json()
    assert response.status_code == 401 # Unauthorized
    assert data['success'] is False
    assert data['message'] == "Invalid credentials" # Check for generic security message

def test_api_login_user_not_found(test_client_db):
    """Test API login attempt for a user that does not exist."""
    client, db, _ = test_client_db
    response = client.post('/api/login', json={
        'username': 'nosuchuser', # Non-existent username
        'password': 'password'
    })
    data = response.get_json()
    assert response.status_code == 401 # Unauthorized (should return same error as wrong password)
    assert data['success'] is False
    assert data['message'] == "Invalid credentials"

def test_api_login_missing_fields(test_client_db):
    """Test API login request missing required username or password fields."""
    client, db, _ = test_client_db
    # Test missing password
    response = client.post('/api/login', json={'username': 'api_user'})
    assert response.status_code == 400 # Bad Request
    assert response.get_json()['message'] == "Username and password required"

    # Test missing username
    response = client.post('/api/login', json={'password': 'password'})
    assert response.status_code == 400 # Bad Request
    assert response.get_json()['message'] == "Username and password required"

def test_api_login_not_json(test_client_db):
    """Test API login endpoint rejects requests that are not JSON."""
    client, db, _ = test_client_db
    response = client.post('/api/login', data="not valid json data") # Send non-JSON data
    assert response.status_code == 415 # Unsupported Media Type
    assert "Request must be JSON" in response.get_json()['message']

# ================================
# === /api/submit_score Tests ===
# ================================

def test_api_submit_score_success(test_client_db):
    """Test successful score submission via the API."""
    client, db, test_user_id = test_client_db # Get the pre-created user's ID
    score_payload = {
        'user_id': test_user_id, # Using the insecure method (sending ID in payload)
        'score': 150,
        'level': 2
    }
    # Make POST request to submit score endpoint
    response = client.post('/api/submit_score', json=score_payload) # Ensure URL prefix matches
    data = response.get_json()

    # Assertions: Check status code and response message
    assert response.status_code == 201 # Created
    assert data['success'] is True
    assert data['message'] == "Score submitted successfully for level 2."

    # Verify the score was actually saved in the database
    score_in_db = Score.query.filter_by(user_id=test_user_id, score_value=150).first()
    assert score_in_db is not None
    assert score_in_db.level == 2
    assert score_in_db.timestamp is not None # Check timestamp was set

def test_api_submit_score_missing_fields(test_client_db):
    """Test score submission API rejects requests with missing required fields."""
    client, db, test_user_id = test_client_db
    # Test missing 'level'
    response = client.post('/api/submit_score', json={'user_id': test_user_id, 'score': 100})
    assert response.status_code == 400 # Bad Request
    assert response.get_json()['message'] == "Missing user_id, score, or level"

    # Test missing 'score'
    response = client.post('/api/submit_score', json={'user_id': test_user_id, 'level': 1})
    assert response.status_code == 400
    assert response.get_json()['message'] == "Missing user_id, score, or level"

    # Test missing 'user_id'
    response = client.post('/api/submit_score', json={'score': 100, 'level': 1})
    assert response.status_code == 400
    assert response.get_json()['message'] == "Missing user_id, score, or level"

def test_api_submit_score_invalid_types(test_client_db):
    """Test score submission API rejects requests with invalid data types."""
    client, db, test_user_id = test_client_db
    # Test invalid 'score' type
    response = client.post('/api/submit_score', json={
        'user_id': test_user_id,
        'score': 'one hundred fifty', # String instead of int
        'level': 1
    })
    assert response.status_code == 400
    assert response.get_json()['message'] == "Invalid data types for user_id, score, or level"

    # Test invalid 'level' type
    response = client.post('/api/submit_score', json={
        'user_id': test_user_id,
        'score': 100,
        'level': 'level two' # String instead of int
    })
    assert response.status_code == 400
    assert response.get_json()['message'] == "Invalid data types for user_id, score, or level"

    # Test invalid 'user_id' type
    response = client.post('/api/submit_score', json={
        'user_id': 'user_one', # String instead of int
        'score': 100,
        'level': 1
    })
    assert response.status_code == 400
    assert response.get_json()['message'] == "Invalid data types for user_id, score, or level"


def test_api_submit_score_user_not_found(test_client_db):
    """Test score submission API when the provided user_id does not exist."""
    client, db, _ = test_client_db
    non_existent_user_id = 9999 # An ID assumed not to exist
    response = client.post('/api/submit_score', json={
        'user_id': non_existent_user_id,
        'score': 50,
        'level': 1
    })
    # Based on the current *insecure* check in api.py, this returns 404
    assert response.status_code == 404 # Not Found
    assert response.get_json()['message'] == "User specified by user_id not found"
    # Note: A secure implementation would likely return 401 Unauthorized if auth failed

def test_api_submit_score_not_json(test_client_db):
    """Test score submission API rejects requests that are not JSON."""
    client, db, test_user_id = test_client_db
    # Send data in a different format (e.g., form-encoded)
    response = client.post('/api/submit_score', data=f"user_id={test_user_id}&score=100&level=1")
    assert response.status_code == 415 # Unsupported Media Type
    assert "Request must be JSON" in response.get_json()['message']

