"""Service for user progress operations.

Manages user game progress tracking, specifically which levels
have been unlocked for each player.
"""

from __future__ import annotations

from ...data import progress_store as _ps


# ============================================================================
# Core Logic
# ============================================================================

class ProgressService:
    """Handles user progress business logic.

    Manages tracking of which game levels each user has unlocked.
    Delegates storage to the progress_store module.
    """

    def get_max_level(self, user_id: int) -> int:
        """Get the maximum unlocked level for a user.

        Args:
            user_id: The ID of the user to check

        Returns:
            The highest level number unlocked by this user

        Examples:
            >>> service = ProgressService()
            >>> service.get_max_level(1)
            3
        """
        return _ps.get_max_unlocked_level_for_user(user_id)

    def set_max_level(self, user_id: int, value: int) -> int:
        """Set the maximum unlocked level for a user.

        Updates the user's progress to unlock up to the specified level.

        Args:
            user_id: The ID of the user to update
            value: The new maximum unlocked level

        Returns:
            The stored maximum level value (same as input if successful)

        Examples:
            >>> service = ProgressService()
            >>> service.set_max_level(1, 5)
            5
        """
        return _ps.set_max_unlocked_level_for_user(user_id, value)


# ============================================================================
# Public API
# ============================================================================

__all__ = ["ProgressService"]
