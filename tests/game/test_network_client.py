# test_network_client.py
import pytest
import requests
import json
from unittest.mock import patch, MagicMock, ANY # Import ANY for flexible payload matching

# Import the module under test
from game import network_client
from game import settings # Need this to potentially check URLs if needed

# Reset module state before each test function if needed
@pytest.fixture(autouse=True)
def reset_network_client_state(monkeypatch):
    """Resets the login state in network_client before each test."""
    monkeypatch.setattr(network_client, '_is_logged_in', False)
    monkeypatch.setattr(network_client, '_current_username', None)
    mock_session = MagicMock(spec=requests.Session)
    monkeypatch.setattr(network_client, 'api_session', mock_session)


# --- Helper to create Mock Responses (Corrected) ---
def create_mock_response(status_code=200, json_data=None, text_data=""):
    """Creates a mock requests.Response object. raise_for_status behaviour is handled."""
    mock_resp = MagicMock(spec=requests.Response)
    mock_resp.status_code = status_code
    mock_resp.text = text_data
    if json_data is not None:
        mock_resp.json.return_value = json_data
    else:
        mock_resp.json.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)

    # --- FIX: Configure raise_for_status correctly ---
    def check_raise():
        if status_code >= 400:
            # Create an instance of HTTPError and attach the mock response to it
            http_error_instance = requests.exceptions.HTTPError(response=mock_resp)
            raise http_error_instance
        # If status_code < 400, raise_for_status does nothing
    mock_resp.raise_for_status.side_effect = check_raise
    # ---------------------------------------------

    return mock_resp

# --- Tests for api_login_user ---

def test_api_login_user_success(monkeypatch):
    """Test successful login."""
    mock_session = MagicMock(spec=requests.Session)
    mock_response = create_mock_response(
        status_code=200,
        json_data={"success": True, "username": "tester", "message": "Login successful"}
    )
    mock_session.post.return_value = mock_response
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    success, username, message = network_client.api_login_user("testuser", "password")

    assert success is True
    assert username == "tester"
    assert message == "Login successful"
    assert network_client._is_logged_in is True
    assert network_client._current_username == "tester"
    mock_session.post.assert_called_once()

def test_api_login_user_failure_server(monkeypatch):
    """Test failed login due to server logic (e.g., bad password)."""
    mock_session = MagicMock(spec=requests.Session)
    mock_response = create_mock_response(
        status_code=200,
        json_data={"success": False, "message": "Invalid credentials"}
    )
    mock_session.post.return_value = mock_response
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    success, username, message = network_client.api_login_user("testuser", "wrongpass")

    assert success is False
    assert username is None
    assert message == "Invalid credentials"
    assert network_client._is_logged_in is False

def test_api_login_user_failure_401(monkeypatch):
    """Test failed login due to 401 Unauthorized."""
    mock_session = MagicMock(spec=requests.Session)
    # create_mock_response now correctly sets up raise_for_status side effect
    mock_response = create_mock_response(
        status_code=401,
        json_data={"message": "Auth Failed"}
    )
    # REMOVED: mock_response.response = mock_response # Not needed anymore
    mock_session.post.return_value = mock_response
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    success, username, message = network_client.api_login_user("testuser", "wrongpass")

    assert success is False
    assert username is None
    # Check the message extracted from the exception's response
    assert message == "Auth Failed"
    assert network_client._is_logged_in is False

def test_api_login_user_timeout(monkeypatch):
    """Test login failure due to network timeout."""
    mock_session = MagicMock(spec=requests.Session)
    mock_session.post.side_effect = requests.exceptions.Timeout
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    success, username, message = network_client.api_login_user("testuser", "password")

    assert success is False
    assert username is None
    assert message == "Network Error: Timeout"
    assert network_client._is_logged_in is False

def test_api_login_user_connection_error(monkeypatch):
    """Test login failure due to connection error."""
    mock_session = MagicMock(spec=requests.Session)
    mock_session.post.side_effect = requests.exceptions.ConnectionError
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    success, username, message = network_client.api_login_user("testuser", "password")

    assert success is False
    assert username is None
    assert message == "Network Error: Connection Failed"
    assert network_client._is_logged_in is False

