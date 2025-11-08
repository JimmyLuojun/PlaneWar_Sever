"""Business logic service for leaderboards.

Aggregates and formats leaderboard data from the database
and available level files.
"""

from __future__ import annotations

import os
import re
from typing import Dict, List, Sequence, Tuple

from ...data.repositories import LeaderboardRepository


# ============================================================================
# Constants
# ============================================================================

TOP_N_PLAYERS = 30


# ============================================================================
# Core Logic
# ============================================================================

class LeaderboardService:
    """Handles leaderboard business logic.

    Retrieves and formats leaderboard data for both individual levels
    and overall rankings. Also discovers available game levels.

    Args:
        repo: Repository for leaderboard data access
        project_root: Optional path to project root (auto-detected if not provided)
    """

    def __init__(self, repo: LeaderboardRepository, project_root: str | None = None):
        self.repo = repo
        self.project_root = project_root or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    def get_leaderboard_by_level(self, level_num: int) -> List[Dict[str, object]]:
        """Get top players for a specific level.

        Retrieves the top scoring players for the given level number,
        ranked by score (descending) and timestamp (ascending for ties).

        Args:
            level_num: The level number to get leaderboard for

        Returns:
            List of dictionaries with keys: rank, username, score, timestamp

        Examples:
            >>> service = LeaderboardService(repo)
            >>> leaderboard = service.get_leaderboard_by_level(1)
            >>> leaderboard[0]
            {'rank': 1, 'username': 'alice', 'score': 5000, 'timestamp': ...}
        """
        rows: Sequence[Tuple[str, int, object]] = self.repo.top_by_level(level_num, TOP_N_PLAYERS)
        leaderboard = []
        for i, (username, score, timestamp) in enumerate(rows):
            leaderboard.append(
                {
                    "rank": i + 1,
                    "username": username,
                    "score": score,
                    "timestamp": timestamp,
                }
            )
        return leaderboard

    def get_overall_leaderboard(self) -> List[Dict[str, object]]:
        """Get overall top players across all levels.

        Calculates total scores by summing each player's best score
        per level, then ranks players by total score.

        Returns:
            List of dictionaries with keys: rank, username, score, timestamp

        Examples:
            >>> service = LeaderboardService(repo)
            >>> overall = service.get_overall_leaderboard()
            >>> overall[0]['rank']
            1
        """
        rows: Sequence[Tuple[str, int, object]] = self.repo.overall(TOP_N_PLAYERS)
        leaderboard = []
        for i, (username, total_score, timestamp) in enumerate(rows):
            leaderboard.append(
                {
                    "rank": i + 1,
                    "username": username,
                    "score": total_score,
                    "timestamp": timestamp,
                }
            )
        return leaderboard

    def get_available_levels(self) -> List[int]:
        """Get all available game levels.

        Combines levels from database records and level definition files
        to return a complete list of available levels.

        Returns:
            Sorted list of level numbers

        Examples:
            >>> service = LeaderboardService(repo)
            >>> service.get_available_levels()
            [1, 2, 3, 4, 5, 6]
        """
        db_levels = self.repo.distinct_levels()
        file_levels = self._get_levels_from_files()
        return sorted(set(db_levels) | set(file_levels))

    def _get_levels_from_files(self) -> List[int]:
        """Scan filesystem for level definition files.

        Private helper method that looks for level_N.json files
        in the game/levels directory.

        Returns:
            List of level numbers found in filesystem
        """
        try:
            levels_dir = os.path.join(self.project_root, "src", "plane_war_server", "game", "levels")
            if not os.path.isdir(levels_dir):
                return []
            levels: List[int] = []
            pattern = re.compile(r"level_(\d+)\.json$")
            for name in os.listdir(levels_dir):
                m = pattern.match(name)
                if m:
                    try:
                        levels.append(int(m.group(1)))
                    except ValueError:
                        continue
            return sorted(set(levels))
        except Exception:
            return []


# ============================================================================
# Public API
# ============================================================================

__all__ = ["LeaderboardService"]

