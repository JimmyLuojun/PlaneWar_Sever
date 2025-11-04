"""Handles network communication between the game client and the server API.

Provides the `NetworkClient` class to interact with the Flask server's API endpoints,
such as user login, score submission, and leaderboard fetching. Uses the 'requests'
library for HTTP calls with session management.

This module follows OOP best practices with proper error handling, type safety,
and clean separation of concerns.
"""

# ============================================================================
# Imports
# ============================================================================

# Standard library
import json
from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict, Any, cast

# Third-party
import requests

# Local
from .settings import SERVER_API_URL


# ============================================================================
# Type Definitions
# ============================================================================

JsonDict = Dict[str, Any]
LeaderboardData = List[JsonDict]


# ============================================================================
# Constants
# ============================================================================

REQUEST_TIMEOUT = 10  # seconds
DEFAULT_HEADERS = {"Content-Type": "application/json"}


# ============================================================================
# Exceptions
# ============================================================================


class NetworkClientError(Exception):
    """Base exception for all network client errors."""

    pass


class AuthenticationError(NetworkClientError):
    """Raised when authentication fails."""

    pass


class NetworkError(NetworkClientError):
    """Raised when network communication fails."""

    pass


class ServerError(NetworkClientError):
    """Raised when the server returns an error."""

    pass


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class LoginResult:
    """Result of a login attempt.

    Attributes:
        success: True if login succeeded
        user_id: User id on success, None on failure
        username: Username on success, None on failure
        message: Status message or error description
    """

    success: bool
    user_id: Optional[int]
    username: Optional[str]
    message: str


@dataclass
class SubmitResult:
    """Result of a score submission.

    Attributes:
        success: True if submission succeeded
        message: Status message or error description
    """

    success: bool
    message: str


@dataclass
class LogoutResult:
    """Result of a logout attempt.

    Attributes:
        success: True if logout succeeded
        message: Status message
    """

    success: bool
    message: str


# ============================================================================
# Concrete Classes
# ============================================================================