def test_api_login_user_json_decode_error(monkeypatch):
    """Test login failure due to invalid JSON response."""
    mock_session = MagicMock(spec=requests.Session)
    mock_response = create_mock_response(status_code=200) # Status OK
    mock_response.json.side_effect = json.JSONDecodeError("msg", "doc", 0) # But JSON fails
    mock_session.post.return_value = mock_response
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    success, username, message = network_client.api_login_user("testuser", "password")

    assert success is False
    assert username is None
    assert message == "Invalid server response"
    assert network_client._is_logged_in is False


# --- Tests for api_submit_score ---

def test_api_submit_score_success(monkeypatch):
    """Test successful score submission."""
    monkeypatch.setattr(network_client, '_is_logged_in', True)
    monkeypatch.setattr(network_client, '_current_username', 'tester')

    mock_session = MagicMock(spec=requests.Session)
    mock_response = create_mock_response(
        status_code=201,
        json_data={"success": True, "message": "Score received"}
    )
    mock_session.post.return_value = mock_response
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    score_to_submit = 100
    level_completed = 5
    success, message = network_client.api_submit_score(score_to_submit, level_completed)

    assert success is True
    assert message == "Score received"
    expected_payload = {"score": score_to_submit, "level": level_completed}
    mock_session.post.assert_called_once_with(
        f"{settings.SERVER_API_URL}/submit_score",
        json=expected_payload,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )

def test_api_submit_score_not_logged_in(monkeypatch):
    """Test score submission fails if user is not logged in."""
    monkeypatch.setattr(network_client, '_is_logged_in', False)
    mock_session = MagicMock(spec=requests.Session)
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    success, message = network_client.api_submit_score(100, 5)

    assert success is False
    assert message == "Not logged in"
    mock_session.post.assert_not_called()

def test_api_submit_score_failure_401_unauthorized(monkeypatch):
    """Test score submission fails with 401 (e.g., session expired server-side)."""
    monkeypatch.setattr(network_client, '_is_logged_in', True)
    monkeypatch.setattr(network_client, '_current_username', 'tester')

    mock_session = MagicMock(spec=requests.Session)
    # create_mock_response now correctly sets up raise_for_status side effect
    mock_response = create_mock_response(
        status_code=401,
        json_data={"message": "Session invalid"} # Message if server sends JSON on 401
    )
    # REMOVED: mock_response.response = mock_response
    mock_session.post.return_value = mock_response
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    success, message = network_client.api_submit_score(100, 5)

    assert success is False
    # The specific message comes from the except block logic now
    assert message == "Not logged in or session expired"
    assert network_client._is_logged_in is False
    assert network_client._current_username is None

def test_api_submit_score_failure_400_bad_request(monkeypatch):
    """Test score submission fails with 400 (e.g., invalid level format)."""
    monkeypatch.setattr(network_client, '_is_logged_in', True)
    monkeypatch.setattr(network_client, '_current_username', 'tester')

    mock_session = MagicMock(spec=requests.Session)
    # create_mock_response now correctly sets up raise_for_status side effect
    mock_response = create_mock_response(
        status_code=400,
        json_data={"message": "Invalid level format"}
    )
    # REMOVED: mock_response.response = mock_response
    mock_session.post.return_value = mock_response
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    success, message = network_client.api_submit_score(100, "five") # Send bad data

    assert success is False
    assert message == "Invalid data: Invalid level format"
    assert network_client._is_logged_in is True # Should still be logged in
    assert network_client._current_username == 'tester'

def test_api_submit_score_network_error(monkeypatch):
    """Test score submission network error."""
    monkeypatch.setattr(network_client, '_is_logged_in', True)
    mock_session = MagicMock(spec=requests.Session)
    mock_session.post.side_effect = requests.exceptions.Timeout
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    success, message = network_client.api_submit_score(100, 5)

    assert success is False
    assert message == "Network Error: Timeout"


