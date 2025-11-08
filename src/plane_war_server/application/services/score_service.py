"""Service for score submission and validation business logic.

Handles score submission with user validation and error handling.
"""

from __future__ import annotations

from typing import Optional

from ...data.models import Score
from ...data.repositories import ScoreRepository, UserRepository


# ============================================================================
# Custom Exceptions
# ============================================================================

class ScoreSubmissionError(Exception):
    """Raised when score submission fails."""


class UserNotFoundError(Exception):
    """Raised when user doesn't exist."""


# ============================================================================
# Core Logic
# ============================================================================

class ScoreService:
    """Handles score submission business logic.

    Args:
        users: Repository for user data access
        scores: Repository for score data access
    """

    def __init__(self, users: UserRepository, scores: ScoreRepository):
        self.users = users
        self.scores = scores

    def submit_score(
        self, user_id: int, score_value: int, level: int
    ) -> Score:
        """Submit a score for a user.

        Args:
            user_id: The ID of the user submitting the score
            score_value: The score value to submit
            level: The level number the score was achieved on

        Returns:
            The created Score object

        Raises:
            UserNotFoundError: If the user_id doesn't exist
            ScoreSubmissionError: If score submission fails
            ValueError: If inputs are invalid (negative values, etc.)
        """
        # Validate inputs
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        if score_value < 0:
            raise ValueError("Score value cannot be negative")
        if level <= 0:
            raise ValueError("Level must be positive")

        # Check user exists
        user = self.users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        # Create and save score
        try:
            new_score = Score(
                user_id=user.id, score_value=score_value, level=level
            )
            self.scores.add(new_score)
            return new_score
        except Exception as e:
            raise ScoreSubmissionError(f"Failed to save score: {e}") from e


# ============================================================================
# Public API
# ============================================================================

__all__ = ["ScoreService", "ScoreSubmissionError", "UserNotFoundError"]
