import pytest
import requests
import requests_mock # Use the requests-mock library installed earlier
from game import network_client as network # Import the module to test
from game.settings import SERVER_API_URL # Get the base URL

# Note: requests_mock fixture is automatically provided when library is installed

def test_api_login_success(requests_mock):
    """Test successful API login call."""
    user_id = 123
    username = 'testuser'
    mock_response = {
        "success": True,
        "message": "Login successful",
        "user_id": user_id,
        "username": username
    }
    # Mock the POST request to the login endpoint
    requests_mock.post(f"{SERVER_API_URL}/login", json=mock_response, status_code=200)

    success, r_user_id, r_username, r_msg = network.api_login_user('testuser', 'password')

    assert success is True
    assert r_user_id == user_id
    assert r_username == username
    assert r_msg == "Login successful"
    # Check if the mock endpoint was called exactly once
    assert requests_mock.call_count == 1
    history = requests_mock.request_history
    assert history[0].method == 'POST'
    assert history[0].url == f"{SERVER_API_URL}/login"
    assert history[0].json() == {'username': 'testuser', 'password': 'password'}

def test_api_login_fail_credentials(requests_mock):
    """Test failed API login call (wrong credentials)."""
    mock_response = {"success": False, "message": "Invalid credentials"}
    requests_mock.post(f"{SERVER_API_URL}/login", json=mock_response, status_code=401)

    success, r_user_id, r_username, r_msg = network.api_login_user('testuser', 'wrong')

    assert success is False
    assert r_user_id is None
    assert r_username is None
    assert r_msg == "Network Error: Invalid credentials" # network_client prepends "Network Error: "

def test_api_login_fail_bad_request(requests_mock):
    """Test failed API login call (missing data -> 400)."""
    mock_response = {"success": False, "message": "Username and password required"}
    requests_mock.post(f"{SERVER_API_URL}/login", json=mock_response, status_code=400)

    success, r_user_id, r_username, r_msg = network.api_login_user('', '') # Simulate empty send

    assert success is False
    assert r_user_id is None
    assert r_username is None
    assert "Network Error: Username and password required" in r_msg

def test_api_login_network_error_connection(requests_mock):
    """Test network connection error during login."""
    requests_mock.post(f"{SERVER_API_URL}/login", exc=requests.exceptions.ConnectionError("Failed to connect"))

    success, r_user_id, r_username, r_msg = network.api_login_user('testuser', 'password')

    assert success is False
    assert r_user_id is None
    assert r_username is None
    assert "Network Error: Connection Failed" in r_msg

def test_api_login_network_error_timeout(requests_mock):
    """Test network timeout during login."""
    requests_mock.post(f"{SERVER_API_URL}/login", exc=requests.exceptions.Timeout("Request timed out"))

    success, r_user_id, r_username, r_msg = network.api_login_user('testuser', 'password')

    assert success is False
    assert r_user_id is None
    assert r_username is None
    assert "Network Error: Timeout" in r_msg

# --- Tests for api_submit_score ---

def test_api_submit_score_success(requests_mock):
    """Test successful score submission."""
    user_id = 456
    score = 1500
    level = 3
    mock_response = {"success": True, "message": "Score submitted"}
    requests_mock.post(f"{SERVER_API_URL}/submit_score", json=mock_response, status_code=201)

    success, msg = network.api_submit_score(user_id, score, level)

    assert success is True
    assert msg == "Score submitted"
    assert requests_mock.call_count == 1
    history = requests_mock.request_history
    assert history[0].method == 'POST'
    assert history[0].url == f"{SERVER_API_URL}/submit_score"
    assert history[0].json() == {'user_id': user_id, 'score': score, 'level_reached': level}

def test_api_submit_score_no_level(requests_mock):
    """Test successful score submission without level."""
    user_id = 456
    score = 1500
    mock_response = {"success": True, "message": "Score submitted"}
    requests_mock.post(f"{SERVER_API_URL}/submit_score", json=mock_response, status_code=201)

    success, msg = network.api_submit_score(user_id, score) # No level passed

    assert success is True
    assert msg == "Score submitted"
    history = requests_mock.request_history
    assert history[0].json() == {'user_id': user_id, 'score': score} # level_reached should be absent

def test_api_submit_score_fail_server(requests_mock):
    """Test failed score submission (server error)."""
    user_id = 456
    score = 1500
    mock_response = {"success": False, "message": "Database error"}
    requests_mock.post(f"{SERVER_API_URL}/submit_score", json=mock_response, status_code=500)

    success, msg = network.api_submit_score(user_id, score)

    assert success is False
    assert "Network Error: Database error" in msg

def test_api_submit_score_not_logged_in():
    """Test submitting score without a user_id."""
    success, msg = network.api_submit_score(None, 1000) # Pass None for user_id
    assert success is False
    assert msg == "Not logged in"

# --- Tests for api_get_leaderboard ---

def test_api_get_leaderboard_success(requests_mock):
    """Test fetching leaderboard successfully."""
    mock_data = [
        {"rank": 1, "username": "player1", "score": 5000, "date": "2025-01-01 10:00:00 UTC"},
        {"rank": 2, "username": "player2", "score": 4500, "date": "2025-01-01 09:00:00 UTC"},
    ]
    requests_mock.get(f"{SERVER_API_URL}/leaderboard?limit=10", json=mock_data, status_code=200)

    data = network.api_get_leaderboard(limit=10)

    assert data == mock_data
    assert requests_mock.call_count == 1
    history = requests_mock.request_history
    assert history[0].method == 'GET'
    assert history[0].url == f"{SERVER_API_URL}/leaderboard?limit=10"

def test_api_get_leaderboard_fail_server(requests_mock):
    """Test server error when fetching leaderboard."""
    requests_mock.get(f"{SERVER_API_URL}/leaderboard?limit=10", status_code=500, text="Server Error")

    data = network.api_get_leaderboard(limit=10)

    assert data is None

def test_api_get_leaderboard_network_error(requests_mock):
    """Test network error when fetching leaderboard."""
    requests_mock.get(f"{SERVER_API_URL}/leaderboard?limit=10", exc=requests.exceptions.Timeout)

    data = network.api_get_leaderboard(limit=10)

    assert data is None 