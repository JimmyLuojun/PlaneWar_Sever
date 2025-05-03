"""
Network client for handling server communication
"""

import requests
from .settings import SERVER_URL

class NetworkClient:
    def __init__(self):
        self.base_url = SERVER_URL
        self.session = requests.Session()
    
    def login(self, username, password):
        """Authenticate user with the server."""
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        return response.json()
    
    def register(self, username, email, password):
        """Register a new user with the server."""
        response = self.session.post(
            f"{self.base_url}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )
        return response.json()
    
    def submit_score(self, score, level):
        """Submit a game score to the server."""
        response = self.session.post(
            f"{self.base_url}/api/scores",
            json={
                "score": score,
                "level": level
            }
        )
        return response.json()
    
    def get_leaderboard(self):
        """Get the current leaderboard from the server."""
        response = self.session.get(f"{self.base_url}/api/leaderboard")
        return response.json() 