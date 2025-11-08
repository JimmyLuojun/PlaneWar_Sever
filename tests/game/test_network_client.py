"""Tests for game/network_client.py - HTTP API client."""

import pytest
from unittest.mock import patch, Mock
import requests
from plane_war_server.game.infrastructure.network_client import (
    NetworkClient,
    NetworkClientError,
    AuthenticationError,
    NetworkError,
    ServerError,
    LoginResult,
    SubmitResult,
    LogoutResult
)


class TestNetworkClientInit:
    """Tests for NetworkClient initialization."""

    def test_network_client_init(self):
        """Test network client initialization."""
        client = NetworkClient("http://localhost:8000")

        assert client.base_url == "http://localhost:8000"
        assert client.user_id is None
        assert client._username is None
        assert not client.is_authenticated

    def test_network_client_creates_session(self):
        """Test network client creates requests session."""
        client = NetworkClient("http://localhost:8000")

        assert client.session is not None


class TestNetworkClientLogin:
    """Tests for NetworkClient.login method."""

    @patch('requests.Session.post')
    def test_login_success(self, mock_post):
        """Test successful login."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'user_id': 123,
            'username': 'testuser'
        }
        mock_post.return_value = mock_response

        client = NetworkClient("http://localhost:8000")
        result = client.login("testuser", "password")

        assert result.success is True
        assert result.user_id == 123
        assert result.username == 'testuser'
        assert client.is_authenticated
        assert client.user_id == 123

    @patch('requests.Session.post')
    def test_login_invalid_credentials(self, mock_post):
        """Test login with invalid credentials."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'success': False, 'message': 'Invalid credentials'}
        mock_post.return_value = mock_response

        client = NetworkClient("http://localhost:8000")
        result = client.login("testuser", "wrongpass")

        assert result.success is False
        assert not client.is_authenticated
        assert client.user_id is None

    @patch('requests.Session.post', side_effect=requests.Timeout)
    def test_login_timeout_error(self, mock_post):
        """Test login handles timeout error."""
        client = NetworkClient("http://localhost:8000")
        result = client.login("testuser", "password")

        assert result.success is False
        assert 'timeout' in result.message.lower()

    @patch('requests.Session.post', side_effect=requests.ConnectionError)
    def test_login_connection_error(self, mock_post):
        """Test login handles connection error."""
        client = NetworkClient("http://localhost:8000")
        result = client.login("testuser", "password")

        assert result.success is False
        assert 'connection' in result.message.lower()

    @patch('requests.Session.post')
    def test_login_server_error(self, mock_post):
        """Test login handles server error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {'message': 'Internal server error'}
        mock_post.return_value = mock_response

        client = NetworkClient("http://localhost:8000")
        result = client.login("testuser", "password")

        assert result.success is False


class TestNetworkClientLogout:
    """Tests for NetworkClient.logout method."""

    @patch('requests.Session.post')
    def test_logout_success(self, mock_post):
        """Test successful logout."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response

        client = NetworkClient("http://localhost:8000")
        client.user_id = 123
        client._username = 'testuser'

        result = client.logout()

        assert result.success is True
        assert client.user_id is None
        assert client._username is None

    @patch('requests.Session.post', side_effect=requests.ConnectionError)
    def test_logout_clears_state_on_error(self, mock_post):
        """Test logout clears auth state even on error."""
        client = NetworkClient("http://localhost:8000")
        client.user_id = 123
        client._username = 'testuser'

        result = client.logout()

        assert client.user_id is None
        assert client._username is None