# --- Tests for api_get_leaderboard --- (Assume unchanged)

def test_api_get_leaderboard_success(monkeypatch):
    """Test fetching leaderboard successfully."""
    mock_session = MagicMock(spec=requests.Session)
    expected_leaderboard = [{"rank": 1, "username": "p1", "score": 1000}]
    mock_response = create_mock_response(
        status_code=200,
        json_data=expected_leaderboard
    )
    mock_session.get.return_value = mock_response
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    limit = 5
    leaderboard = network_client.api_get_leaderboard(limit=limit)

    assert leaderboard == expected_leaderboard
    mock_session.get.assert_called_once_with(
        f"{settings.SERVER_API_URL}/leaderboard",
        params={"limit": limit},
        timeout=10
    )

def test_api_get_leaderboard_network_error(monkeypatch):
    """Test leaderboard fetch network error."""
    mock_session = MagicMock(spec=requests.Session)
    mock_session.get.side_effect = requests.exceptions.ConnectionError
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    leaderboard = network_client.api_get_leaderboard()

    assert leaderboard is None

def test_api_get_leaderboard_json_error(monkeypatch):
    """Test leaderboard fetch with invalid JSON response."""
    mock_session = MagicMock(spec=requests.Session)
    mock_response = create_mock_response(status_code=200)
    mock_response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)
    mock_session.get.return_value = mock_response
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    leaderboard = network_client.api_get_leaderboard()

    assert leaderboard is None

# --- Tests for check_login_status --- (Assume unchanged)

def test_check_login_status_initial(monkeypatch):
    """Test initial login status."""
    logged_in, username = network_client.check_login_status()
    assert logged_in is False
    assert username is None

def test_check_login_status_after_login(monkeypatch):
    """Test login status after a simulated successful login."""
    monkeypatch.setattr(network_client, '_is_logged_in', True)
    monkeypatch.setattr(network_client, '_current_username', 'logged_in_user')

    logged_in, username = network_client.check_login_status()
    assert logged_in is True
    assert username == 'logged_in_user'


# --- Tests for api_logout_user --- (Assume unchanged)

def test_api_logout_user_success(monkeypatch):
    """Test successful logout."""
    monkeypatch.setattr(network_client, '_is_logged_in', True)
    monkeypatch.setattr(network_client, '_current_username', 'tester')

    mock_session = MagicMock(spec=requests.Session)
    mock_response = create_mock_response(
        status_code=200,
        json_data={"success": True, "message": "Logout successful"}
    )
    mock_session.post.return_value = mock_response
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    success, message = network_client.api_logout_user()

    assert success is True
    assert message == "Logout successful"
    assert network_client._is_logged_in is False
    assert network_client._current_username is None
    mock_session.post.assert_called_once_with(f"{settings.SERVER_API_URL}/logout", timeout=10)

def test_api_logout_user_failure_server(monkeypatch):
    """Test logout failure due to server logic."""
    monkeypatch.setattr(network_client, '_is_logged_in', True)
    monkeypatch.setattr(network_client, '_current_username', 'tester')

    mock_session = MagicMock(spec=requests.Session)
    mock_response = create_mock_response(
        status_code=200,
        json_data={"success": False, "message": "Server logout issue"}
    )
    mock_session.post.return_value = mock_response
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    success, message = network_client.api_logout_user()

    assert success is False
    assert message == "Server logout issue"
    assert network_client._is_logged_in is False
    assert network_client._current_username is None

def test_api_logout_user_network_error(monkeypatch):
    """Test logout network error."""
    monkeypatch.setattr(network_client, '_is_logged_in', True)
    monkeypatch.setattr(network_client, '_current_username', 'tester')

    mock_session = MagicMock(spec=requests.Session)
    mock_session.post.side_effect = requests.exceptions.Timeout
    monkeypatch.setattr(network_client, 'api_session', mock_session)

    success, message = network_client.api_logout_user()

    assert success is False
    assert "Network error" in message
    assert network_client._is_logged_in is False
    assert network_client._current_username is None