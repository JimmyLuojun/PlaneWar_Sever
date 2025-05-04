# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/game/network_client.py
import requests
import json
# Assume settings.py is in the same directory or adjust import path
from .settings import SERVER_API_URL # This relative import is correct

def api_login_user(username, password):
    """
    Attempts to log in via the server API.

    Returns:
        tuple: (bool: success, int|None: user_id, str|None: username, str: message)
    """
    try:
        response = requests.post(
            f"{SERVER_API_URL}/login",
            json={"username": username, "password": password},
            headers={'Content-Type': 'application/json'},
            timeout=10 # Add a timeout
        )
        response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
        data = response.json()
        if data.get("success"):
            return True, data.get("user_id"), data.get("username"), "Login successful"
        else:
            # Use the message from the server if available
            return False, None, None, data.get("message", "Login failed (Unknown reason)")
    except requests.exceptions.Timeout:
        print("Network Error during login: Connection timed out.")
        return False, None, None, "Network Error: Timeout"
    except requests.exceptions.ConnectionError:
        print("Network Error during login: Could not connect to server.")
        return False, None, None, "Network Error: Connection Failed"
    except requests.exceptions.RequestException as e:
        # Catch other request errors (like 401, 404 if not handled by success flag)
        status_code = e.response.status_code if e.response is not None else "N/A"
        server_msg = "Unknown Server Error"
        if e.response is not None:
            try:
                 server_data = e.response.json()
                 server_msg = server_data.get("message", f"HTTP Error {status_code}")
            except json.JSONDecodeError:
                 server_msg = f"HTTP Error {status_code} (Invalid Response)"

        print(f"Network Error during login: {e} (Status: {status_code})")
        return False, None, None, f"Network Error: {server_msg}"
    except json.JSONDecodeError:
         print("Error decoding server response during login.")
         return False, None, None, "Invalid server response"


def api_submit_score(user_id, score, level_reached=None):
    """
    Submits the score to the server API using the insecure user_id method.

    !! SECURITY WARNING: This method is insecure for production.
    !! Use token-based authentication instead.

    Args:
        user_id (int): The ID of the logged-in user.
        score (int): The score to submit.
        level_reached (int, optional): The highest level reached. Defaults to None.

    Returns:
        tuple: (bool: success, str: message)
    """
    if user_id is None:
         print("Cannot submit score, user not logged in (no user_id).")
         return False, "Not logged in"

    payload = {"user_id": user_id, "score": score}
    if level_reached is not None:
        payload["level_reached"] = level_reached

    try:
        response = requests.post(
            f"{SERVER_API_URL}/submit_score",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            print(f"Score {score} submitted successfully.")
            return True, data.get("message", "Score submitted")
        else:
            print(f"Failed to submit score: {data.get('message')}")
            return False, data.get("message", "Score submission failed")
    except requests.exceptions.Timeout:
        print("Network Error during score submission: Connection timed out.")
        return False, "Network Error: Timeout"
    except requests.exceptions.ConnectionError:
        print("Network Error during score submission: Could not connect to server.")
        return False, "Network Error: Connection Failed"
    except requests.exceptions.RequestException as e:
        status_code = e.response.status_code if e.response is not None else "N/A"
        server_msg = "Unknown Server Error"
        if e.response is not None:
            try:
                 server_data = e.response.json()
                 server_msg = server_data.get("message", f"HTTP Error {status_code}")
            except json.JSONDecodeError:
                 server_msg = f"HTTP Error {status_code} (Invalid Response)"
        print(f"Network Error during score submission: {e} (Status: {status_code})")
        return False, f"Network Error: {server_msg}"
    except json.JSONDecodeError:
         print("Error decoding server response during score submission.")
         return False, "Invalid server response"


def api_get_leaderboard(limit=10):
    """
    Fetches the leaderboard data from the server API.

    Args:
        limit (int): The maximum number of scores to retrieve.

    Returns:
        list | None: A list of dictionaries representing scores, or None on error.
                      Each dict might contain keys like 'rank', 'username', 'score', 'date'.
    """
    try:
        response = requests.get(
            f"{SERVER_API_URL}/leaderboard",
            params={"limit": limit},
            timeout=10
        )
        response.raise_for_status()
        return response.json() # Returns list of score dicts or raises error
    except requests.exceptions.RequestException as e:
        print(f"Network Error fetching leaderboard: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding server response for leaderboard.")
        return None
