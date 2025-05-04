"""Handles network communication between the game client and the server API.

Provides a class (`NetworkClient`) with methods to interact with the Flask server's
API endpoints, such as user login, score submission, and potentially fetching
leaderboard data. Uses the 'requests' library for HTTP calls.
"""
# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/game/network_client.py
import requests
import json
# Assume settings.py is in the same directory or adjust import path
from .settings import SERVER_API_URL # Use the correct URL from your settings

# --- Create the persistent session object at the module level ---
api_session = requests.Session()
# -------------------------------------------------------------

# --- Store login status within this module ---
# Other modules can import and call check_login_status if needed
_current_username = None
_is_logged_in = False
# --------------------------------------------

def api_login_user(username, password):
    """
    Attempts to log in via the server API using the persistent session.

    Returns:
        tuple: (bool: success, str|None: username, str: message)
               Username is returned on success, None otherwise.
    """
    # --- FIX: Declare globals at the beginning of the function ---
    global _current_username, _is_logged_in
    # -----------------------------------------------------------
    login_url = f"{SERVER_API_URL}/login" # Ensure this endpoint matches your Flask API blueprint
    payload = {"username": username, "password": password}

    try:
        # Use the shared session object
        response = api_session.post(
            login_url,
            json=payload,
            headers={'Content-Type': 'application/json'}, # Content-Type is often set automatically for json=
            timeout=10
        )
        response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)

        data = response.json()
        if data.get("success"):
            _is_logged_in = True # Now modifying the global variable correctly
            _current_username = data.get("username") # Store username from successful login
            print(f"Network Client: Login successful for {_current_username}")
            return True, _current_username, data.get("message", "Login successful")
        else:
            _is_logged_in = False # Modifying global variable
            _current_username = None # Modifying global variable
            return False, None, data.get("message", "Login failed (Unknown reason)")

    # Keep detailed error handling
    except requests.exceptions.HTTPError as http_err:
        _is_logged_in = False; _current_username = None # Modifying global variables
        status_code = http_err.response.status_code
        error_message = f"HTTP Error {status_code}"
        try: error_message = http_err.response.json().get("message", error_message)
        except Exception: pass
        print(f"Network Client: Login failed ({error_message})")
        return False, None, error_message
    except requests.exceptions.Timeout:
        _is_logged_in = False; _current_username = None # Modifying global variables
        print("Network Client: Login Timeout.")
        return False, None, "Network Error: Timeout"
    except requests.exceptions.ConnectionError:
        _is_logged_in = False; _current_username = None # Modifying global variables
        print("Network Client: Login Connection Failed.")
        return False, None, "Network Error: Connection Failed"
    except requests.exceptions.RequestException as e:
        _is_logged_in = False; _current_username = None # Modifying global variables
        print(f"Network Client: Login Request Error: {e}")
        return False, None, f"Network Error: {e}"
    except json.JSONDecodeError:
        _is_logged_in = False; _current_username = None # Modifying global variables
        print("Network Client: Error decoding server response during login.")
        return False, None, "Invalid server response"

def api_submit_score(score, level_completed):
    """
    Submits the score to the server API using the persistent session.
    The server identifies the user via the session cookie.

    Args:
        score (int): The score to submit.
        level_completed (int): The level on which the score was achieved.

    Returns:
        tuple: (bool: success, str: message)
    """
    # --- FIX: Declare globals at the beginning if they might be modified (e.g., on 401 error) ---
    global _is_logged_in, _current_username
    # --------------------------------------------------------------------------------------
    if not _is_logged_in: # Reading global is fine without declaration if not assigned locally
         print("Network Client: Cannot submit score, user not logged in.")
         return False, "Not logged in"

    submit_url = f"{SERVER_API_URL}/submit_score" # Ensure endpoint matches Flask API
    payload = {
        "score": score,
        "level": level_completed
    }

    try:
        response = api_session.post(
            submit_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        if data.get("success"):
            print(f"Network Client: Score {score} for level {level_completed} submitted successfully.")
            return True, data.get("message", "Score submitted")
        else:
            print(f"Network Client: Failed to submit score - {data.get('message')}")
            return False, data.get("message", "Score submission failed")

    except requests.exceptions.HTTPError as http_err:
        status_code = http_err.response.status_code
        error_message = f"HTTP Error {status_code}"
        try: error_message = http_err.response.json().get("message", error_message)
        except Exception: pass

        if status_code == 401: # Unauthorized
            # Modifying globals here
            _is_logged_in = False
            _current_username = None
            error_message = "Not logged in or session expired"
            print(f"Network Client: Score submission failed ({error_message})")
            return False, error_message
        elif status_code == 400:
             print(f"Network Client: Score submission failed - Invalid data ({error_message})")
             return False, f"Invalid data: {error_message}"
        else:
            print(f"Network Client: Score submission failed ({error_message})")
            return False, error_message
    except requests.exceptions.Timeout:
        print("Network Client: Score Submission Timeout.")
        return False, "Network Error: Timeout"
    except requests.exceptions.ConnectionError:
        print("Network Client: Score Submission Connection Failed.")
        return False, "Network Error: Connection Failed"
    except requests.exceptions.RequestException as e:
        print(f"Network Client: Score Submission Request Error: {e}")
        return False, f"Network Error: {e}"
    except json.JSONDecodeError:
         print("Network Client: Error decoding server response during score submission.")
         return False, "Invalid server response"


def api_get_leaderboard(limit=10):
    """
    Fetches the leaderboard data from the server API using the persistent session.
    (Using session is good practice, even if endpoint isn't protected).

    Args:
        limit (int): The maximum number of scores to retrieve.

    Returns:
        list | None: A list of dictionaries representing scores, or None on error.
    """
    # This function READS globals (_is_logged_in) but doesn't MODIFY them,
    # so 'global' declaration is not strictly needed here unless you plan
    # to modify them based on leaderboard results (unlikely).
    leaderboard_url = f"{SERVER_API_URL}/leaderboard"
    try:
        response = api_session.get(
            leaderboard_url,
            params={"limit": limit},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Network Client: Error fetching leaderboard: {e}")
        return None
    except json.JSONDecodeError:
        print("Network Client: Error decoding server response for leaderboard.")
        return None

def check_login_status():
    """Returns the current login status and username stored in this module."""
    # This function only READS globals, no 'global' needed.
    return _is_logged_in, _current_username

def api_logout_user():
    """Attempts to log out via the server API using the persistent session."""
    # --- FIX: Declare globals at the beginning of the function ---
    global _is_logged_in, _current_username
    # -----------------------------------------------------------
    logout_url = f"{SERVER_API_URL}/logout" # Ensure you have this API endpoint
    try:
        response = api_session.post(logout_url, timeout=10) # Use session
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            print("Network Client: Logout successful.")
            _is_logged_in = False # Modifying global
            _current_username = None # Modifying global
            return True, "Logout successful"
        else:
            print(f"Network Client: Logout failed on server - {data.get('message')}")
            # Still clear client state even if server had an issue
            _is_logged_in = False # Modifying global
            _current_username = None # Modifying global
            return False, data.get("message", "Logout failed on server.")
    except requests.exceptions.RequestException as e:
        print(f"Network Client: Network error during logout: {e}")
        # Clear client state on network error too
        _is_logged_in = False # Modifying global
        _current_username = None # Modifying global
        return False, f"Network error: {e}"
    except json.JSONDecodeError:
        _is_logged_in = False; _current_username = None # Modifying global
        print("Network Client: Error decoding server response during logout.")
        return False, "Invalid server response"