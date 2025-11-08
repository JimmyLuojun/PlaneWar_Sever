"""Repository layer for database access.

Encapsulates SQL/ORM operations for users, scores, and leaderboard queries.
Provides clean abstractions over SQLAlchemy operations.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Score, User


# ============================================================================
# Core Logic
# ============================================================================

class UserRepository:
    """Repository for user data access.

    Handles all database operations related to User entities.

    Args:
        session: SQLAlchemy database session
    """

    def __init__(self, session: Session):
        self.session = session

    def get_by_username(self, username: str) -> Optional[User]:
        """Fetch a user by username.

        Args:
            username: The username to search for

        Returns:
            User object if found, None otherwise

        Examples:
            >>> repo = UserRepository(session)
            >>> user = repo.get_by_username("alice")
            >>> user.username if user else None
            'alice'
        """
        return self.session.query(User).filter_by(username=username).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Fetch a user by ID.

        Args:
            user_id: The user ID to search for

        Returns:
            User object if found, None otherwise

        Examples:
            >>> repo = UserRepository(session)
            >>> user = repo.get_by_id(1)
            >>> user.id if user else None
            1
        """
        return self.session.get(User, user_id)

    def add(self, user: User) -> None:
        """Add a new user to the database.

        Commits the transaction immediately.

        Args:
            user: The User object to persist

        Examples:
            >>> repo = UserRepository(session)
            >>> new_user = User(username="bob")
            >>> repo.add(new_user)
        """
        self.session.add(user)
        self.session.commit()


class ScoreRepository:
    """Repository for score data access.

    Handles all database operations related to Score entities.

    Args:
        session: SQLAlchemy database session
    """

    def __init__(self, session: Session):
        self.session = session

    def add(self, score: Score) -> None:
        """Add a new score to the database.

        Commits the transaction immediately.

        Args:
            score: The Score object to persist

        Examples:
            >>> repo = ScoreRepository(session)
            >>> new_score = Score(user_id=1, score_value=1000, level=1)
            >>> repo.add(new_score)
        """
        self.session.add(score)
        self.session.commit()


class LeaderboardRepository:
    """Repository for leaderboard queries.

    Executes complex aggregation queries to generate leaderboard data
    for specific levels and overall rankings.

    Args:
        session: SQLAlchemy database session
    """

    def __init__(self, session: Session):
        self.session = session

    def top_by_level(self, level_num: int, limit: int = 30) -> Sequence[Tuple[str, int, object]]:
        """Get top players for a specific level.

        Retrieves players ranked by their maximum score for the given level.
        In case of ties, earlier timestamps rank higher.

        Args:
            level_num: The level number to query
            limit: Maximum number of results to return (default: 30)

        Returns:
            List of tuples containing (username, max_score, earliest_timestamp)
            sorted by score (descending) and timestamp (ascending)

        Examples:
            >>> repo = LeaderboardRepository(session)
            >>> top_players = repo.top_by_level(1, limit=10)
            >>> top_players[0]
            ('alice', 5000, datetime(...))
        """
        subq_max_score = (
            self.session.query(Score.user_id, func.max(Score.score_value).label("max_score"))
            .filter(Score.level == level_num)
            .group_by(Score.user_id)
            .subquery()
        )

        subq_earliest_timestamp = (
            self.session.query(Score.user_id, func.min(Score.timestamp).label("earliest_timestamp"))
            .join(
                subq_max_score,
                (Score.user_id == subq_max_score.c.user_id)
                & (Score.score_value == subq_max_score.c.max_score),
            )
            .filter(Score.level == level_num)
            .group_by(Score.user_id)
            .subquery()
        )

        return (
            self.session.query(
                User.username,
                subq_max_score.c.max_score,
                subq_earliest_timestamp.c.earliest_timestamp,
            )
            .select_from(User)
            .join(subq_max_score, User.id == subq_max_score.c.user_id)
            .join(subq_earliest_timestamp, User.id == subq_earliest_timestamp.c.user_id)
            .order_by(
                subq_max_score.c.max_score.desc(),
                subq_earliest_timestamp.c.earliest_timestamp.asc(),
            )
            .limit(limit)
            .all()
        )

    def overall(self, limit: int = 30) -> Sequence[Tuple[str, int, object]]:
        """Get overall top players across all levels.

        Calculates total scores by summing each player's best score per level,
        then ranks players by total score. Ties are broken by earliest timestamp.

        Args:
            limit: Maximum number of results to return (default: 30)

        Returns:
            List of tuples containing (username, total_score, earliest_timestamp)
            sorted by total score (descending) and timestamp (ascending)

        Examples:
            >>> repo = LeaderboardRepository(session)
            >>> overall = repo.overall(limit=10)
            >>> overall[0]
            ('alice', 15000, datetime(...))
        """
        subq_max_per_level = (
            self.session.query(
                Score.user_id, Score.level, func.max(Score.score_value).label("max_score_for_level")
            )
            .group_by(Score.user_id, Score.level)
            .subquery()
        )

        subq_max_score_timestamps = (
            self.session.query(
                Score.user_id,
                Score.level,
                func.min(Score.timestamp).label("earliest_timestamp_for_max"),
            )
            .join(
                subq_max_per_level,
                (Score.user_id == subq_max_per_level.c.user_id)
                & (Score.level == subq_max_per_level.c.level)
                & (Score.score_value == subq_max_per_level.c.max_score_for_level),
            )
            .group_by(Score.user_id, Score.level)
            .subquery()
        )

        subq_overall = (
            self.session.query(
                subq_max_per_level.c.user_id,
                func.sum(subq_max_per_level.c.max_score_for_level).label("total_score"),
                func.min(subq_max_score_timestamps.c.earliest_timestamp_for_max).label(
                    "earliest_best_score_timestamp"
                ),
            )
            .select_from(subq_max_per_level)
            .join(
                subq_max_score_timestamps,
                (subq_max_per_level.c.user_id == subq_max_score_timestamps.c.user_id)
                & (subq_max_per_level.c.level == subq_max_score_timestamps.c.level),
            )
            .group_by(subq_max_per_level.c.user_id)
            .subquery()
        )

        return (
            self.session.query(
                User.username,
                subq_overall.c.total_score,
                subq_overall.c.earliest_best_score_timestamp,
            )
            .select_from(User)
            .join(subq_overall, User.id == subq_overall.c.user_id)
            .order_by(
                subq_overall.c.total_score.desc(),
                subq_overall.c.earliest_best_score_timestamp.asc(),
            )
            .limit(limit)
            .all()
        )

    def distinct_levels(self) -> List[int]:
        """Get all distinct level numbers that have scores.

        Returns:
            Sorted list of level numbers that appear in the scores table

        Examples:
            >>> repo = LeaderboardRepository(session)
            >>> repo.distinct_levels()
            [1, 2, 3, 4, 5, 6]
        """
        levels = self.session.query(Score.level).distinct().order_by(Score.level.asc()).all()
        return [level[0] for level in levels]


# ============================================================================
# Public API
# ============================================================================

__all__ = ["UserRepository", "ScoreRepository", "LeaderboardRepository"]