class NetworkClient:
    """Client for communicating with the PlaneWar server API.

    This class manages authentication state and provides methods for:
    - User login and logout
    - Score submission
    - Leaderboard retrieval

    The client maintains a persistent session with the server and handles
    all error cases gracefully.

    Example:
        >>> client = NetworkClient()
        >>> result = client.login("player1", "password123")
        >>> if result.success:
        ...     client.submit_score(1000, level=1)
        ...     client.logout()
    """

    # ========================================================================
    # Initialization
    # ========================================================================

    def __init__(self, base_url: str = SERVER_API_URL):
        """Initialize the network client.

        Args:
            base_url: Base URL of the server API (default from settings)
        """
        self.base_url = base_url
        self.session = self._create_session()
        self._username: Optional[str] = None
        self._authenticated: bool = False
        self.user_id: Optional[int] = None

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return (self.user_id is not None) or self._authenticated

    @property
    def username(self) -> Optional[str]:
        """Get the current authenticated username."""
        return self._username

    # ========================================================================
    # Public Methods - Authentication
    # ========================================================================

    def login(self, username: str, password: str) -> LoginResult:
        """Attempt to log in via the server API.

        Args:
            username: Username for login
            password: Password for login

        Returns:
            LoginResult containing success status, username, and message
        """
        login_url = f"{self.base_url}/login"
        payload = {"username": username, "password": password}

        try:
            response = self.session.post(
                login_url,
                json=payload,
                headers=DEFAULT_HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            data = response.json()
            if data.get("success"):
                self._authenticated = True
                self.user_id = data.get("user_id")
                self._username = data.get("username")
                message = data.get("message", "Login successful")
                print(f"Network Client: Login successful for {self._username}")
                return LoginResult(
                    success=True, user_id=self.user_id, username=self._username, message=message
                )
            else:
                self._clear_auth_state()
                message = data.get("message", "Login failed (Unknown reason)")
                return LoginResult(success=False, user_id=None, username=None, message=message)

        except requests.exceptions.HTTPError as http_err:
            self._clear_auth_state()
            error_message = self._extract_error_message(http_err, "HTTP Error")
            print(f"Network Client: Login failed ({error_message})")
            return LoginResult(success=False, user_id=None, username=None, message=error_message)

        except requests.exceptions.Timeout:
            self._clear_auth_state()
            print("Network Client: Login Timeout.")
            return LoginResult(
                success=False, user_id=None, username=None, message="Network Error: Timeout"
            )

        except requests.exceptions.ConnectionError:
            self._clear_auth_state()
            print("Network Client: Login Connection Failed.")
            return LoginResult(
                success=False, user_id=None, username=None, message="Network Error: Connection Failed"
            )

        except requests.exceptions.RequestException as e:
            self._clear_auth_state()
            print(f"Network Client: Login Request Error: {e}")
            return LoginResult(
                success=False, user_id=None, username=None, message=f"Network Error: {e}"
            )

        except json.JSONDecodeError:
            self._clear_auth_state()
            print("Network Client: Error decoding server response during login.")
            return LoginResult(
                success=False, user_id=None, username=None, message="Invalid server response"
            )

    def logout(self) -> LogoutResult:
        """Attempt to log out via the server API.

        Returns:
            LogoutResult containing success status and message
        """
        logout_url = f"{self.base_url}/logout"

        try:
            response = self.session.post(logout_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                print("Network Client: Logout successful.")
                self._clear_auth_state()
                return LogoutResult(success=True, message="Logout successful")
            else:
                message = data.get("message", "Logout failed on server.")
                print(f"Network Client: Logout failed on server - {message}")
                # Still clear client state even if server had an issue
                self._clear_auth_state()
                return LogoutResult(success=False, message=message)

        except requests.exceptions.RequestException as e:
            print(f"Network Client: Network error during logout: {e}")
            # Clear client state on network error too
            self._clear_auth_state()
            return LogoutResult(success=False, message=f"Network error: {e}")

        except json.JSONDecodeError:
            self._clear_auth_state()
            print("Network Client: Error decoding server response during logout.")
            return LogoutResult(success=False, message="Invalid server response")

    # ========================================================================
    # Public Methods - Game Operations
    # ========================================================================

    def submit_score(self, score: int, level: int) -> SubmitResult:
        """Submit a score to the server API.

        The server identifies the user via the session cookie.
        User must be authenticated before calling this method.

        Args:
            score: The score to submit
            level: The level on which the score was achieved

        Returns:
            SubmitResult containing success status and message
        """
        if not self.is_authenticated:
            print("Network Client: Cannot submit score, user not authenticated.")
            return SubmitResult(success=False, message="Not authenticated")

        submit_url = f"{self.base_url}/submit_score"
        payload = {"score": score, "level": level}

        try:
            response = self.session.post(
                submit_url,
                json=payload,
                headers=DEFAULT_HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            # Treat 401 as unauthorized even if raise_for_status isn't configured to raise
            if getattr(response, "status_code", None) == 401:
                self._clear_auth_state()
                return SubmitResult(success=False, message="Not authenticated")
            response.raise_for_status()

            data = response.json()
            if data.get("success"):
                message = data.get("message", "Score submitted")
                print(
                    f"Network Client: Score {score} for level {level} submitted successfully."
                )
                return SubmitResult(success=True, message=message)
            else:
                message = data.get("message", "Score submission failed")
                print(f"Network Client: Failed to submit score - {message}")
                return SubmitResult(success=False, message=message)

        except requests.exceptions.HTTPError as http_err:
            status_code = http_err.response.status_code
            error_message = self._extract_error_message(
                http_err, f"HTTP Error {status_code}"
            )

            if status_code == 401:  # Unauthorized - session expired
                self._clear_auth_state()
                error_message = "Not logged in or session expired"
                print(f"Network Client: Score submission failed ({error_message})")
                return SubmitResult(success=False, message=error_message)
            elif status_code == 400:  # Bad request
                print(
                    f"Network Client: Score submission failed - Invalid data ({error_message})"
                )
                return SubmitResult(
                    success=False, message=f"Invalid data: {error_message}"
                )
            else:
                print(f"Network Client: Score submission failed ({error_message})")
                return SubmitResult(success=False, message=error_message)

        except requests.exceptions.Timeout:
            print("Network Client: Score Submission Timeout.")
            return SubmitResult(success=False, message="Network Error: Timeout")

        except requests.exceptions.ConnectionError:
            print("Network Client: Score Submission Connection Failed.")
            return SubmitResult(
                success=False, message="Network Error: Connection Failed"
            )

        except requests.exceptions.RequestException as e:
            print(f"Network Client: Score Submission Request Error: {e}")
            return SubmitResult(success=False, message=f"Network Error: {e}")

        except json.JSONDecodeError:
            print(
                "Network Client: Error decoding server response during score submission."
            )
            return SubmitResult(success=False, message="Invalid server response")

    def get_leaderboard(self, limit: int = 10) -> Optional[LeaderboardData]:
        """Fetch the leaderboard data from the server API.

        Args:
            limit: The maximum number of scores to retrieve (default: 10)

        Returns:
            A list of dictionaries representing scores, or None on error
        """
        leaderboard_url = f"{self.base_url}/leaderboard"

        try:
            response = self.session.get(
                leaderboard_url, params={"limit": limit}, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Network Client: Error fetching leaderboard: {e}")
            return []

        except json.JSONDecodeError:
            print("Network Client: Error decoding server response for leaderboard.")
            return []

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _create_session(self) -> requests.Session:
        """Create and configure a requests session.

        Returns:
            Configured requests.Session instance
        """
        session = requests.Session()
        # Configure session to bypass proxy for localhost
        # Type checker expects str, but None is valid at runtime to disable proxies
        session.proxies = cast(Dict[str, str], {"http": None, "https": None})
        return session

    def _clear_auth_state(self) -> None:
        """Clear authentication state (username and authenticated flag)."""
        self._authenticated = False
        self._username = None
        self.user_id = None

    def _extract_error_message(self, source: Any, default_message: str) -> str:
        """Extract error message from a response-like source or HTTP error.

        Accepts either an exception with a `.response` attribute or an object
        providing a `.json()` method that returns a dict possibly containing
        a 'message' key.

        Args:
            source: Response-like object or exception
            default_message: Default message if extraction fails

        Returns:
            Extracted error message or default message
        """
        try:
            # Prefer the embedded response only for real HTTPError exceptions
            if isinstance(source, requests.exceptions.HTTPError) and getattr(source, "response", None) is not None:
                obj = source.response
            else:
                obj = source
            data = obj.json()
            if isinstance(data, dict):
                return data.get("message", default_message)
            return default_message
        except Exception:
            return default_message


# ============================================================================
# Public API Functions (Backward Compatibility)
# ============================================================================
# DEPRECATED: These functions maintain the old module-level API for existing code.
# New code should use NetworkClient class directly.

_default_client: Optional[NetworkClient] = None


def _get_default_client() -> NetworkClient:
    """Get or create the default module-level client (for backward compatibility).

    Returns:
        Singleton NetworkClient instance
    """
    global _default_client
    if _default_client is None:
        _default_client = NetworkClient()
    return _default_client


def api_login_user(username: str, password: str) -> Tuple[bool, Optional[str], str]:
    """DEPRECATED: Use NetworkClient.login() instead.

    Args:
        username: Username for login
        password: Password for login

    Returns:
        Tuple of (success, username, message)
    """
    result = _get_default_client().login(username, password)
    return result.success, result.username, result.message


def api_logout_user() -> Tuple[bool, str]:
    """DEPRECATED: Use NetworkClient.logout() instead.

    Returns:
        Tuple of (success, message)
    """
    result = _get_default_client().logout()
    return result.success, result.message


def api_submit_score(score: int, level: int) -> Tuple[bool, str]:
    """DEPRECATED: Use NetworkClient.submit_score() instead.

    Args:
        score: The score to submit
        level: The level on which the score was achieved

    Returns:
        Tuple of (success, message)
    """
    result = _get_default_client().submit_score(score, level)
    return result.success, result.message


def submit_score_to_server(client: NetworkClient, score: int, level: int) -> Tuple[bool, str]:
    """Backward-compatible helper to submit a score using a provided client.

    Args:
        client: NetworkClient instance to use
        score: Score value to submit
        level: Level index

    Returns:
        Tuple of (success, message)
    """
    res = client.submit_score(score, level)
    return res.success, res.message


def api_get_leaderboard(limit: int = 10) -> Optional[LeaderboardData]:
    """DEPRECATED: Use NetworkClient.get_leaderboard() instead.

    Args:
        limit: The maximum number of scores to retrieve

    Returns:
        A list of dictionaries representing scores, or None on error
    """
    return _get_default_client().get_leaderboard(limit)


def check_login_status() -> Tuple[bool, Optional[str]]:
    """DEPRECATED: Use NetworkClient.is_authenticated and .username instead.

    Returns:
        Tuple of (is_authenticated, username)
    """
    client = _get_default_client()
    return client.is_authenticated, client.username