class TestNetworkClientSubmitScore:
    """Tests for NetworkClient.submit_score method."""

    @patch('requests.Session.post')
    def test_submit_score_success(self, mock_post):
        """Test successful score submission."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response

        client = NetworkClient("http://localhost:8000")
        client.user_id = 123

        result = client.submit_score(1000, 1)

        assert result.success is True

    @patch('requests.Session.post')
    def test_submit_score_requires_authentication(self, mock_post):
        """Test submit score requires authentication."""
        client = NetworkClient("http://localhost:8000")

        result = client.submit_score(1000, 1)

        assert result.success is False
        assert 'not authenticated' in result.message.lower()

    @patch('requests.Session.post')
    def test_submit_score_session_expired(self, mock_post):
        """Test submit score handles expired session."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'success': False}
        mock_post.return_value = mock_response

        client = NetworkClient("http://localhost:8000")
        client.user_id = 123

        result = client.submit_score(1000, 1)

        assert result.success is False
        assert client.user_id is None

    @patch('requests.Session.post')
    def test_submit_score_validation_error(self, mock_post):
        """Test submit score handles validation error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'success': False, 'message': 'Invalid data'}
        mock_post.return_value = mock_response

        client = NetworkClient("http://localhost:8000")
        client.user_id = 123

        result = client.submit_score(-1, 0)

        assert result.success is False


class TestNetworkClientGetLeaderboard:
    """Tests for NetworkClient.get_leaderboard method."""

    @patch('requests.Session.get')
    def test_get_leaderboard_success(self, mock_get):
        """Test successful leaderboard retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'rank': 1, 'username': 'player1', 'score': 1000}
        ]
        mock_get.return_value = mock_response

        client = NetworkClient("http://localhost:8000")
        result = client.get_leaderboard()

        assert len(result) == 1
        assert result[0]['username'] == 'player1'

    @patch('requests.Session.get', side_effect=requests.ConnectionError)
    def test_get_leaderboard_connection_error(self, mock_get):
        """Test get leaderboard handles connection error."""
        client = NetworkClient("http://localhost:8000")
        result = client.get_leaderboard()

        assert result == []


class TestNetworkClientProperties:
    """Tests for NetworkClient properties."""

    def test_is_authenticated_false_by_default(self):
        """Test is_authenticated is False by default."""
        client = NetworkClient("http://localhost:8000")

        assert not client.is_authenticated

    def test_is_authenticated_true_when_logged_in(self):
        """Test is_authenticated is True when logged in."""
        client = NetworkClient("http://localhost:8000")
        client.user_id = 123

        assert client.is_authenticated

    def test_username_property(self):
        """Test username property returns username."""
        client = NetworkClient("http://localhost:8000")
        client._username = 'testuser'

        assert client.username == 'testuser'


class TestNetworkClientHelpers:
    """Tests for NetworkClient helper methods."""

    def test_extract_error_message_from_json(self):
        """Test extracting error message from JSON response."""
        client = NetworkClient("http://localhost:8000")
        mock_response = Mock()
        mock_response.json.return_value = {'message': 'Error occurred'}

        message = client._extract_error_message(mock_response, 'Default')

        assert message == 'Error occurred'

    def test_extract_error_message_default(self):
        """Test extracting error message returns default."""
        client = NetworkClient("http://localhost:8000")
        mock_response = Mock()
        mock_response.json.return_value = {}

        message = client._extract_error_message(mock_response, 'Default message')

        assert message == 'Default message'

    def test_extract_error_message_json_error(self):
        """Test extracting error message handles JSON decode error."""
        client = NetworkClient("http://localhost:8000")
        mock_response = Mock()
        mock_response.json.side_effect = ValueError

        message = client._extract_error_message(mock_response, 'Default')

        assert message == 'Default'


class TestBackwardCompatibility:
    """Tests for backward compatibility functions."""

    @patch('requests.Session.post')
    def test_backward_compat_submit_score_success(self, mock_post):
        """Test backward compatible submit_score_to_server."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response

        from plane_war_server.game.infrastructure.network_client import submit_score_to_server

        client = NetworkClient("http://localhost:8000")
        client.user_id = 123

        success, message = submit_score_to_server(client, 1000, 1)

        assert success is True
