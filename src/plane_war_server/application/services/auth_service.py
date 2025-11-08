"""Service for authentication-related business logic.

Handles user registration and login verification.
"""

from __future__ import annotations

from typing import Optional

from ...data.models import User
from ...data.repositories import UserRepository


# ============================================================================
# Core Logic
# ============================================================================

class AuthService:
    """Handles user authentication business logic.

    Manages user registration and login verification without
    direct database access.

    Args:
        users: Repository for user data access
    """

    def __init__(self, users: UserRepository):
        self.users = users

    def register(self, username: str, password: str) -> Optional[User]:
        """Register a new user.

        Creates a new user account if the username is available
        and credentials are valid.

        Args:
            username: Desired username for the new account
            password: Password for the new account

        Returns:
            The created User object if successful, None if validation fails
            or username already exists

        Examples:
            >>> auth = AuthService(user_repo)
            >>> user = auth.register("alice", "secure123")
            >>> user.username
            'alice'
        """
        if not username or not password:
            return None
        if self.users.get_by_username(username) is not None:
            return None
        user = User(username=username)
        user.set_password(password)
        self.users.add(user)
        return user

    def verify_login(self, username: str, password: str) -> Optional[User]:
        """Verify user login credentials.

        Checks if the username exists and the password is correct.

        Args:
            username: Username to verify
            password: Password to verify

        Returns:
            The User object if credentials are valid, None otherwise

        Examples:
            >>> auth = AuthService(user_repo)
            >>> user = auth.verify_login("alice", "secure123")
            >>> user.username if user else "Login failed"
            'alice'
        """
        user = self.users.get_by_username(username)
        if user and user.check_password(password):
            return user
        return None


# ============================================================================
# Public API
# ============================================================================

__all__ = ["AuthService"]

